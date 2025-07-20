#!/usr/bin/env python3
"""
Simple script to test backend connectivity and API endpoints
"""

import requests
import json
import sys

def test_backend():
    base_url = "http://localhost:8081"
    
    print("🔍 Testing CV Updater Backend...")
    print("=" * 50)
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: Health check
    try:
        response = requests.get(f"{base_url}/test")
        print(f"✅ Health check: {response.status_code}")
        data = response.json()
        print(f"   Status: {data.get('status')}")
        print(f"   Database: {data.get('database')}")
        print(f"   Projects: {data.get('projects_count')}")
        print(f"   CVs: {data.get('cvs_count')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 3: Projects endpoint
    try:
        response = requests.get(f"{base_url}/projects/list")
        print(f"✅ Projects list: {response.status_code}")
        data = response.json()
        print(f"   Projects count: {data.get('total_count', 0)}")
        if data.get('projects'):
            for i, project in enumerate(data['projects'][:3]):  # Show first 3
                print(f"   Project {i+1}: {project.get('title', 'No title')}")
    except Exception as e:
        print(f"❌ Projects list failed: {e}")
        return False
    
    # Test 4: CV endpoint
    try:
        response = requests.get(f"{base_url}/cv/current/")
        print(f"✅ CV current: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   CV found: {bool(data.get('content'))}")
            print(f"   Content length: {len(data.get('content', ''))}")
        else:
            print(f"   No CV found (expected for empty database)")
    except Exception as e:
        print(f"❌ CV current failed: {e}")
        return False
    
    print("=" * 50)
    print("✅ All tests completed successfully!")
    return True

if __name__ == "__main__":
    success = test_backend()
    sys.exit(0 if success else 1) 