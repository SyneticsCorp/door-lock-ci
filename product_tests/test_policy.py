"""! @brief 확장 제품 요구사항 VA-001의 경계값과 상태 조합 검증."""

import pytest

from vehicle_access.policy import should_lock


@pytest.mark.parametrize('speed,expected', [
    (0, False), (14, False), (14.99, False), (15, True), (15.01, True), (60, True), (300, True),
])
def test_auto_lock_boundary(speed, expected):
    """! @brief VA-001: 닫힌 미잠금 도어는 15 km/h 이상에서 잠근다."""
    assert should_lock(speed, all_locked=False, all_closed=True) is expected


@pytest.mark.parametrize('speed', [0, 14, 15, 60, 300])
@pytest.mark.parametrize('locked,closed', [(True, True), (True, False), (False, False)])
def test_lock_requires_closed_unlocked_doors(speed, locked, closed):
    """! @brief VA-001: 열린 도어를 잠그거나 이미 잠긴 도어를 재잠그지 않는다."""
    assert should_lock(speed, locked, closed) is False
