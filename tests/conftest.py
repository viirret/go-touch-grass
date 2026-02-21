from __future__ import annotations

import pytest
import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock
from go_touch_grass.tracker import TimeTracker
from go_touch_grass.outputs.file import FileOutput


@pytest.fixture
def temp_state_file() -> Generator[Path, None, None]:
    with tempfile.NamedTemporaryFile(suffix='.json') as tmp:
        yield Path(tmp.name)


@pytest.fixture
def tracker(temp_state_file: Path, monkeypatch: pytest.MonkeyPatch) -> TimeTracker:
    monkeypatch.setenv('XDG_STATE_HOME', str(temp_state_file.parent))
    return TimeTracker(username="test_user")


@pytest.fixture
def mock_output() -> MagicMock:
    mock = MagicMock()
    mock.send.return_value = True
    return mock


@pytest.fixture
def file_output(tmp_path: Path) -> FileOutput:
    log_file = tmp_path / "test_log.txt"
    return FileOutput(username="test_user", filename=str(log_file))
