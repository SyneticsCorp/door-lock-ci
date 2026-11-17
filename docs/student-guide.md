# 수강자 실습 순서

강의자료 Ⅵ장과 같은 순서로 진행합니다.

1. 로컬에서 먼저 실행합니다.
2. 같은 명령을 Jenkins Freestyle Job에 맡깁니다.
3. 정적 분석과 Quality Gate가 빌드를 막는 것을 봅니다.
4. 고친 코드를 붙여 넣어 빌드 결과가 바뀌는 것을 봅니다.
5. 마지막으로 강사가 Pipeline 시연을 보여 줍니다.

Java·Jenkins 설치, 플러그인, Git 경로 설정은 [강사 안내](instructor-guide.md)를 따릅니다.
수강자가 직접 쓰는 코드는 없습니다. 5장에서 준비된 파일을 복사해 붙여 넣는 것만 합니다.

## 1. Fork와 Clone

1. GitHub에 자신의 수강자 계정으로 로그인합니다.
2. `https://github.com/SyneticsCorp/door-lock-ci`에서 **Fork → Create fork**를 선택합니다.
3. 자신의 Fork URL로 Clone합니다. 원본 저장소 소유자는 자기 저장소를 Fork할 수 없습니다.

```powershell
git clone https://github.com/<내계정>/door-lock-ci.git
cd door-lock-ci
```

Python 버전은 `python --version`, 위치는 `where.exe python`으로 확인합니다.
PowerShell에서는 `where` 대신 `where.exe`를 사용합니다.

## 2. 로컬에서 먼저 실행

```powershell
python -m pip install -r requirements.txt
python -m pytest
python -m flake8 doorlock tests
python -m lizard doorlock -C 10
```

기대 결과는 다음과 같습니다.

* pytest: `3 passed`
* Flake8: `doorlock/door_warning.py`에서 경고 5건(F401, E501, E711, E712, W291)
* Lizard: `select_door_warning`이 순환 복잡도 초과(CCN 15 > 10)로 표시되고, 종료 코드 1로 끝남

`door_warning.py`는 급하게 기능을 덧붙인 코드의 예입니다. 지금은 고치지 않고 결과만 읽습니다.
테스트는 통과하지만 정적 분석과 복잡도 기준에는 못 미치는 상태입니다.

## 3. Freestyle Job — 테스트

1. Jenkins → 새로운 Item → `door-lock-freestyle` → Freestyle project.
2. 소스 코드 관리: Git, 자신의 Fork URL, Branch Specifier `*/main`.
3. Build Triggers: **Poll SCM**, Schedule `H/2 * * * *`.
   5장에서 Fork에 커밋하면 2분 안에 자동으로 빌드됩니다. 외부 웹훅이 없어도 변경을 감지합니다.
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
6. Build Now → Console Output 및 Test Result에서 3건 통과, **SUCCESS**를 확인합니다.

## 4. Flake8 · Quality Gate · Lizard

### 4-1. Flake8 결과 게시

Build Steps에 별도 Windows batch 단계를 추가합니다. pytest 단계에 덧붙이지 않습니다.

```bat
python -m flake8 doorlock tests --format=pylint --output-file=reports/flake8.txt --exit-zero
```

빌드 후 조치 → **Record compiler warnings and static analysis results**를 추가합니다.

* Tool: **Flake8**, Report File Pattern: `reports/flake8.txt`.
* **Publish issues when build is failed** 옵션을 켭니다.
* **Fail the build on errors** 옵션을 켭니다. 보고서 누락·파싱 오류를 경고 0건으로 오인하지 않습니다.

Build Now. 기대 결과: 테스트 3 passed, Flake8 **경고 5건**, 빌드 **SUCCESS**.
경고 목록에서 파일·행·규칙·메시지를 열어 봅니다. 아직 판정 기준이 없어서 빌드는 성공입니다.

### 4-2. Quality Gate

같은 빌드 후 조치에서 Quality gates → Threshold **1**, Type **TOTAL**, 빌드 결과 **FAILURE**를 추가합니다.

Build Now. 기대 결과: 테스트 3 passed, Flake8 경고 5건, Quality Gate **FAILURE**.
**테스트는 통과했는데 빌드는 실패합니다.** 게이트가 기준 미달 코드를 막은 것입니다.

### 4-3. Lizard

Build Steps에 세 번째 Windows batch 단계를 추가합니다.

```bat
python -m lizard doorlock -C 10
```

Build Now. Console Output에서 `select_door_warning`의 복잡도 경고와, 종료 코드 1로 이 단계가 실패하는 것을 확인합니다.
이제 빌드 단계는 ① pip + pytest ② flake8 ③ lizard 세 개, 빌드 후 조치는 JUnit과 Flake8 + Quality Gate 두 개입니다.

## 5. 위반 해결 — 고친 코드 붙여 넣기

경고와 복잡도 초과를 고친 판이 `fixes/door_warning.py`에 준비되어 있습니다. 동작은 원래 판과 같습니다.
수강자는 코드를 직접 고치지 않고, 이 파일 내용을 그대로 붙여 넣어 빌드 결과가 어떻게 바뀌는지 봅니다.

1. 브라우저에서 **내 Fork**의 `fixes/door_warning.py`를 엽니다.
   오른쪽 위 **Copy raw file**(복사 아이콘)을 누르거나, **Raw**를 열어 전체를 복사합니다.
2. 내 Fork의 `doorlock/door_warning.py`를 열고 연필 모양 **Edit this file**을 누릅니다.
3. 편집 창의 내용을 모두 지우고(Ctrl+A → Delete) 복사한 내용을 붙여 넣습니다.
4. **Commit changes...** → 메시지 예: `fix: resolve door warning lint and complexity` → `main`에 커밋합니다.
5. Poll SCM이 2분 안에 새 빌드를 시작합니다. 기다리지 않으려면 Build Now를 누릅니다.

기대 결과: 테스트 3 passed, Flake8 **경고 0건**, Lizard 단계 통과, Quality Gate 통과, 빌드 **SUCCESS**.

* Build History: 실패 → 성공으로 바뀐 빌드와, 그 빌드를 만든 커밋을 확인합니다.
* Flake8 결과 화면: 경고 추이가 5건 → 0건으로 내려갑니다.
* Test Result Trend: 테스트는 처음부터 끝까지 3건 통과입니다. 바뀐 것은 코드 품질 기준 판정뿐입니다.

로컬 Clone도 맞추려면 `git pull`을 실행한 뒤 `python -m flake8 doorlock tests`와 `python -m lizard doorlock -C 10`을 다시 실행합니다.
둘 다 경고 없이 끝납니다.

## 6. Pipeline — 강사 시연

강사가 자신의 Fork로 보여 줍니다. 수강자가 직접 해 보려면 같은 설정을 따릅니다.

새 Item → Pipeline → **Pipeline script from SCM** → SCM Git → Fork URL → `*/main` →
Script Path **Jenkinsfile**을 설정합니다. 첫 Build Now 이후 Poll SCM이 활성화됩니다.

Stage View에서 Setup → Unit Test → Static Analysis → Complexity를 확인합니다.

* 고친 코드를 붙여 넣기 전: Unit Test까지 성공합니다. Complexity 단계가 Lizard 경고로 실패하고, post의 Quality Gate도 경고 5건으로 FAILURE를 냅니다.
* 붙여 넣은 뒤: 네 단계와 Quality Gate가 모두 통과하고 SUCCESS입니다.

Freestyle에서 화면으로 설정한 빌드 단계 세 개와 빌드 후 조치 두 개가 Jenkinsfile 한 파일에 들어 있습니다.
`reports/`가 매 빌드 비워지므로 이전 경고 파일이 다음 빌드에 섞이지 않습니다.

## 7. 확장 실습 (선택) — Red · Green

개발 경험이 있거나 시간이 남는 조만 합니다. 로컬에서 커밋·Push하므로 `git config --global user.name`과 `user.email`을 먼저 설정합니다.
5장을 GitHub 웹에서 했다면 먼저 `git pull`로 로컬을 맞춥니다.

**Red.** `tests/test_door_lock.py` 마지막에 두 테스트를 추가합니다.

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

기대 결과는 **1 failed, 4 passed / FAILURE**입니다. Test Result에서 `test_locks_at_15_kmh`의 실패를 찾습니다.

**Green.** `doorlock/door_lock.py` 마지막 조건을 인수 기준의 **15 km/h 이상**과 일치하도록 한 줄 수정합니다.
로컬에서 `python -m pytest`로 **5 passed**를 확인하고 커밋·푸시합니다.
Jenkins의 SUCCESS와 Test Result Trend의 이전 실패 이력을 확인합니다.

## 8. 더 많은 결과 살펴보기

강사 안내에 따라 제품 Job `Jenkinsfile.product`를 실행합니다.
`clean`: 106건 통과와 경고 0건. `warnings`: 테스트 통과, 여러 파일에 20개 경고, 게이트 실패.
`complexity`: 테스트 통과, 복잡한 진단 라우팅 함수 때문에 Lizard 실패.
마지막에는 `clean`으로 다시 실행하여 정상 상태를 확인합니다.
