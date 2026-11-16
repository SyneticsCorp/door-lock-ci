"""! @file prepare_demo.py
@brief 원본을 보존하고 별도 복제본에만 정적 분석·복잡도 교육용 결함을 넣는다.
"""

import argparse
import shutil
from pathlib import Path


def inject_warnings(target):
    """! @brief 진단·제어 제품 파일에서 다양한 Flake8 경고를 재현한다.
    @param target 실습 복제본의 루트.
    """
    files = ['controller.py', 'diagnostics.py', 'policy.py', 'cli.py']
    for index, name in enumerate(files):
        path = target / 'vehicle_access' / name
        text = path.read_text(encoding='utf-8')
        ending = text.index('"""', 3) + 3
        text = text[:ending] + '\n\nimport os\nimport tempfile\n' + text[ending:]
        text += '\n\n"""! @brief Demo diagnostic label with excessive line length."""\n'
        text += f'DIAGNOSTIC_LABEL_{index} = ' + repr('vehicle-access-diagnostic-' * 6) + '\n'
        text += '\n\ndef is_missing_sensor(value):\n'
        text += '    """! @brief Demo legacy sensor validity check with E711."""\n'
        text += '    return value == None  \n'
        path.write_text(text, encoding='utf-8')


def inject_complexity(target):
    """! @brief 복잡한 진단 라우팅 함수로 CCN 10 초과를 재현한다.
    @param target 실습 복제본의 루트.
    """
    lines = ['"""! @brief Complexity gate demonstration for diagnostic routing."""', '', '',
             'def route_diagnostic(code):',
             '    """! @brief Legacy diagnostic router requiring refactoring."""']
    for code in range(12):
        lines.extend([f'    if code == {code}:', f'        return "door-event-{code}"'])
    lines.append('    return "unknown"')
    (target / 'vehicle_access' / 'routing.py').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def prepare(case, destination):
    """! @brief 빈 대상 폴더에 분석 가능한 원본 복제본을 생성한다.
    @param case warnings 또는 complexity.
    @param destination 원본과 다른 빈 폴더.
    @exception ValueError 기존 폴더 또는 원본을 덮어쓰려는 경우.
    """
    source = Path(__file__).resolve().parents[1]
    target = Path(destination).resolve()
    if target == source or target.exists():
        raise ValueError('destination must be a new directory')
    target.mkdir(parents=True)
    for name in ['vehicle_access', 'product_tests']:
        shutil.copytree(source / name, target / name, ignore=shutil.ignore_patterns('__pycache__'))
    for name in ['pytest.ini', '.flake8', '.coveragerc']:
        shutil.copyfile(source / name, target / name)
    if case == 'warnings':
        inject_warnings(target)
    else:
        inject_complexity(target)
    return target


def main():
    """! @brief 명시한 복제본에 선택한 교육용 결함을 생성하는 CLI."""
    parser = argparse.ArgumentParser(description='Create an isolated quality gate demonstration')
    parser.add_argument('case', choices=['warnings', 'complexity'])
    parser.add_argument('destination', type=Path)
    arguments = parser.parse_args()
    print(prepare(arguments.case, arguments.destination))


if __name__ == '__main__':
    main()
