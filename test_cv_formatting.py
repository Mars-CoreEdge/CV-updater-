#!/usr/bin/env python3
"""
Test script to verify CV formatting changes
"""

import requests
import time

def test_cv_formatting():
    """Test the CV formatting changes"""
    
    base_url = "http://localhost:8081"
    
    print("🧪 Testing CV Formatting Changes")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Backend is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it first.")
        return False
    
    # Test 2: Check current CV formatting
    try:
        response = requests.get(f"{base_url}/cv/current/")
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            print(f"✅ CV content retrieved successfully")
            print(f"   Content length: {len(content)} characters")
            
            # Check if emoji icons are removed
            if '📋' in content:
                print("❌ Emoji icons still present in content")
            else:
                print("✅ Emoji icons removed from content")
            
            # Check if underlines are removed
            if '─' in content:
                print("❌ Underlines still present in content")
            else:
                print("✅ Underlines removed from content")
            
            # Show first few lines
            lines = content.split('\n')[:10]
            print("\n📋 First 10 lines of formatted content:")
            for i, line in enumerate(lines, 1):
                print(f"   {i:2d}: {line}")
                
        else:
            print(f"⚠️ No CV found (status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error testing CV formatting: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ CV formatting test completed!")
    return True

if __name__ == "__main__":
    test_cv_formatting() 