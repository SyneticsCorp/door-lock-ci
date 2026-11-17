"""! @file door_warning.py
@brief 클러스터 도어 경고 문구 선택: Flake8 경고와 복잡도 초과를 고친 판.
@details doorlock/door_warning.py에 이 파일 내용을 그대로 붙여 넣는다.
같은 입력에 원래 판과 같은 문구를 돌려주며, 판단을 작은 함수로 나눠 순환 복잡도를 낮췄다.
"""

WARNING_SPEED_KMH = 15
DRIVING_DOOR_OPEN = (
    "주행 중 문 열림 - 안전한 곳에 정차한 뒤 모든 문이 닫혔는지 확인하고 다시 출발하십시오. "
    "문이 열린 채로 계속 주행하면 승객이 떨어질 수 있어 매우 위험합니다."
)
DOOR_OPEN_BY_GEAR = {
    "R": "후진 중 문 열림",
    "D": "출발 전 문 닫힘 확인",
    "N": "중립 상태 문 열림",
}


def _door_open_message(speed_kmh, gear):
    """! @brief 문이 열려 있을 때의 문구를 고른다.
    @param speed_kmh 차량 속도(km/h).
    @param gear 변속 위치.
    @return 경고 문구.
    """
    if speed_kmh >= WARNING_SPEED_KMH:
        return DRIVING_DOOR_OPEN
    return DOOR_OPEN_BY_GEAR.get(gear, "문 열림")


def _trunk_open_message(speed_kmh):
    """! @brief 트렁크가 열려 있을 때의 문구를 고른다.
    @param speed_kmh 차량 속도(km/h).
    @return 경고 문구.
    """
    if speed_kmh > 0:
        return "주행 중 트렁크 열림"
    return "트렁크 열림"


def _lock_message(speed_kmh, all_locked, gear, child_lock):
    """! @brief 문과 트렁크가 닫혀 있을 때 잠금 관련 문구를 고른다.
    @param speed_kmh 차량 속도(km/h).
    @param all_locked 모든 문이 잠겨 있는지.
    @param gear 변속 위치.
    @param child_lock 뒷좌석 어린이 보호 잠금이 켜져 있는지.
    @return 경고 문구. 없으면 None.
    """
    if not all_locked and speed_kmh >= WARNING_SPEED_KMH:
        return "주행 중 문 잠김 해제"
    if child_lock is False and gear == "D":
        return "뒷좌석 어린이 보호 잠금 꺼짐"
    return None


def select_door_warning(speed_kmh, door_open, trunk_open, all_locked,
                        gear, child_lock, key_battery_low):
    """! @brief 차량 상태로 클러스터에 띄울 도어 경고 문구를 하나 고른다.
    @param speed_kmh 차량 속도(km/h).
    @param door_open 문이 하나라도 열려 있는지.
    @param trunk_open 트렁크가 열려 있는지.
    @param all_locked 모든 문이 잠겨 있는지.
    @param gear 변속 위치('P', 'R', 'N', 'D').
    @param child_lock 뒷좌석 어린이 보호 잠금이 켜져 있는지.
    @param key_battery_low 스마트키 배터리가 부족한지.
    @return 경고 문구. 띄울 경고가 없으면 None.
    """
    if speed_kmh < 0:
        return None
    if door_open:
        message = _door_open_message(speed_kmh, gear)
    elif trunk_open:
        message = _trunk_open_message(speed_kmh)
    else:
        message = _lock_message(speed_kmh, all_locked, gear, child_lock)
    if key_battery_low and message is None:
        message = "스마트키 배터리 부족"
    return message
