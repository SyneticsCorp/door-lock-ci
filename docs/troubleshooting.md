# 문제 해결

| 증상 | 확인과 조치 |
|---|---|
| Jenkins에서 python을 찾지 못함 | 서비스 계정은 로그인 사용자의 PATH와 다를 수 있습니다. 모든 사용자용 설치·실제 경로·서비스 PATH를 확인하고 서비스를 재시작합니다. |
| 설치한 Python과 다른 버전 실행 | `python --version`, `where.exe python`, `py --list-paths`를 확인합니다. `py -3.15`로 로컬 가상환경을 만들 수 있습니다. |
| Java 버전 오류 | Java 21 또는 25 지원 여부를 Jenkins 공식 정책에서 확인합니다. 검증 환경은 Temurin 25입니다. |
| ModuleNotFoundError: doorlock | 저장소 루트에서 실행하고 `pytest.ini`의 `pythonpath = .`와 `testpaths = tests`를 확인합니다. |
| Git revision을 찾지 못함 | Branch Specifier `*/main`을 확인합니다. 원본과 Fork URL을 혼동하지 않습니다. |
| Git 실행 권한/경로 오류 | Jenkins의 Git 전역 도구에 실제 경로를 설정합니다. 서비스 계정이 실행할 수 있어야 합니다. |
| pip SSL/timeout | 네트워크·프록시·사내 미러·인증서 설정을 확인합니다. TLS 검증을 끄는 대신 승인된 미러를 사용합니다. |
| Flake8 경고가 항상 0 | `--format=pylint`와 `reports/flake8.txt`를 확인합니다. 실제 F401 주입으로 파싱을 검증합니다. |
| Red 빌드에서 분석 보고서 없음 | pytest에서 실패하여 다음 단계가 생략되는 정상 동작입니다. JUnit 실패 결과를 확인합니다. |
| Red 이후 Stage View의 여러 단계가 빨간색 | 플러그인의 집계 표시일 수 있습니다. Console Output의 `skipped due to earlier failure(s)`와 최초 Unit Test 실패를 확인합니다. |
| 테스트는 통과했는데 Gate 실패 | 경고 1건 이상을 차단하는 의도된 동작입니다. Warnings NG 규칙·파일·행 상세를 확인합니다. |
| 제품 테스트가 기본 pytest에 안 나옴 | 교재의 3/5건을 유지하기 위한 구성입니다. `python scripts/ci.py test --suite product --reports reports/product`를 사용합니다. |
| warnings 시연에서 경고 외 실패 | 복제본에 원본의 코드 규칙 오류가 섞였는지 확인합니다. 정상 main에서 새 빌드를 시작합니다. |
| prepare_demo 대상 폴더가 이미 존재 | 덮어쓰지 않도록 거부합니다. 새 대상 이름을 사용합니다. Jenkins는 매 빌드 reports를 초기화합니다. |
| Doxygen 출력 디렉터리 생성 오류 | 저장소 루트에서 실행하고 docs, reports 디렉터리가 있는지 확인합니다. |

JUnit 보고서는 `reports/junit.xml` 또는 제품의 `reports/product/junit.xml`입니다.
Warnings NG는 Flake8 종료 코드 대신 보고서의 경고 수로 판정합니다.
Lizard는 `-C 10` 분석 종료 코드로 기준 초과를 판정합니다. 기준 자체를 완화하여 실패를 숨기지 않습니다.

