from typing import Type, Union, Mapping, Iterable
from typing_extensions import override, Self

from nonebot.adapters import Message as BaseMessage, MessageSegment as BaseMessageSegment


class MessageSegment(BaseMessageSegment["Message"]):

    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @override
    def __str__(self) -> str:
        if self.type == "text":
            return self.data["content"]
        return str(self.type)

    @override
    def is_text(self) -> bool:
        return self.type == "text"
    
    @classmethod
    def text(cls, content: str, ats: str = "") -> Self:
        """文本消息
        :param content: 文本内容
        :param ats: 被@的用户列表，格式为`wxid1,wxid2`
        """
        return cls("text", {"content": content, "ats": ats})
    
    @classmethod
    def image(cls, imgUrl: str) -> Self:
        """图片消息
        :param imgUrl: 图片链接
        """
        return cls("image", {"imgUrl": imgUrl})

    @classmethod
    def voice(cls, voiceUrl: str ,voiceDuration: int) -> Self:
        """语音消息
        :param voiceUrl: 语音链接, 仅支持silk格式
        :param voiceDuration: 语音时长, 单位毫秒
        """
        return cls("voice", {"voiceUrl": voiceUrl, "voiceDuration": voiceDuration})
    
    @classmethod
    def video(cls, videoUrl: str, thumbUrl: str, videoDuration: int) -> Self:
        """视频消息
        :param videoUrl: 视频链接
        :param thumbUrl: 视频缩略图链接
        :param videoDuration: 视频时长, 单位秒
        """
        return cls("video", {"videoUrl": videoUrl, "thumbUrl": thumbUrl, "videoDuration": videoDuration})

    @classmethod
    def file(cls, fileUrl: str, fileName: str) -> Self:
        """文件消息
        :param fileUrl: 文件链接
        :param fileName: 文件名
        """
        return cls("file", {"fileUrl": fileUrl, "fileName": fileName})

    @classmethod
    def namecard(cls, nameCardWxid: str, nickName: str) -> Self:
        """名片消息
        :param nameCardWxid: 名片用户wxid
        :param nickName: 名片用户昵称
        """
        return cls("namecard", {"nameCardWxid": nameCardWxid, "nickName": nickName})
    
    @classmethod
    def link(cls, title: str, desc: str, linkUrl: str, thumbUrl: str) -> Self:
        """链接消息
        :param title: 链接标题
        :param desc: 链接描述
        :param linkUrl: 链接地址
        :param thumbUrl: 链接缩略图链接
        """
        return cls("link", {"title": title, "desc": desc, "linkUrl": linkUrl, "thumbUrl": thumbUrl})

    @classmethod
    def emoji(cls, emojiMd5: str, emojiSize: int) -> Self:
        """表情消息
        :param emojiMd5: 表情md5
        :param emojiSize: 表情大小
        """
        return cls("emoji", {"emojiMd5": emojiMd5, "emojiSize": emojiSize})
    
    @classmethod
    def appmsg(cls, appmsg: str) -> Self:
        """公众号消息
        :param appmsg: 回调消息中的appmsg节点内容
        """
        return cls("appmsg", {"appmsg": appmsg})
    
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
        return cls("mp", {"miniAppId": miniAppId, "displayName": displayName, "pagePath": pagePath, "coverImgUrl": coverImgUrl, "title": title, "userName": userName})
    
    @classmethod
    def revoke(cls, msgId: str, newMsgId: str, createTime: str) -> Self:
        """撤回消息
        :param msgId: 回调消息中的msgId
        :param newMsgId: 回调消息中的newMsgId
        :param createTime: 回调消息中的createTime
        """
        return cls("revoke", {"msgId": msgId, "newMsgId": newMsgId, "createTime": createTime})
    
    @classmethod
    def forwardFile(cls, xml: str) -> Self:
        """转发文件
        :param xml: 文件消息的xml
        """
        return cls("forwardFile", {"xml": xml})
    
    @classmethod
    def forwardImage(cls, xml: str) -> Self:
        """转发图片
        :param xml: 图片消息的xml
        """
        return cls("forwardImage", {"xml": xml})
    
    @classmethod
    def forwardVideo(cls, xml: str) -> Self:
        """转发视频
        :param xml: 视频消息的xml
        """
        return cls("forwardVideo", {"xml": xml})
    
    @classmethod
    def forwardLink(cls, xml: str) -> Self:
        """转发链接
        :param xml: 链接消息的xml
        """
        return cls("forwardLink", {"xml": xml})
    
    @classmethod
    def forwardMP(cls, xml: str, coverImgUrl: str) -> Self:
        """转发小程序
        :param xml: 小程序消息的xml
        :param coverImgUrl: 小程序封面图片链接
        """
        return cls("forwardMP", {"xml": xml, "coverImgUrl": coverImgUrl})

    @classmethod
    def xml(cls, xml: str) -> Self:
        """xml消息
        :param xml: xml
        """
        return cls("xml", {"xml": xml})

class Message(BaseMessage[MessageSegment]):

    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @staticmethod
    @override
    def _construct(msg: str) -> Iterable[MessageSegment]:
        return [MessageSegment.text(msg)]
