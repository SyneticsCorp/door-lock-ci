# 제품 모델과 요구사항

이 명세의 VA 요구사항은 이 저장소의 추가 교육용 제품을 위해 정의했습니다.
강의자료의 실제 차량 요구사항이나 공식 안전 요구사항을 대신하지 않습니다.

| ID | 동작과 제약 | 구현 | 주요 테스트 |
|---|---|---|---|
| VA-001 | 모든 도어가 닫혔고 아직 모두 잠기지 않았을 때 15 km/h 이상에서 잠금 | `policy.py`, `controller.py` | `test_auto_lock_boundary`, `test_driving_at_boundary_locks_all_doors` |
| VA-002 | 열린 도어는 잠글 수 없고, 잠긴 도어는 열 수 없음. 주행 중 마지막 열린 도어가 닫히면 자동 잠금 재평가 | `controller.py` | `test_open_door_blocks_manual_lock`, `test_locked_door_cannot_be_opened`, `test_closing_last_open_door_allows_driving_lock` |
| VA-003 | 어린이 보호 잠금은 뒷좌석의 안쪽 열림 허용만 제한. 외부 열림 센서와 구별 | `controller.py` | `test_child_lock_changes_inside_release_only`, `test_front_doors_reject_child_lock` |
| VA-004 | 해제 후 도어를 열지 않으면 기본 30초에 재잠금. 열림 이벤트는 타이머 취소. 시각 역행 금지 | `controller.py` | `test_relock_deadline`, `test_opening_door_cancels_relock`, `test_clock_cannot_move_backwards` |
| VA-005 | 진단 이벤트 순번 증가, 보존량 1~10000 제한, 초과 시 오래된 항목부터 제거 | `diagnostics.py` | `test_ring_retains_newest_events_with_original_sequence`, `test_event_is_immutable` |
| VA-006 | 유한한 0~300 km/h 입력, 0.001~3600초 재잠금 시간, bool 상태 입력. 잘못된 입력은 상태 변경 전 거부 | `policy.py`, `controller.py` | `test_invalid_speed_leaves_state_unchanged`, `test_invalid_relock_configuration`, `test_open_state_requires_boolean` |
| VA-007 | UTF-8 JSON 명령 배열을 순서대로 실행하고 최종 상태/진단 이벤트를 JSON으로 출력. 잘못된 파일/명령은 종료 코드 2 | `cli.py` | `test_commute_scenario`, `test_cli_error`, `test_module_entry_point` |

도어 이름은 `front_left`, `front_right`, `rear_left`, `rear_right`입니다.
CLI 명령은 `open`, `speed`, `lock`, `unlock`, `tick`, `child_lock`이며 인자는 Python 공개 메서드와 같습니다.
시각은 초 단위의 시뮬레이션 값으로, 0~10^12 범위에서 같거나 증가해야 합니다.
`unlock`은 학습용 원격 명령이므로 주행 중 해제 차단 기능은 별도 요구사항으로 정의하지 않았습니다.

