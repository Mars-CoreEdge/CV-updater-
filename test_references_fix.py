#!/usr/bin/env python3
"""
Test script specifically for REFERENCES section fix.
"""

import requests
import time

API_BASE_URL = "http://localhost:8081"

def test_references_section():
    """Test REFERENCES section specifically"""
    print("🧪 Testing REFERENCES Section Fix")
    print("=" * 50)
    
    test_cases = [
        "References available upon request",
        "Professional references from Google and Microsoft"
    ]
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: '{message}'")
        print("-" * 40)
        
        try:
            # Make API call
            response = requests.post(f"{API_BASE_URL}/chat/", json={"message": message})
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                print(f"Response: {response_text[:200]}...")
                
                # Check if it was added to references section
                if "references" in response_text.lower() and "added" in response_text.lower() and "contact" not in response_text.lower():
                    print("✅ PASS - Correctly added to references section")
                    results.append("PASS")
                    passed_tests += 1
                else:
                    print("❌ FAIL - Wrong section or no section detected")
                    print(f"Expected: references")
                    if "contact" in response_text.lower():
                        print(f"Actually went to: contact section")
                    results.append("FAIL")
            else:
                print(f"❌ API Error: {response.status_code}")
                results.append("ERROR")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append("ERROR")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 REFERENCES TEST RESULTS")
    print("=" * 50)
    
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result == "PASS" else "❌"
        print(f"{status_icon} Test {i}: {result}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 REFERENCES section is now working correctly!")
    else:
        print("⚠️ REFERENCES section still needs attention.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/test")
        if response.status_code == 200:
            print("✅ Backend is running")
            test_references_section()
        else:
            print("❌ Backend is not responding properly")
    except:
        print("❌ Backend is not running. Please start the backend first.") 