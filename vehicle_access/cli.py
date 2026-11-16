"""! @file cli.py
@brief VA-007: JSON 시나리오의 명령을 검증 가능한 제품 상태 전이로 실행한다.
"""

import argparse
import json
import sys
from pathlib import Path

from vehicle_access.controller import AccessController


def _execute(controller, step):
    """! @brief 명시적으로 허용한 차량 접근 제어 명령만 호출한다.
    @param controller 상태 기계 인스턴스.
    @param step command와 명령 인자를 담은 사전.
    @exception ValueError 명령 구조나 인자가 잘못된 경우.
    """
    if not isinstance(step, dict):
        raise ValueError('each step must be an object')
    arguments = dict(step)
    command = arguments.pop('command', '')
    handlers = {'speed': controller.set_speed, 'lock': controller.lock_all,
                'unlock': controller.unlock_all, 'tick': controller.tick,
                'open': controller.set_open, 'child_lock': controller.set_child_lock}
    if not isinstance(command, str) or command not in handlers:
        raise ValueError(f'unknown command: {command}')
    try:
        handlers[command](**arguments)
    except TypeError as error:
        raise ValueError(f'invalid arguments for {command}: {error}') from error


def run_scenario(steps):
    """! @brief VA-007: 새 차량 모델에서 주어진 명령 목록을 순서대로 수행한다.
    @param steps JSON 배열에서 읽은 명령 사전 목록.
    @return 최종 상태와 보존된 진단 이벤트를 담은 사전.
    """
    if not isinstance(steps, list):
        raise ValueError('scenario must be a list')
    controller = AccessController()
    for step in steps:
        _execute(controller, step)
    return {'state': controller.snapshot(), 'events': controller.events.as_dicts()}


def main(argv=None):
    """! @brief 시나리오 파일을 실행하는 CLI 진입점.
    @param argv 인자 목록. None이면 프로세스 인자를 사용한다.
    @return 성공 시 0, 파일 또는 시나리오 오류 시 2.
    """
    parser = argparse.ArgumentParser(description='Vehicle access classroom simulator')
    parser.add_argument('scenario', type=Path, help='UTF-8 JSON command list')
    arguments = parser.parse_args(argv)
    try:
        steps = json.loads(arguments.scenario.read_text(encoding='utf-8'))
        result = run_scenario(steps)
    except (OSError, ValueError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0
