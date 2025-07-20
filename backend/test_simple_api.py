#!/usr/bin/env python3
"""
Simple API test for intelligent content extraction
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081"

def test_simple_messages():
    """Test simple messages with the API"""
    print("🧠 Testing Simple Messages with API")
    print("=" * 50)
    
    # Simple test messages
    test_messages = [
        "Machine Learning",
        "Led a team of developers", 
        "Bachelor's in Computer Science",
        "Built a web application"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        
        chat_data = {"message": message}
        
        try:
            response = requests.post(f"{BASE_URL}/chat/", json=chat_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                print(f"   ✅ API Response: {response_text[:150]}...")
            else:
                print(f"   ❌ API failed: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            print("   ❌ Connection failed - server not running")
            break
        except Exception as e:
            print(f"   ❌ API request failed: {e}")
        
        time.sleep(1)

def main():
    print("🚀 Simple API Test for Intelligent Extraction")
    print("=" * 50)
    
    test_simple_messages()
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    main() 