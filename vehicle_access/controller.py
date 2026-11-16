"""! @file controller.py
@brief VA-001~006: 네 도어의 상태 전이와 재잠금 타이머를 제어한다.
@details 시각은 호출자가 주입한다. 실제 차량 버스, 센서, 액추에이터에 연결하지 않는다.
"""

from dataclasses import asdict, dataclass

from vehicle_access.diagnostics import EventLog
from vehicle_access.policy import bounded_number, should_lock

DOORS = ('front_left', 'front_right', 'rear_left', 'rear_right')
REAR_DOORS = ('rear_left', 'rear_right')


@dataclass
class DoorState:
    """! @brief 도어 하나의 열림·잠금·어린이 보호 잠금 상태."""

    open: bool = False
    locked: bool = False
    child_lock: bool = False


def require_boolean(value):
    """! @brief 숫자나 문자열의 암묵 변환을 막고 도어 입력을 검증한다.
    @param value 확인할 bool 입력.
    @exception ValueError bool이 아닌 경우.
    """
    if not isinstance(value, bool):
        raise ValueError('door state must be a boolean')


class AccessController:
    """! @brief 외부 장치 없이 재현 가능한 차량 접근 제어 상태 기계."""

    def __init__(self, relock_seconds=30, event_capacity=100):
        """! @brief 모든 도어가 닫히고 해제된 정지 상태로 시작한다.
        @param relock_seconds 재잠금 대기 시간(0.001~3600초).
        @param event_capacity 보관할 최근 이벤트 수(1~10000).
        """
        self.relock_seconds = bounded_number(relock_seconds, 'relock_seconds', 0.001, 3600)
        self.events = EventLog(event_capacity)
        self._doors = {name: DoorState() for name in DOORS}
        self.speed_kmh = 0.0
        self._deadline = None
        self._now = 0.0

    @property
    def locked(self):
        """! @return 네 도어가 모두 잠겨 있으면 True."""
        return all(door.locked for door in self._doors.values())

    @property
    def all_closed(self):
        """! @return 네 도어가 모두 닫혔으면 True."""
        return not any(door.open for door in self._doors.values())

    def _door(self, name):
        """! @param name DOORS에 정의한 도어 이름.
        @return 해당 도어 상태 객체.
        @exception ValueError 미지원 도어 이름.
        """
        if name not in DOORS:
            raise ValueError(f'unknown door: {name}')
        return self._doors[name]

    def _advance_time(self, now):
        """! @brief 타이머 입력을 검증하고 마지막 관측 시각을 갱신한다.
        @param now 단조 증가하는 시뮬레이션 시각(초).
        @return 검증한 시각.
        """
        timestamp = bounded_number(now, 'now', 0, 1e12)
        if timestamp < self._now:
            raise ValueError('time cannot move backwards')
        self._now = timestamp
        return timestamp

    def _lock(self, reason):
        """! @brief 중복 명령을 제거하고 원인을 담은 잠금 이벤트를 기록한다.
        @param reason manual, speed 또는 timeout.
        """
        if self.locked:
            return
        for door in self._doors.values():
            door.locked = True
        self._deadline = None
        self.events.record('locked', reason)

    def _auto_lock(self):
        """! @brief VA-001: 차속과 모든 도어 상태를 결합해 자동 잠금을 적용한다."""
        if should_lock(self.speed_kmh, self.locked, self.all_closed):
            self._lock('speed')

    def set_speed(self, speed_kmh):
        """! @brief 차속 입력을 검증한 후 자동 잠금 정책을 평가한다.
        @param speed_kmh 0~300 km/h 사이의 유한 숫자.
        """
        self.speed_kmh = bounded_number(speed_kmh, 'speed_kmh', 0, 300)
        self._auto_lock()

    def lock_all(self):
        """! @brief VA-002: 닫힌 도어를 수동으로 모두 잠근다.
        @exception ValueError 도어 하나라도 열려 있으면 요청을 거부한다.
        """
        if not self.all_closed:
            raise ValueError('cannot lock while a door is open')
        self._lock('manual')

    def unlock_all(self, now):
        """! @brief VA-004: 잠금을 해제하고 필요하면 재잠금 타이머를 설정한다.
        @param now 단조 증가하는 시뮬레이션 시각(초).
        """
        timestamp = self._advance_time(now)
        for door in self._doors.values():
            door.locked = False
        self._deadline = timestamp + self.relock_seconds if self.all_closed else None
        self.events.record('unlocked', 'remote')

    def tick(self, now):
        """! @brief VA-004: 대기 기한이 된 경우 자동 재잠금을 수행한다.
        @param now 단조 증가하는 시뮬레이션 시각(초).
        """
        timestamp = self._advance_time(now)
        if self._deadline is not None and timestamp >= self._deadline:
            self._lock('timeout')

    def set_open(self, name, opened):
        """! @brief VA-002: 외부 도어 열림 센서 이벤트를 반영한다.
        @param name 네 도어 중 하나의 이름.
        @param opened 열렸으면 True, 닫혔으면 False.
        @details 열림 센서는 안쪽 손잡이 판단과 별개이며, 열리면 재잠금을 취소한다.
        """
        door = self._door(name)
        require_boolean(opened)
        if opened and door.locked:
            raise ValueError('cannot open a locked door')
        door.open = opened
        if opened:
            self._deadline = None
        self.events.record('door_open' if opened else 'door_closed', name)
        self._auto_lock()

    def set_child_lock(self, name, enabled):
        """! @brief VA-003: 뒷좌석 안쪽 손잡이에 대한 보호 잠금을 설정한다.
        @param name rear_left 또는 rear_right.
        @param enabled 활성화 여부(bool).
        """
        door = self._door(name)
        require_boolean(enabled)
        if name not in REAR_DOORS:
            raise ValueError('child lock is only available on rear doors')
        door.child_lock = enabled
        self.events.record('child_lock', f'{name}:{enabled}')

    def can_open_inside(self, name):
        """! @brief VA-003: 안쪽 손잡이의 열림 허용 여부를 계산한다.
        @param name 도어 이름.
        @return 잠금과 어린이 보호 잠금이 모두 꺼졌으면 True.
        """
        door = self._door(name)
        return not door.locked and not door.child_lock

    def snapshot(self):
        """! @return 외부에서 내부 상태를 바꿀 수 없는 독립된 상태 사전."""
        return {'speed_kmh': self.speed_kmh,
                'doors': {name: asdict(door) for name, door in self._doors.items()},
                'relock_deadline': self._deadline}
