from __future__ import annotations

from pathlib import Path
from pytest_mock import MockerFixture
from go_touch_grass.outputs.file import FileOutput


def test_file_output_initialization(file_output: FileOutput, tmp_path: Path) -> None:
    log_file = tmp_path / "test_log.txt"
    assert log_file.exists()
    assert "Go Touch Grass Activity Log" in log_file.read_text()


def test_file_output_send(file_output: FileOutput, tmp_path: Path) -> None:
    log_file = tmp_path / "test_log.txt"
    message = "Test message"

    assert file_output.send(message) is True
    assert message in log_file.read_text()


def test_file_output_error_handling(mocker: MockerFixture, tmp_path: Path) -> None:
    log_file = tmp_path / "error_log.txt"
    log_file.touch()

    mock_open = mocker.patch('builtins.open')
    mock_open.side_effect = Exception("Test error")

    output = FileOutput(username="test_user", filename=str(log_file))
    assert output.send("test") is False
    mock_open.assert_called_once()
