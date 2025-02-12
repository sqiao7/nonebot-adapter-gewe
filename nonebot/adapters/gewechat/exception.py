from nonebot.exception import AdapterException
from nonebot.exception import ActionFailed as BaseActionFailed
from nonebot.exception import NetworkError as BaseNetworkError
from nonebot.exception import NoLogException as BaseNoLogException
from nonebot.exception import ApiNotAvailable as BaseApiNotAvailable


class GewechatAdapterException(AdapterException):
    def __init__(self):
        super().__init__("Gewechat")

class NoLogException(BaseNoLogException, GewechatAdapterException):
    pass


class ActionFailed(BaseActionFailed, GewechatAdapterException):
    """
    API 请求返回错误信息。
    """

    def __init__(self, description: str = None):
        super().__init__()
        self.description = description

    def __repr__(self):
        return f"<ActionFailed {self.description}>"

    def __str__(self):
        return self.__repr__()


class NetworkError(BaseNetworkError, GewechatAdapterException):
    """
    网络错误。
    """

    def __init__(self, msg: str = None):
        super().__init__()
        self.msg = msg

    def __repr__(self):
        return f"<NetWorkError message={self.msg}>"

    def __str__(self):
        return self.__repr__()


class ApiNotAvailable(BaseApiNotAvailable, GewechatAdapterException):
    """
    API 不可用。
    """

    def __init__(self, msg: str = None):
        super().__init__()
        self.msg = msg

    def __repr__(self):
        return f"<ApiNotAvailable message={self.msg}>"

    def __str__(self):
        return self.__repr__()

