#!/usr/bin/env python3
"""
Test script for CREATE operations only
Shows detailed debug output from backend
"""

import requests
import time
import json

def test_create_operations():
    """Test only CREATE operations with detailed debug output"""
    
    base_url = "http://localhost:8081"
    
    # Test messages for CREATE operations
    create_tests = [
        ("OBJECTIVE_ADD", "Add my objective: To become a senior software engineer in a leading tech company"),
        ("CERTIFICATION_ADD", "Add my certification: Microsoft Azure Developer Associate"),
        ("RESEARCH_ADD", "Add my research: Machine Learning Applications in Healthcare"),
        ("ACHIEVEMENT_ADD", "Add my achievement: Employee of the Year 2023"),
        ("LEADERSHIP_ADD", "Add my leadership role: Technical Lead for 10-person team"),
        ("VOLUNTEER_ADD", "Add my volunteer work: Disaster relief coordinator"),
        ("LANGUAGE_ADD", "Add my language: Fluent in Spanish"),
        ("TECHNOLOGY_ADD", "Add my technology: React.js and Node.js"),
        ("INTEREST_ADD", "Add my interest: Playing guitar, mountain biking"),
        ("REFERENCE_ADD", "Add my reference: John Smith, Senior Manager at TechCorp"),
        ("ADDITIONAL_ADD", "Add additional info: Available for remote work")
    ]
    
    print("🧪 Testing CREATE Operations Only")
    print("=" * 50)
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
    print("🔧 Testing CREATE Operations:")
    print("-" * 50)
    
    results = []
    
    for i, (test_name, message) in enumerate(create_tests, 1):
        print(f"\n{i}. Testing {test_name}...")
        print(f"   Message: '{message}'")
        print("   Backend debug output:")
        print("   " + "-" * 40)
        
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
                    print(f"   Response: {response_text[:100]}...")
                    results.append((test_name, "FAILED"))
                else:
                    print(f"   ✅ SUCCESS")
                    print(f"   Response: {response_text[:100]}...")
                    results.append((test_name, "SUCCESS"))
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                results.append((test_name, "HTTP_ERROR"))
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append((test_name, "EXCEPTION"))
        
        print("   " + "-" * 40)
        time.sleep(1)  # Small delay between tests
    
    print("\n📊 CREATE Operations Summary:")
    print("=" * 50)
    
    success_count = 0
    for test_name, status in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"{status_icon} {test_name}: {status}")
        if status == "SUCCESS":
            success_count += 1
    
    print(f"\n🎯 Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("🎉 ALL CREATE OPERATIONS PASSED!")
    else:
        print(f"⚠️  {len(results) - success_count} CREATE operations still failing")
        print("   Check the debug output above to identify the issues")

if __name__ == "__main__":
    test_create_operations() 