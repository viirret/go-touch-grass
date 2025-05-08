import pytest
from go_touch_grass.outputs.discord import DiscordOutput

@pytest.fixture
def discord_output(monkeypatch):
    monkeypatch.setenv('DISCORD_WEBHOOK_URL', 'https://example.com/webhook')
    return DiscordOutput(username="test_user")

def test_discord_send_success(discord_output, mocker):
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.status_code = 204
    
    assert discord_output.send("Test message") is True
    mock_post.assert_called_once()

def test_discord_send_failure(discord_output, mocker):
    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = Exception("Test error")
    
    assert discord_output.send("Test message") is False