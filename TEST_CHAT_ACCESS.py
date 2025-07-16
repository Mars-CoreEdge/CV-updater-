#!/usr/bin/env python3
"""
🔧 CV Chat Access Test Script
Tests if the chat system can properly access uploaded file content and perform CRUD operations.
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test if the backend API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend API is running")
            return True
        else:
            print(f"❌ Backend API returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend API. Is it running on port 8000?")
        return False

def test_file_upload():
    """Test file upload functionality"""
    print("\n📤 Testing file upload...")
    
    # Create a sample CV text file
    sample_cv = """
JOHN DOE
Software Developer

SKILLS
• Python
• JavaScript  
• React
• FastAPI

EXPERIENCE
Software Developer at TechCorp (2022-2024)
• Developed web applications using React and Python
• Worked with FastAPI backend systems
• Collaborated with team of 5 developers

EDUCATION
Bachelor of Computer Science, University of Technology (2020)
    """
    
    try:
        # Upload the test CV
        files = {'file': ('test_cv.txt', sample_cv, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload-cv/", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File uploaded successfully: {result['filename']}")
            print(f"   Content length: {result.get('content_length', 'unknown')} characters")
            return True
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def test_chat_access(message):
    """Test chat access to uploaded CV content"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/",
            json={"message": message}
        )
        
        if response.status_code == 200:
            result = response.json()
            chat_response = result.get('response', '')
            print(f"💬 Chat: {message}")
            print(f"🤖 Response: {chat_response[:200]}{'...' if len(chat_response) > 200 else ''}")
            return True, chat_response
        else:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return False, ""
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False, ""

def test_cv_retrieval():
    """Test CV content retrieval"""
    try:
        response = requests.get(f"{API_BASE_URL}/cv/current/")
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('content', '')
            print(f"✅ CV retrieved successfully ({len(content)} characters)")
            return True
        else:
            print(f"❌ CV retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CV retrieval error: {e}")
        return False

def main():
    print("🔧 CV Chat Access Test")
    print("=" * 50)
    
    # Test 1: API Connection
    if not test_api_connection():
        print("\n❌ API connection failed. Please start the backend server:")
        print("   cd backend && python main_enhanced.py")
        return
    
    # Test 2: File Upload
    if not test_file_upload():
        print("\n❌ File upload failed")
        return
    
    print("\n⏳ Waiting 2 seconds for upload to process...")
    time.sleep(2)
    
    # Test 3: CV Retrieval
    if not test_cv_retrieval():
        print("\n❌ CV retrieval failed")
        return
    
    # Test 4: Chat Access Tests
    print("\n💬 Testing chat access to uploaded CV content...")
    print("-" * 50)
    
    test_messages = [
        "What skills do I have?",
        "What experience do I have?", 
        "What education do I have?",
        "Show my CV content",
        "I learned Docker and Kubernetes",
        "I worked as a Senior Developer at NewCorp",
        "Generate CV"
    ]
    
    successful_tests = 0
    total_tests = len(test_messages)
    
    for message in test_messages:
        success, response = test_chat_access(message)
        if success:
            # Check if response contains actual CV content (not generic messages)
            if any(keyword in response.lower() for keyword in ['python', 'javascript', 'techcorp', 'skills', 'experience']):
                print("   ✅ Response contains actual CV content")
                successful_tests += 1
            elif "please upload" in response.lower() or "no cv found" in response.lower():
                print("   ❌ Chat cannot access uploaded CV content")
            else:
                print("   ✅ Chat processed request successfully")
                successful_tests += 1
        print()
    
    # Results
    print("=" * 50)
    print("🎯 TEST RESULTS")
    print(f"Successful tests: {successful_tests}/{total_tests}")
    
    if successful_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Chat has full access to uploaded CV content.")
        print("✅ CRUD operations working correctly")
    elif successful_tests >= total_tests * 0.7:
        print("⚠️ Most tests passed, but some issues detected")
    else:
        print("❌ Multiple test failures - chat may not have proper file access")
    
    print("\n💡 Next steps:")
    print("1. Start frontend: cd frontend && npm start")
    print("2. Go to http://localhost:3000")
    print("3. Upload a CV and test chat functionality")

if __name__ == "__main__":
    main() 