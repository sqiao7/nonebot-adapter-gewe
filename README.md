<div align="center">

# NoneBot-Adapter-Gewechat

_✨ NoneBot2 Gewechat Protocol适配器 / Gewechat Protocol Adapter for NoneBot2 ✨_

<a href="https://cdn.jsdelivr.net/gh/Shine-Light/nonebot-adapter-gewechat@master/LICENSE">
  <img src="https://img.shields.io/github/license/Shine-Light/nonebot-adapter-gewechat" alt="license">
</a>
<img src="https://img.shields.io/pypi/v/nonebot-adapter-gewechat" alt="version">
<img src="https://img.shields.io/badge/Python-3.9+-yellow" alt="python">
<a href="https://pypi.python.org/pypi/nonebot-adapter-gewechat">
  <img src="https://img.shields.io/pypi/dm/nonebot-adapter-gewechat" alt="pypi download">
</a>

</div>

## 简介

本项目为 [NoneBot2](https://github.com/nonebot/nonebot2) 提供了一个 [Gewechat](https://github.com/Devo919/Gewechat) 适配器。

## 安装
### pip
```bash
pip install nonebot-adapter-gewechat
```
### nb cli
```bash
nb adapter install nonebot-adapter-gewechat
```

## 配置
### Driver 配置
需要 `HTTP 客户端驱动器` 和 `ASGI 服务端驱动器`  
推荐 `fastapi+httpx`
```
DRIVER="~fastapi+~httpx"
```
### Gewechat 配置
```dotenv
GEWECHAT_API_URL="http://127.0.0.1:2531/v2/api"
GEWECHAT_DOWNLOAD_API_URL="http://127.0.0.1:2532/download"
GEWECHAT_CALLBACK_URL="http://127.0.0.1:8080/gewechat/callback/collect"
GEWECHAT_CALLBACK_PATH="/callback/collect"
SELF_MSG=false
```
配置对应 [Gewechat](https://github.com/Devo919/Gewechat) 的配置
- `GEWECHAT_API_URL` Gewechat API 地址
- `GEWECHAT_DOWNLOAD_API_URL` Gewechat 下载 API 地址
- `GEWECHAT_CALLBACK_URL` 接收回调地址
- `GEWECHAT_CALLBACK_PATH` Gewechat 回调路径
- `SELF_MSG` 是否接收自己发送的消息

### 账号配置
```dotenv
WXID="wxid_xxxxx"
APPID="wx_xxxxxxx"
```
其中，`APPID` 留空即为更换设备登录，首次登录请留空

## API接口
具体接口可前往[GeweChat文档](https://apifox.com/apidoc/shared-69ba62ca-cb7d-437e-85e4-6f3d3df271b1)查看, Bot类中已封装接口

## 示例
```python
from nonebot import on_command, on_message
from nonebot.adapters.gewechat.message import MessageSegment, Message
from nonebot.adapters.gewechat.event import TextMessageEvent, EmojiMessageEvent
from nonebot.adapters.gewechat.bot import Bot
from nonebot.params import CommandArg

revoke = on_command("revoke", priority=5)
@revoke.handle()
async def _(bot: Bot, event: TextMessageEvent, content: Message = CommandArg()):
    text = str(content)
    msgId = text.split(" ")[0]
    newMsgId = text.split(" ")[1]
    createdTime = text.split(" ")[2]
    await revoke.send(MessageSegment.revoke(
        msgId,
        newMsgId,
        createdTime
    ))

emoji = on_message(priority=10)
@emoji.handle()
async def _(bot: Bot, event: EmojiMessageEvent):
    await emoji.send(MessageSegment.emoji(
        event.md5,
        event.md5_size
    ))
```