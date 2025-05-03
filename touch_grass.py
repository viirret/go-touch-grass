import os
import time
import json
import requests
import atexit
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import argparse
import signal
import sys
import logging
from pathlib import Path

tmp_dir = Path('/tmp/go_touch_grass')
tmp_dir.mkdir(parents=True, exist_ok=True)

log_file = tmp_dir / 'log.log'
state_file = tmp_dir / 'state.json'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

load_dotenv()

class TimeTracker:
    def __init__(self, username):
        self.username = username
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self.data_file = Path(state_file)

        if not self.webhook_url:
            raise ValueError("Discord webhook URL not found in .env file")
        
        self.state = self.load_state() or { 'running': False }

        # Register handlers.
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGHUP, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
        atexit.register(self.on_shutdown)

        # If fresh start, set the start time.
        if not self.state.get('running', False):
            self.state = {
                'session_start': time.time(),
                'running': True,
                'last_shutdown': self.state.get('last_shutdown', None),
                'last_online_duration': self.state.get('last_online_duration', None)
            }
            self.save_state()
            logger.info("New tracking session started.")

    def load_state(self):
        """Load tracking state from file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    state = json.load(f)
                    if not isinstance(state, dict):
                        return {'running': False}
                    
                    # Convert string timestamps to numbers.
                    if 'session_start' in state:
                        state['session_start'] = float(state['session_start'])
                    if 'last_shutdown' in state:
                        state['last_shutdown'] = float(state['last_shutdown'])
                    if 'last_online_duration' in state:
                        state['last_online_duration'] = float(state['last_online_duration'])
                    return state
        except Exception as e:
            logger.error(f"Error loading state file: {e}")
            return {'running': False}
        
    def save_state(self):
        """Save current state to a file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.state, f)
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def handle_shutdown(self, signum=None, frame=None):
        """Handle termination signals."""
        logger.info(f"Received shutdown signal: {signum}")
        self.on_shutdown()
        sys.exit(0)

    def on_shutdown(self):
        """Save shutdown time and calculate session duration."""
        if not self.state.get('running', False):
            logger.info("No active session to save.")
            return
        
        try:
            # Calculate computer usage duration.
            end_time = time.time()
            online_duration = end_time - self.state['session_start']
            self.state['last_online_duration'] = online_duration
            self.state['last_shutdown'] = end_time
            self.state['running'] = False
            self.save_state()

            # Send discord message.
            duration_str = self.format_duration(online_duration)
            message = f"{self.username} was online for {duration_str}."
            self.send_to_discord(message)

            logger.info(f"Session ended. Duration: {duration_str}")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    def report_offline_time(self):
        """Report how long computer was offline (touching grass time)"""
        if not self.state.get('last_shutdown'):
            logger.info("No previous shutdown detected")
            return
            
        offline_duration = time.time() - self.state['last_shutdown']
        
        # Only report if offline for >1 minute.
        if offline_duration > 60:  
            duration_str = self.format_duration(offline_duration)
            message = f"{self.username} touched grass for: {duration_str}."
            self.send_to_discord(message)
            logger.info(message)


    def format_duration(self, seconds):
        """Format seconds into human-readable time."""
        duration = timedelta(seconds=seconds)
        parts = []
        
        if duration.days > 0:
            parts.append(f"{duration.days} day{'s' if duration.days != 1 else ''}")
        
        hours, remainder = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not parts:
            parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        return ' '.join(parts)

    def send_to_discord(self, message):
        """Send message to Discord webhook."""
        data = {
            "username": "Go Touch Grass!",
            "embeds": [{
                "title": "️Grass Touching Update",
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
                timeout=5
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send to Discord: {e}")
            return False

    def run(self):
        """Main tracking loop"""
        self.report_offline_time()
        
        # Keep running until shutdown.
        try:
            while True:
                time.sleep(60)  # Check every minute.
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            self.handle_shutdown()
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Time tracking tool that reports to Discord on shutdown.')
    parser.add_argument('--username', required=True, help='Username to include in the Discord message')
    args = parser.parse_args()

    tracker = TimeTracker(args.username)
    print(f"Time tracking started for user: {args.username}")
    print("The tracker will run in the background and report when the system shuts down.")

    tracker.run()

if __name__ == "__main__":
    main()
