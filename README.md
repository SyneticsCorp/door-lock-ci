# Door Lock CI — SDV 개발방법론 실습

도어 자동 잠금의 인수 기준을 테스트로 옮기고 Jenkins에서 Red → Green → Quality Gate를
확인하는 Python 교육용 저장소입니다. Python **3.12 이상**, 주 검증 버전은 **3.15.2**입니다.
수강자는 이 저장소를 자신의 GitHub 계정으로 Fork한 뒤 실습합니다.

**중요:** `doorlock/door_lock.py`는 경계값 결함을 의도적으로 남긴 시작 코드입니다.
기본 테스트 3개에는 경계값이 없으므로 처음에는 모두 통과합니다. `vehicle_access/`는
독립된 정상 제품 모델이며 기본 실습 함수에 의존하지 않습니다.

| 구분 | 소스 / 테스트 | 실행 결과 |
|---|---|---|
| 교재 기본 실습 | `doorlock/`, `tests/` | 준비 3 passed → Red 1 failed, 4 passed → Green 5 passed |
| 확장 제품 | `vehicle_access/`, `product_tests/` | 106개 테스트, 상태 전이·진단·CLI, 분기 커버리지 검사 |
| 경고 시연 | `scripts/prepare_demo.py`가 생성한 복제본 | 테스트는 통과하고 Flake8 경고 또는 Lizard 게이트가 실패 |

## Windows 빠른 시작

Git과 Python을 설치한 새 PowerShell 또는 명령 프롬프트에서 실행합니다.
Jenkins 서비스에서도 사용할 Python은 모든 사용자용으로 설치하고 PATH에 등록합니다.

```powershell
git clone https://github.com/SyneticsCorp/door-lock-ci.git
cd door-lock-ci
py -3.15 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m flake8 doorlock tests
.\.venv\Scripts\python.exe -m lizard doorlock -C 10
```

기본 결과는 `3 passed`, Flake8 경고 0건, Lizard 기준 초과 0건입니다.
Linux/macOS는 `python3 -m venv .venv`, 이후 `.venv/bin/python`을 사용합니다.
교재 명령처럼 `python -m pip install -r requirements.txt`로 활성 Python에 설치해도 됩니다.

## 확장 제품 실행

```powershell
.\.venv\Scripts\python.exe -m vehicle_access examples/commute.json
.\.venv\Scripts\python.exe scripts/ci.py test --suite product --reports reports/product
.\.venv\Scripts\python.exe scripts/ci.py lint --suite product --reports reports/product
.\.venv\Scripts\python.exe scripts/ci.py complexity --suite product --reports reports/product
```

도어별 열림/잠금, 15 km/h 자동 잠금, 뒷좌석 어린이 보호 잠금, 해제 후 자동 재잠금,
용량 제한 진단 이벤트와 JSON 시나리오 CLI를 제공합니다. 시각은 외부에서 주입하므로
테스트에서 실제 시간을 기다리지 않습니다. 교육용 시뮬레이터이며 실제 차량에 연결하지 않습니다.
제품 요구사항과 테스트 연결은 [제품 명세](docs/product.md)를 참고합니다.

## Jenkins

Java 25와 Jenkins LTS를 설치하고 Git, JUnit, Warnings Next Generation, Pipeline,
Pipeline: Stage View, Timestamper 플러그인을 설치합니다.

* 기본 Pipeline: **Pipeline script from SCM**, Git 저장소의 `main`, Script Path `Jenkinsfile`.
* 제품 Pipeline: 별도 Job, Script Path `Jenkinsfile.product`. `SCENARIO=clean`으로 시작합니다.
* 제품 경고 시연: `SCENARIO=warnings`. JUnit은 통과하고 Warnings NG의 TOTAL ≥ 1 게이트가 실패합니다.
* 복잡도 시연: `SCENARIO=complexity`. JUnit은 통과하고 CCN > 10인 함수가 Lizard 게이트를 실패시킵니다.

Pipeline은 작업 폴더의 가상환경을 만들고 매 빌드의 보고서 폴더를 비웁니다.
Red에서 정적 분석 단계가 생략되어도 JUnit 보고서를 게시하며, 지난 빌드의 경고 파일을 재사용하지 않습니다.
제품 결함 시연은 복제본만 바꾸며, 결함 추가 함수에 대한 커버리지 측정은 하지 않습니다.
정상 제품 빌드는 구문·분기 커버리지 100%를 검사합니다.

## 수업 안내

* [수강자 실습 순서](docs/student-guide.md): Fork/Clone, Freestyle, Red/Green/Gate, Pipeline.
* [강사 준비 및 리허설](docs/instructor-guide.md): 설치, 플러그인, Job 설정, 결과 판정.
* [페이지별 파일 대응](docs/course-map.md): 193쪽 이후 실습과 저장소 파일 연결.
* [문제 해결](docs/troubleshooting.md): Python PATH, 서비스 계정, 분석 보고서와 게이트.
* [검증 기록](docs/validation.md): 실제 실행 환경·빌드·검증 범위.

## Doxygen

```powershell
New-Item -ItemType Directory -Path reports -Force
doxygen Doxyfile
```

HTML은 `docs/api/html/index.html`에 생성됩니다. Python 모듈·클래스·함수의 프로젝트 설명과
입출력 설명에 Doxygen 주석을 사용합니다. 자동 생성 결과는 Git 추적 대상이 아닙니다.

## 공개 범위

신규 작성 소스·테스트·CI 설정·실습 문서는 MIT 라이선스입니다. 원본 강의자료는 포함하지 않습니다.
가상환경, Jenkins 설치물/홈, 인증 정보와 실행 결과는 공개 파일에 포함하지 않습니다.
GitHub Actions는 Windows와 Linux에서 Python 3.12/3.14/3.15를 검사합니다.
GitLab CI 파일은 교재 비교·이식용이며 실제 GitLab 서버 실행 여부는 검증 기록에 따릅니다.

