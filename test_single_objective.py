#!/usr/bin/env python3
"""
Test single OBJECTIVE_ADD operation to see debug output
"""

import requests
import json

def test_objective_add():
    """Test only OBJECTIVE_ADD operation"""
    
    base_url = "http://localhost:8081"
    
    # Test message for OBJECTIVE_ADD
    message = "Add my objective: To become a senior software engineer in a leading tech company"
    
    print("🧪 Testing OBJECTIVE_ADD Only")
    print("=" * 50)
    print(f"Message: '{message}'")
    print("Check the backend terminal for debug output...")
    print()
    
    try:
        response = requests.post(
            f"{base_url}/chat/",
            json={"message": message},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '')
            
            print("📤 Response received:")
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
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_objective_add() 