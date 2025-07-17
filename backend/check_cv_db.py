#!/usr/bin/env python3
"""
Check CV database content
"""

import sqlite3

def check_cv_database():
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Check if CV table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cvs'")
        if not cursor.fetchone():
            print("❌ CV table does not exist")
            return
        
        # Get active CV
        cursor.execute("SELECT filename, current_content, updated_at FROM cvs WHERE is_active = TRUE LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            filename, content, updated_at = row
            print("✅ CV found in database:")
            print(f"   Filename: {filename}")
            print(f"   Content length: {len(content) if content else 0}")
            print(f"   Updated: {updated_at}")
            print(f"   Content preview: {content[:200] if content else 'None'}...")
        else:
            print("❌ No active CV found")
            
            # Check for any CVs
            cursor.execute("SELECT COUNT(*) FROM cvs")
            count = cursor.fetchone()[0]
            print(f"   Total CVs in database: {count}")
            
            if count > 0:
                cursor.execute("SELECT filename, current_content FROM cvs ORDER BY updated_at DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    filename, content = row
                    print(f"   Most recent CV: {filename}")
                    print(f"   Content length: {len(content) if content else 0}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_cv_database() 