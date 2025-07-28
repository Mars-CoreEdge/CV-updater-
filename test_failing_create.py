#!/usr/bin/env python3
"""
Test script for FAILING CREATE operations only
Shows detailed debug output from backend
"""

import requests
import time
import json

def test_failing_create_operations():
    """Test only the failing CREATE operations with detailed debug output"""
    
    base_url = "http://localhost:8081"
    
    # Test messages for FAILING CREATE operations
    failing_create_tests = [
        ("OBJECTIVE_ADD", "Add my objective: To become a senior software engineer in a leading tech company"),
        ("VOLUNTEER_ADD", "Add my volunteer work: Disaster relief coordinator"),
        ("INTEREST_ADD", "Add my interest: Playing guitar, mountain biking"),
        ("REFERENCE_ADD", "Add my reference: John Smith, Senior Manager at TechCorp")
    ]
    
    print("🧪 Testing FAILING CREATE Operations Only")
    print("=" * 60)
    print("Make sure the backend is running on http://localhost:8081")
    print("Backend debug output will show below each test:")
    print()
    
    # First upload a test CV
    print("📤 Uploading test CV...")
    test_cv_content = """JOHN DOE
Software Engineer
john.doe@email.com
+1 (555) 123-4567
LinkedIn: linkedin.com/in/johndoe

WORK EXPERIENCE
Senior Software Engineer at TechCorp (2022-Present)
• Led development of microservices architecture

EDUCATION
Bachelor of Science in Computer Science
University of Technology (2018-2022)"""
    
    try:
        files = {'file': ('test_cv.txt', test_cv_content, 'text/plain')}
        response = requests.post(f"{base_url}/upload-cv/", files=files)
        if response.status_code == 200:
            print("✅ Test CV uploaded successfully")
        else:
            print(f"❌ Failed to upload test CV: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error uploading test CV: {e}")
        return
    
    print()
    print("🔧 Testing FAILING CREATE Operations:")
    print("-" * 60)
    
    results = []
    
    for i, (test_name, message) in enumerate(failing_create_tests, 1):
        print(f"\n{i}. Testing {test_name}...")
        print(f"   Message: '{message}'")
        print("   Backend debug output:")
        print("   " + "-" * 50)
        
        try:
            response = requests.post(
                f"{base_url}/chat/",
                json={"message": message},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Check if it's a success response (not help message)
                if "I'm your AI CV Assistant" in response_text:
                    print(f"   ❌ FAILED - Got help message")
                    print(f"   Response: {response_text[:150]}...")
                    results.append((test_name, "FAILED"))
                else:
                    print(f"   ✅ SUCCESS")
                    print(f"   Response: {response_text[:150]}...")
                    results.append((test_name, "SUCCESS"))
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                results.append((test_name, "HTTP_ERROR"))
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append((test_name, "EXCEPTION"))
        
        print("   " + "-" * 50)
        time.sleep(2)  # Longer delay between tests to see debug output
    
    print("\n📊 FAILING CREATE Operations Summary:")
    print("=" * 60)
    
    success_count = 0
    for test_name, status in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if status == "SUCCESS":
            success_count += 1
    
    print(f"\n🎯 Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("🎉 ALL FAILING CREATE OPERATIONS NOW PASSED!")
    else:
        print(f"⚠️  {len(results) - success_count} CREATE operations still failing")
        print("   Check the debug output above to identify the issues")

if __name__ == "__main__":
    test_failing_create_operations() 