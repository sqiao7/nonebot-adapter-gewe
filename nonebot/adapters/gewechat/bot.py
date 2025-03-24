import re
import asyncio

from typing import TYPE_CHECKING, Any, Union
from typing_extensions import override

from nonebot.adapters import Bot as BaseBot
from nonebot.message import handle_event
from nonebot.compat import type_validate_python, model_dump
from nonebot.adapters.gewechat.event import Event
from .message import Message, MessageSegment
from .event import Event, MessageEvent, TextMessageEvent, ImageMessageEvent
from .utils import log, resp_json
from .api_model import *

if TYPE_CHECKING:
    from .adapter import Adapter
    

def check_at_me(bot: "Bot", event: TextMessageEvent):
    if event.message.has("at_all"):
        event.to_me = True
        event.message = event.message.exclude("at_all")
    
    if not event.message:
        event.message.append(MessageSegment.text(""))

    def _is_at_me_seg(segment: MessageSegment):
        return segment.type == "at" and str(segment.data.get("wxid", "")) == str(bot.self_id)

    if _is_at_me_seg(event.message[0]):
        event.to_me = True
        event.message.pop(0)
        if event.message and event.message[0].type == "text":
            event.message[0].data["text"] = event.message[0].data["text"].lstrip()
            if not event.message[0].data["text"]:
                event.message.pop(0)
        if event.message and _is_at_me_seg(event.message[0]):
            event.message.pop(0)
            if event.message and event.message[0].type == "text":
                event.message[0].data["text"] = event.message[0].data["text"].lstrip()
                if not event.message[0].data["text"]:
                    event.message.pop(0)

    if not event.to_me:
        i = -1
        last_msg_seg = event.message[i]
        if (
            last_msg_seg.type == "text"
            and not last_msg_seg.data["text"].strip()
            and len(event.message) >= 2
        ):
            i -= 1
            last_msg_seg = event.message[i]

        if _is_at_me_seg(last_msg_seg):
            event.to_me = True
            del event.message[i:]

    if not event.message:
        event.message.append(MessageSegment.text(""))


def check_nickname(bot: "Bot", event: TextMessageEvent):
    nicknames = bot.config.nickname
    nickname_regex = "|".join(nicknames)
    m = re.search(rf"^({nickname_regex})([\s,, ]*|$)", event.message[0].data["text"], re.IGNORECASE)
    if m:
        nickname = m.group(1).strip()
        log("DEBUG", f"User is calling me: {nickname}")
        event.to_me = True
        loc = m.end()
        event.message.include("text")[0].data["text"] = event.message.include("text")[0].data["text"][loc:]


class Bot(BaseBot):
    """Gewechat Bot 适配"""

    @override
    def __init__(self, adapter, self_id: str, **kwargs: Any):
        super().__init__(adapter, self_id)
        self.adapter: Adapter = adapter

    async def handle_event(self, event: Event):
        # 根据需要, 对事件进行某些预处理, 例如：
        # 检查事件是否和机器人有关操作, 去除事件消息首尾的 @bot
        # 检查事件是否有回复消息, 调用平台 API 获取原始消息的消息内容
        if isinstance(event, MessageEvent):
            if isinstance(event, TextMessageEvent):
                await event.get_ats_wxid(self)
                check_at_me(self, event)
                check_nickname(self, event)
            elif isinstance(event, ImageMessageEvent):
                await event.download_image(self)
            if not event.is_group_message():
                event.to_me = True
        # 调用 handle_event 让 NoneBot 对事件进行处理
        await handle_event(self, event)

    async def call_api(self, api: str, **data: Any) -> Response:
        if not data.get("appId"):
            data["appId"] = self.config.appid
        return await self.adapter._do_call_api(api, **data)

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
        tasks = []
        for (api, data) in message.to_payload():
            data["toWxid"] = toWxid
            data["appId"] = self.adapter.adapter_config.appid

            tasks.append(self.call_api(api, **data))

        return await asyncio.gather(*tasks)
    
    async def check_online(self) -> bool:
        """检查是否在线"""
        return resp_json(await self.call_api("/login/checkOnline"))['data']
    
    async def reconnect(self) -> dict:
        """重连"""
        return resp_json(await self.call_api("/login/reconnection"))
    
    async def logout(self) -> dict:
        """登出"""
        self.adapter.bot_disconnect(self)
        return resp_json(await self.call_api("/login/logout"))
    
    async def fetchContactsList(self, cache: bool = False) -> ContactListResponse:
        """
        获取联系人列表
        cache: 是否使用缓存, 默认为 False
        """
        if cache:
            await self.call_api("/contacts/fetchContactsListCache")
        return type_validate_python(ContactListResponse, resp_json(await self.call_api("/contacts/fetchContactsList")))

    async def search(self, keyword: str) -> SearchResponse:
        """
        搜索联系人
        搜索的联系人信息若已经是好友, 响应结果的v3则为好友的wxid
        本接口返回的数据可通过添加联系人接口发送添加好友请求
        keyword: 搜索的联系人信息, 微信号、手机号...
        """
        request = SearchRequest(contactsInfo=keyword)
        return type_validate_python(SearchResponse, resp_json(await self.call_api("/contacts/search", **model_dump(request))))

    async def addContact(self, scene: int, option: int, v3: str, v4: str, content: str) -> Response:
        """
        添加/同意添加联系人
        本接口建议在线3天后再进行调用。
        好友添加成功后, 会通过回调消息推送一条包含v3的消息, 可用于判断好友是否添加成功。
        scene: 添加来源
        option: 操作类型
        v3: 通过搜索或回调消息获取到的v3
        v4: 通过搜索或回调消息获取到的v4
        content: 添加好友时的招呼语
        """
        request = AddContactRequest(scene=scene, option=option, v3=v3, v4=v4, content=content)
        return type_validate_python(Response, resp_json(await self.call_api("/contacts/addContacts", **model_dump(request))))
    
    async def deleteFriend(self, wxid: str) -> Response:
        """
        删除联系人
        wxid: 联系人v3
        """
        request = DeleteFriendRequest(wxid=wxid)
        return type_validate_python(Response, resp_json(await self.call_api("/contacts/deleteFriend", **model_dump(request))))
    
    async def uploadPhoneAddressList(self, phones: List[str], opType: int) -> Response:
        """
        上传手机通讯录
        phones: 需要上传的手机号
        opType: 操作类型, 1:上传 2:删除
        """
        request = uploadPhoneAddressRequest(phones=phones, opType=opType)
        return type_validate_python(Response, resp_json(await self.call_api("/contacts/uploadPhoneAddressList", **model_dump(request))))
    
    async def getBreifInfo(self, wxids: List[str]) -> GetBreifInfoResponse:
        """
        获取联系人简要信息
        wxids: 好友的wxid(>=1, <=100)
        """
        if len(wxids) > 100 or len(wxids) == 0:
            log("error", "wxid数量错误", ValueError("wxid数量错误"))
        request = GetBreifInfoRequest(wxids=wxids)
        return type_validate_python(GetBreifInfoResponse, resp_json(await self.call_api("/contacts/getBriefInfo", **model_dump(request))))


    async def getDetailInfo(self, wxids: List[str]) -> GetDetailInfoResponse:
        """
        获取联系人详细信息
        wxid: 好友的wxid(>=1, <=20)
        """
        if len(wxids) > 20 or len(wxids) == 0:
            log("error", "wxid数量错误", ValueError("wxid数量错误"))
        request = GetDetailInfoRequest(wxids=wxids)
        return type_validate_python(GetDetailInfoResponse, resp_json(await self.call_api("/contacts/getDetailInfo", **model_dump(request))))

    async def setFriendPermissions(self, wxid: str, onlyChat: bool) -> Response:
        """
        设置好友仅聊天
        wxid: 好友的wxid
        onlyChat: 是否仅聊天
        """
        request = SetFriendPermissionsRequest(wxid=wxid, onlyChat=onlyChat)
        return type_validate_python(Response, resp_json(await self.call_api("/contacts/setFriendPermissions", **model_dump(request))))
    
    async def setFriendRemark(self, wxid: str, remark: str) -> Response:
        """
        设置好友备注
        wxid: 好友的wxid
        remark: 备注
        """
        request = SetFriendRemarkRequest(wxid=wxid, remark=remark)
        return type_validate_python(Response, resp_json(await self.call_api("/contacts/setFriendRemark", **model_dump(request))))
    
    async def getPhoneAddressList(self, phones: Optional[List[str]] = None) -> GetPhoneAddressListResponse:
        """
        获取手机通讯录
        phones: 获取哪些手机号的好友详情, 不传获取所有
        """
        request = GetPhoneAddressListRequest(phones=phones)
        return type_validate_python(GetPhoneAddressListResponse, resp_json(await self.call_api("/contacts/getPhoneAddressList"), **model_dump(request)))
    
    async def createChatroom(self, wxids: List[str]) -> createChatroomResponse:
        """
        创建群聊
        wxids: 群聊成员的wxid(>=2)
        """
        if len(wxids) < 2:
            log("error", "wxid数量错误", ValueError("wxid数量错误"))
        request = createChatroomRequest(wxids=wxids)
        return type_validate_python(createChatroomResponse, resp_json(await self.call_api("/group/createChatroom", **model_dump(request))))
    
    async def modifyChatroomName(self, chatroomId: str, chatroomName: str) -> Response:
        """
        修改群聊名称
        chatroomId: 群聊id
        chatroomName: 群聊名称
        """
        request = modifyChatroomNameRequest(chatroomId=chatroomId, chatroomName=chatroomName)
        return type_validate_python(Response, resp_json(await self.call_api("/group/modifyChatroomName", **model_dump(request))))
    
    async def modifyChatroomRemark(self, chatroomId: str, chatroomRemark: str) -> Response:
        """
        修改群聊备注,群备注仅自己可见
        chatroomId: 群聊id
        chatroomRemark: 群聊备注
        """
        request = modifyChatroomRemarkRequest(chatroomId=chatroomId, chatroomRemark=chatroomRemark)
        return type_validate_python(Response, resp_json(await self.call_api("/group/modifyChatroomRemark", **model_dump(request))))

    async def modifyChatroomNickNameForSelf(self, chatroomId: str, nickName: str) -> Response:
        """
        修改我在群内的昵称
        chatroomId: 群聊id
        nickName: 昵称
        """
        request = modifyChatroomNickNameForSelfRequest(chatroomId=chatroomId, nickName=nickName)
        return type_validate_python(Response, resp_json(await self.call_api("/group/modifyChatroomNickNameForSelf", **model_dump(request))))

    async def inviteMember(self, chatroomId: str, wxids: List[str], reason: str) -> Response:
        """
        邀请好友入群
        chatroomId: 群聊id
        wxids: 好友wxid
        reason: 邀请理由
        """
        request = inviteMemberRequest(chatroomId=chatroomId, wxids=",".join(wxids), reason=reason)
        return type_validate_python(Response, resp_json(await self.call_api("/group/inviteMember", **model_dump(request))))
    
    async def removeMember(self, chatroomId: str, wxids: List[str]) -> Response:
        """
        移除群成员
        chatroomId: 群聊id
        wxids: 好友wxid
        """
        request = removeMemberRequest(chatroomId=chatroomId, wxids=",".join(wxids))
        return type_validate_python(Response, resp_json(await self.call_api("/group/removeMember", **model_dump(request))))
    
    async def quitChatroom(self, chatroomId: str) -> Response:
        """
        退出群聊
        chatroomId: 群聊id
        """
        request = quitChatroomRequest(chatroomId=chatroomId)
        return type_validate_python(Response, resp_json(await self.call_api("/group/quitChatroom", **model_dump(request))))
    
    async def disbandChatroom(self, chatroomId: str) -> Response:
        """
        解散群聊
        chatroomId: 群聊id
        """
        request = disbandChatroomRequest(chatroomId=chatroomId)
        return type_validate_python(Response, resp_json(await self.call_api("/group/disbandChatroom", **model_dump(request))))
    
    async def getChatroomInfo(self, chatroomId: str) -> getChatroomInfoResponse:
        """
        获取群聊信息
        chatroomId: 群聊id
        """
        request = getChatroomInfoRequest(chatroomId=chatroomId)
        return type_validate_python(getChatroomInfoResponse, resp_json(await self.call_api("/group/getChatroomInfo", **model_dump(request))))
    
    async def getChatroomMemberList(self, chatroomId: str) -> getChatroomMemberListResponse:
        """
        获取群聊成员列表
        chatroomId: 群聊id
        """
        request = getChatroomMemberListRequest(chatroomId=chatroomId)
        return type_validate_python(getChatroomMemberListResponse, resp_json(await self.call_api("/group/getChatroomMemberList", **model_dump(request))))
    
    async def getChatroomMemberDetail(self, chatroomId: str, memberWxids: List[str]) -> getChatroomMemberDetailResponse:
        """
        获取群聊成员详细信息
        chatroomId: 群聊id
        memberWxids: 成员wxid
        """
        request = getChatroomMemberDetailRequest(chatroomId=chatroomId, memberWxids=memberWxids)
        return type_validate_python(getChatroomMemberDetailResponse, resp_json(await self.call_api("/group/getChatroomMemberDetail", **model_dump(request))))
    
    async def getChatroomAnnouncement(self, chatroomId: str) -> getChatroomAnnouncementResponse:
        """
        获取群公告
        chatroomId: 群聊id
        """
        request = getChatroomAnnouncementRequest(chatroomId=chatroomId)
        return type_validate_python(getChatroomAnnouncementResponse, resp_json(await self.call_api("/group/getChatroomAnnouncement", **model_dump(request))))
    
    async def setChatroomAnnouncement(self, chatroomId: str, content: str) -> Response:
        """
        设置群公告
        chatroomId: 群聊id
        content: 公告内容
        """
        request = setChatroomAnnouncementRequest(chatroomId=chatroomId, content=content)
        return type_validate_python(Response, resp_json(await self.call_api("/group/setChatroomAnnouncement", **model_dump(request))))
    
    async def agreeJoinRoom(self, url: str) -> agreeJoinRoomResponse:
        """
        同意入群申请
        url: 邀请进群回调消息中的url
        """
        request = agreeJoinRoomRequest(url=url)
        return type_validate_python(agreeJoinRoomResponse, resp_json(await self.call_api("/group/agreeJoinRoom", **model_dump(request))))

    async def addGroupMemberAsFriend(self, chatroomId: str, memberWxid: str, content: str) -> addGroupMemberAsFriendResponse:
        """
        添加群成员为好友
        chatroomId: 群聊id
        memberWxid: 成员wxid
        content: 添加好友申请内容
        """
        request = addGroupMemberAsFriendRequest(chatroomId=chatroomId, memberWxid=memberWxid, content=content)
        return type_validate_python(addGroupMemberAsFriendResponse, resp_json(await self.call_api("/group/addGroupMemberAsFriend", **model_dump(request))))
    
    async def getChatroomQrCode(self, chatroomId: str) -> getChatroomQrCodeResponse:
        """
        获取群聊二维码
        chatroomId: 群聊id
        """
        request = getChatroomQrCodeRequest(chatroomId=chatroomId)
        return type_validate_python(getChatroomQrCodeResponse, resp_json(await self.call_api("/group/getChatroomQrCode", **model_dump(request))))
    
    async def saveContractList(self, chatroomId: str, operType: str) -> Response:
        """
        保存群聊到通讯录
        chatroomId: 群聊id
        operType: 操作类型 3保存到通讯录 2从通讯录移除
        """
        request = saveContractListRequest(chatroomId=chatroomId, operType=operType)
        return type_validate_python(Response, resp_json(await self.call_api("/group/saveContractList", **model_dump(request))))
    
    async def adminOperate(self, chatroomId: str, operType: str, wxids: List[str]) -> Response:
        """
        群管理员操作
        chatroomId: 群聊id
        operType: 操作类型 1：添加群管理（可添加多个微信号） 2：删除群管理（可删除多个） 3：转让（只能转让一个微信号）
        """
        request = adminOperateRequest(chatroomId=chatroomId, operType=operType, wxids=wxids)
        return type_validate_python(Response, resp_json(await self.call_api("/group/adminOperate", **model_dump(request))))

    async def pinChat(self, chatroomId: str, top: bool) -> Response:
        """
        置顶聊天
        chatroomId: 群聊id
        top: 是否置顶
        """
        request = pinChatRequest(chatroomId=chatroomId, top=top)
        return type_validate_python(Response, resp_json(await self.call_api("/group/pinChat", **model_dump(request))))
    
    async def setMsgSilence(self, chatroomId: str, silence: bool) -> Response:
        """
        设置消息免打扰
        chatroomId: 群聊id
        silence: 是否免打扰
        """
        request = setMsgSilenceRequest(chatroomId=chatroomId, silence=silence)
        return type_validate_python(Response, resp_json(await self.call_api("/group/setMsgSilence", **model_dump(request))))

    async def joinRoomUsingQRCode(self, qrUrl: str) -> joinRoomUsingQRCodeResponse:
        """
        使用群聊二维码进群
        qrUrl: 通过解析群二维码图片获得的链接
        """
        request = joinRoomUsingQRCodeRequest(qrUrl=qrUrl)
        return type_validate_python(joinRoomUsingQRCodeResponse, resp_json(await self.call_api("/group/joinRoomUsingQRCode", **model_dump(request))))
    
    async def roomAccessApplyCheckApprove(self, chatroomId: str, newMsgId: str, msgContent: str) -> Response:
        """
        群聊进群申请审核
        chatroomId: 群聊id
        newMsgId: 消息id
        msgContent: 消息内容
        """
        request = roomAccessApplyCheckApproveRequest(chatroomId=chatroomId, newMsgId=newMsgId, msgContent=msgContent)
        return type_validate_python(Response, resp_json(await self.call_api("/group/roomAccessApplyCheckApprove", **model_dump(request))))
    
    async def revokeMsg(self, toWxid: str, msgId: str, newMsgId: str, createTime: str) -> Response:
        """
        撤回消息
        toWxid: 好友/群的ID
        msgId: 回调中的msgId
        newMsgId: 回调中的newMsgId
        createTime: 回调中的createTime
        """
        request = revokeMsgRequest(toWxid=toWxid, msgId=msgId, newMsgId=newMsgId, createTime=createTime)
        return type_validate_python(Response, resp_json(await self.call_api("/message/revokeMsg", **model_dump(request))))

    async def downloadImage(self, xml: str, type: int = 2) -> downloadImageResponse:
        """
        下载图片
        xml: 回调中的xml
        type: 下载的图片类型 1:高清图片 2:常规图片 3:缩略图
        """
        request = downloadImageRequest(xml=xml, type=type)
        return type_validate_python(downloadImageResponse, resp_json(await self.call_api("/message/downloadImage", **model_dump(request))))
    
    async def postText(self, toWxid: str, content: str, at_list: Optional[List[str]] = None) -> postTextResponse:
        """
        发送文本消息
        toWxid: 好友/群的ID
        content: 文本内容
        at_list: @的用户列表
        """
        ats = ",".join(at_list or [])
        request = postTextRequest(toWxid=toWxid, content=content, ats=ats)
        return type_validate_python(Response, resp_json(await self.call_api("/message/postText", **model_dump(request))))
    
    async def postFile(self, toWxid: str, fileUrl: str, fileName: str) -> postFileResponse:
        """
        发送文件
        toWxid: 好友/群的ID
        fileUrl: 文件url
        fileName: 文件名
        """
        request = postFileRequest(toWxid=toWxid, fileUrl=fileUrl, fileName=fileName)
        return type_validate_python(Response, resp_json(await self.call_api("/message/postFile", **model_dump(request))))
    
    async def postImage(self, toWxid: str, imgUrl: str) -> postImageResponse:
        """
        发送图片
        toWxid: 好友/群的ID
        imgUrl: 图片url
        """
        request = postImageRequest(toWxid=toWxid, imgUrl=imgUrl)
        return type_validate_python(Response, resp_json(await self.call_api("/message/postImage", **model_dump(request))))
    
    async def postVoice(self, toWxid: str, voiceUrl: str, voiceDuration: int) -> postVoiceResponse:
        """
        发送语音
        toWxid: 好友/群的ID
        voiceUrl: 语音url,仅支持silk格式
        voiceDuration: 语音时长,单位毫秒
        """
        request = postVoiceRequest(toWxid=toWxid, voiceUrl=voiceUrl, voiceDuration=voiceDuration)
        return type_validate_python(Response, resp_json(await self.call_api("/message/postVoice", **model_dump(request))))

    async def postVideo(self, toWxid: str, videoUrl: str, thumbUrl: str, videoDuration: int) -> postVideoResponse:
        """
        发送视频
        toWxid: 好友/群的ID
        videoUrl: 视频url
        thumbUrl: 视频缩略图url
        videoDuration: 视频时长,单位秒
        """
        request = postVideoRequest(toWxid=toWxid, videoUrl=videoUrl, thumbUrl=thumbUrl, videoDuration=videoDuration)
        return type_validate_python(Response, resp_json(await self.call_api("/message/postVideo", **model_dump(request))))
    
    async def postLink(self, toWxid: str, title: str, desc: str, linkUrl: str, thumbUrl: str) -> postLinkResponse:
        """
        发送链接
        toWxid: 好友/群的ID
        title: 链接标题
        desc: 链接描述
        linkUrl: 链接url
        thumbUrl: 链接图片url
        """
        request = postLinkRequest(toWxid=toWxid, title=title, desc=desc, linkUrl=linkUrl, thumbUrl=thumbUrl)
        return type_validate_python(Response, resp_json(await self.call_api("/message/postLink", **model_dump(request))))
    
    async def postNameCard(self, toWxid: str, nickName: str, nameCardWxid: str) -> postNameCardResponse:
        """
        发送名片
        toWxid: 好友/群的ID
        nickName: 昵称
        nameCardWxid: 名片wxid
        """
        request = postNameCardRequest(toWxid=toWxid, nickName=nickName, nameCardWxid=nameCardWxid)
        return type_validate_python(postNameCardResponse, resp_json(await self.call_api("/message/postNameCard", **model_dump(request))))

    async def postEmoji(self, toWxid: str, emojiMd5: str, emojiSize: str) -> postEmojiResponse:
        """
        发送表情
        toWxid: 好友/群的ID
        emojiMd5: 表情md5
        emojiSize: 表情大小
        """
        request = postEmojiRequest(toWxid=toWxid, emojiMd5=emojiMd5, emojiSize=emojiSize)
        return type_validate_python(postEmojiResponse, resp_json(await self.call_api("/message/postEmoji", **model_dump(request))))
    
    async def postAppMsg(self, toWxid: str, appmsg: str) -> postAppMsgResponse:
        """
        发送小程序,本接口可用于发送所有包含节点的消息，例如：音乐分享、视频号、引用消息等等
        toWxid: 好友/群的ID
        appmsg: 回调消息中的appmsg节点内容
        """
        request = postAppMsgRequest(toWxid=toWxid, appmsg=appmsg)
        return type_validate_python(postAppMsgResponse, resp_json(await self.call_api("/message/postAppMsg", **model_dump(request))))
    
    async def postMiniApp(self, toWxid: str, miniAppId: str, displayName: str, pagePath: str, coverImgUrl: str, title: str, userName: str) -> postMiniAppResponse:
        """
        发送小程序
        toWxid: 好友/群的ID
        miniAppId: 小程序id
        displayName: 小程序名称
        pagePath: 小程序页面路径
        coverImgUrl: 小程序封面图片url
        title: 小程序标题
        userName: 归属的用户ID
        """
        request = postMiniAppRequest(toWxid=toWxid, miniAppId=miniAppId, displayName=displayName, pagePath=pagePath, coverImgUrl=coverImgUrl, title=title, userName=userName)
        return type_validate_python(postMiniAppResponse, resp_json(await self.call_api("/message/postMiniApp", **model_dump(request))))
    
    async def forwardFile(self, toWxid: str, xml: str) -> forwardFileResponse:
        """
        转发文件
        toWxid: 好友/群的ID
        xml: 文件消息的xml
        """
        request = forwardFileRequest(toWxid=toWxid, xml=xml)
        return type_validate_python(forwardFileResponse, resp_json(await self.call_api("/message/forwardFile", **model_dump(request))))
    
    async def forwardImage(self, toWxid: str, xml: str) -> forwardImageResponse:
        """
        转发图片
        toWxid: 好友/群的ID
        xml: 图片消息的xml
        """
        request = forwardImageRequest(toWxid=toWxid, xml=xml)
        return type_validate_python(forwardImageResponse, resp_json(await self.call_api("/message/forwardImage", **model_dump(request))))
    
    async def forwardVideo(self, toWxid: str, xml: str) -> forwardVideoResponse:
        """
        转发视频
        toWxid: 好友/群的ID
        xml: 视频消息的xml
        """
        request = forwardVideoRequest(toWxid=toWxid, xml=xml)
        return type_validate_python(forwardVideoResponse, resp_json(await self.call_api("/message/forwardVideo", **model_dump(request))))
    
    async def forwardUrl(self, toWxid: str, xml: str) -> forwardUrlResponse:
        """
        转发链接
        toWxid: 好友/群的ID
        xml: 链接消息的xml
        """
        request = forwardUrlRequest(toWxid=toWxid, xml=xml)
        return type_validate_python(forwardUrlResponse, resp_json(await self.call_api("/message/forwardUrl", **model_dump(request))))
    
    async def forwardMiniApp(self, toWxid: str, xml: str, coverImgUrl: str) -> forwardMiniAppResponse:
        """
        转发小程序
        toWxid: 好友/群的ID
        xml: 小程序消息的xml
        coverImgUrl: 小程序封面图片url
        """
        request = forwardMiniAppRequest(toWxid=toWxid, xml=xml, coverImgUrl=coverImgUrl)
        return type_validate_python(forwardMiniAppResponse, resp_json(await self.call_api("/message/forwardMiniApp", **model_dump(request))))


    async def addLabel(self, labelName: str) -> addLabelResponse:
        """
        添加标签
        labelName: 标签名称
        """
        request = addLabelRequest(labelName=labelName)
        return type_validate_python(addLabelResponse, resp_json(await self.call_api("/label/add", **model_dump(request))))
    
    async def delLabelRequest(self, labels: List[str]) -> Response:
        """
        删除标签
        labels: 标签id列表
        """
        request = delLabelRequest(labels=",".join(labels))
        return type_validate_python(Response, resp_json(await self.call_api("/label/delete", **model_dump(request))))
    
    async def getLabelList(self) -> getLabelListResponse:
        """
        获取标签列表
        """
        return type_validate_python(getLabelListResponse, resp_json(await self.call_api("/label/list")))
    
    async def modifyMemberList(self, labelIds: List[str], wxIds: List[str]) -> Response:
        """
        修改标签
        labelIds: 标签id列表
        wxid: 好友id
        """
        request = modifyMemberListRequest(labelIds=",".join(labelIds), wxIds=wxIds)
        return type_validate_python(Response, resp_json(await self.call_api("/label/modifyMemberList", **model_dump(request))))
    
    async def getProfile(self) -> getProfileResponse:
        """
        获取个人信息
        """
        return type_validate_python(getProfileResponse, resp_json(await self.call_api("/personal/getProfile")))
    
    async def getQrCode(self) -> getQrCodeResponse:
        """
        获取个人二维码
        """
        return type_validate_python(getQrCodeResponse, resp_json(await self.call_api("/personal/getQrCode")))

    async def getSafetyInfo(self) -> getSafetyInfoResponse:
        """
        获取设备记录
        """
        return type_validate_python(getSafetyInfoResponse, resp_json(await self.call_api("/personal/getSafetyInfo")))
    
    async def privacySettings(self, option: int, open: bool) -> Response:
        """
        隐私设置
        option: 4: 加我为朋友时需要验证 7: 向我推荐通讯录朋友 8: 添加我的方式 手机号 25: 添加我的方式 微信号 38: 添加我的方式 群聊 39: 添加我的方式 我的二维码 40: 添加我的方式 名片
        open: 是否开启
        """
        request = privacySettingsRequest(option=option, open=open)
        return type_validate_python(Response, resp_json(await self.call_api("/personal/privacySettings", **model_dump(request))))
    
    async def updateProfile(self, city: str, country: str, nickName: str, province: str, sex: int, signature: str) -> Response:
        """
        更新个人信息
        city: 城市
        country: 国家
        nickName: 昵称
        province: 省份
        sex: 性别 1:男 2:女
        signature: 个性签名
        """
        request = updateProfileRequest(city=city, country=country, nickName=nickName, province=province, sex=sex, signature=signature)
        return type_validate_python(Response, resp_json(await self.call_api("/personal/updateProfile", **model_dump(request))))

    async def updateHeadImg(self, headImgUrl: str) -> Response:
        """
        更新头像
        img: 图片地址
        """
        request = updateHeadImgRequest(headImgUrl=headImgUrl)
        return type_validate_python(Response, resp_json(await self.call_api("/personal/updateHeadImg", **model_dump(request))))
    
    async def syncFavorFolder(self, syncKey: str = "") -> syncFavorResponse:
        """
        同步收藏文件夹,响应结果中会包含已删除的的收藏夹记录, 通过flag=1来判断已删除
        syncKey: 翻页key, 首次传空, 获取下一页传接口返回的syncKey
        """
        request = syncFavorRequest(syncKey=syncKey)
        return type_validate_python(syncFavorResponse, resp_json(await self.call_api("/favor/sync", **model_dump(request))))

    async def getFavorContent(self, favId: str) -> getFavorContentResponse:
        """
        获取收藏内容
        favId: 收藏id
        """
        request = getFavorContentRequest(favId=favId)
        return type_validate_python(getFavorContentResponse, resp_json(await self.call_api("/favor/getContent", **model_dump(request))))

    async def deleteFavorFolder(self, favId: str) -> Response:
        """
        删除收藏夹
        favId: 收藏id
        """
        request = deleteFavorFolderRequest(favId=favId)
        return type_validate_python(Response, resp_json(await self.call_api("/favor/delete", **model_dump(request))))
