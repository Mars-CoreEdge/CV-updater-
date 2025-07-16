#!/usr/bin/env python3
"""
Test script to check exact routes and their responses
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_routes():
    """Test specific routes to identify issues"""
    
    print("🔍 Testing specific routes...")
    
    # Test 1: Check if projects/create-from-chat exists
    print("\n1. Testing /projects/create-from-chat...")
    try:
        response = requests.post(f"{BASE_URL}/projects/create-from-chat", 
                               json={"message": "test"}, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Check if cv/add-projects exists
    print("\n2. Testing /cv/add-projects...")
    try:
        response = requests.post(f"{BASE_URL}/cv/add-projects", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check if projects/ exists (GET)
    print("\n3. Testing GET /projects/...")
    try:
        response = requests.get(f"{BASE_URL}/projects/", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Check if projects/ exists (POST)
    print("\n4. Testing POST /projects/...")
    try:
        response = requests.post(f"{BASE_URL}/projects/", 
                               json={"title": "test", "description": "test"}, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Check if projects/create exists (POST)
    print("\n5. Testing POST /projects/create...")
    try:
        response = requests.post(f"{BASE_URL}/projects/create", 
                               json={"title": "test", "description": "test"}, 
                               timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_routes() 