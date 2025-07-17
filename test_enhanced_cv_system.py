#!/usr/bin/env python3
"""
Enhanced CV Processing System Test Script
Tests the robust section detection, content insertion, and PDF generation features.
"""

import requests
import json
import time
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_CV_CONTENT = """Abubakar Mehboob
Full Stack Developer
+92-346-1496202
abubakarmehboob4@gmail.com
Sabzazar, Lahore
www.linkedin.com/in/abubakar4

___________________________ PROFILE SUMMARY ___________________________
Accomplished Full Stack Developer with 1 years of experience contributing to outstanding success in the software development industry. Confident in ability to effectively build responsive web applications and optimize performance for scalability.

___________________________ SKILLS ___________________________
Technical Skills:
React.js | JavaScript | HTML | CSS | Bootstrap | JQuery | FastAPI | Supabase | GitHub | Python | C++

Professional Skills:
Problem Solving | Team Leadership | Data Visualization | Critical Thinking | Decision Making | Presentation Skills

___________________________ WORK EXPERIENCE ___________________________
Full Stack Developer Intern
Code Soft | Internship | February, 2025 – May, 2025
• Assisted in developing and maintaining web applications using React.js, JavaScript, and FastAPI.
• Implemented front-end features and optimized UI for better user experience.
• Worked with back-end APIs and integrated Supabase for data storage and authentication.

___________________________ EDUCATION ___________________________
Bachelor of Computer Science
Graduated in 2024, from University of Engineering and Technology, Lahore

___________________________ PROJECTS ___________________________
Task Management Web Application
March, 2025 – April, 2025
• Developed a web app for creating, updating, and managing tasks with deadlines and status tracking.
• Built the front-end using React.js, JavaScript, HTML, CSS, and Bootstrap for a responsive UI.
• Created REST APIs with FastAPI and integrated Supabase for database and user authentication.
"""

def test_upload_cv():
    """Test CV upload with extracted text"""
    print("🔄 Testing CV upload...")
    
    # Create a test file
    with open("test_cv.txt", "w", encoding="utf-8") as f:
        f.write(TEST_CV_CONTENT)
    
    try:
        with open("test_cv.txt", "rb") as f:
            files = {"file": ("test_cv.txt", f, "text/plain")}
            data = {"extracted_text": TEST_CV_CONTENT}
            
            response = requests.post(f"{API_BASE_URL}/upload-cv/", files=files, data=data)
            
        if response.status_code == 200:
            print("✅ CV upload successful!")
            result = response.json()
            print(f"   Filename: {result.get('filename')}")
            print(f"   Content length: {result.get('content_length')}")
            return True
        else:
            print(f"❌ CV upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CV upload error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists("test_cv.txt"):
            os.remove("test_cv.txt")

def test_section_detection():
    """Test section detection in CV"""
    print("\n🔍 Testing section detection...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/cv/current/")
        
        if response.status_code == 200:
            cv_data = response.json()
            content = cv_data.get('content', '')
            
            # Test education section detection
            if 'EDUCATION' in content.upper():
                print("✅ Education section detected")
            else:
                print("❌ Education section not found")
            
            # Test skills section detection
            if 'SKILLS' in content.upper():
                print("✅ Skills section detected")
            else:
                print("❌ Skills section not found")
            
            # Test experience section detection
            if 'EXPERIENCE' in content.upper():
                print("✅ Experience section detected")
            else:
                print("❌ Experience section not found")
            
            return True
        else:
            print(f"❌ Failed to get CV: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Section detection error: {e}")
        return False

def test_education_update():
    """Test adding content to education section"""
    print("\n📚 Testing education section update...")
    
    test_messages = [
        "Add MSc in Artificial Intelligence at Oxford University to my education",
        "Include PhD in Computer Science from MIT in my education",
        "Add Bachelor of Engineering in Software Engineering from Stanford to my education"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"   Test {i}: {message}")
        
        try:
            response = requests.post(f"{API_BASE_URL}/chat/", json={"message": message})
            
            if response.status_code == 200:
                result = response.json()
                if "✅ Added to education section" in result.get('response', ''):
                    print(f"   ✅ Education update {i} successful")
                else:
                    print(f"   ⚠️ Education update {i} response: {result.get('response', '')[:100]}...")
            else:
                print(f"   ❌ Education update {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Education update {i} error: {e}")
        
        time.sleep(1)  # Small delay between requests

def test_pdf_generation():
    """Test PDF generation"""
    print("\n📄 Testing PDF generation...")
    
    try:
        # Test PDF preview
        response = requests.get(f"{API_BASE_URL}/cv/pdf-preview")
        
        if response.status_code == 200:
            print("✅ PDF preview generation successful")
            
            # Save PDF for inspection
            with open("test_cv_preview.pdf", "wb") as f:
                f.write(response.content)
            print("   📁 PDF saved as 'test_cv_preview.pdf'")
        else:
            print(f"❌ PDF preview generation failed: {response.status_code}")
            return False
            
        # Test PDF download
        response = requests.post(f"{API_BASE_URL}/cv/download")
        
        if response.status_code == 200:
            print("✅ PDF download generation successful")
            
            # Save PDF for inspection
            with open("test_cv_download.pdf", "wb") as f:
                f.write(response.content)
            print("   📁 PDF saved as 'test_cv_download.pdf'")
        else:
            print(f"❌ PDF download generation failed: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return False

def test_real_time_updates():
    """Test real-time CV updates"""
    print("\n🔄 Testing real-time updates...")
    
    try:
        # Get initial CV
        response = requests.get(f"{API_BASE_URL}/cv/current/")
        if response.status_code != 200:
            print("❌ Failed to get initial CV")
            return False
            
        initial_cv = response.json()
        initial_content = initial_cv.get('content', '')
        initial_length = len(initial_content)
        
        print(f"   Initial CV length: {initial_length}")
        
        # Add content
        test_message = "Add certification in AWS Cloud Computing to my skills"
        response = requests.post(f"{API_BASE_URL}/chat/", json={"message": test_message})
        
        if response.status_code == 200:
            # Wait a moment for processing
            time.sleep(2)
            
            # Get updated CV
            response = requests.get(f"{API_BASE_URL}/cv/current/")
            if response.status_code == 200:
                updated_cv = response.json()
                updated_content = updated_cv.get('content', '')
                updated_length = len(updated_content)
                
                print(f"   Updated CV length: {updated_length}")
                
                if updated_length > initial_length:
                    print("✅ Real-time update successful - CV content increased")
                    return True
                else:
                    print("⚠️ Real-time update - CV content unchanged")
                    return False
            else:
                print("❌ Failed to get updated CV")
                return False
        else:
            print(f"❌ Failed to add content: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Real-time update error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced CV Processing System Test Suite")
    print("=" * 50)
    
    tests = [
        ("CV Upload", test_upload_cv),
        ("Section Detection", test_section_detection),
        ("Education Updates", test_education_update),
        ("PDF Generation", test_pdf_generation),
        ("Real-time Updates", test_real_time_updates)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced CV system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    # Cleanup
    for filename in ["test_cv_preview.pdf", "test_cv_download.pdf"]:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    main() 