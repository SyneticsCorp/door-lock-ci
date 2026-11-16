"""! @file door_lock.py
@brief 도어 자동 잠금 판정: 수강자가 경계값 결함을 찾는 교육용 시작 코드.
@details 인수 기준: 15 km/h 이상 잠금, 14 km/h 미잠금, 이미 잠겼으면 재잠금 금지.
"""

LOCK_SPEED_KMH = 15


def should_auto_lock(speed_kmh, all_locked):
    """! @brief 현재 차속과 잠금 상태로 자동 잠금 명령의 필요성을 판정한다.
    @param speed_kmh 차량 속도(km/h).
    @param all_locked 모든 도어가 이미 잠겨 있는지 나타내는 값.
    @return 잠금 명령이 필요하면 True.
    """
    if all_locked:
        return False
    return speed_kmh > LOCK_SPEED_KMH
