import re
import asyncio

from typing import TYPE_CHECKING, Any, Union
from typing_extensions import override

from nonebot.adapters import Bot as BaseBot
from nonebot.message import handle_event

from nonebot.adapters.gewechat.event import Event
from .message import Message, MessageSegment
from .event import Event, TextMessageEvent
from .utils import log, resp_json

if TYPE_CHECKING:
    from .adapter import Adapter
    

def check_at_me(bot: "Bot", event: TextMessageEvent):
    if bot.self_id in event.at_list:
        event.to_me = True

def check_nickname(bot: "Bot", event: TextMessageEvent):
    nicknames = bot.config.nickname
    nickname_regex = "|".join(nicknames)
    m = re.search(rf"^({nickname_regex})([\s,，]*|$)", event.msg, re.IGNORECASE)
    if m:
        nickname = m.group(1)
        log("DEBUG", f"User is calling me: {nickname}")
        event.to_me = True
        loc = m.end()
        event.msg = event.msg[loc:]

def to_me(bot: "Bot", event: TextMessageEvent):
    check_at_me(bot, event)
    check_nickname(bot, event)

class Bot(BaseBot):
    """Gewechat Bot 适配"""

    @override
    def __init__(self, adapter, self_id: str, **kwargs: Any):
        super().__init__(adapter, self_id)
        self.adapter: Adapter = adapter

    async def handle_event(self, event: Event):
        # 根据需要，对事件进行某些预处理，例如：
        # 检查事件是否和机器人有关操作，去除事件消息首尾的 @bot
        # 检查事件是否有回复消息，调用平台 API 获取原始消息的消息内容
        if isinstance(event, TextMessageEvent):
            to_me(self, event)
        # 调用 handle_event 让 NoneBot 对事件进行处理
        await handle_event(self, event)

    @override
    async def send(
        self,
        event: Event,
        message: Union[str, Message, MessageSegment],
        **kwargs,
    ) -> Any:
        try:
            toWxid = getattr(event, "FromUserName")
        except AttributeError:
            raise ValueError("该事件不支持发送消息")
        if isinstance(message, str) or isinstance(message, MessageSegment):
            message = Message(message)


        api_map = {
            "text": "Text",
            "image": "Image",
            "file": "File",
            "video": "Video",
            "voice": "Voice",
            "emoji": "Emoji",
            "namecard": "NameCard",
            "appmsg": "AppMsg",
            "mp": "MiniApp"
        }

        msg_list = []
        for segment in message:
            if segment.type == "revoke":
                api = "/message/revokeMsg"
            elif "forward" in segment.type:
                api = f"/message/{segment.type}"
            else:
                api = f"/message/post{api_map[segment.type]}"

            segment.data["toWxid"] = toWxid
            segment.data["appId"] = self.adapter.adapter_config.appid

            msg_list.append(self.call_api(api, **segment.data))

        return await asyncio.gather(*msg_list)
    
    async def check_online(self) -> bool:
        return resp_json(await self.call_api("/login/checkOnline"))['data']
    
    async def reconnect(self) -> dict:
        return resp_json(await self.call_api("/login/reconnection"))
    
    async def logout(self) -> dict:
        self.adapter.bot_disconnect(self)
        return resp_json(await self.call_api("/login/logout"))
