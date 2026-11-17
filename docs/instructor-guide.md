# 강사 준비와 리허설

## 설치

1. Windows에 Git, Python 3.15(또는 3.12 이상)를 설치합니다. Python은 모든 사용자용 설치와 PATH 옵션을 선택합니다.
2. Eclipse Temurin JDK 25를 설치하면서 JAVA_HOME과 PATH 옵션을 선택합니다.
3. Jenkins LTS Windows MSI를 설치합니다. 서비스 계정은 전용 로컬 사용자 또는 LocalService를 사용합니다.
4. 서비스 계정에 Jenkins Home의 읽기/쓰기와 Java·Git·Python 실행 권한이 있는지 확인합니다.
5. Jenkins Home을 변경하려면 설치 폴더 `jenkins.xml`의 `JENKINS_HOME`을 수정한 뒤 서비스를 재시작합니다.
6. 초기 관리자 암호로 로그인하고 관리자 계정을 만듭니다. 로컬 실습은 loopback 주소로 접근합니다.

2026-11 검증 대상: Jenkins LTS 2.580.2 / Temurin 25.0.5+8 / Python 3.15.2.
현장에서 다른 버전을 쓰면 검증된 버전 조합과 구분해 기록합니다.

공식 설치 안내:
[Jenkins Windows](https://www.jenkins.io/doc/book/installing/windows/),
[Java 지원 정책](https://www.jenkins.io/doc/book/platform-information/support-policy-java/),
[Python](https://www.python.org/downloads/).

## 플러그인과 도구

Jenkins 관리 → Plugins에서 Git, JUnit, Warnings Next Generation, Pipeline,
Pipeline: Stage View, Timestamper를 설치하고 재시작합니다. `jenkins/plugins.txt`는 직접 의존성,
`jenkins/plugins.lock.txt`는 실제 검증한 전체 플러그인 버전입니다.
Global Tool Configuration에서 Git executable을 실제 `git.exe` 경로로 설정합니다.
기본 Windows 설치 예는 `C:\Program Files\Git\cmd\git.exe`입니다.

Python PATH를 바꾼 뒤에는 새 터미널뿐 아니라 Jenkins 서비스도 재시작합니다.
가상환경은 사용자가 만든 것을 서비스에 넘기지 않고 각 Job 작업 폴더에서 생성합니다.

## Job 구성

기본 Freestyle과 기본 Pipeline은 [수강자 안내](student-guide.md)를 그대로 따라 만듭니다.
원본 저장소에 강사 리허설의 정답 변경을 푸시하지 말고 별도 실습 브랜치나 복제본을 사용합니다.

제품 Job은 Pipeline script from SCM에서 `Jenkinsfile.product`를 지정합니다.
첫 빌드 후 **Build with Parameters** 메뉴가 나타납니다.

| SCENARIO | JUnit | Flake8 | Lizard | 빌드 결과 |
|---|---|---|---|---|
| clean | 106 통과, 커버리지 100% | 0 | 통과 | SUCCESS |
| warnings | 106 통과 | F401/E501/E711/W291 총 20건 | 통과 | FAILURE |
| complexity | 106 통과 | 0 | CCN 13 함수 1개 | FAILURE |

경고 시연의 소스는 `reports/demo-source`에 생성됩니다. Warnings NG 파일 화면에서 보고서에 적힌 경로를 확인합니다.
시연은 테스트 결과와 정적 분석 판정을 분리하여 보여 주기 위해 커버리지 수집을 생략합니다.
정상 `clean`에서는 커버리지 기준이 그대로 적용됩니다.

## 강의 전 확인표

* 수강자 계정이 원본 저장소를 Fork할 수 있고 Clone URL을 읽을 수 있는지 확인합니다.
* 기본 상태에서 로컬 명령 네 개를 실행해 3 passed / Flake8 경고 5건 / Lizard `select_door_warning` 경고(종료 코드 1)를 확인합니다.
  `python scripts/check_classroom_demo.py`가 같은 기대 결과를 한 번에 검사합니다.
* Freestyle에서 pytest(3 passed, SUCCESS) → Flake8 게시(경고 5건, SUCCESS) → Quality Gate·Lizard 추가(FAILURE) 순서로 실행합니다.
* 코드를 고치는 Red·Green은 확장 실습입니다. 할 경우 Red 1 failed, 4 passed / Green 5 passed를 확인합니다.
* Pipeline에서 Unit Test까지 성공, Complexity 단계 실패, Quality Gate FAILURE, JUnit 게시를 확인합니다.
* 경고 시연에서 Warnings NG에 실제 20건이 표시되고 TOTAL 게이트가 실패하는지 확인합니다.
* 복잡도 시연에서 CCN 13과 비정상 종료 코드가 빌드를 막는지 확인합니다.
* 플러그인 재시작 후 이력·보고서가 남는지 확인하고 마지막 빌드는 정상 상태로 둡니다.

