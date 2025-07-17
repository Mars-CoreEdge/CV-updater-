#!/usr/bin/env python3
"""
Clear CV database for testing
"""

import sqlite3

def clear_cv_database():
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Clear all CVs
        cursor.execute("DELETE FROM cvs")
        cursor.execute("DELETE FROM manual_projects")
        cursor.execute("DELETE FROM chat_messages")
        
        # Reset auto-increment counters
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='cvs'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='manual_projects'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='chat_messages'")
        
        conn.commit()
        conn.close()
        
        print("✅ CV database cleared successfully")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    clear_cv_database() 