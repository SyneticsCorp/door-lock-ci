# 수강자 실습 순서

## 1. Fork와 Clone

1. GitHub에 자신의 수강자 계정으로 로그인합니다.
2. `https://github.com/SyneticsCorp/door-lock-ci`에서 **Fork → Create fork**를 선택합니다.
3. 자신의 Fork URL로 Clone합니다. 원본 저장소 소유자는 자기 저장소를 Fork할 수 없습니다.

```powershell
git clone https://github.com/<내계정>/door-lock-ci.git
cd door-lock-ci
python -m pip install -r requirements.txt
python -m pytest
python -m flake8 doorlock tests
python -m lizard doorlock -C 10
```

준비 결과: `3 passed`.
Flake8은 `doorlock/door_warning.py`에서 경고 5건(F401, E501, E711, E712, W291)을 출력합니다.
Lizard는 `select_door_warning`을 순환 복잡도 초과(CCN > 10)로 표시하고 종료 코드 1로 끝납니다.
`door_warning.py`는 결과를 읽기 위한 교육용 예제입니다. 고치지 않습니다.
Python 버전은 `python --version`, 위치는 `where.exe python`으로 확인합니다.
PowerShell에서는 `where` 대신 `where.exe`를 사용합니다.

## 2. Freestyle Job

1. Jenkins → 새로운 Item → `door-lock-freestyle` → Freestyle project.
2. 소스 코드 관리: Git, 자신의 Fork URL, Branch Specifier `*/main`.
3. Build Triggers: Poll SCM을 사용할 경우 `H/2 * * * *`. 외부 웹훅이 없어도 변경을 감지합니다.
4. Build Steps → Execute Windows batch command. 테스트용 단계에 아래를 입력합니다.

```bat
@echo off
if exist reports rmdir /s /q reports
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
python -m pytest --junitxml=reports/junit.xml
```

`reports`는 이 Job 작업 폴더의 실행 결과 전용 디렉터리입니다.
`pip` 실패가 뒤 명령에 의해 숨겨지지 않도록 종료 코드를 확인합니다.

5. 빌드 후 조치 → **Publish JUnit test result report**, `reports/junit.xml`.
6. Build Now → Console Output 및 Test Result에서 3건 통과를 확인합니다.

## 3. Red

`tests/test_door_lock.py` 마지막에 두 테스트를 직접 추가합니다.

```python
def test_locks_at_15_kmh():
    """! @brief 인수 기준: 15 km/h에서 자동 잠금 명령을 내린다."""
    assert should_auto_lock(15, all_locked=False) is True


def test_not_lock_at_14_kmh():
    """! @brief 인수 기준: 14 km/h에서는 자동 잠금 명령을 내리지 않는다."""
    assert should_auto_lock(14, all_locked=False) is False
```

기존 파일 마지막 함수와 새 함수 사이에도 빈 줄 두 줄을 둡니다.

```powershell
git add tests/test_door_lock.py
git commit -m "test: add door lock acceptance boundaries"
git push
```

Poll SCM 또는 Build Now로 실행합니다. 기대 결과는 **1 failed, 4 passed / FAILURE**입니다.
Test Result에서 `test_locks_at_15_kmh`의 실패를 찾습니다.

## 4. Green

`doorlock/door_lock.py` 마지막 조건을 인수 기준의 **15 km/h 이상**과 일치하도록 한 줄 수정합니다.
로컬에서 `python -m pytest`로 **5 passed**를 확인하고 커밋·푸시합니다.
Jenkins의 SUCCESS와 Test Result Trend의 이전 실패 이력을 확인합니다.

## 5. Flake8과 Quality Gate

Freestyle Job의 Build Steps에 별도 Windows batch 단계를 추가합니다.

```bat
python -m flake8 doorlock tests --format=pylint --output-file=reports/flake8.txt --exit-zero
```

그 다음 별도 단계에 다음을 추가합니다.

```bat
python -m lizard doorlock -C 10
```

빌드 후 조치 → **Record compiler warnings and static analysis results**:

* Tool: **Flake8**, Report File Pattern: `reports/flake8.txt`.
* Quality gates → Threshold **1**, Type **TOTAL**, 빌드 결과 **FAILURE**.
* **Publish issues when build is failed** 옵션을 켭니다.
* **Fail the build on errors** 옵션을 켭니다. 보고서 누락·파싱 오류를 경고 0건으로 오인하지 않습니다.

코드는 고치지 않고 빌드합니다.
기대 결과: 테스트 통과(3 passed, Red·Green을 했다면 5 passed), Flake8 **경고 5건**, Quality Gate **FAILURE**,
Lizard 단계는 `select_door_warning`의 복잡도 초과로 종료 코드 1. **테스트는 통과했는데 빌드는 실패합니다.**
경고 목록에서 파일·행·규칙·메시지를, Console Output에서 Lizard 경고 줄을 열어 봅니다.
게이트 설정 전(Flake8 게시만 한 상태)에는 경고 5건이 보여도 빌드는 SUCCESS입니다.

## 6. Pipeline으로 다시 실행

새 Item → Pipeline → **Pipeline script from SCM** → SCM Git → 자신의 Fork URL → `*/main` →
Script Path **Jenkinsfile**을 설정합니다. 첫 Build Now 이후 Poll SCM이 활성화됩니다.
이미 Green으로 수정했다면 5건부터 시작합니다. 처음부터 재현하려면 **새 Fork/작업 브랜치의 시작 커밋**을 사용합니다.
기존 작업을 덮어쓰는 reset 명령 대신 새 브랜치/새 Clone을 권장합니다.

Stage View에서 Setup → Unit Test → Static Analysis → Complexity를 확인합니다.
Red는 Unit Test에서 실패하므로 뒤 단계는 생략되며, JUnit 결과는 계속 게시됩니다.
테스트가 통과하면 Complexity 단계가 `door_warning.py`의 Lizard 경고로 실패하고, post의 Quality Gate도 경고 5건으로 FAILURE를 냅니다.
`reports/`가 매 빌드 비워지므로 이전 경고 파일이 Red 빌드에 섞이지 않습니다.

## 7. 더 많은 결과 살펴보기

강사 안내에 따라 제품 Job `Jenkinsfile.product`를 실행합니다.
`clean`: 106건 통과와 경고 0건. `warnings`: 테스트 통과, 여러 파일에 20개 경고, 게이트 실패.
`complexity`: 테스트 통과, 복잡한 진단 라우팅 함수 때문에 Lizard 실패.
마지막에는 `clean`으로 다시 실행하여 정상 상태를 확인합니다.

