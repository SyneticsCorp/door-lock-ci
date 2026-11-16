"""! @brief VA-007 JSON 시나리오 실행과 사용자 오류 메시지 검증."""

import json
import runpy
import sys

import pytest

from vehicle_access.cli import main, run_scenario


def test_commute_scenario():
    """! @brief VA-007: 탑승·주행·하차·재잠금 명령을 하나의 흐름으로 실행한다."""
    result = run_scenario([
        {'command': 'open', 'name': 'front_left', 'opened': True},
        {'command': 'open', 'name': 'front_left', 'opened': False},
        {'command': 'child_lock', 'name': 'rear_left', 'enabled': True},
        {'command': 'speed', 'speed_kmh': 15},
        {'command': 'speed', 'speed_kmh': 0},
        {'command': 'unlock', 'now': 10},
        {'command': 'tick', 'now': 40},
        {'command': 'lock'},
    ])
    assert all(door['locked'] for door in result['state']['doors'].values())
    assert result['events'][-1]['detail'] == 'timeout'
    assert result['state']['doors']['rear_left']['child_lock']


@pytest.mark.parametrize('steps', [
    None, {}, 'speed', [None], [1], [{}], [{'command': 'erase'}],
    [{'command': 'speed'}], [{'command': 'speed', 'unexpected': 1}],
])
def test_rejects_malformed_scenario(steps):
    """! @brief VA-007: 미지원 명령과 잘못된 시나리오 구조를 설명 가능한 오류로 처리한다."""
    with pytest.raises(ValueError):
        run_scenario(steps)


def test_cli_success(tmp_path, capsys):
    """! @brief VA-007: UTF-8 파일을 읽고 상태·이벤트 JSON을 출력한다."""
    scenario = tmp_path / '주행.json'
    scenario.write_text('[{"command":"speed","speed_kmh":15}]', encoding='utf-8')
    assert main([str(scenario)]) == 0
    assert json.loads(capsys.readouterr().out)['events'][0]['detail'] == 'speed'


@pytest.mark.parametrize('contents', ['{bad json', '{}', '[{"command":"lock","extra":1}]'])
def test_cli_error(tmp_path, capsys, contents):
    """! @brief VA-007: 잘못된 파일은 종료 코드 2와 오류 메시지를 남긴다."""
    scenario = tmp_path / 'invalid.json'
    scenario.write_text(contents, encoding='utf-8')
    assert main([str(scenario)]) == 2
    assert 'error:' in capsys.readouterr().err


def test_cli_missing_file(tmp_path, capsys):
    """! @brief VA-007: 없는 파일의 오류를 traceback 없이 표시한다."""
    assert main([str(tmp_path / 'missing.json')]) == 2
    assert 'error:' in capsys.readouterr().err


def test_module_entry_point(tmp_path, monkeypatch, capsys):
    """! @brief VA-007: python -m vehicle_access 진입점을 검증한다."""
    scenario = tmp_path / 'empty.json'
    scenario.write_text('[]', encoding='utf-8')
    monkeypatch.setattr(sys, 'argv', ['vehicle_access', str(scenario)])
    with pytest.raises(SystemExit) as result:
        runpy.run_module('vehicle_access', run_name='__main__')
    assert result.value.code == 0
    assert json.loads(capsys.readouterr().out)['events'] == []
