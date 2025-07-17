import sqlite3
import os
from contextlib import contextmanager

def get_db_cursor():
    """Get database connection with proper timeout and error handling"""
    try:
        # Temporary SQLite connection while we fix Supabase
        conn = sqlite3.connect('cv_updater.db', timeout=60.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=memory")
        cursor = conn.cursor()
        return cursor, conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

@contextmanager
def get_db_cursor_context():
    """Context manager for database operations with automatic cleanup"""
    conn = None
    cursor = None
    try:
        cursor, conn = get_db_cursor()
        yield cursor, conn
        if conn:
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database operation error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 