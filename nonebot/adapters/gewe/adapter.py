import asyncio
from datetime import datetime
from typing import Any
from typing_extensions import override

import qrcode
import ujson as json
from nonebot import get_plugin_config
from nonebot.compat import type_validate_python
from nonebot.drivers import URL, Driver, Request, Response, ASGIMixin, HTTPClientMixin, HTTPServerSetup, ASGIMixin

from nonebot.adapters import Adapter as BaseAdapter
from nonebot.log import logger
from pydantic import ValidationError
from qrcode.compat.png import PngWriter

from .bot import Bot
from .event import Event
from .config import Config
from .utils import log, resp_json
from .model import *
from .exception import ActionFailed, NetworkError
from .event_store import EventStorage


if PngWriter:
    from qrcode.image.pure import PyPNGImage
else:
    PyPNGImage = None


class Adapter(BaseAdapter):
    bots: dict[str, Bot]
    tasks: set[asyncio.Task]
    event_store: EventStorage

    @override
    def __init__(self, driver: Driver, **kwargs: Any):
        super().__init__(driver, **kwargs)
        self.event_store = EventStorage()
        self.token = ""
        self.adapter_config = get_plugin_config(Config)
        self.tasks = set()
        self.setup()

    def setup(self):
        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(f"Current driver {self.config.driver} does not support " "http client requests! " "Gewechat Adapter need a HTTPClient Driver to work.")
        if not isinstance(self.driver, ASGIMixin):
            raise RuntimeError(f"Current driver {self.config.driver} does not support " "ASGI server! " "Gewechat Adapter need a ASGI server Driver to work.")
        self.on_ready(self.startup)
        self.driver.on_shutdown(self.shutdown)

    async def shutdown(self) -> None:
        """定义退出时的操作，例如和平台断开连接"""
        for task in self.tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(
            *(asyncio.wait_for(task, timeout=10) for task in self.tasks),
            return_exceptions=True,
        )
        self.tasks.clear()

    async def startup(self) -> None:
        """定义启动时的操作，例如和平台建立连接"""

        await self._setup_http()
        await self._setup_bot()
        # http服务启动后,设置回调地址
        self.tasks.add(asyncio.create_task(self._setup_callback()))
        # 添加定时清理任务
        self.tasks.add(asyncio.create_task(self._schedule_cleanup()))

    async def _setup_http(self) -> None:
        if not isinstance(self.driver, ASGIMixin):
            raise RuntimeError(f"Current driver {self.config.driver} doesn't support ASGI server!" f"{self.get_name()} Adapter need a ASGI server driver to work.")

        http_setup = HTTPServerSetup(URL("/gewechat" + self.adapter_config.gewechat_callback_path), method="POST", name="gewechat_callback", handle_func=self._handle_http)

        self.setup_http_server(http_setup)

    async def _setup_bot(self) -> None:
        if not isinstance(self.driver, HTTPClientMixin):
            raise RuntimeError(f"Current driver {self.config.driver} doesn't support HTTPClient server!" f"{self.get_name()} Adapter need a HTTPClient driver to work.")

        connected: bool = False
        wxid = self.adapter_config.wxid
        appId = self.adapter_config.appid
        # 1. 获取token
        log("DEBUG", "获取token")
        self.get_token()
        
        # 2. 获取二维码
        log("DEBUG", "获取二维码")
        data: dict = resp_json(await self._do_call_api("/login/getLoginQrCode", appId=appId, regionId=self.adapter_config.gewechat_region_id, proxyIp=self.adapter_config.gewechat_proxy))

        if data["ret"] != 200 and data["msg"] == "账户已达登录上限":
            log("INFO", "GEWE服务端已登录,尝试通过配置中的APPID获取账号信息")
            data: dict = resp_json(await self._do_call_api("/personal/getProfile", appId=appId))
            bot = Bot(self, data["data"]["wxid"])
            self.bot_connect(bot)
            log("INFO", "登入成功")
            return

        elif data["ret"] == 200:
            appId: str = data["data"]["appId"]
            qr_code = qrcode.QRCode()
            qr_code.add_data(data["data"]["qrData"])
            qr_code.print_ascii(invert=True)
            if PyPNGImage:
                log("INFO", "正在保存二维码到文件 qrcode.png")
                with open("qrcode.png", "wb") as f:
                    qr_code.make_image(PyPNGImage).save(f)
            log("INFO", "请使用微信扫描二维码登录")
            captchCode: str = input("扫码后输入验证码(如果有): ")
        else:
            log("INFO", "当前未登入任何账号，尝试")
            appId = self.adapter_config.appid
            connected = True

        count: int = 0
        # 3. 轮询登录状态
        while connected is False:
            log("DEBUG", "轮询登录状态")
            data: dict = resp_json(await self._do_call_api("/login/checkLogin", appId=appId, uuid=data["data"]["uuid"], captchCode=captchCode, proxyIp=self.adapter_config.gewechat_proxy))
            count += 1
            if data["ret"] == 200:
                if data["data"]["status"] == 2:
                    wxid = data["data"]["loginInfo"]["wxid"]
                    log("INFO", "登录成功")
                    log("INFO", f"登录用户: {data['data']['loginInfo']['nickName']}\n" + f"wxid: {wxid}\tappId: {appId}\n" + "请妥善保管登录信息,频繁更换appId可能导致风控\n" + "填写appId,wxid到配置文件中,重启即可使用")
                    break
            elif count > 15:
                log("ERROR", "登录失败,请重启后重新扫码登录")
                raise NetworkError("登录失败")
            else:
                await asyncio.sleep(5)

        bot = Bot(self, wxid)
        self.bot_connect(bot)

    async def _setup_callback(self):
        count = 0
        # 4. 设置回调地址
        log("INFO", "设置回调地址")
        while True:
            data = resp_json(await self._do_call_api("/login/setCallback", token=self.token, callbackUrl=self.adapter_config.gewechat_callback_url))
            log("INFO", f"设置回调地址返回: {data}")

            count += 1
            if data["ret"] == 200:
                log("INFO", "设置回调地址成功")

                break
            elif count > 15:
                log("ERROR", "设置回调地址超时,检查配置是否正确")
                raise NetworkError("设置回调地址失败")
            else:
                await asyncio.sleep(5)

    @classmethod
    @override
    def get_name(cls) -> str:
        return "gewechat"

    def get_token(self) -> None:
        """获取token"""
        self.token = self.adapter_config.gewechat_token
        return self.adapter_config.gewechat_token

    @override
    async def _call_api(self, bot: Bot, api: str, **data: Any) -> Response:
        re = await self._do_call_api(api, **data)
        if re.status_code != 200:
            raise ActionFailed(f"调用API失败: {re.status_code}")
        else:
            content = json.loads(re.content.decode("utf-8"))  # type: ignore
            if content["ret"] != 200:
                raise ActionFailed(f"调用API失败: {str(content)}")
            else:
                return re

    async def _do_call_api(self, api: str, **data: Any) -> Response:
        log("DEBUG", f"Calling API <y>{api}</y>")
        api_url = self.adapter_config.gewechat_api_url + api.strip()

        headers = {
            "Content-Type": "application/json",
            "X-GEWE-TOKEN": self.token,
        }
        request = Request("POST", api_url, json=data, headers=headers)
        re = await self.request(request)  # Changed from request.json to request

        # 如果请求失败, 重新获取token并重试
        if re.status_code != 200:
            self.get_token()
            log("DEBUG", f"Calling API <y>{api}</y>")
            api_url = self.adapter_config.gewechat_api_url + api
            headers = {"Content-Type": "application/json", "X-GEWE-TOKEN": self.token}
            request = Request("POST", api_url, json=data, headers=headers)
            re = await self.request(request)
        return re

    async def _handle_http(self, request: Request) -> Response:
        await self._forward(self.bots[self.adapter_config.wxid], request.json)
        return Response(200)

    @classmethod
    def payload_to_event(cls, payload: dict[str, Any], adapter: "Adapter"):
        """
        转换Event
        当payload无法转换为Event时, 返回None
        """
        log("DEBUG", f"parse payload")
        try:
            raw = type_validate_python(TestMessage, payload)
        except ValidationError:
            try:
                raw = type_validate_python(Message, payload)
            except ValidationError as e:
                log("DEBUG", f"parse payload failed: {e}")
                return None

        # 过滤自身的消息
        if not adapter.adapter_config.self_msg and isinstance(raw, Message):
            if raw.TypeName in TypeName.AddMsg and isinstance(raw.Data, AddMessageData) and raw.Data.FromUserName.string == adapter.adapter_config.wxid:
                return None

        event = Event.parse_event(raw)
        return event

    async def _forward(self, bot: Bot, payload: dict):
        event = self.payload_to_event(payload, bot.adapter)
        # 让 bot 对事件进行处理
        if event:
            log("DEBUG", f"handle event: {event}")
            self.event_store.store_event(event)
            self.tasks.add(asyncio.create_task(bot.handle_event(event)))

    async def _schedule_cleanup(self):
        """定时清理任务"""
        while True:
            try:
                await asyncio.sleep(3600)  # 每小时检查一次
                if datetime.now().hour == 3:  # 每天凌晨3点执行
                    self.event_store.cleanup_expired_events(self.adapter_config.msg_expire_time)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"定时清理任务异常: {str(e)}")
