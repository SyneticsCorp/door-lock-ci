"""! @brief 교재 준비 단계의 세 테스트. 경계값 테스트는 수강자가 추가한다."""

from doorlock.door_lock import should_auto_lock


def test_locks_when_driving_fast():
    """! @brief 60 km/h 주행 중 미잠금 도어에는 잠금 명령이 필요하다."""
    assert should_auto_lock(60, all_locked=False) is True


def test_not_lock_when_stopped():
    """! @brief 정지 상태에서는 주행에 의한 잠금 명령을 내리지 않는다."""
    assert should_auto_lock(0, all_locked=False) is False


def test_not_lock_again_when_already_locked():
    """! @brief 이미 잠긴 도어에는 같은 잠금 명령을 반복하지 않는다."""
    assert should_auto_lock(60, all_locked=True) is False
