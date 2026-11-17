# 실습 페이지와 파일 대응

원본 강의자료는 배포하지 않습니다. 아래 쪽수는 실습 내용을 찾기 위한 대응표입니다.

| 쪽 | 실습 내용 | 저장소 파일/안내 |
|---|---|---|
| 193~197 | 도어 잠금 시나리오, 시작 함수, 기본 3건과 경계값 추가 | `doorlock/door_lock.py`, `tests/test_door_lock.py`, 수강자 안내 |
| 198 | 환경·규칙을 코드로 관리 | `requirements.txt`, `pytest.ini`, `.flake8`, `.gitignore` |
| 199 | Jenkins Pipeline | `Jenkinsfile` |
| 200 | GitHub Actions / GitLab CI 비교 | `.github/workflows/ci.yml`, `.gitlab-ci.yml` |
| 201~212 | 환경, Fork/Clone, Python과 로컬 도구 | README, 수강자 안내 1~2 |
| 213~228 | Windows Java/Jenkins 설치, Home 설정 | 강사 안내 설치, 문제 해결 |
| 229~242 | 관리자 설정, 플러그인, Git 경로 | `jenkins/plugins.txt`, 강사 안내 |
| 243~252 | Freestyle, 테스트, JUnit | 수강자 안내 3 |
| 253~260 | Red → Green (확장 실습) | 수강자 안내 7 |
| 261~271 | Flake8, Warnings NG | `.flake8`, `doorlock/door_warning.py`, 수강자 안내 4 |
| 272~277 | TOTAL 경고 게이트, Lizard, 위반 해결 후 재빌드 | `doorlock/door_warning.py`, `fixes/door_warning.py`, `Jenkinsfile`, `scripts/ci.py`, 수강자 안내 4~5 |
| 278~283 | Pipeline script from SCM, Stage View | `Jenkinsfile`, 수강자 안내 6 |
| 284~286 | 문제 해결, 결과와 증거 회고 | 문제 해결, 검증 기록 |

교재의 예시 도구 버전과 Python 3.12 CI 이미지는 최신 안정판 호환성을 위해 갱신했습니다.
기본 테스트 개수와 수강자가 수정하는 파일은 유지했습니다.
보고서 초기화, 실패 시 JUnit 게시, 보고서 누락 처리, 작업별 가상환경은 재현성을 위한 보완입니다.
제품 코드와 `Jenkinsfile.product`는 결과 탐색용 추가 실습입니다.

