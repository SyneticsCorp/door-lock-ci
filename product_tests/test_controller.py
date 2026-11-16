"""! @brief VA-001 차량 상태와 실제 잠금 명령의 결합 검증."""

import pytest

from vehicle_access.controller import AccessController


DOORS = ('front_left', 'front_right', 'rear_left', 'rear_right')


def test_driving_at_boundary_locks_all_doors():
    """! @brief VA-001: 차속 15 km/h 입력으로 네 도어의 잠금 상태가 바뀐다."""
    controller = AccessController()
    controller.set_speed(15)
    assert controller.locked is True
    assert controller.speed_kmh == 15


@pytest.mark.parametrize('name', DOORS)
def test_open_door_blocks_manual_lock(name):
    """! @brief VA-002: 어느 도어든 열려 있으면 수동 잠금 요청을 거부한다."""
    controller = AccessController()
    controller.set_open(name, True)
    with pytest.raises(ValueError, match='open'):
        controller.lock_all()
    assert controller.locked is False


@pytest.mark.parametrize('name', DOORS)
def test_closing_last_open_door_allows_driving_lock(name):
    """! @brief VA-002: 주행 중 열린 도어를 닫으면 자동 잠금을 적용한다."""
    controller = AccessController()
    controller.set_open(name, True)
    controller.set_speed(15)
    assert not controller.locked
    controller.set_open(name, False)
    assert controller.locked


@pytest.mark.parametrize('name', DOORS)
def test_locked_door_cannot_be_opened(name):
    """! @brief VA-002: 잠긴 도어의 열림 요청은 상태를 바꾸지 않는다."""
    controller = AccessController()
    controller.lock_all()
    with pytest.raises(ValueError, match='locked'):
        controller.set_open(name, True)
    assert controller.snapshot()['doors'][name]['open'] is False


@pytest.mark.parametrize('name', DOORS)
def test_unlocked_door_can_open_inside(name):
    """! @brief VA-003: 기본 미잠금 상태의 모든 도어는 안쪽에서 열 수 있다."""
    assert AccessController().can_open_inside(name)


@pytest.mark.parametrize('name', ('rear_left', 'rear_right'))
def test_child_lock_changes_inside_release_only(name):
    """! @brief VA-003: 뒷좌석 어린이 보호 잠금은 안쪽 열림 판단을 제한한다."""
    controller = AccessController()
    controller.set_child_lock(name, True)
    assert controller.can_open_inside(name) is False
    controller.set_open(name, True)
    assert controller.snapshot()['doors'][name]['open'] is True
    controller.set_child_lock(name, False)
    assert controller.can_open_inside(name) is True


@pytest.mark.parametrize('name', ('front_left', 'front_right'))
def test_front_doors_reject_child_lock(name):
    """! @brief VA-003: 앞좌석에는 어린이 보호 잠금 기능을 제공하지 않는다."""
    with pytest.raises(ValueError, match='rear'):
        AccessController().set_child_lock(name, True)


@pytest.mark.parametrize('now,expected', [(10, False), (39.999, False), (40, True), (41, True)])
def test_relock_deadline(now, expected):
    """! @brief VA-004: 해제 후 30초 동안 열지 않은 차량을 경계 시각에 재잠근다."""
    controller = AccessController()
    controller.lock_all()
    controller.unlock_all(10)
    controller.tick(now)
    assert controller.locked is expected


@pytest.mark.parametrize('name', DOORS)
def test_opening_door_cancels_relock(name):
    """! @brief VA-004: 사용자가 도어를 열었다면 타이머 재잠금을 취소한다."""
    controller = AccessController()
    controller.unlock_all(0)
    controller.set_open(name, True)
    controller.set_open(name, False)
    controller.tick(30)
    assert not controller.locked
    assert controller.snapshot()['relock_deadline'] is None


def test_unlock_with_open_door_does_not_arm_timer():
    """! @brief VA-004: 이미 열린 도어가 있으면 해제 시 재잠금 타이머를 설정하지 않는다."""
    controller = AccessController()
    controller.set_open('front_left', True)
    controller.unlock_all(0)
    controller.tick(31)
    assert controller.snapshot()['relock_deadline'] is None


def test_clock_cannot_move_backwards():
    """! @brief VA-004: 역행하는 입력 시각을 거부하고 이전 상태를 보존한다."""
    controller = AccessController()
    controller.tick(10)
    with pytest.raises(ValueError, match='backwards'):
        controller.unlock_all(9)
    assert controller.snapshot()['relock_deadline'] is None


def test_lock_is_idempotent():
    """! @brief VA-005: 중복 잠금 명령은 진단 이벤트를 중복 생성하지 않는다."""
    controller = AccessController()
    controller.lock_all()
    first = controller.events.as_dicts()
    controller.lock_all()
    assert controller.events.as_dicts() == first


@pytest.mark.parametrize('value', [-1, 301, float('nan'), float('inf'), True, '15', None])
def test_invalid_speed_leaves_state_unchanged(value):
    """! @brief VA-006: 비정상 센서 입력을 거부하고 상태를 보존한다."""
    controller = AccessController()
    before = controller.snapshot()
    with pytest.raises(ValueError):
        controller.set_speed(value)
    assert controller.snapshot() == before


@pytest.mark.parametrize('value', [-1, float('nan'), float('inf'), True, '30', None])
def test_invalid_time_is_rejected(value):
    """! @brief VA-006: 타이머는 유한한 비음수 숫자만 받는다."""
    with pytest.raises(ValueError):
        AccessController().tick(value)


@pytest.mark.parametrize('value', [0, -1, 3601, True, '30', None])
def test_invalid_relock_configuration(value):
    """! @brief VA-006: 재잠금 설정은 0초 초과 3600초 이하이다."""
    with pytest.raises(ValueError):
        AccessController(relock_seconds=value)


@pytest.mark.parametrize('value', [1, 'true', None])
def test_open_state_requires_boolean(value):
    """! @brief VA-006: 도어 열림 입력의 암묵적 형 변환을 금지한다."""
    with pytest.raises(ValueError):
        AccessController().set_open('front_left', value)


@pytest.mark.parametrize('name', ['trunk', '', None])
def test_unknown_door_is_rejected(name):
    """! @brief VA-006: 네 도어 이외의 주소는 거부한다."""
    with pytest.raises(ValueError, match='door'):
        AccessController().can_open_inside(name)


def test_snapshot_cannot_mutate_controller():
    """! @brief VA-006: 외부에서 스냅샷을 수정해도 제어 상태는 바뀌지 않는다."""
    controller = AccessController()
    controller.snapshot()['doors']['front_left']['locked'] = True
    assert controller.can_open_inside('front_left')
