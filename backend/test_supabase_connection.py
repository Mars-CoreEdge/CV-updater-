#!/usr/bin/env python3
"""
Test script to find the correct Supabase hostname
"""

import psycopg2
import socket

def test_hostname(hostname):
    """Test if a hostname resolves and can connect to PostgreSQL"""
    print(f"\n🔍 Testing hostname: {hostname}")
    
    # Test DNS resolution
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution: {hostname} -> {ip}")
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    
    # Test PostgreSQL connection
    try:
        conn = psycopg2.connect(
            host=hostname,
            database="postgres",
            user="postgres",
            password="Abuzarasif2027,",
            port=5432,
            sslmode="require",
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL connection successful!")
        print(f"   Server version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def main():
    """Test different hostname formats"""
    project_id = "mqzmgrycagqyaqrxyrbl"
    
    hostnames_to_test = [
        f"db.{project_id}.supabase.co",
        f"{project_id}.supabase.co",
        f"aws-0-{project_id}.supabase.co",
        f"db.aws-0-{project_id}.supabase.co"
    ]
    
    print("🧪 Testing Supabase hostname formats...")
    print("=" * 50)
    
    working_hostname = None
    for hostname in hostnames_to_test:
        if test_hostname(hostname):
            working_hostname = hostname
            break
    
    if working_hostname:
        print(f"\n🎉 Found working hostname: {working_hostname}")
        print(f"Update your backend/db.py with: host='{working_hostname}'")
    else:
        print("\n❌ No working hostname found.")
        print("Please check your Supabase dashboard for the correct database hostname.")

if __name__ == "__main__":
    main() 