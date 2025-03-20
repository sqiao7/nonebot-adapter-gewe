from pydantic import BaseModel
from typing import List, Dict, Union, Optional

# 联系人模块

class InfoData(BaseModel):
    """好友/群聊数据"""
    # 用户名
    userName: str
    nickName: str
    pyInitial: str
    quanPin: str
    sex: int
    remark: str
    remarkPyInitial: str
    remarkQuanPin: str
    signature: Optional[str] = None
    alias: str
    snsBgImg: Optional[str] = None
    country: str
    bigHeadImgUrl: str
    smallHeadImgUrl: str
    description: Optional[str] = None
    cardImgUrl: Optional[str] = None
    labelList: Optional[str] = None
    province: str
    city: str
    phoneNumList: Optional[List[str]] = None

class Response(BaseModel):
    ret: int
    """状态码"""
    msg: str
    """返回信息"""
    data: Optional[Dict] = None
    """返回数据"""

class ContactListData(BaseModel):
    """联系人列表数据"""
    friends: List[str]
    """好友列表"""
    chatrooms: List[str]
    """群聊列表"""
    ghs: List[str]
    """公众号列表"""

class ContactListResponse(Response):
    data: ContactListData

class SearchRequest(BaseModel):
    """搜索请求"""
    contactsInfo: str
    """搜索的联系人信息, 微信号、手机号..."""

class SearchSuccessData(BaseModel):
    """搜索成功数据"""
    v3: str
    nickName: str
    """昵称"""
    sex: str
    """性别"""
    signature: str
    """个性签名"""
    bigHeadImgUrl: str
    """头像大图"""
    smallHeadImgUrl: str
    """头像小图"""
    v4: str

class SearchFailureData(BaseModel):
    code: str
    msg: str

class SearchResponse(Response):
    data: Union[SearchSuccessData, SearchFailureData]

class AddContactRequest(BaseModel):
    """添加联系人请求"""
    scene: str
    """添加来源"""
    option: str
    """操作类型"""
    v3: str
    v4: str
    content: str
    """添加好友时的招呼语"""

class DeleteFriendRequest(BaseModel):
    """删除好友请求"""
    wxid: str
    """好友的微信号"""

class uploadPhoneAddressRequest(BaseModel):
    """上传手机通讯录请求"""
    phones: List[str]
    """需要上传的手机号"""
    opType: int
    """操作类型, 1:添加, 2:删除"""

class GetBreifInfoRequest(BaseModel):
    """获取简要信息请求"""
    wxids: List[str]
    """好友的微信号,>=1 <=100"""

class GetBreifInfoResponse(Response):
    data: List[InfoData]

class GetDetailInfoRequest(BaseModel):
    """获取详细信息请求"""
    wxids: List[str]
    """好友的微信号,>=1 <=20"""

class GetDetailInfoResponse(Response):
    data: List[InfoData]

class SetFriendPermissionsRequest(BaseModel):
    """设置好友权限请求"""
    wxid: str
    """好友的微信号"""
    onlyChat: bool
    """设置好友是否仅聊天"""

class SetFriendRemarkRequest(BaseModel):
    """设置好友备注请求"""
    wxid: str
    """好友的微信号"""
    remark: str
    """备注"""

class GetPhoneAddressListRequest(BaseModel):
    """获取手机通讯录请求"""
    phones: Optional[List[str]] = None
    """获取哪些手机号的好友详情, 不传获取所有"""

class GetPhoneAddressListResponse(Response):
    data: List[InfoData]

# 群模块

class createChatroomRequest(BaseModel):
    """创建群聊请求"""
    wxids: List[str]
    """群聊成员的微信号,>=2"""

class createChatroomData(BaseModel):
    """创建群聊数据"""
    headImgBase64: str
    """群聊头像的base64编码"""
    chatroomId: str
    """群聊ID"""

class createChatroomResponse(Response):
    data: createChatroomData

class modifyChatroomNameRequest(BaseModel):
    """修改群聊请求"""
    chatroomName: str
    """群聊ID"""
    chatroomId: str
    """群聊名称"""

class modifyChatroomRemarkRequest(BaseModel):
    """修改群聊备注请求"""
    chatroomId: str
    """群聊ID"""
    chatroomRemark: str
    """备注"""

class modifyChatroomNickNameForSelfRequest(BaseModel):
    """修改群聊昵称请求"""
    chatroomId: str
    """群聊ID"""
    nickName: str
    """昵称"""

class inviteMemberRequest(BaseModel):
    """邀请成员请求"""
    chatroomId: str
    """群聊ID"""
    wxids: str
    """成员的微信号,用英文逗号分隔"""
    reason: str
    """邀请理由"""

class removeMemberRequest(BaseModel):
    """移除成员请求"""
    chatroomId: str
    """群聊ID"""
    wxids: str
    """成员的微信号,用英文逗号分隔"""

class quitChatroomRequest(BaseModel):
    """退出群聊请求"""
    chatroomId: str
    """群聊ID"""

class disbandChatroomRequest(BaseModel):
    """解散群聊请求"""
    chatroomId: str
    """群聊ID"""

class getChatroomInfoRequest(BaseModel):
    """获取群聊信息请求"""
    chatroomId: str
    """群聊ID"""

class ChatroomMemberInfo(BaseModel):
    """群成员信息数据"""
    wxid: str
    """成员的wxid"""
    nickName: str
    """成员的昵称"""
    inviterUserName: Optional[str] = None
    """邀请人的wxid"""
    memberFlag: Optional[int] = None
    """标识"""
    displayName: Optional[str] = None
    """在本群内的昵称"""
    bigHeadImgUrl: Optional[str] = None
    """大尺寸头像"""
    smallHeadImgUrl: Optional[str] = None
    """小尺寸头像"""

class getChatroomInfoData(BaseModel):
    """获取群聊信息数据"""
    chatroomId: str
    """群聊ID"""
    nickName: str
    """群聊名称"""
    pyInitial: str
    """群聊名称的拼音首字母"""
    quanPin: str
    """群聊名称的拼音全拼"""
    sex: int
    remark: str
    """群备注, 仅自己可见"""
    remarkPyInitial: str
    """备注的拼音首字母"""
    remarkQuanPin: str
    """备注的拼音全拼"""
    chatRoomNotify: int
    """群消息是否提醒"""
    chatRoomOwner: str
    """群主的wxid"""
    smallHeadImgUrl: int
    """群头像链接"""
    memberList: List[ChatroomMemberInfo]
    """群成员信息"""

class getChatroomInfoResponse(Response):
    data: getChatroomInfoData

class getChatroomMemberListRequest(BaseModel):
    """获取群成员列表请求"""
    chatroomId: str
    """群聊ID"""
    
class getChatroomMemberListData(BaseModel):
    """获取群成员列表数据"""
    memberList: List[ChatroomMemberInfo]
    """群成员信息"""
    chatroomOwner: Optional[str] = None
    """群主wxid"""
    adminWxid: Optional[List[Dict[str, str]]] = None
    """管理员wxid"""
    
class getChatroomMemberListResponse(Response):
    data: getChatroomMemberListData

class getChatroomMemberDetailRequest(BaseModel):
    """获取群成员详情请求"""
    chatroomId: str
    """群聊ID"""
    memberWxids: List[str]
    """成员的wxid"""

class MemberDetail(BaseModel):
    """成员详情数据"""
    userName: str
    """成员的wxid"""
    nickName: str
    """成员的昵称"""
    pyInitial: Optional[str] = None
    """成员昵称的拼音首字母"""
    quanPin: Optional[str] = None
    """成员昵称的拼音全拼"""
    sex: int
    """成员的性别"""
    remark: Optional[str] = None
    """成员的备注"""
    remarkPyInitial: Optional[str] = None
    """成员备注的拼音首字母"""
    remarkQuanPin: Optional[str] = None
    """成员备注的拼音全拼"""
    chatRoomNotify: int
    """群消息是否提醒"""
    signature: Optional[str] = None
    """个性签名"""
    alias: Optional[str] = None
    """微信号"""
    snsBgImg: Optional[str] = None
    """朋友圈背景图片"""
    bigHeadImgUrl: str
    """大尺寸头像"""
    smallHeadImgUrl: str
    """小尺寸头像"""
    description: Optional[str] = None
    """描述"""
    cardImgUrl: Optional[str] = None
    """描述的图片链接"""
    labelList: Optional[str] = None
    """标签列表, 多个英文逗号分隔"""
    country: Optional[str] = None
    """国家"""
    province: Optional[str] = None
    """省份"""
    city: Optional[str] = None
    """城市"""
    phoneNumList: Optional[List[str]] = None
    """手机号码"""
    friendUserName: Optional[str] = None
    """好友wxid"""
    inviterUserName: Optional[str] = None
    """邀请人的wxid"""
    memberFlag: Optional[int] = None
    """标识"""

class getChatroomMemberDetailResponse(Response):
    data: List[MemberDetail]

class getChatroomAnnouncementRequest(BaseModel):
    """获取群公告请求"""
    chatroomId: str
    """群聊ID"""

class ChatroomAnnouncement(BaseModel):
    """群公告数据"""
    announcement: str
    """公告内容"""
    announcementEditor: int
    """群公告作者的wxid"""
    publishTime: int
    """群公告发布时间"""

class getChatroomAnnouncementResponse(Response):
    data: ChatroomAnnouncement

class setChatroomAnnouncementRequest(BaseModel):
    """设置群公告请求"""
    chatroomId: str
    """群聊ID"""
    content: str
    """公告内容"""

class agreeJoinRoomRequest(BaseModel):
    """同意加群请求"""
    url: str
    """邀请进群回调消息中的url"""

class agreeJoinRoomData(BaseModel):
    chatroomId: str

class agreeJoinRoomResponse(Response):
    data: agreeJoinRoomData

class addGroupMemberAsFriendRequest(BaseModel):
    """添加群成员为好友请求"""
    chatroomId: str
    """群聊ID"""
    memberWxid: str
    """成员的wxid"""
    content: str
    """加好友的招呼语"""

class addGroupMemberAsFriendData(BaseModel):
    """添加群成员为好友数据"""
    v3: str
    """添加群成员的v3, 通过好友后会通过回调消息返回此值"""

class addGroupMemberAsFriendResponse(Response):
    data: addGroupMemberAsFriendData

class getChatroomQrCodeRequest(BaseModel):
    """获取群二维码请求"""
    chatroomId: str
    """群聊ID"""

class getChatroomQrCodeData(BaseModel):
    """获取群二维码数据"""
    qrBase64: str
    """群二维码图片的base64"""
    qrTips: str
    """群二维码的提示信息"""

class getChatroomQrCodeResponse(Response):
    data: getChatroomQrCodeData

class saveContractListRequest(BaseModel):
    """群保存到通讯录请求"""
    chatroomId: str
    """群聊ID"""
    operType: int
    """操作类型 3保存到通讯录 2从通讯录移除"""

class adminOperateRequest(BaseModel):
    """管理员操作请求"""
    chatroomId: str
    """群聊ID"""
    operType: str
    """操作类型 1: 添加群管理(可添加多个微信号) 2: 删除群管理(可删除多个) 3: 转让(只能转让一个微信号)"""
    wxids: List[str]
    """操作对象的wxid"""

class pinChatRequest(BaseModel):
    """置顶聊天请求"""
    chatroomId: str
    """群聊ID"""
    top: bool
    """是否置顶"""

class setMsgSilenceRequest(BaseModel):
    """消息免打扰请求"""
    chatroomId: str
    """群聊ID"""
    silence: bool
    """是否免打扰"""

class joinRoomUsingQRCodeRequest(BaseModel):
    """扫码进群"""
    qrUrl: str
    """通过解析群二维码图片获得的链接"""

class joinRoomUsingQRCodeData(BaseModel):
    """扫码进群数据"""
    chatroomName: str
    """群聊名称"""
    html: Optional[str] = None
    chatroomId: str
    """群聊ID"""

class joinRoomUsingQRCodeResponse(Response):
    data: joinRoomUsingQRCodeData

class roomAccessApplyCheckApproveRequest(BaseModel):
    """群申请审核"""
    chatroomId: str
    """群聊ID"""
    wnewMsgIdxid: str
    """消息ID"""
    msgContent: str
    """消息内容"""

# 消息模块

class messageResponseData(BaseModel):
    """消息响应数据"""
    toWxid: str
    """接收人的wxid"""
    createTime: Optional[int] = None
    """发送时间"""
    msgId: int
    """消息ID"""
    newMsgId: int
    """新消息ID"""
    type: Optional[int] = None
    """消息类型"""

class revokeMsgRequest(BaseModel):
    """撤回消息请求"""
    toWxid: str
    """好友/群的ID"""
    msgId: str
    """发送类接口返回的msgId"""
    newMsgId: str
    """发送类接口返回的newMsgId"""
    createTime: str
    """发送类接口返回的createTime"""

class downloadImageRequest(BaseModel):
    """下载图片请求"""
    xml: str
    """回调消息中的XML"""
    type: int = 2
    """下载的图片类型 1:高清图片 2:常规图片 3:缩略图"""

class downloadImageData(BaseModel):
    """下载图片数据"""
    fileUrl: str
    """图片链接地址, 7天有效"""

class downloadImageResponse(Response):
    data: downloadImageData

class postTextRequest(BaseModel):
    """发送文本消息请求"""
    toWxid: str
    """好友/群的ID"""
    content: str
    """消息内容"""
    ats: str = ""
    """@好友列表, 多个逗号分隔, 群主或管理员@全部的人，则填写'notify@all'"""

class postTextResponse(Response):
    data: messageResponseData

class postImageRequest(BaseModel):
    """发送图片请求"""
    toWxid: str
    """好友/群的ID"""
    imgUrl: str
    """图片链接地址"""

class postImageData(messageResponseData):
    aesKey: str
    """cdn相关的aeskey"""
    fileId: str
    """cdn相关的fileid"""
    length: int
    """图片文件大小"""
    width: int
    """图片宽度"""
    height: int
    """图片高度"""
    md5: str
    """图片md5"""

class postImageResponse(Response):
    data: postImageData

class postFileRequest(BaseModel):
    """发送文件请求"""
    toWxid: str
    """好友/群的ID"""
    fileUrl: str
    """文件链接地址"""
    fileName: str
    """文件名称"""

class postFileResponse(Response):
    data: messageResponseData

class postVoiceRequest(BaseModel):
    """发送语音请求"""
    toWxid: str
    """好友/群的ID"""
    voiceUrl: str
    """语音链接地址, 仅支持silk格式"""
    voiceDuration: int
    """语音时长，单位毫秒"""

class postVoiceResponse(Response):
    data: messageResponseData

class postVideoRequest(BaseModel):
    """发送视频请求"""
    toWxid: str
    """好友/群的ID"""
    videoUrl: str
    """视频链接地址"""
    thumbUrl: str
    """视频封面链接地址"""
    videoDuration: int
    """视频时长，单位秒"""

class postVideoData(messageResponseData):
    """消息类型"""
    aesKey: str
    """cdn相关的aeskey"""
    fileId: Optional[str] = None
    """cdn相关的fileid"""
    length: int
    """视频文件大小"""

class postVideoResponse(Response):
    data: postVideoData

class postLinkRequest(BaseModel):
    """发送链接请求"""
    toWxid: str
    """好友/群的ID"""
    title: str
    """链接标题"""
    desc: str
    """链接描述"""
    linkUrl: str
    """链接地址"""
    thumbUrl: str
    """链接图片地址"""

class postLinkResponse(Response):
    data: messageResponseData

class postNameCardRequest(BaseModel):
    """发送名片请求"""
    toWxid: str
    """好友/群的ID"""
    nickName: str
    """名片的昵称"""
    nameCardWxid: str
    """名片的wxid"""

class postNameCardResponse(Response):
    data: messageResponseData

class postEmojiRequest(BaseModel):
    """发送表情包请求"""
    toWxid: str
    """好友/群的ID"""
    emojiMd5: str
    """表情包md5"""
    emojiSize: int
    """表情包大小"""

class postEmojiResponse(Response):
    data: messageResponseData

class postAppMsgRequest(BaseModel):
    """发送小程序请求,本接口可用于发送所有包含节点的消息，例如：音乐分享、视频号、引用消息等等"""
    toWxid: str
    """好友/群的ID"""
    appmsg: str
    """回调消息中的appmsg节点内容"""

class postAppMsgResponse(Response):
    data: messageResponseData

class postMiniAppRequest(BaseModel):
    """发送小程序请求"""
    toWxid: str
    """好友/群的ID"""
    miniAppId: str
    """小程序ID"""
    displayName: str
    """小程序名称"""
    pagePath: str
    """小程序页面路径"""
    coverImgUrl: str
    """小程序封面链接地址"""
    title: str
    """小程序标题"""
    userName: str
    """归属的用户ID"""

class postMiniAppResponse(Response):
    data: messageResponseData

class forwardFileRequest(BaseModel):
    """转发文件请求"""
    toWxid: str
    """好友/群的ID"""
    xml: str
    """xml"""

class forwardFileResponse(Response):
    data: messageResponseData

class forwardImageRequest(BaseModel):
    """转发图片请求"""
    toWxid: str
    """好友/群的ID"""
    xml: str
    """xml"""

class forwardImageResponse(Response):
    data: postImageData

class forwardVideoRequest(BaseModel):
    """转发视频请求"""
    toWxid: str
    """好友/群的ID"""
    xml: str
    """xml"""

class forwardVideoResponse(Response):
    data: postVideoData

class forwardUrlRequest(BaseModel):
    """转发链接请求"""
    toWxid: str
    """好友/群的ID"""
    xml: str
    """xml"""

class forwardUrlResponse(Response):
    data: messageResponseData

class forwardMiniAppRequest(BaseModel):
    """转发小程序请求"""
    toWxid: str
    """好友/群的ID"""
    xml: str
    """xml"""
    coverImgUrl: str
    """小程序封面链接地址"""

class forwardMiniAppResponse(Response):
    data: messageResponseData

# 标签模块

class Label(BaseModel):
    """标签数据"""
    labelId: int
    """标签ID"""
    labelName: str
    """标签名称"""

class addLabelRequest(BaseModel):
    """添加标签请求"""
    labelName: str
    """标签名称"""

class addLabelResponse(Response):
    data: Label

class delLabelRequest(BaseModel):
    """删除标签请求"""
    labels: str
    """标签ID, 多个逗号分隔"""

class getLabelListData(BaseModel):
    """获取标签列表数据"""
    labelList: List[Label]
    """标签列表"""

class getLabelListResponse(Response):
    data: getLabelListData

class modifyMemberListRequest(BaseModel):
    """修改好友标签,每次在修改时都需要进行全量修改"""
    labelIds: str
    """标签ID, 多个逗号分隔"""
    wxIds: List[str]
    """好友wxid"""

# 个人模块

class profileRequest(BaseModel):
    """获取个人资料请求"""
    proxyIp: str = ""
    """proxyIp"""

class Profile(BaseModel):
    """个人资料"""
    alias: Optional[str] = None
    """微信号"""
    wxid: str
    """wxid"""
    nickName: str
    """昵称"""
    mobile: str
    """手机号"""
    uin: int
    """uin"""
    sex: int
    """性别"""
    province: Optional[str] = None
    """省份"""
    city: Optional[str] = None
    """城市"""
    signature: Optional[str] = None
    """个性签名"""
    country: Optional[str] = None
    """国家"""
    bigHeadImgUrl: Optional[str] = None
    """大尺寸头像"""
    smallHeadImgUrl: Optional[str] = None
    """小尺寸头像"""
    regCountry: str
    """注册国家"""
    snsBgImg: Optional[str] = None
    """朋友圈背景图"""

class getProfileResponse(Response):
    data: Profile

class getQrCodeData(BaseModel):
    """获取二维码数据"""
    qrCode: str
    """二维码图片的base64"""

class getQrCodeResponse(Response):
    data: getQrCodeData

class SafetyInfoData(BaseModel):
    """获取设备记录"""
    uuid: str
    """设备uuid"""
    deviceName: str
    """设备名称"""
    deviceType: str
    """设备类型"""
    lastTime: int
    """最后使用时间"""

class getSafetyInfoData(BaseModel):
    """获取设备记录请求"""
    list: List[SafetyInfoData]

class getSafetyInfoResponse(Response):
    data: getSafetyInfoData

class privacySettingsRequest(BaseModel):
    """隐私设置请求"""
    option: int
    """
    隐私设置的选项
    4: 加我为朋友时需要验证
    7: 向我推荐通讯录朋友
    8: 添加我的方式 手机号
    25: 添加我的方式 微信号
    38: 添加我的方式 群聊
    39: 添加我的方式 我的二维码
    40: 添加我的方式 名片
    """
    open: bool
    """开关"""

class updateProfileRequest(BaseModel):
    """修改个人资料请求"""
    city: str
    """城市"""
    country: str
    """国家"""
    nickName: str
    """昵称"""
    province: str
    """省份"""
    signature: str
    """个性签名"""
    sex: int
    """性别"""

class updateHeadImgRequest(BaseModel):
    """修改头像请求"""
    headImgUrl: str
    """头像的图片地址"""

# 收藏夹模块

class FavorFold(BaseModel):
    """收藏夹"""
    favId: str
    """收藏夹ID"""
    type: str
    """收藏夹类型"""
    flag: str
    """收藏夹标识"""
    updateTime: str
    """更新时间"""

class FavorItem(BaseModel):
    """收藏夹内容"""
    favId: str
    """收藏夹ID"""
    status: str
    """状态"""
    flag: str
    """收藏夹标识"""
    updateTime: str
    """更新时间"""
    content: str
    """收藏夹内容"""

class syncFavorRequest(BaseModel):
    """同步收藏夹请求,响应结果中会包含已删除的的收藏夹记录, 通过flag=1来判断已删除"""
    syncKey: str
    """翻页key, 首次传空, 获取下一页传接口返回的syncKey"""

class syncFavorData(BaseModel):
    syncKey: str
    list: Optional[List[FavorFold]] = None

class syncFavorResponse(Response):
    data: syncFavorData

class getFavorContentRequest(BaseModel):
    """获取收藏夹内容请求"""
    favId: str
    """收藏夹ID"""

class getFavorContentResponse(Response):
    data: FavorItem

class deleteFavorFolderRequest(BaseModel):
    """删除收藏夹请求"""
    favId: str
    """收藏夹ID"""
