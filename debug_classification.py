#!/usr/bin/env python3
"""
Debug classification for failing cases
"""

import requests
import json

def test_specific_classifications():
    """Test specific failing classifications"""
    
    base_url = "http://localhost:8081"
    
    # Test the specific failing messages
    failing_messages = [
        "Add my objective: To become a senior software engineer in a leading tech company",
        "Add my interest: Playing guitar, mountain biking", 
        "Add additional info: Available for remote work",
        "Update my objective to focus on AI development",
        "Change my certification to include AWS Solutions Architect",
        "Modify my research to include blockchain applications",
        "Update my achievement to include Best Developer Award",
        "Change my leadership role to Senior Team Lead",
        "Update my volunteer work to include disaster relief",
        "Change my interests to include rock climbing",
        "Update my references to include current manager",
        "Modify additional info to include travel availability"
    ]
    
    print("🔍 Debugging Classification Issues")
    print("=" * 50)
    
    for i, message in enumerate(failing_messages, 1):
        print(f"\n{i}. Testing: {message}")
        
        try:
            response = requests.post(f"{base_url}/chat/", json={"message": message})
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                if "👋 I'm your AI CV Assistant" in response_text:
                    print(f"   ❌ FAILED - Falling back to help message")
                    print(f"   Response: {response_text[:100]}...")
                elif "✅ Added" in response_text or "✅ Updated" in response_text:
                    print(f"   ✅ SUCCESS - Operation completed")
                else:
                    print(f"   ⚠️ PARTIAL - Unexpected response")
                    print(f"   Response: {response_text[:100]}...")
            else:
                print(f"   ❌ ERROR - Status code: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_specific_classifications() 