import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class FileOutput:
    def __init__(self, username, filename="activity_log.txt"):
        self.username = username
        self.log_file = Path(filename)

        # Write header if file doesn't exist
        if not self.log_file.exists():
            with open(self.log_file, 'w') as f:
                f.write("Go Touch Grass Activity Log\n")
                f.write("="*30 + "\n\n")

    def send(self, message):
        """Append message to log file"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"

            with open(self.log_file, 'a') as f:
                f.write(log_entry)
            return True
        except Exception as e:
            logger.error(f"Failed to write to log file: {e}")
            return False
