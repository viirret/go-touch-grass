import json
import pytest
import time
from go_touch_grass.tracker import TimeTracker

@pytest.fixture
def tracker_env(tmp_path, monkeypatch):
    """Fixture that sets up the complete tracking environment"""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state_file = state_dir / "state.json"
    
    monkeypatch.setenv('XDG_STATE_HOME', str(tmp_path))
    monkeypatch.setattr('go_touch_grass.tracker.app_state_dir', state_dir)
    monkeypatch.setattr('go_touch_grass.tracker.state_file', state_file)
    
    return {'state_dir': state_dir, 'state_file': state_file}

@pytest.fixture
def tracker(tracker_env):
    tracker_env['state_file'].unlink(missing_ok=True)
    return TimeTracker(username="test_user")

@pytest.fixture
def state_file(tmp_path):
    """Helper fixture to get the state file path"""
    return tmp_path / "state" / "state.json"

def test_tracker_initialization(tracker, tracker_env):
    state_file = tracker_env['state_file']
    
    assert tracker.username == "test_user"
    assert tracker.state['running'] is True
    
    for _ in range(10):
        if state_file.exists():
            break
        time.sleep(0.1)
    else:
        pytest.fail("State file was not created")
    
    with open(state_file) as f:
        data = json.load(f)
        assert data['running'] is True
        assert isinstance(data['session_start'], float)

def test_shutdown_handling(tracker, tracker_env, mocker):
    state_file = tracker_env['state_file']
    mock_output = mocker.MagicMock()
    
    tracker.add_output_handler(mock_output)
    tracker.on_shutdown()
    
    with open(state_file) as f:
        data = json.load(f)
        assert data['running'] is False
        assert isinstance(data['last_online_duration'], float)
        assert isinstance(data['last_shutdown'], float)
    
    assert mock_output.send.call_count == 1

def test_format_duration():
    tracker = TimeTracker(username="test_user")
    assert tracker.format_duration(65) == "1 minute 5 seconds"
    assert tracker.format_duration(3600) == "1 hour"
    assert tracker.format_duration(86400) == "1 day"

def test_network_wait(mocker):
    tracker = TimeTracker(username="test_user")
    mock_get = mocker.patch('requests.get')
    mock_get.side_effect = [Exception(), Exception(), True]
    
    assert tracker.wait_for_network(timeout=10) is True
    assert mock_get.call_count == 3
