"""Best-effort per-instance SQLite daily call quota. NOT a billing hard cap."""
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DB = Path(os.getenv('QFD_QUOTA_DB', str(Path(tempfile.gettempdir()) / 'qfd_demo_api_quota.sqlite3')))

def allowed_daily():
    return max(0, int(os.getenv('QFD_GLOBAL_DAILY_LIMIT', '12')))

def reserve(action):
    """Atomically consume a slot, including failed requests, to avoid bursts."""
    if os.getenv('QFD_LLM_ENABLED', 'true').lower() not in ('1', 'true', 'yes'):
        return False, 'Live AI calls are disabled by the application owner.'
    day = datetime.now(timezone.utc).date().isoformat()
    try:
        with sqlite3.connect(DB, timeout=8) as cx:
            cx.execute('BEGIN IMMEDIATE')
            cx.execute('CREATE TABLE IF NOT EXISTS calls (day TEXT NOT NULL, action TEXT NOT NULL)')
            cx.execute('DELETE FROM calls WHERE day < ?', (day,))
            count = cx.execute('SELECT COUNT(*) FROM calls WHERE day=?', (day,)).fetchone()[0]
            if count >= allowed_daily():
                return False, 'The shared daily AI demonstration quota has been reached. Deterministic scenarios are still available.'
            cx.execute('INSERT INTO calls(day,action) VALUES (?,?)', (day, action))
            cx.commit()
        return True, f'AI demo quota: {count + 1}/{allowed_daily()} calls reserved today (UTC) on this app instance.'
    except sqlite3.Error:
        return False, 'Shared AI quota store unavailable; live calls disabled for safety.'

def quota_status():
    try:
        with sqlite3.connect(DB, timeout=3) as cx:
            count = cx.execute('SELECT COUNT(*) FROM calls WHERE day=?', (datetime.now(timezone.utc).date().isoformat(),)).fetchone()[0]
        return count, allowed_daily()
    except sqlite3.Error:
        return 0, allowed_daily()
