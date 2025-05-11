import sqlite3
from go_touch_grass.config import DB_FILE, ensure_dirs_exist


class Db:
    def __init__(self, db_path=None):
        ensure_dirs_exist()
        self.db_path = db_path if db_path else DB_FILE
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    duration REAL NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('online', 'offline')),
                    is_record INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_session(self, username, session_type, start_time, end_time, duration):
        """
        Save a session to the database.

        Args:
            username: User identifier
            session_type: 'online' or 'offline'
            start_time: Unix timestamp
            end_time: Unix timestamp
            duration: Duration in seconds

        Returns:
            bool: True if this is a new record, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if this is a record duration
            cursor.execute('''
                SELECT MAX(duration) FROM sessions
                WHERE username = ? AND type = ?
            ''', (username, session_type))
            max_duration = cursor.fetchone()[0]

            is_record = max_duration is None or duration > max_duration

            # Insert the new session
            cursor.execute('''
                INSERT INTO sessions
                (username, start_time, end_time, duration, type, is_record)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, start_time, end_time, duration, session_type, int(is_record)))

            conn.commit()

            return is_record

    def get_stats(self, username):
        """
        Get usage statistics for a specific user.

        Args:
            username: User identifier

        Returns:
            dict: Dictionary containing statistics
        """
        stats = {
            'online': {},
            'offline': {}
        }

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get longest online session.
            cursor.execute('''
                SELECT start_time, end_time, duration
                FROM sessions
                WHERE username = ? AND type = 'online' AND is_record = 1
                ORDER BY duration DESC
                LIMIT 1
            ''', (username,))
            row = cursor.fetchone()
            if row:
                stats['online']['longest'] = dict(row)

            # Get longest offline session.
            cursor.execute('''
                SELECT start_time, end_time, duration
                FROM sessions
                WHERE username = ? AND type = 'offline' AND is_record = 1
                ORDER BY duration DESC
                LIMIT 1
            ''', (username,))
            row = cursor.fetchone()
            if row:
                stats['offline']['longest'] = dict(row)

            # Get total online time.
            cursor.execute('''
                SELECT SUM(duration) as total
                FROM sessions
                WHERE username = ? AND type = 'online'
            ''', (username,))
            row = cursor.fetchone()
            stats['online']['total'] = row['total'] if row['total'] else 0

            # Get total offline time.
            cursor.execute('''
                SELECT SUM(duration) as total
                FROM sessions
                WHERE username = ? AND type = 'offline'
            ''', (username,))
            row = cursor.fetchone()
            stats['offline']['total'] = row['total'] if row['total'] else 0

        return stats
