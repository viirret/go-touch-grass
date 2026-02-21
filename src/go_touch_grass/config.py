from __future__ import annotations

import os
from pathlib import Path

# Base directories.
XDG_STATE_HOME: Path = Path(os.getenv('XDG_STATE_HOME', str(Path.home() / '.local' / 'state')))
XDG_CACHE_HOME: Path = Path(os.getenv('XDG_CACHE_HOME', str(Path.home() / '.cache')))

# Application directories.
APP_NAME: str = 'go_touch_grass'
APP_STATE_DIR: Path = XDG_STATE_HOME / APP_NAME
APP_CACHE_DIR: Path = XDG_CACHE_HOME / APP_NAME

# File paths.
STATE_FILE: Path = APP_STATE_DIR / 'state.json'
LOG_FILE: Path = APP_CACHE_DIR / 'log.log'
DB_FILE: Path = APP_STATE_DIR / 'usage_stats.db'


def ensure_dirs_exist() -> None:
    """Ensure all application directories exist."""
    APP_STATE_DIR.mkdir(parents=True, exist_ok=True)
    APP_CACHE_DIR.mkdir(parents=True, exist_ok=True)
