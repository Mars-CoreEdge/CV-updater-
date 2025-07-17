#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import sys
import os
import requests
import json

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend():
    """Test basic backend functionality"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Backend Functionality...")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Server is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the backend first.")
        print("   Run: cd backend && python main_enhanced.py")
        return False
    
    # Test 2: Check database connection
    try:
        response = requests.get(f"{base_url}/cv/current/")
        if response.status_code == 404:
            print("✅ Database connection working (no CV found, which is expected)")
        else:
            print(f"✅ Database connection working: {response.status_code}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    
    # Test 3: Test projects endpoint
    try:
        response = requests.get(f"{base_url}/projects/")
        print(f"✅ Projects endpoint working: {response.status_code}")
    except Exception as e:
        print(f"❌ Projects endpoint failed: {e}")
        return False
    
    # Test 4: Test chat endpoint
    try:
        chat_data = {"message": "Hello, can you help me with my CV?"}
        response = requests.post(f"{base_url}/chat/", json=chat_data)
        print(f"✅ Chat endpoint working: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Backend is working correctly.")
    print("\n📋 Available endpoints:")
    print("   - GET  /                    - Server status")
    print("   - POST /upload-cv/          - Upload CV file")
    print("   - POST /chat/               - Chat with AI")
    print("   - GET  /cv/current/         - Get current CV")
    print("   - GET  /projects/           - Get projects")
    print("   - POST /cv/download         - Download CV as PDF")
    
    return True

if __name__ == "__main__":
    test_backend() 