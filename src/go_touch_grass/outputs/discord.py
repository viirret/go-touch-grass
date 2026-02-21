from __future__ import annotations

import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()


class DiscordOutput:
    def __init__(self, username: str) -> None:
        self.username: str = username
        self.webhook_url: str | None = os.getenv('DISCORD_WEBHOOK_URL')
        if not self.webhook_url:
            raise ValueError("Discord webhook URL not found in .env file")

    def send(self, message: str) -> bool:
        """Send a message to the Discord webhook."""
        data = {
            "username": "Go Touch Grass!",
            "embeds": [{
                "title": "Grass Touching Update",
                "description": message,
                "color": 0x3498db,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "footer": {
                    "text": "Automated computer usage tracker"
                },
                "author": {
                    "name": "github.com/viirret/go-touch-grass",
                    "url": "https://github.com/viirret/go-touch-grass",
                    "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
                }
            }]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send to Discord: {e}")
            return False
