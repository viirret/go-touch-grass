import os
from pathlib import Path

# Base directories.
XDG_STATE_HOME = Path(os.getenv('XDG_STATE_HOME', Path.home() / '.local' / 'state'))
XDG_CACHE_HOME = Path(os.getenv('XDG_CACHE_HOME', Path.home() / '.cache'))

# Application directories.
APP_NAME = 'go_touch_grass'
APP_STATE_DIR = XDG_STATE_HOME / APP_NAME
APP_CACHE_DIR = XDG_CACHE_HOME / APP_NAME

# File paths.
STATE_FILE = APP_STATE_DIR / 'state.json'
LOG_FILE = APP_CACHE_DIR / 'log.log'
DB_FILE = APP_STATE_DIR / 'usage_stats.db'


def ensure_dirs_exist():
    """Ensure all application directories exist."""
    APP_STATE_DIR.mkdir(parents=True, exist_ok=True)
    APP_CACHE_DIR.mkdir(parents=True, exist_ok=True)
