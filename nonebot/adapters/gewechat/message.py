import re
from typing import Type, Iterable, TypedDict, TYPE_CHECKING
from typing_extensions import override, Self
from dataclasses import dataclass
from nonebot.adapters import Message as BaseMessage, MessageSegment as BaseMessageSegment


class MessageSegment(BaseMessageSegment["Message"]):

    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @override
    def __str__(self) -> str:
        if self.type == "text":
            return self.data["text"]
        return str(self.type)

    @override
    def is_text(self) -> bool:
        return self.type == "text"
    
    @classmethod
    def text(cls, text: str) -> Self:
        """文本消息
        :param text: 文本内容
        """
        return Text("text", {"text": text})

    @classmethod
    def at(cls, wxid: str) -> Self:
        """@消息
        :param wxid: 被@的wxid
        """
        return At("at", {"wxid": wxid})
    
    @classmethod
    def at_all(cls) -> Self:
        """@所有人"""
        return AtAll("at_all")

    @classmethod
    def image(cls, imgUrl: str) -> Self:
        """图片消息
        :param imgUrl: 图片链接
        """
        return Image("image", {"imgUrl": imgUrl})

    @classmethod
    def voice(cls, voiceUrl: str ,voiceDuration: int) -> Self:
        """语音消息
        :param voiceUrl: 语音链接, 仅支持silk格式
        :param voiceDuration: 语音时长, 单位毫秒
        """
        return Voice("voice", {"voiceUrl": voiceUrl, "voiceDuration": voiceDuration})
    
    @classmethod
    def video(cls, videoUrl: str, thumbUrl: str, videoDuration: int) -> Self:
        """视频消息
        :param videoUrl: 视频链接
        :param thumbUrl: 视频缩略图链接
        :param videoDuration: 视频时长, 单位秒
        """
        return Video("video", {"videoUrl": videoUrl, "thumbUrl": thumbUrl, "videoDuration": videoDuration})

    @classmethod
    def file(cls, fileUrl: str, fileName: str) -> Self:
        """文件消息
        :param fileUrl: 文件链接
        :param fileName: 文件名
        """
        return File("file", {"fileUrl": fileUrl, "fileName": fileName})

    @classmethod
    def namecard(cls, nameCardWxid: str, nickName: str) -> Self:
        """名片消息
        :param nameCardWxid: 名片用户wxid
        :param nickName: 名片用户昵称
        """
        return NameCard("namecard", {"nameCardWxid": nameCardWxid, "nickName": nickName})
    
    @classmethod
    def link(cls, title: str, desc: str, linkUrl: str, thumbUrl: str) -> Self:
        """链接消息
        :param title: 链接标题
        :param desc: 链接描述
        :param linkUrl: 链接地址
        :param thumbUrl: 链接缩略图链接
        """
        return Link("link", {"title": title, "desc": desc, "linkUrl": linkUrl, "thumbUrl": thumbUrl})

    @classmethod
    def emoji(cls, emojiMd5: str, emojiSize: int) -> Self:
        """表情消息
        :param emojiMd5: 表情md5
        :param emojiSize: 表情大小
        """
        return Emoji("emoji", {"emojiMd5": emojiMd5, "emojiSize": emojiSize})
    
    @classmethod
    def appmsg(cls, appmsg: str) -> Self:
        """公众号消息
        :param appmsg: 回调消息中的appmsg节点内容
        """
        return AppMsg("appmsg", {"appmsg": appmsg})
    
    @classmethod
    def miniapp(cls, miniAppId: str, displayName: str, pagePath: str, coverImgUrl: str, title: str, userName: str) -> Self:
        """小程序消息
        :param miniAppId: 小程序id
        :param displayName: 小程序名称
        :param pagePath: 小程序打开的地址
        :param coverImgUrl: 小程序封面图片链接
        :param title: 小程序标题
        :param userName: 归属的用户ID
        """
        return MiniApp("mp", {"miniAppId": miniAppId, "displayName": displayName, "pagePath": pagePath, "coverImgUrl": coverImgUrl, "title": title, "userName": userName})

    @classmethod
    def forwardFile(cls, xml: str) -> Self:
        """转发文件
        :param xml: 文件消息的xml
        """
        return forwardFile("forwardFile", {"xml": xml})
    
    @classmethod
    def forwardImage(cls, xml: str) -> Self:
        """转发图片
        :param xml: 图片消息的xml
        """
        return forwardImage("forwardImage", {"xml": xml})
    
    @classmethod
    def forwardVideo(cls, xml: str) -> Self:
        """转发视频
        :param xml: 视频消息的xml
        """
        return forwardVideo("forwardVideo", {"xml": xml})
    
    @classmethod
    def forwardLink(cls, xml: str) -> Self:
        """转发链接
        :param xml: 链接消息的xml
        """
        return forwardLink("forwardLink", {"xml": xml})
    
    @classmethod
    def forwardMP(cls, xml: str, coverImgUrl: str) -> Self:
        """转发小程序
        :param xml: 小程序消息的xml
        :param coverImgUrl: 小程序封面图片链接
        """
        return forwardMP("forwardMP", {"xml": xml, "coverImgUrl": coverImgUrl})

    @classmethod
    def xml(cls, xml: str) -> Self:
        """xml消息
        :param xml: xml
        """
        return Xml("xml", {"xml": xml})


class _TextData(TypedDict):
    text: str

@dataclass
class Text(MessageSegment):
    if TYPE_CHECKING:
        data: _TextData

    @override
    def __str__(self):
        return self.data["text"]
    
    @override
    def is_text(self) -> bool:
        return True


class _AtData(TypedDict):
    wxid: str

@dataclass
class At(MessageSegment):
    if TYPE_CHECKING:
        data: _AtData


@dataclass
class AtAll(MessageSegment):
    @override
    def __str__(self):
        return "notify@all"


class _ImageData(TypedDict):
    imgUrl: str

@dataclass
class Image(MessageSegment):
    if TYPE_CHECKING:
        data: _ImageData

class _VoiceData(TypedDict):
    voiceUrl: str
    voiceDuration: int

@dataclass
class Voice(MessageSegment):
    if TYPE_CHECKING:
        data: _VoiceData

class _VideoData(TypedDict):
    videoUrl: str
    thumbUrl: str
    videoDuration: int

@dataclass
class Video(MessageSegment):
    if TYPE_CHECKING:
        data: _VideoData

class _FileData(TypedDict):
    fileUrl: str
    fileName: str

@dataclass
class File(MessageSegment):
    if TYPE_CHECKING:
        data: _FileData

class _NameCardData(TypedDict):
    nameCardWxid: str
    nickName: str

@dataclass
class NameCard(MessageSegment):
    if TYPE_CHECKING:
        data: _NameCardData

class _LinkData(TypedDict):
    title: str
    desc: str
    linkUrl: str
    thumbUrl: str

@dataclass
class Link(MessageSegment):
    if TYPE_CHECKING:
        data: _LinkData

class _EmojiData(TypedDict):
    emojiMd5: str
    emojiSize: str

@dataclass
class Emoji(MessageSegment):
    if TYPE_CHECKING:
        data: _EmojiData

class _AppMsg(TypedDict):
    appmsg: str

@dataclass
class AppMsg(MessageSegment):
    if TYPE_CHECKING:
        data: _AppMsg

class _MiniAppData(TypedDict):
    miniAppId: str
    displayName: str
    pagePath: str
    coverImgUrl: str
    title: str
    userName: str

@dataclass
class MiniApp(MessageSegment):
    if TYPE_CHECKING:
        data: _MiniAppData

class _RevokeData(TypedDict):
    msgId: str
    newMsgId: str
    createTime: int

@dataclass
class Revoke(MessageSegment):
    if TYPE_CHECKING:
        data: _RevokeData

class _XmlData(TypedDict):
    xml: str

@dataclass
class Xml(MessageSegment):
    if TYPE_CHECKING:
        data: _XmlData

@dataclass
class forwardFile(MessageSegment):
    if TYPE_CHECKING:
        data: _XmlData

@dataclass
class forwardImage(MessageSegment):
    if TYPE_CHECKING:
        data: _XmlData

@dataclass
class forwardVideo(MessageSegment):
    if TYPE_CHECKING:
        data: _XmlData

@dataclass
class forwardLink(MessageSegment):
    if TYPE_CHECKING:
        data: _XmlData

class _ForwardMiniAppData(TypedDict):
    xml: str
    coverImgUrl: str

@dataclass
class forwardMP(MessageSegment):
    if TYPE_CHECKING:
        data: _ForwardMiniAppData


class Message(BaseMessage[MessageSegment]):

    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        text_begin = 0
        for embed in re.finditer(r"@(?:所有人| all people|\S+)\s?", msg):
            content = msg[text_begin:embed.pos + embed.start()]
            if content:
                yield MessageSegment.text(content)
            text_begin = embed.pos + embed.end()
            at = embed.group().strip()
            if at == "@所有人" or at == "@ all people":
                yield MessageSegment.at_all()
            else:
                yield MessageSegment.at(at[1:])
        content = msg[text_begin:]
        if content:
            yield MessageSegment.text(content)

    def to_payload(self) -> list[tuple[str, dict]]:
        segments = self.exclude("at", "at_all")
        if segments.has("text"):
            first_text = segments["text", 0]
        else:
            first_text = MessageSegment.text("")
            segments.insert(0, first_text)
        if self.has("at_all"):
            first_text.data["ats"] = "notify@all"
        if self.has("at"):
            at_list = self.get("at")
            if "ats" in first_text.data:
                first_text.data["ats"] += "," + ",".join([at.data["wxid"] for at in at_list])
            else:
                first_text.data["ats"] = ",".join([at.data["wxid"] for at in at_list])
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

        msg_payload = []
        for segment in segments:
            if "forward" in segment.type:
                api = f"/message/{segment.type}"
            else:
                api = f"/message/post{api_map[segment.type]}"
            if segment.type == "text":
                msg_payload.append((api, {"content": segment.data["text"], "ats": segment.data.get("ats", "")}))
            else:
                msg_payload.append((api, segment.data))

        return msg_payload
