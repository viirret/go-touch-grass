from __future__ import annotations

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConsoleOutput:
    def __init__(self, username: str) -> None:
        self.username: str = username

    def send(self, message: str) -> bool:
        """Print message to console"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to print to console: {e}")
            return False
