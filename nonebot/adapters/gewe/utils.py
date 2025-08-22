import ujson as json
import re

from selectolax.parser import HTMLParser
from nonebot.drivers import Response
from nonebot.utils import logger_wrapper


log = logger_wrapper("Gewechat")


def resp_json(resp: Response) -> dict:
    """
    将Response对象转换为JSON格式
    """
    return json.loads(resp.content.decode("utf-8"))  # type: ignore


def get_sender_from_xml(xml: str) -> str:
    """
    获取发送者的wxid
    """
    reg = re.compile(r"^wxid_[a-zA-Z0-9]+:\n")
    if reg.findall(xml):
        sender = reg.findall(xml)[0].split(":")[0]
        return sender
    else:
        return ""


def remove_prefix_tag(xml: str) -> str:
    """
    移除信息中发送者的前置标签, 返回正确的字符串
    """

    result = re.sub(r"^\d+@chatroom:\n", "", xml)
    result = re.sub(r"^wxid_[a-zA-Z0-9]+:\n", "", result)
    return result


def get_appmsg_type(xml: str) -> int:
    """
    获取appmsg_type
    """
    tree = HTMLParser(remove_prefix_tag(xml))
    appmsg = tree.css_first("appmsg")
    if appmsg is None:
        return -1
    t = tree.css_first("type")
    # 先尝试标准 CDATA 解析
    if t.text():
        return int(t.text())
    elif not t.html:
        return -1
    else:
        # 处理被错误注释的 CDATA
        cdata_match = re.search(r"<!--\[CDATA\[(\d+)\]\]-->", t.html)
        if cdata_match:
            return int(cdata_match.group(1))
        return -1
