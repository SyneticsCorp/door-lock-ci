"""! @file ci.py
@brief 로컬·Jenkins가 같은 명령과 보고서 경로를 사용하는 교차 플랫폼 실행기.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def commands(arguments, reports):
    """! @brief 테스트·정적 분석·복잡도 명령을 명시적인 인자 목록으로 만든다.
    @param arguments 해석한 CLI 옵션.
    @param reports 절대 보고서 폴더.
    @return 명령 이름에 대응하는 모듈 인자 사전.
    """
    product = arguments.suite == 'product'
    targets = ['vehicle_access', 'product_tests'] if product else ['doorlock', 'tests']
    test = ['pytest', 'product_tests' if product else 'tests',
            f'--junitxml={reports / "junit.xml"}']
    if product and not arguments.no_coverage:
        test += ['--cov=vehicle_access', '--cov-report=term-missing',
                 f'--cov-report=xml:{reports / "coverage.xml"}']
    analysis_targets = [str(arguments.source.resolve() / target) for target in targets]
    lint = ['flake8', *analysis_targets, '--format=pylint',
            f'--output-file={reports / "flake8.txt"}']
    if arguments.collect:
        lint.append('--exit-zero')
    return {'test': test, 'lint': lint,
            'complexity': ['lizard', targets[0], '-C', '10']}


def main(argv=None):
    """! @brief 검사 도구의 종료 코드를 호출자에게 그대로 전달한다.
    @param argv CLI 인자 목록 또는 None.
    @return 실행 도구의 종료 코드.
    """
    parser = argparse.ArgumentParser(description='Run classroom quality checks')
    parser.add_argument('command', choices=['test', 'lint', 'complexity'])
    parser.add_argument('--suite', choices=['classroom', 'product'], default='classroom')
    parser.add_argument('--source', type=Path, default=Path('.'))
    parser.add_argument('--reports', type=Path, default=Path('reports'))
    parser.add_argument('--collect', action='store_true', help='let Warnings NG enforce lint gate')
    parser.add_argument('--no-coverage', action='store_true', help='run tests only in defect demos')
    arguments = parser.parse_args(argv)
    reports = arguments.reports.resolve()
    reports.mkdir(parents=True, exist_ok=True)
    module = commands(arguments, reports)[arguments.command]
    result = subprocess.run([sys.executable, '-m', *module], cwd=arguments.source,
                            check=False, capture_output=True, text=True, encoding='utf-8')
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)
    if arguments.command == 'complexity':
        (reports / 'lizard.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
