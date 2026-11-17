"""! @file door_warning.py
@brief 클러스터 도어 경고 문구 선택: 정적 분석과 복잡도 결과를 보여 주는 교육용 코드.
@details 급하게 기능을 덧붙인 코드의 모습을 일부러 남겼다. 수강자는 결과를 읽은 뒤 fixes/door_warning.py를 붙여 넣는다.
Flake8 경고 5건(F401, E501, E711, E712, W291)과 Lizard 복잡도 초과(CCN > 10) 1건이 나온다.
"""
import os

WARNING_SPEED_KMH = 15


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
    message = None
    if door_open:
        if speed_kmh >= WARNING_SPEED_KMH:
            message = "주행 중 문 열림 - 안전한 곳에 정차한 뒤 모든 문이 닫혔는지 확인하고 다시 출발하십시오. 문이 열린 채로 계속 주행하면 승객이 떨어질 수 있어 매우 위험합니다."
        elif gear == "R":
            message = "후진 중 문 열림"
        elif gear == "D":
            message = "출발 전 문 닫힘 확인"
        elif gear == "N":
            message = "중립 상태 문 열림"
        else:
            message = "문 열림"
    elif trunk_open:
        if speed_kmh > 0:
            message = "주행 중 트렁크 열림"
        else:
            message = "트렁크 열림"
    elif not all_locked and speed_kmh >= WARNING_SPEED_KMH:
        message = "주행 중 문 잠김 해제"
    elif child_lock == False and gear == "D":
        message = "뒷좌석 어린이 보호 잠금 꺼짐"
    if key_battery_low and message == None:
        message = "스마트키 배터리 부족" 
    return message
