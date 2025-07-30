#!/usr/bin/env python3
"""
🧪 Test Contact Information Fix
Tests if contact information is properly added to the CV
"""

import requests
import time

API_BASE_URL = "http://localhost:8081"

def test_contact_functionality():
    """Test contact information functionality"""
    
    print("🧪 Testing Contact Information Fix")
    print("=" * 50)
    
    # Test cases for contact information
    test_cases = [
        "My email is john.doe@example.com",
        "Phone: +1-555-123-4567",
        "LinkedIn: linkedin.com/in/johndoe",
        "Address: 123 Main Street, New York, NY 10001",
        "Contact me at john.doe@example.com"
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{message}'")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/",
                json={"message": message},
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                response_text = response_data.get('response', '')
                
                print(f"   Response: {response_text[:200]}...")
                
                # Check if the response indicates contact section
                if "contact" in response_text.lower():
                    print(f"   ✅ PASS - Contact information added successfully")
                else:
                    print(f"   ❌ FAIL - Contact information not detected")
            else:
                print(f"   ❌ ERROR - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
        
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print("Contact Information Test Complete")

if __name__ == "__main__":
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            test_contact_functionality()
        else:
            print("❌ Backend is not responding properly")
    except Exception as e:
        print(f"❌ Backend is not running: {e}")
        print("Please start the backend first: cd backend && python main_enhanced.py") 