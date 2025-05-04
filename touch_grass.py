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

xdg_state_home = Path(os.getenv('XDG_STATE_HOME', Path.home() / '.local' / 'state'))
xdg_cache_home = Path(os.getenv('XDG_CACHE_HOME', Path.home() / '.cache'))

# Create application directories
app_state_dir = xdg_state_home / 'go_touch_grass'
app_cache_dir = xdg_cache_home / 'go_touch_grass'

app_state_dir.mkdir(parents=True, exist_ok=True)
app_cache_dir.mkdir(parents=True, exist_ok=True)

# File paths
state_file = app_state_dir / 'state.json'
log_file = app_cache_dir / 'log.log'

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
        if not self.webhook_url:
            raise ValueError("Discord webhook URL not found in .env file")

        self.data_file = Path(state_file)
        self.state = self.load_state() or { 'running': False }

        # Check for existing running session.
        if self.state.get('running', False):
            logger.warning("Existing running session detected - cleaning up")
            self.state['running'] = False
            self.save_state()

        # Register handlers.
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGHUP, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
        atexit.register(self.on_shutdown)

        # Initialize new session.
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
        try:
            if not self.state.get('running', False):
                logger.info("No active session to save.")
                return

            # Calculate duration.
            end_time = time.time()
            online_duration = end_time - self.state['session_start']

            # Save state.
            self.state.update({
                'last_online_duration': online_duration,
                'last_shutdown': end_time,
                'running': False
            })
            self.save_state()

            # Send discord message.
            duration_str = self.format_duration(online_duration)
            message = f"{self.username} was online for {duration_str}."
            try:
                if self.send_to_discord(message):
                    logger.info(f"Session ended. Duration: {duration_str}")
                else:
                    logger.error("Failed to send message to Discord.")
            except Exception as e:
                logger.error(f"Discord send error: {e}")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            raise

    def report_offline_time(self):
        """Report how long computer was offline (touching grass time)"""
        if not self.state.get('last_shutdown'):
            logger.info("No previous shutdown detected")
            return
            
        offline_duration = time.time() - self.state['last_shutdown']
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
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to send to Discord: {e}")
            return False

    def wait_for_network(self, timeout=300, check_interval=10):
        """Wait for network connection to be available"""
        start_time = time.time()
        logger.info("Waiting for network connection...")

        test_urls = [
            'https://1.1.1.1',  # Cloudflare DNS
            'https://8.8.8.8',  # Google DNS
            'https://discord.com'  # Our actual target
        ]

        while time.time() - start_time < timeout:
            try:
                for url in test_urls:
                    try:
                        requests.get(url, timeout=5)
                        logger.info(f"Network connection established (reached {url})")
                        return True
                    except:
                        continue

                # If all URLs failed
                logger.warning(f"No network connectivity yet. Retrying in {check_interval} seconds...")
                time.sleep(check_interval)

            except Exception as e:
                logger.warning(f"Network check error: {e}. Retrying...")
                time.sleep(check_interval)

        logger.error("Network connection timeout exceeded")
        return False

    def run(self):
        """Main tracking loop"""
        # Wait for network connection before starting.
        if not self.wait_for_network():
            logger.info("Starting offline, will retry operations when network is available.")

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
