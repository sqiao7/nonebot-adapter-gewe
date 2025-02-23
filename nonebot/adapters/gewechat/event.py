import xml.etree.ElementTree as ET

from typing_extensions import override
from datetime import datetime
from pydantic import BaseModel, model_validator
from nonebot.adapters import Event as BaseEvent
from nonebot.compat import model_dump, type_validate_python

from nonebot.adapters.gewechat.message import Message
from typing import Dict, Union, Optional, List, Final
from copy import deepcopy
from .model import TestMessage, MessageType, TypeName, ImgBuf, AppType, SystemMsgType, FriendRequestData, GroupRequestData
from .model import Message as RawMessage
from .message import Message, MessageSegment
from .utils import get_at_list, remove_prefix_tag

class Event(BaseEvent):
    """
    gewechat 事件基类
    """

    data: Dict
    """事件原始数据"""
    type: str
    """事件类型"""
    sub_type: Optional[MessageType] = None
    """事件子类型"""
    to_me: bool = False
    """是否与机器人有关"""
    time: datetime = datetime.now()

    @staticmethod
    def type_validator(event: "Event") -> bool:
        raise NotImplementedError("Not implemented!")

    @classmethod
    def parse_event(cls, data: Union[TestMessage, RawMessage]) -> "Event":

        sub_event: List[Event] = [
            MessageEvent,
            NoticeEvent,
            RequestEvent,
            MetaEvent
        ]

        type = "Test" if isinstance(data, TestMessage) else data.TypeName
        sub_type = data.Data.MsgType if type == TypeName.AddMsg else None


        event = cls(
            data=model_dump(data),
            type=type,
            sub_type=sub_type,
            to_me=False
        )

        for sub in sub_event:
            if sub.type_validator(event):
                event = sub._parse_event(event)
                break

        return event
    
    @classmethod
    def _parse_event(cls, event: "Event") -> "Event":
        raise NotImplementedError("Not implemented!")

    @override
    def get_type(self) -> str:
        return self.type

    @override
    def get_event_name(self) -> str:
        return self.__class__.__name__

    @override
    def get_event_description(self) -> str:
        if self.type == TypeName.AddMsg:
            return self.data.Data.PushContent
        return "Event"

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_plaintext(self) -> str:
        raise ValueError("Event has no plaintext!")

    @override
    def get_user_id(self) -> str:
        raise ValueError("Event has no user id!")

    @override
    def get_session_id(self) -> str:
        raise ValueError("Event has no session!")

    @override
    def is_tome(self) -> bool:
        return False



class MessageEvent(Event):
    """
    消息事件基类
    """

    type: Final[str] = "message"
    """消息事件类型"""
    MsgId: int
    """消息ID"""
    FromUserName: str
    """发送者"""
    ToUserName: str
    """接收者"""
    CreateTime: int
    """消息创建时间"""
    MsgType: MessageType
    """消息类型"""
    message: Optional[Message] = None
    """消息内容"""
    original_message: Optional[Message] = None
    """原始消息内容"""
    PushContent: Optional[str] = None
    """消息推送时简略内容"""
    NewMsgId: int
    """消息排重用消息ID"""
    MsgSeq: int
    """消息序列"""

    @override
    @staticmethod
    def type_validator(event: Event) -> bool:
        if event.type == TypeName.AddMsg:
            if event.sub_type in [MessageType.FriendAdd, MessageType.GroupOp, MessageType.SystemMsg]:
                return False
            # 群聊邀请和公众号链接特判
            if event.sub_type == MessageType.AppMsg:
                root = ET.fromstring(remove_prefix_tag(event.data["Data"]["Content"]["string"]))
                type = root.find("appmsg").find("type").text
                if int(type) != AppType.Link.value:
                    return True
                title = root.find("appmsg").find("title").text
                if "邀请你加入群聊" not in title:
                    return True
            else:
                return True
        return False

    @override
    @classmethod
    def _parse_event(cls, event: Event) -> "MessageEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        FromUserName = data["FromUserName"]["string"]
        ToUserName = data["ToUserName"]["string"]
        data["Content"]["string"] = remove_prefix_tag(data["Content"]["string"])
        obj.update(data)
        obj.update({
            "FromUserName": FromUserName,
            "ToUserName": ToUserName,
            "message": "",
            "original_message": ""
        })
        event: "MessageEvent" = type_validate_python(cls, obj)

        sub_event: List[MessageEvent] = [
            TextMessageEvent,
            ImageMessageEvent,
            VoiceMessageEvent,
            LocationMessageEvent,
            VideoMessageEvent,
            EmojiMessageEvent,
            PublicLinkMessageEvent,
            FileUploadingMessageEvent,
            FileMessageEvent,
            NamecardMessageEvent,
            MiniProgramMessageEvent,
            QuoteMessageEvent,
            TransferMessageEvent,
            RedPactMessageEvent,
            VideoChannelMessageEvent
        ]

        for event_type in sub_event:
            if event_type.type_validator(event):
                if hasattr(event_type, "_parse__event"):
                    event = event_type._parse__event(event)
                else:
                    event = type_validate_python(event_type, obj)
                break

        return event

    @override
    def get_message(self) -> Message:
        return self.message

    @override
    def get_plaintext(self) -> str:
        return self.message.extract_plain_text()

    @override
    def get_user_id(self) -> str:
        return self.FromUserName
    
    def is_group_message(self) -> bool:
        return "@chatroom" in self.ToUserName
    
    @override
    def get_event_description(self):
        return self.PushContent

class TextMessageEvent(MessageEvent):
    """
    文本消息事件
    """
    sub_type: MessageType = MessageType.Text
    """消息子类型"""
    at_list: list[str] = []
    """@列表"""
    msg: str = ""
    """消息内容"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        return event.MsgType == MessageType.Text
    
    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "TextMessageEvent":
        obj = deepcopy(model_dump(event))
        msg = obj["data"]["Data"]["Content"]["string"]
        at_list = get_at_list(msg)
        obj.update({
            "at_list": at_list,
            "msg": msg
        })
        event: "TextMessageEvent" = type_validate_python(cls, obj)
        return event
    
    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.text(self.msg)
        )
        self.original_message = Message(
            MessageSegment.text(self.data["Data"]["Content"]["string"])
        )
        return self

    @override
    def get_plaintext(self) -> str:
        return self.msg

    def get_at_list(self) -> list[str]:
        return self.at_list

class ImageMessageEvent(MessageEvent):
    """
    图片消息事件
    """
    sub_type: MessageType = MessageType.Image
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式,可用于下载"""
    ImgBuf: ImgBuf
    """图片数据,有的图片可能没有"""

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "ImageMessageEvent":
        obj = deepcopy(model_dump(event))
        obj.update({
            "raw_msg": obj["data"]["Data"]["Content"]["string"]
        })
        event: "ImageMessageEvent" = type_validate_python(cls, obj)
        return event
    
    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        return event.MsgType == MessageType.Image

class VoiceMessageEvent(MessageEvent):
    """
    语音消息事件
    """
    sub_type: MessageType = MessageType.Voice
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式,可用于下载"""
    ImgBuf: ImgBuf
    """语音数据,有的语音可能没有"""

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "VoiceMessageEvent":
        obj = deepcopy(model_dump(event))
        obj.update({
            "raw_msg": obj["data"]["Data"]["Content"]["string"]
        })
        event: "VoiceMessageEvent" = type_validate_python(cls, obj)
        return event

    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self
    
    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        return event.MsgType == MessageType.Voice

class LocationMessageEvent(MessageEvent):
    """
    位置消息事件
    """
    sub_type: MessageType = MessageType.Location
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式,可用于下载"""

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "LocationMessageEvent":
        obj = deepcopy(model_dump(event))
        obj.update({
            "raw_msg": obj["data"]["Data"]["Content"]["string"]
        })
        event: "LocationMessageEvent" = type_validate_python(cls, obj)
        return event

    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self
    
    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        return event.MsgType == MessageType.Location

class VideoMessageEvent(MessageEvent):
    """
    视频消息事件
    """
    sub_type: MessageType = MessageType.Video
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式,可用于下载"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        return event.MsgType == MessageType.Video

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "VideoMessageEvent":
        obj = deepcopy(model_dump(event))
        obj.update({
            "raw_msg": obj["data"]["Data"]["Content"]["string"]
        })
        event: "VideoMessageEvent" = type_validate_python(cls, obj)
        return event

    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class EmojiMessageEvent(MessageEvent):
    """
    表情消息事件
    """
    sub_type: MessageType = MessageType.Emoji
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    md5: str
    """表情包md5,可用于发送"""
    md5_size: int
    """表情包大小,可用于发送"""

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "EmojiMessageEvent":
        obj = deepcopy(model_dump(event))
        md5: str = ""
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        md5 = root.find('emoji').get('md5')
        md5_size = int(root.find('emoji').get('len'))
        obj.update({
            "raw_msg": raw_msg,
            "md5": md5,
            "md5_size": md5_size
        })
        event: "EmojiMessageEvent" = type_validate_python(cls, obj)
        return event

    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.md5)
        )
        self.original_message = deepcopy(self.message)
        return self

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        return event.MsgType == MessageType.Emoji

class PublicLinkMessageEvent(MessageEvent):
    """
    公众号链接消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "msg":
            return False
        if root.find("appmsg") is None:
            return False
        if root.find("appmsg").find("title") is None:
            return False
        type = root.find("appmsg").find("type").text
        title = root.find("appmsg").find("title").text
        if int(type) == AppType.Link.value and ("邀请你加入群聊" not in title):
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "PublicLinkMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "PublicLinkMessageEvent" = type_validate_python(cls, obj)
        return event

    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class FileUploadingMessageEvent(MessageEvent):
    """
    文件上传事件
    该事件仅用于通知，不可下载与转发
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "msg":
            return False
        if root.find("appmsg") is None:
            return False
        type = root.find("appmsg").find("type").text
        if int(type) == AppType.FileSend.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "FileUploadingMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "FileUploadingMessageEvent" = type_validate_python(cls, obj)
        return event
    
    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class FileMessageEvent(MessageEvent):
    """
    文件消息事件
    该事件可下载与转发
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "msg":
            return False
        if root.find("appmsg") is None:
            return False
        type = root.find("appmsg").find("type").text
        if int(type) == AppType.FileDone.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "FileMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "FileMessageEvent" = type_validate_python(cls, obj)
        return event
    
    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class NamecardMessageEvent(MessageEvent):
    """
    名片消息事件
    """
    sub_type: MessageType = MessageType.NameCard
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        return event.sub_type == MessageType.NameCard

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "NamecardMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "NamecardMessageEvent" = type_validate_python(cls, obj)
        return event
    
    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class MiniProgramMessageEvent(MessageEvent):
    """
    小程序消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "msg":
            return False
        if root.find("appmsg") is None:
            return False
        type = root.find("appmsg").find("type").text
        if int(type) in [AppType.MiniProgram1.value, AppType.MiniProgram2.value]:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "MiniProgramMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "MiniProgramMessageEvent" = type_validate_python(cls, obj)
        return event

    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class QuoteMessageEvent(MessageEvent):
    """
    引用消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "msg":
            return False
        if root.find("appmsg") is None:
            return False
        type = root.find("appmsg").find("type").text
        if int(type) == AppType.Quote.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "QuoteMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "QuoteMessageEvent" = type_validate_python(cls, obj)
        return event

    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class TransferMessageEvent(MessageEvent):
    """
    转账消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "msg":
            return False
        if root.find("appmsg") is None:
            return False
        type = root.find("appmsg").find("type").text
        if int(type) == AppType.Transfer.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "TransferMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "TransferMessageEvent" = type_validate_python(cls, obj)
        return event
    
    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class RedPactMessageEvent(MessageEvent):
    """
    红包消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "msg":
            return False
        if root.find("appmsg") is None:
            return False
        type = root.find("appmsg").find("type").text
        if int(type) == AppType.RedPacket.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "RedPactMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "RedPactMessageEvent" = type_validate_python(cls, obj)
        return event
    
    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self

class VideoChannelMessageEvent(MessageEvent):
    """
    视频号消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""

    @override
    @staticmethod
    def type_validator(event: MessageEvent) -> bool:
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "msg":
            return False
        if root.find("appmsg") is None:
            return False
        type = root.find("appmsg").find("type").text
        if int(type) == AppType.VideoChannel.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: MessageEvent) -> "VideoChannelMessageEvent":
        obj = deepcopy(model_dump(event))
        raw_msg: str = obj["data"]["Data"]["Content"]["string"]
        obj.update({
            "raw_msg": raw_msg
        })
        event: "VideoChannelMessageEvent" = type_validate_python(cls, obj)
        return event
    
    @model_validator(mode="after")
    def post_process(self):
        self.message = Message(
            MessageSegment.xml(self.raw_msg)
        )
        self.original_message = deepcopy(self.message)
        return self
    


class NoticeEvent(Event):
    """
    通知事件基类
    """
    type: Final[str] = "notice"
    """事件类型"""
    FromUserName: str
    """发送者"""
    ToUserName: Optional[str] = None
    """接收者"""

    @override
    @staticmethod
    def type_validator(event: Event) -> bool:
        if event.type in [TypeName.AddMsg, TypeName.ModContacts, TypeName.DelContacts]:
            if event.type == TypeName.AddMsg:
                if event.sub_type in [MessageType.GroupOp, MessageType.SystemMsg]:
                    return True
            else:
                return True
        return False

    @override
    @classmethod
    def _parse_event(cls, event: Event) -> "NoticeEvent":
        obj = deepcopy(model_dump(event))
        if obj["data"]["TypeName"] == TypeName.AddMsg:
            data = obj["data"]["Data"]
            FromUserName = data["FromUserName"]["string"]
            ToUserName = data["ToUserName"]["string"]
            obj.update({
                "FromUserName": FromUserName,
                "ToUserName": ToUserName
            })
        else:
            FromUserName = obj["data"]["Data"]["UserName"]["string"]
            obj.update({
                "FromUserName": FromUserName
            })
        obj.update(obj["data"])

        event: NoticeEvent = type_validate_python(cls, obj)

        sub_event: List[NoticeEvent] = [
            PokeEvent,
            RevokeEvent,
            GroupRemovedEvent,
            GroupMemberRemovedEvent,
            GroupDismissedEvent,
            GroupTitleChangeEvent,
            GroupOwnerChangeEvent,
            GroupInfoChangeEvent,
            GroupNoteEvent,
            GroupTodoEvent,
            FriendInfoChangeEvent,
            FriendRemovedEvent,
            GroupQuitEvent
        ]

        for event_type in sub_event:
            if event_type.type_validator(event):
                if hasattr(event_type, "_parse__event"):
                    event = event_type._parse__event(event)
                else:
                    event = type_validate_python(event_type, obj)
                break

        return event

    @override
    def get_user_id(self) -> str:
        return self.FromUserName
    
    @override
    def get_event_description(self):
        if self.data["TypeName"] == TypeName.AddMsg:
            return self.data["Data"]["PushContent"]
        elif self.data["TypeName"] == TypeName.ModContacts:
            return "信息变更事件"
        elif self.data["TypeName"] == TypeName.DelContacts:
            return "信息删除事件"
        else:
            super().get_event_description()

class PokeEvent(NoticeEvent):
    """
    拍一拍消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """消息发送人的wxid"""
    ToUserName: str
    """消息接收人的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.SystemMsg:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        t = remove_prefix_tag(raw_msg)
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "sysmsg":
            return False
        type = root.get("type")
        if type == SystemMsgType.Poke.value:
            return True
        return False
    
    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "PokeEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        ToUserName: str = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: PokeEvent = type_validate_python(cls, obj)
        return event

class RevokeEvent(NoticeEvent):
    """
    撤回消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """消息发送(撤回)人的wxid"""
    ToUserName: str
    """消息接收人的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.SystemMsg:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "sysmsg":
            return False
        type = root.get("type")
        if type == SystemMsgType.Revoke.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "RevokeEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: RevokeEvent = type_validate_python(cls, obj)
        return event

class GroupRemovedEvent(NoticeEvent):
    """
    被踢出群事件
    """
    sub_type: MessageType = MessageType.GroupOp
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """所在群聊的ID"""
    ToUserName: str
    """消息接收人(当前账号)的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.GroupOp:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        if "移出群聊" in raw_msg:
            return True
        return False
    
    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "GroupRemovedEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: GroupRemovedEvent = type_validate_python(cls, obj)
        return event

class GroupMemberRemovedEvent(NoticeEvent):
    """
    群成员被移除事件
    """
    sub_type: MessageType = MessageType.SystemMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """所在群聊的ID"""
    ToUserName: str
    """消息接收人(被踢出人)的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.SystemMsg:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "sysmsg":
            return False
        type = root.get("type")
        if type != SystemMsgType.Template.value:
            return False
        if "移出了群聊" in raw_msg:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "GroupMemberRemovedEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: GroupMemberRemovedEvent = type_validate_python(cls, obj)
        return event

class GroupDismissedEvent(NoticeEvent):
    """
    群解散事件
    """
    sub_type: MessageType = MessageType.SystemMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """所在群聊的ID"""
    ToUserName: str
    """消息接收人的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.SystemMsg:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "sysmsg":
            return False
        type = root.get("type")
        if type != SystemMsgType.Template.value:
            return False
        if "已解散该群聊" in raw_msg:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "GroupDismissedEvent":
        obj = deepcopy(model_dump(event))
        
        data = obj["data"]["Data"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: GroupDismissedEvent = type_validate_python(cls, obj)
        return event

class GroupTitleChangeEvent(NoticeEvent):
    """
    群名变更事件
    """
    sub_type: MessageType = MessageType.GroupOp
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """所在群聊的ID"""
    ToUserName: str
    """消息接收人的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.GroupOp:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        if "修改群名为" in raw_msg:
            return True
        return False
    
    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "GroupTitleChangeEvent":
        obj = deepcopy(model_dump(event))

        
        data = obj["data"]["Data"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: GroupTitleChangeEvent = type_validate_python(cls, obj)
        return event

class GroupOwnerChangeEvent(NoticeEvent):
    """
    群主变更事件
    """
    sub_type: MessageType = MessageType.GroupOp
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """所在群聊的ID"""
    ToUserName: str
    """消息接收人的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.GroupOp:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        if "已成为新群主" in raw_msg:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "GroupOwnerChangeEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: GroupOwnerChangeEvent = type_validate_python(cls, obj)
        return event

class GroupInfoChangeEvent(NoticeEvent):
    """
    群信息变更事件
    """
    sub_type: Optional[MessageType] = None
    """消息子类型"""
    FromUserName: str
    """所在群聊的ID"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.ModContacts:
            return False
        if "@chatroom" in event.FromUserName:
            return True
        return False

class GroupNoteEvent(NoticeEvent):
    """
    群公告消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """所在群聊的ID"""
    ToUserName: str
    """消息接收人的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.SystemMsg:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "sysmsg":
            return False
        type = root.get("type")
        if type == SystemMsgType.GroupNotice.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "GroupNoteEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: GroupNoteEvent = type_validate_python(cls, obj)
        return event

class GroupTodoEvent(NoticeEvent):
    """
    群待办消息事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""
    raw_msg: str = ""
    """原始消息,xml格式"""
    FromUserName: str
    """所在群聊的ID"""
    ToUserName: str
    """消息接收人的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.AddMsg:
            return False
        if event.data["Data"]["MsgType"] != MessageType.SystemMsg:
            return False
        raw_msg: str = event.data["Data"]["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        if root.tag != "sysmsg":
            return False
        type = root.get("type")
        if type == SystemMsgType.GroupTodo.value:
            return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: NoticeEvent) -> "GroupTodoEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg: str = data["Content"]["string"]
        obj.update({
            "ToUserName": ToUserName,
            "raw_msg": raw_msg
        })
        event: GroupTodoEvent = type_validate_python(cls, obj)
        return event

class FriendInfoChangeEvent(NoticeEvent):
    """
    好友信息变更/好友通过验证事件
    """
    sub_type: Optional[MessageType] = None
    """消息子类型"""
    FromUserName: str
    """好友的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.ModContacts:
            return False
        if "@chatroom" not in event.FromUserName:
            return True
        return False
        
class FriendRemovedEvent(NoticeEvent):
    """
    好友删除事件
    """
    sub_type: Optional[MessageType] = None
    """消息子类型"""
    FromUserName: str
    """好友的wxid"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.DelContacts:
            return False
        if "@chatroom" not in event.FromUserName:
            return True
        return False

class GroupQuitEvent(NoticeEvent):
    """
    退出群聊事件
    """
    sub_type: MessageType = None
    """消息子类型"""
    FromUserName: str
    """所在群聊的ID"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.data["TypeName"] != TypeName.DelContacts:
            return False
        if "@chatroom" in event.FromUserName:
            return True
        return False



class RequestEvent(Event):
    """
    请求事件基类
    """
    type: Final[str] = "request"
    """消息事件类型"""
    FromUserName: str
    """消息发送人的wxid"""
    ToUserName: str
    """消息接收人的wxid"""
    raw_msg: str
    """原始消息内容"""
    flag: Dict
    """消息标识,可用于操作请求"""

    @override
    @staticmethod
    def type_validator(event: Event) -> bool:
        if event.type == TypeName.AddMsg:
            if event.sub_type == MessageType.FriendAdd:
                return True
            if event.sub_type == MessageType.AppMsg:
                root = ET.fromstring(remove_prefix_tag(event.data["Data"]["Content"]["string"]))
                if root.tag != "msg":
                    return False
                type = root.find("appmsg").find("type").text
                title = root.find("appmsg").find("title").text
                if int(type) == AppType.Link.value and "邀请你加入群聊" in title:
                    return True
        return False

    @override
    @classmethod
    def _parse_event(cls, event: Event) -> "RequestEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        FromUserName = data["FromUserName"]["string"]
        ToUserName = data["ToUserName"]["string"]
        raw_msg = data["Content"]["string"]
        flag = {}
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        msg = root.find("msg")

        # 好友请求
        if data["MsgType"] == MessageType.FriendAdd:
            scene = msg.get("scene")
            v3 = msg.get("encryptusername")
            v4 = msg.get("ticket")
            flag = FriendRequestData(
                scene=scene,
                option=2,
                v3=v3,
                v4=v4
            )
        # 群聊邀请
        else:
            url = msg.find("appmsg").find("url").text
            start_index = url.find('![CDATA[') + len('![CDATA[')
            end_index = url.find(']]>')
            url = data[start_index:end_index]
            flag = GroupRequestData(
                url=url
            )
        
        obj.update({
            "FromUserName": FromUserName,
            "ToUserName": ToUserName,
            "raw_msg": raw_msg,
            "flag": flag
        })

        event: "RequestEvent" = type_validate_python(cls, obj)

        sub_event: List[RequestEvent] = [
            FriendRequestEvent,
            GroupInviteEvent
        ]

        for event_type in sub_event:
            if event_type.type_validator(event):
                if hasattr(event_type, "_parse__event"):
                    event = event_type._parse__event(event)
                else:
                    event = type_validate_python(event_type, obj)
                break

        return event
    
    @override
    def get_user_id(self) -> str:
        return self.FromUserName
    
    @override
    def get_event_description(self):
        return super().get_event_description()

class FriendRequestEvent(RequestEvent):
    """
    好友请求事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.sub_type == MessageType.FriendAdd:
            return True
        return False
    
    @override
    @classmethod
    def _parse__event(cls, event: RequestEvent) -> "FriendRequestEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        raw_msg = data["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        msg = root.find("msg")
        scene = msg.get("scene")
        v3 = msg.get("encryptusername")
        v4 = msg.get("ticket")
        flag = FriendRequestData(
            scene=scene,
            option=2,
            v3=v3,
            v4=v4
        )
        obj.update(model_dump(flag))
        event: "FriendRequestEvent" = type_validate_python(cls, obj)
        return event

class GroupInviteEvent(RequestEvent):
    """
    群邀请事件
    """
    sub_type: MessageType = MessageType.AppMsg
    """消息子类型"""

    @override
    @staticmethod
    def type_validator(event: NoticeEvent) -> bool:
        if event.sub_type == MessageType.AppMsg:
            root = ET.fromstring(remove_prefix_tag(event.data["Data"]["Content"]["string"]))
            if root.tag != "msg":
                return False
            type = root.find("appmsg").find("type").text
            title = root.find("appmsg").find("title").text
            if int(type) == AppType.Link.value and "邀请你加入群聊" in title:
                return True
        return False

    @override
    @classmethod
    def _parse__event(cls, event: RequestEvent) -> "GroupInviteEvent":
        obj = deepcopy(model_dump(event))
        data = obj["data"]["Data"]
        raw_msg: str = data["Content"]["string"]
        root = ET.fromstring(remove_prefix_tag(raw_msg))
        msg = root.find("msg")
        url = msg.find("appmsg").find("url").text
        start_index = url.find('![CDATA[') + len('![CDATA[')
        end_index = url.find(']]>')
        url = data[start_index:end_index]
        flag = GroupRequestData(
            url=url
        )
        obj.update(model_dump(flag))
        event: "GroupInviteEvent" = type_validate_python(cls, obj)
        return event



class MetaEvent(Event):
    """
    元事件基类
    """
    type: Final[str] = "meta"

    @override
    @classmethod
    def _parse_event(cls, event: Event) -> "RequestEvent":
        obj = deepcopy(model_dump(event))
        event: "MetaEvent" = type_validate_python(cls, obj)

        sub_event: List[MetaEvent] = [
            OfflineEvent,
            TestEvent
        ]

        for event_type in sub_event:
            if event_type.type_validator(event):
                if hasattr(event_type, "_parse__event"):
                    event = event_type._parse__event(event)
                else:
                    event = type_validate_python(event_type, obj)
                break

        return event

    @override
    @staticmethod
    def type_validator(event: Event) -> bool:
        return event.type in [TypeName.Offline, TypeName.Test]
    
    @override
    def get_event_description(self):
        return "元事件"

class OfflineEvent(MetaEvent):
    """
    离线事件
    """

    @override
    @staticmethod
    def type_validator(event: Event) -> bool:
        return event.type == TypeName.Offline
    
    @override
    def get_event_description(self):
        return "离线事件"

class TestEvent(MetaEvent):
    """
    测试事件
    """

    @override
    @staticmethod
    def type_validator(event: Event) -> bool:
        return event.type == TypeName.Test

    @override
    def get_event_description(self):
        return "测试连接事件"
