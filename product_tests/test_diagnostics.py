"""! @brief VA-005 이벤트 보존 순서·용량·변경 방지 검증."""

from dataclasses import FrozenInstanceError

import pytest

from vehicle_access.diagnostics import EventLog


@pytest.mark.parametrize('capacity', [0, -1, 10001, True, '10', 1.5, None])
def test_invalid_event_capacity(capacity):
    """! @brief VA-005: 제한되지 않은 진단 메모리 설정을 거부한다."""
    with pytest.raises(ValueError):
        EventLog(capacity)


def test_ring_retains_newest_events_with_original_sequence():
    """! @brief VA-005: 순번은 증가시키고 가장 오래된 이벤트부터 제거한다."""
    events = EventLog(2)
    events.record('locked', 'manual')
    events.record('unlocked', 'remote')
    events.record('locked', 'timeout')
    assert events.as_dicts() == [
        {'sequence': 2, 'kind': 'unlocked', 'detail': 'remote'},
        {'sequence': 3, 'kind': 'locked', 'detail': 'timeout'},
    ]


def test_event_is_immutable():
    """! @brief VA-005: 이미 기록한 진단 이벤트의 종류를 덮어쓰지 못한다."""
    event = EventLog().record('locked', 'speed')
    with pytest.raises(FrozenInstanceError):
        event.kind = 'unlocked'


def test_export_is_a_copy():
    """! @brief VA-005: 보고서 소비자가 이벤트 원본을 변경하지 못한다."""
    events = EventLog()
    events.record('locked', 'speed')
    events.as_dicts()[0]['kind'] = 'unlocked'
    assert events.as_dicts()[0]['kind'] == 'locked'
