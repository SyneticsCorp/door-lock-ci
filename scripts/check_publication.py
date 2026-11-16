"""! @file check_publication.py
@brief Git 추적 파일에 강의자료·설치물·인증 정보가 들어가지 않았는지 검사한다.
"""

import re
import subprocess
from pathlib import PurePosixPath


def main():
    """! @brief 스테이징된 파일의 이름과 내용을 검사하고 공개 부적합 파일을 보고한다.
    @return 공개 범위에 맞으면 0, 제외 파일이 있으면 1.
    """
    names = subprocess.check_output(['git', 'ls-files', '-z']).decode('utf-8').split('\0')
    forbidden = {'.ppt', '.pptx', '.pdf', '.potx', '.ppsx', '.msi', '.war', '.hpi', '.jpi',
                 '.key', '.pem'}
    problems = []
    key_marker = b'-----BEGIN ' + rb'[A-Z ]*' + b'PRIVATE KEY-----'
    token = re.compile(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|' + key_marker + rb')')
    for name in filter(None, names):
        path = PurePosixPath(name)
        content = subprocess.check_output(['git', 'show', ':' + name])
        excluded = path.suffix.lower() in forbidden or path.name == '.env'
        excluded = excluded or any(p.startswith('.venv') for p in path.parts)
        if excluded or len(content) > 5_000_000 or token.search(content):
            problems.append(name)
    for name in problems:
        print('Excluded from publication:', name)
    print(f'Publication check: {len(problems)} problem(s)')
    return int(bool(problems))


if __name__ == '__main__':
    raise SystemExit(main())
