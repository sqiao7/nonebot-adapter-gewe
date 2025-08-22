import bisect

from nonebot.log import logger
from datetime import date, timedelta
from typing import Optional

from .event import Event, MessageEvent


class EventStorage:
    """事件存储类"""

    def __init__(self):
        self._events = {}  # {event_id: event}
        # 消息事件专用索引
        self._msg_id_index = {}  # {NewMsgId: event_id}
        # 自增ID计数器
        self._autoinc_id = 0
        # 时间索引
        self._date_index = {}  # {date: set(event_ids)}
        self._sorted_dates = []  # 有序日期列表

    def store_event(self, event: Event) -> int:
        """存储事件并返回系统生成的event_id"""
        event_id = self._generate_id()
        self._events[event_id] = event
        
        # 维护消息索引
        if isinstance(event, MessageEvent):
            if event.NewMsgId in self._msg_id_index:
                logger.warning(f"Duplicate NewMsgId: {event.NewMsgId}")
            self._msg_id_index[event.NewMsgId] = event_id
        
        # 维护日期索引
        event_date = event.time.date()
        if event_date not in self._date_index:
            bisect.insort(self._sorted_dates, event_date)
            self._date_index[event_date] = set()
        self._date_index[event_date].add(event_id)
        
        return event_id

    def get_by_newmsgid(self, msg_id: str) -> Optional[MessageEvent]:
        """通过NewMsgId快速获取消息事件"""
        event_id = self._msg_id_index.get(int(msg_id))
        if event_id is None:
            return None
            
        event = self._events.get(event_id)
        if not isinstance(event, MessageEvent):
            return None
            
        return event

    def _generate_id(self) -> int:
        """生成自增ID"""
        self._autoinc_id += 1
        return self._autoinc_id

    def cleanup_expired_events(self, expire_days: int = 31):
        """清理过期事件（天级精度）"""
        if not self._sorted_dates:
            return

        cutoff_date = date.today() - timedelta(days=expire_days)
        
        # 使用bisect查找过期分界点
        pos = bisect.bisect_left(self._sorted_dates, cutoff_date)
        expired_dates = self._sorted_dates[:pos]
        
        removed_count = 0
        for day in expired_dates:
            event_ids = self._date_index.pop(day, set())
            
            for event_id in event_ids:
                event = self._events.pop(event_id, None)
                if not event:
                    continue
                
                # 清理消息索引
                if isinstance(event, MessageEvent):
                    self._msg_id_index.pop(event.MsgId, None)
                
                # 清理其他索引
                # FIXME: _additional_indices 未定义
                # for index in self._additional_indices.values():
                #     index_key = index["key_func"](event)
                #     index["storage"][index_key].discard(event_id)
                
                removed_count += 1
        
        # 更新有序日期列表
        self._sorted_dates = self._sorted_dates[pos:]
        logger.info(f"清理完成，移除 {removed_count} 条事件（截止日期：{cutoff_date}）")
