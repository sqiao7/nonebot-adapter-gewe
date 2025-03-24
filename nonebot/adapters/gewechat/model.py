from enum import Enum
from pydantic import BaseModel
from typing import Optional, Union

class TypeName(str, Enum):
    Test = "Test"
    AddMsg = "AddMsg"
    ModContacts = "ModContacts"
    DelContacts = "DelContacts"
    Offline = "Offline"

class MessageType(int, Enum):
    Text = 1
    Image = 3
    Voice = 34
    FriendAdd = 37
    NameCard = 42
    Video = 43
    Emoji = 47
    Location = 48
    AppMsg = 49 # 公众号/文件/小程序/引用/转账/红包/视频号/群聊邀请
    RePush = 51 # 重新推送?
    GroupOp = 10000 # 被踢出群聊/更换群主/修改群名称
    SystemMsg = 10002 # 撤回/拍一拍/成员被移出群聊/解散群聊/群公告/群待办

class AppType(int, Enum):
    Link = 5 # 公众号链接/群聊邀请
    FileSend = 74
    FileDone = 6
    MiniProgram1 = 33
    MiniProgram2 = 36
    Quote = 57
    Transfer = 2000
    RedPacket = 2001
    VideoChannel = 51

class SystemMsgType(Enum):
    Revoke = "revokemsg"
    Poke = "pat"
    Template = "sysmsgtemplate" # 踢出群聊/解散群聊
    GroupNotice = "mmchatroombarannouncememt"
    GroupTodo = "roomtoolstips"

class ImgBuf(BaseModel):
    iLen: int
    buffer: Optional[str] = None
    """缩略图base64字符串"""

class StringDict(BaseModel):
    string: str

class AddMessageData(BaseModel):
    MsgId: int
    FromUserName: StringDict
    ToUserName: StringDict
    MsgType: MessageType
    Content: StringDict
    Status: int
    ImgStatus: int
    ImgBuf: ImgBuf
    CreateTime: int
    MsgSource: str
    PushContent: Optional[str] = None
    NewMsgId: int
    MsgSeq: int

class SnsUserInfo(BaseModel):
    SnsFlag: int
    SnsBgimgId: Optional[str] = None
    SnsBgobjectId: int
    SnsFlagEx: int

class CustomizedInfo(BaseModel):
    BrandFlag: int

class AdditionalContactList(BaseModel):
    LinkedinContactItem: Optional[dict[str, dict]] = {}

class ModContactsData(BaseModel):
    UserName: Union[StringDict, dict] = {}
    NickName: Union[StringDict, dict] = {}
    PyInitial: Union[StringDict, dict] = {}
    QuanPin: Union[StringDict, dict] = {}
    Sex: int
    ImgBuf: ImgBuf
    BitMask: int
    BitVal: int
    ImgFlag: int
    Remark: Optional[dict] = {}
    RemarkPyinitial: Optional[dict] = {}
    RemarkQuanPin: Optional[dict] = {}
    ContactType: int
    RoomInfoCount: int
    DomainList: Optional[list[dict]] = [{}]
    ChatRoomNotify: int
    AddContactScene: int
    PersonalCard: int
    HasWeiXinHdHeadImg: int
    VerifyFlag: int
    Level: int
    Source: int
    WeiboFlag: int
    AlbumStyle: int
    AlbumFlag: int
    SnsUserInfo: SnsUserInfo
    CustomizedInfo: CustomizedInfo
    AdditionalContactList: AdditionalContactList
    ChatroomMaxCount: int
    DeleteFlag: int
    Description: str
    ChatroomStatus: int
    Extflag: int
    ChatRoomBusinessType: int

    ChatRoomOwner: Optional[str] = None

    Province: Optional[str] = None
    City: Optional[str] = None
    Signature: Optional[str] = None
    Country: Optional[str] = None
    BigHeadImgUrl: Optional[str] = None
    SmallHeadImgUrl: Optional[str] = None
    EncryptUserName: Optional[str] = None

class DelContactsData(BaseModel):
    username: str
    delete_contact_scene: int

class OfflineData(BaseModel):
    pass

class Message(BaseModel):
    TypeName: TypeName
    Appid: str
    Wxid: Optional[str]
    Data: Union[AddMessageData, ModContactsData, DelContactsData]

class TestMessage(BaseModel):
    testMsg: str
    token: str

class FriendRequestScene(Enum):
    WX_SEARCH = 3
    """微信搜索"""
    QQ_FRIEND = 4
    """QQ好友"""
    FROM_NAMECARD = 6
    """来自名片"""
    FROM_GROUP = 8
    """来自群聊"""
    PHONE_NUMBER = 15
    """手机号"""

class FriendRequestOption(Enum):
    ADD = 2
    """添加"""
    AGREE = 3
    """同意"""
    REJECT = 4
    """拒绝"""

class FriendRequestData(BaseModel):
    scene: FriendRequestScene
    """添加来源"""
    option: FriendRequestOption
    """操作"""
    v3: str
    v4: str
    content: str
    """好友请求内容"""

class GroupRequestData(BaseModel):
    url: str
    """群聊邀请链接"""
