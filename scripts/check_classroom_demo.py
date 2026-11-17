"""! @file check_classroom_demo.py
@brief 수업용 경고 예제(doorlock/door_warning.py)가 기대한 결과를 내는지 검사한다.
@details 수강자 화면에 나올 결과가 도구 버전이 바뀌어도 그대로인지 CI에서 확인한다.
"""

import subprocess
import sys

EXPECTED_FLAKE8 = ['E501', 'E711', 'E712', 'F401', 'W291']
DEMO_FILE = 'doorlock/door_warning.py'
COMPLEX_FUNCTION = 'select_door_warning'


def run(arguments):
    """! @brief 현재 Python으로 모듈을 실행하고 종료 코드와 출력을 돌려준다.
    @param arguments python -m 뒤에 붙을 인자 목록.
    @return (종료 코드, 표준 출력과 표준 오류를 합친 문자열).
    """
    result = subprocess.run([sys.executable, '-m', *arguments], check=False,
                            capture_output=True, text=True, encoding='utf-8')
    return result.returncode, result.stdout + result.stderr


def check_flake8():
    """! @brief 경고가 예제 파일에만 있고, 규칙 코드가 기대와 같은지 확인한다.
    @return 문제 설명 목록.
    """
    _, output = run(['flake8', 'doorlock', 'tests', '--format=%(path)s %(code)s'])
    print(output, end='')
    rows = [line.replace('\\', '/').split() for line in output.splitlines() if line.strip()]
    codes = sorted(code for _, code in rows)
    paths = {path for path, _ in rows}
    problems = []
    if codes != EXPECTED_FLAKE8:
        problems.append(f'Flake8 codes {codes}, expected {EXPECTED_FLAKE8}')
    if paths != {DEMO_FILE}:
        problems.append(f'Flake8 files {sorted(paths)}, expected only {DEMO_FILE}')
    return problems


def check_lizard():
    """! @brief Lizard가 예제 함수만 복잡도 초과로 표시하고 실패 코드를 돌려주는지 확인한다.
    @return 문제 설명 목록.
    """
    code, output = run(['lizard', 'doorlock', '-C', '10'])
    print(output, end='')
    warnings = output.partition('Warnings (')[2]
    problems = []
    if code == 0 or COMPLEX_FUNCTION not in warnings:
        problems.append(f'Lizard must flag {COMPLEX_FUNCTION} (exit code {code})')
    if 'should_auto_lock' in warnings:
        problems.append('Lizard flagged should_auto_lock')
    return problems


def main():
    """! @brief 두 검사를 실행하고 결과를 요약한다.
    @return 기대와 같으면 0, 다르면 1.
    """
    problems = check_flake8() + check_lizard()
    for problem in problems:
        print('Classroom demo check:', problem)
    print(f'Classroom demo check: {len(problems)} problem(s)')
    return int(bool(problems))


if __name__ == '__main__':
    raise SystemExit(main())
