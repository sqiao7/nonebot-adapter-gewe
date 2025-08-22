from pydantic import Field, BaseModel


class Config(BaseModel):
    gewechat_api_url: str = Field(default="https://www.geweapi.com/gewe/v2/api", description="Gewe API接口域名")
    gewechat_callback_path: str = Field(default="/callback/collect", description="Gewe 消息回调路由")
    gewechat_callback_url: str = Field(default="http://127.0.0.1:8080/gewechat/callback/collect", description="Gewe 消息回调路由")
    gewechat_region_id: int = Field(default=350000, description="Gewe 区域id")
    gewechat_proxy: str = Field(default="socks5://user:pass@addr:port", description="代理服务信息")
    gewechat_token: str = Field(default="XXXX-XXXX-XXXX-XXXX", description="Gewe 接口token")
    wxid: str = Field(default="wxid_xxxxxx", description="微信id")
    appid: str = Field(default="", description="设备id,首次登录留空")
    self_msg: bool = Field(default=True, description="是否接收自身消息")
    msg_expire_time: int = Field(default=31, description="消息存储到期时间,单位天")
