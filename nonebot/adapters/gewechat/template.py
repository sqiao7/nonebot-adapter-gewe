from datetime import datetime

def quote_msg(FromUserName: str, ToUserName: str, svrId: str, title: str, content: str = "", displayName: str = "", createTime: int = 0):
    """
    生成引用消息

    :param FromUserName: 发送者/群聊ID
    :param ToUserName: 接收者ID
    :param svrId: 被引用消息ID(NewMsgId)
    :param title: 引用消息内容
    :param content: 被引用消息内容
    :param displayName: 发送者昵称
    """

    createTime = datetime.now().timestamp()
    QUOTE_MSG_TEMPLATE = f"""<appmsg appid="" sdkver="0">
        <title>{title}</title>
        <des />
        <username />
        <action>view</action>
        <type>57</type>
        <showtype>0</showtype>
        <content />
        <url />
        <lowurl />
        <forwardflag>0</forwardflag>
        <dataurl />
        <lowdataurl />
        <contentattr>0</contentattr>
        <streamvideo>
            <streamvideourl />
            <streamvideototaltime>0</streamvideototaltime>
            <streamvideotitle />
            <streamvideowording />
            <streamvideoweburl />
            <streamvideothumburl />
            <streamvideoaduxinfo />
            <streamvideopublishid />
        </streamvideo>
        <canvasPageItem>
            <canvasPageXml><![CDATA[]]></canvasPageXml>
        </canvasPageItem>
        <refermsg>
            <type>1</type>
            <svrid>{svrId}</svrid>
            <fromusr>{FromUserName}</fromusr>
            <chatusr>{ToUserName}</chatusr>
            <displayname>{displayName}</displayname>
            <msgsource></msgsource>
            <content>{content}</content>
            <strid />
            <createtime>{createTime}</createtime>
        </refermsg>
        <appattach>
            <totallen>0</totallen>
            <attachid />
            <cdnattachurl />
            <emoticonmd5></emoticonmd5>
            <aeskey></aeskey>
            <fileext />
            <islargefilemsg>0</islargefilemsg>
        </appattach>
        <extinfo />
        <androidsource>0</androidsource>
        <thumburl />
        <mediatagname />
        <messageaction><![CDATA[]]></messageaction>
        <messageext><![CDATA[]]></messageext>
        <emoticongift>
            <packageflag>0</packageflag>
            <packageid />
        </emoticongift>
        <emoticonshared>
            <packageflag>0</packageflag>
            <packageid />
        </emoticonshared>
        <designershared>
            <designeruin>0</designeruin>
            <designername>null</designername>
            <designerrediretcturl><![CDATA[null]]></designerrediretcturl>
        </designershared>
        <emotionpageshared>
            <tid>0</tid>
            <title>null</title>
            <desc>null</desc>
            <iconUrl><![CDATA[null]]></iconUrl>
            <secondUrl>null</secondUrl>
            <pageType>0</pageType>
            <setKey>null</setKey>
        </emotionpageshared>
        <webviewshared>
            <shareUrlOriginal />
            <shareUrlOpen />
            <jsAppId />
            <publisherId />
            <publisherReqId />
        </webviewshared>
        <template_id />
        <md5 />
        <websearch>
            <rec_category>0</rec_category>
            <channelId>0</channelId>
        </websearch>
        <weappinfo>
            <username />
            <appid />
            <appservicetype>0</appservicetype>
            <secflagforsinglepagemode>0</secflagforsinglepagemode>
            <videopageinfo>
                <thumbwidth>0</thumbwidth>
                <thumbheight>0</thumbheight>
                <fromopensdk>0</fromopensdk>
            </videopageinfo>
        </weappinfo>
        <statextstr />
        <musicShareItem>
            <musicDuration>0</musicDuration>
        </musicShareItem>
        <finderLiveProductShare>
            <finderLiveID><![CDATA[]]></finderLiveID>
            <finderUsername><![CDATA[]]></finderUsername>
            <finderObjectID><![CDATA[]]></finderObjectID>
            <finderNonceID><![CDATA[]]></finderNonceID>
            <liveStatus><![CDATA[]]></liveStatus>
            <appId><![CDATA[]]></appId>
            <pagePath><![CDATA[]]></pagePath>
            <productId><![CDATA[]]></productId>
            <coverUrl><![CDATA[]]></coverUrl>
            <productTitle><![CDATA[]]></productTitle>
            <marketPrice><![CDATA[0]]></marketPrice>
            <sellingPrice><![CDATA[0]]></sellingPrice>
            <platformHeadImg><![CDATA[]]></platformHeadImg>
            <platformName><![CDATA[]]></platformName>
            <shopWindowId><![CDATA[]]></shopWindowId>
            <flashSalePrice><![CDATA[0]]></flashSalePrice>
            <flashSaleEndTime><![CDATA[0]]></flashSaleEndTime>
            <ecSource><![CDATA[]]></ecSource>
            <sellingPriceWording><![CDATA[]]></sellingPriceWording>
            <platformIconURL><![CDATA[]]></platformIconURL>
            <firstProductTagURL><![CDATA[]]></firstProductTagURL>
            <firstProductTagAspectRatioString><![CDATA[0.0]]></firstProductTagAspectRatioString>
            <secondProductTagURL><![CDATA[]]></secondProductTagURL>
            <secondProductTagAspectRatioString><![CDATA[0.0]]></secondProductTagAspectRatioString>
            <firstGuaranteeWording><![CDATA[]]></firstGuaranteeWording>
            <secondGuaranteeWording><![CDATA[]]></secondGuaranteeWording>
            <thirdGuaranteeWording><![CDATA[]]></thirdGuaranteeWording>
            <isPriceBeginShow>false</isPriceBeginShow>
            <lastGMsgID><![CDATA[]]></lastGMsgID>
            <promoterKey><![CDATA[]]></promoterKey>
            <discountWording><![CDATA[]]></discountWording>
            <priceSuffixDescription><![CDATA[]]></priceSuffixDescription>
            <productCardKey><![CDATA[]]></productCardKey>
            <isWxShop><![CDATA[]]></isWxShop>
            <brandIconUrl><![CDATA[]]></brandIconUrl>
            <showBoxItemStringList />
        </finderLiveProductShare>
        <finderOrder>
            <appID><![CDATA[]]></appID>
            <orderID><![CDATA[]]></orderID>
            <path><![CDATA[]]></path>
            <priceWording><![CDATA[]]></priceWording>
            <stateWording><![CDATA[]]></stateWording>
            <productImageURL><![CDATA[]]></productImageURL>
            <products><![CDATA[]]></products>
            <productsCount><![CDATA[0]]></productsCount>
            <orderType><![CDATA[0]]></orderType>
            <newPriceWording><![CDATA[]]></newPriceWording>
            <newStateWording><![CDATA[]]></newStateWording>
            <useNewWording><![CDATA[0]]></useNewWording>
        </finderOrder>
        <finderShopWindowShare>
            <finderUsername><![CDATA[]]></finderUsername>
            <avatar><![CDATA[]]></avatar>
            <nickname><![CDATA[]]></nickname>
            <commodityInStockCount><![CDATA[]]></commodityInStockCount>
            <appId><![CDATA[]]></appId>
            <path><![CDATA[]]></path>
            <appUsername><![CDATA[]]></appUsername>
            <query><![CDATA[]]></query>
            <liteAppId><![CDATA[]]></liteAppId>
            <liteAppPath><![CDATA[]]></liteAppPath>
            <liteAppQuery><![CDATA[]]></liteAppQuery>
            <platformTagURL><![CDATA[]]></platformTagURL>
            <saleWording><![CDATA[]]></saleWording>
            <lastGMsgID><![CDATA[]]></lastGMsgID>
            <profileTypeWording><![CDATA[]]></profileTypeWording>
            <saleWordingExtra><![CDATA[]]></saleWordingExtra>
            <isWxShop><![CDATA[]]></isWxShop>
            <platformIconUrl><![CDATA[]]></platformIconUrl>
            <brandIconUrl><![CDATA[]]></brandIconUrl>
            <description><![CDATA[]]></description>
            <backgroundUrl><![CDATA[]]></backgroundUrl>
            <darkModePlatformIconUrl><![CDATA[]]></darkModePlatformIconUrl>
            <reputationInfo>
                <hasReputationInfo>0</hasReputationInfo>
                <reputationScore>0</reputationScore>
                <reputationWording />
                <reputationTextColor />
                <reputationLevelWording />
                <reputationBackgroundColor />
            </reputationInfo>
            <productImageURLList />
        </finderShopWindowShare>
        <findernamecard>
            <username />
            <avatar><![CDATA[]]></avatar>
            <nickname />
            <auth_job />
            <auth_icon>0</auth_icon>
            <auth_icon_url />
            <ecSource><![CDATA[]]></ecSource>
            <lastGMsgID><![CDATA[]]></lastGMsgID>
        </findernamecard>
        <finderGuarantee>
            <scene><![CDATA[0]]></scene>
        </finderGuarantee>
        <directshare>0</directshare>
        <gamecenter>
            <namecard>
                <iconUrl />
                <name />
                <desc />
                <tail />
                <jumpUrl />
            </namecard>
        </gamecenter>
        <patMsg>
            <chatUser />
            <records>
                <recordNum>0</recordNum>
            </records>
        </patMsg>
        <secretmsg>
            <issecretmsg>0</issecretmsg>
        </secretmsg>
        <referfromscene>0</referfromscene>
        <gameshare>
            <liteappext>
                <liteappbizdata />
                <priority>0</priority>
            </liteappext>
            <appbrandext>
                <litegameinfo />
                <priority>-1</priority>
            </appbrandext>
            <gameshareid />
            <sharedata />
            <isvideo>0</isvideo>
            <duration>-1</duration>
            <isexposed>0</isexposed>
            <readtext />
        </gameshare>
        <mpsharetrace>
            <hasfinderelement>0</hasfinderelement>
            <lastgmsgid />
        </mpsharetrace>
        <wxgamecard>
            <framesetname />
            <mbcarddata />
            <minpkgversion />
            <clientextinfo />
            <mbcardheight>0</mbcardheight>
            <isoldversion>0</isoldversion>
        </wxgamecard>
        <liteapp>
            <id>null</id>
            <path />
            <query />
            <istransparent>0</istransparent>
            <hideicon>0</hideicon>
        </liteapp>
        <opensdk_share_is_modified>0</opensdk_share_is_modified>
    </appmsg>
"""
    return QUOTE_MSG_TEMPLATE

