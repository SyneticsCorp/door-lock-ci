"""! @file policy.py
@brief VA-001 자동 잠금 정책. 실습 함수와 독립된 정상 제품 모델이다.
"""

from math import isfinite
from numbers import Real


def bounded_number(value, name, minimum, maximum):
    """! @brief 센서 값과 타이머 인자의 단위별 허용 범위를 검증한다.
    @param value 검증할 숫자. bool과 문자열은 허용하지 않는다.
    @param name 오류 메시지에 표시할 입력 이름.
    @param minimum 허용 최솟값(포함).
    @param maximum 허용 최댓값(포함).
    @return float로 변환한 유효 값.
    @exception ValueError 타입, 유한성 또는 범위가 맞지 않는 경우.
    """
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f'{name} must be a finite number')
    if not isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f'{name} must be between {minimum} and {maximum}')
    return float(value)


def should_lock(speed_kmh, all_locked, all_closed):
    """! @brief VA-001: 모든 도어가 닫혔으면 15 km/h 이상에서 자동 잠근다.
    @param speed_kmh 0~300 km/h의 유효 차속.
    @param all_locked 모든 도어가 이미 잠겼는지 여부.
    @param all_closed 모든 도어가 닫혔는지 여부.
    @return 새로운 자동 잠금 명령의 필요 여부.
    """
    speed = bounded_number(speed_kmh, 'speed_kmh', 0, 300)
    return speed >= 15 and not all_locked and all_closed
