#!/usr/bin/env python3
"""
Test only OBJECTIVE_ADD operation
"""

import requests
import json

def test_objective_only():
    """Test only OBJECTIVE_ADD operation"""
    
    base_url = "http://localhost:8081"
    
    # Test message for OBJECTIVE_ADD
    message = "Add my objective: To become a senior software engineer in a leading tech company"
    
    print("🧪 Testing OBJECTIVE_ADD Only")
    print("=" * 50)
    print(f"Message: '{message}'")
    print()
    
    try:
        response = requests.post(
            f"{base_url}/chat/",
            json={"message": message},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            print("📤 Full Response:")
            print("-" * 40)
            print(response_text)
            print("-" * 40)
            
            # Check if it's a success response (not help message)
            if "I'm your AI CV Assistant" in response_text:
                print("❌ FAILED - Got help message")
            else:
                print("✅ SUCCESS")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_objective_only() 