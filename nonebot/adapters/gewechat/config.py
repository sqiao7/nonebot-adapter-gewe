from pydantic import Field, BaseModel


class Config(BaseModel):
    gewechat_api_url: str = Field(default="http://127.0.0.1:2531/v2/api", description="Gewechat api地址")
    gewechat_download_api_url: str = Field(default="http://127.0.0.1:2532/download", description="Gewechat 下载api地址")
    gewechat_callback_path: str = Field(default="/callback/collect", description="Gewechat 信息回调路径")
    gewechat_callback_url: str = Field(default="http://127.0.0.1:8080/gewechat/callback/collect", description="Gewechat 信息回调地址")
    wxid: str = Field(default="wxid_xxxxxx", description="微信id")
    appid: str = Field(default="", description="设备id,首次登录留空")
    self_msg: bool = Field(default=True, description="是否接收自身消息")
