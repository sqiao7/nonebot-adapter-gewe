import ujson as json
import re

from nonebot.drivers import Response
from nonebot.utils import logger_wrapper

from typing import List, Dict, Any

log = logger_wrapper("Gewechat")

def get_at_list(text: str) -> List[str]:
    """
    获取@列表,只包含@的 用户名/群昵称
    若有@所有人, 返回["all"]
    """
    # 判断依据: @xxx 为一个@元素, 空格结束
    at_list = []
    if "@所有人" in text or "@ all people" in text:
        at_list.append("notify@all")
        return at_list
    else:
        reg_at = re.compile(r'@\S+\s')
        at_list = reg_at.findall(text)
        at_list = [at.strip("@").strip() for at in at_list]
    return at_list

def resp_json(resp: Response) -> Dict:
    """
    将Response对象转换为JSON格式
    """
    return json.loads(resp.content.decode("utf-8"))

def remove_prefix_tag(xml: str) -> str:
    """
    移除信息中的无用前置标签, 返回正确的字符串
    """

    result = re.sub(r'^\d+@chatroom:\n', '', xml)
    result = re.sub(r'^wxid_[a-zA-Z0-9]+:\n', '', result)
    return result
