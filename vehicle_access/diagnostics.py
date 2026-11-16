"""! @file diagnostics.py
@brief VA-005: 용량을 제한한 메모리 진단 이벤트. 실제 개인정보를 수집하지 않는다.
"""

from collections import deque
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AccessEvent:
    """! @brief 증가하는 순번, 종류, 원인으로 구성한 변경 불가 진단 이벤트."""

    sequence: int
    kind: str
    detail: str


class EventLog:
    """! @brief 최근 이벤트만 보관하여 장시간 실습의 메모리 사용량을 제한한다."""

    def __init__(self, capacity=100):
        """! @param capacity 보관할 이벤트 개수. 1~10000의 정수."""
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise ValueError('capacity must be an integer')
        if not 1 <= capacity <= 10000:
            raise ValueError('capacity must be between 1 and 10000')
        self._events = deque(maxlen=capacity)
        self._sequence = 0

    def record(self, kind, detail):
        """! @brief 이벤트를 추가하고 용량 초과 시 가장 오래된 항목을 버린다.
        @param kind 이벤트 분류.
        @param detail 도어 이름 또는 명령 원인.
        @return 추가한 AccessEvent.
        """
        self._sequence += 1
        event = AccessEvent(self._sequence, kind, detail)
        self._events.append(event)
        return event

    def as_dicts(self):
        """! @return JSON으로 저장할 수 있는 독립된 이벤트 사전 목록."""
        return [asdict(event) for event in self._events]
