
<div align="center">

# NoneBot-Adapter-Gewe

_✨ NoneBot2 Gewe Protocol适配器 / Gewe Protocol Adapter for NoneBot2 ✨_

<a href="https://github.com/sqiao7/nonebot-adapter-gewe/blob/master/LICENSE.txt">
  <img src="https://img.shields.io/github/license/sqiao7/nonebot-adapter-gewe" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-adapter-gewe">
  <img src="https://img.shields.io/pypi/v/nonebot-adapter-gewe" alt="version">
</a>
<img src="https://img.shields.io/badge/Python-3.9+-blue" alt="python">
<a href="https://pypi.python.org/pypi/nonebot-adapter-gewe">
  <img src="https://img.shields.io/pypi/dm/nonebot-adapter-gewe" alt="pypi download">
</a>
<a href="https://github.com/nonebot/nonebot2">
  <img src="https://img.shields.io/badge/NoneBot-2.4.2+-red" alt="nonebot">
</a>

</div>

## 📖 简介

本项目为 [NoneBot2](https://github.com/nonebot/nonebot2) 提供了一个 [Gewe](https://github.com/Devo919/Gewe) 微信协议适配器，让您能够轻松地在 NoneBot2 框架中接入微信机器人功能。

**项目来源：** Fork 自 [nonebot-adapter-gewechat](https://github.com/Shine-Light/nonebot-adapter-gewechat)，专门适配 GEWE 服务。

## ✨ 特性

- 🚀 **完整的微信消息支持**：文本、图片、表情等多种消息类型
- 🔧 **简单易用的配置**：通过环境变量快速配置
- 📡 **实时消息推送**：支持 Webhook 回调机制
- 🛡️ **类型安全**：完整的类型注解支持
- 📦 **插件生态**：完美兼容 NoneBot2 插件系统

## 📦 安装

### 使用 pip 安装

```bash
# 基础安装
pip install nonebot-adapter-gewe

# 如果需要将登录二维码保存为图片
pip install nonebot-adapter-gewe[png]
```

### 使用 nb-cli 安装

```bash
# 基础安装
nb adapter install nonebot-adapter-gewe

# 如果需要将登录二维码保存为图片
nb adapter install nonebot-adapter-gewe[png]
```

## ⚙️ 配置

### 1. Driver 配置

需要同时启用 `HTTP 客户端驱动器` 和 `ASGI 服务端驱动器`，推荐使用 `fastapi+httpx`：

```dotenv
DRIVER="~fastapi+~httpx"
```

### 2. Gewe 服务配置

```dotenv
# Gewe API 地址
GEWECHAT_API_URL="http://127.0.0.1:2531/v2/api"

# 回调地址配置
GEWECHAT_CALLBACK_URL="http://127.0.0.1:8080/gewe/callback/collect"
GEWECHAT_CALLBACK_PATH="/callback/collect"
GEWECHAT_REGION_ID=350000
GEWECHAT_PROXY="socks5://user:pass@addr:port"
GEWECHAT_TOKEN="XXXX-XXXX-XXXX-XXXX"

# 是否接收自己发送的消息
SELF_MSG=false
```

### 3. 账号配置

```dotenv
# 微信ID（登录后获得）
WXID="wxid_xxxxx"

# 应用ID（首次登录请留空）
APPID="wx_xxxxxxx"
```

> **💡 提示：** `APPID` 留空表示更换设备登录，首次登录时请保持为空。

## 🔌 在 NoneBot2 中使用

### 注册适配器

```python
import nonebot
from nonebot.adapters.gewe import Adapter as GeweAdapter

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(GeweAdapter)

# 启动
nonebot.run()
```

## 📚 API 接口

具体接口文档请参考：[GeweChat API 文档](https://apifox.com/apidoc/shared-69ba62ca-cb7d-437e-85e4-6f3d3df271b1)

Bot 类中已封装了常用接口，可直接调用。

> [!WARNING]
> **功能限制：** Gewe 目前仅支持图片的下载，语音、视频等媒体文件暂不支持下载。

## 🎯 使用示例

### 基础消息处理

```python
from nonebot import on_message
from nonebot.adapters.gewe.message import MessageSegment, Message
from nonebot.adapters.gewe.event import (
    TextMessageEvent, 
    ImageMessageEvent, 
    EmojiMessageEvent
)
from nonebot.adapters.gewe.bot import Bot

# 文本消息处理
text_handler = on_message(priority=5)

@text_handler.handle()
async def handle_text(bot: Bot, event: TextMessageEvent):
    # 回复文本消息
    await text_handler.send(f"收到消息：{event.get_plaintext()}")

# 图片消息撤回示例
revoke_handler = on_message(priority=5)

@revoke_handler.handle()
async def handle_revoke(bot: Bot, event: ImageMessageEvent):
    # 撤回图片消息
    await bot.revokeMsg(
        event.FromUserName,
        event.MsgId,
        event.newMsgId,
        event.CreateTime
    )

# 表情消息处理
emoji_handler = on_message(priority=10)

@emoji_handler.handle()
async def handle_emoji(bot: Bot, event: EmojiMessageEvent):
    # 发送表情回复
    await emoji_handler.send(MessageSegment.emoji(
        event.md5,
        event.md5_size
    ))
```

### 发送不同类型消息

```python
from nonebot.adapters.gewe.message import MessageSegment

# 发送文本
await bot.send_message(user_id, "Hello, World!")

# 发送图片
await bot.send_message(user_id, MessageSegment.image("path/to/image.jpg"))

# 发送组合消息
message = MessageSegment.text("这是一张图片：") + MessageSegment.image("path/to/image.jpg")
await bot.send_message(user_id, message)
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/sqiao7/nonebot-adapter-gewe.git
cd nonebot-adapter-gewe

# 安装依赖
poetry install

# 运行测试
poetry run pytest
```

## 📄 许可证

本项目基于 [MIT](LICENSE.txt) 许可证开源。

## 🔗 相关链接

- [NoneBot2 官方文档](https://nonebot.dev/)
- [Gewe 官方文档](http://doc.geweapi.com)
- [原项目地址](https://github.com/Shine-Light/nonebot-adapter-gewechat)

## ❓ 常见问题

### Q: 如何获取微信ID？
A: 成功登录后，可以通过 Gewe 接口获取当前登录账号的微信ID。

### Q: 首次登录需要注意什么？
A: 首次登录时请将 `APPID` 配置项留空，登录成功后会自动获取。

### Q: 支持哪些消息类型？
A: 目前支持文本、图片、表情等消息类型，语音和视频消息的下载功能暂不支持。
