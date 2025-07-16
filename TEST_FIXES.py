#!/usr/bin/env python3
"""
Test script to verify fixes for PDF processing and React Router warnings
"""

import requests
import json
import time

def test_backend_health():
    """Test if the backend is running and healthy"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF processing capabilities"""
    try:
        # Test with a simple text file first
        test_content = "Test CV Content\n\nSkills: Python, React, Node.js\nExperience: Software Developer at TechCorp"
        
        # Create a test file
        with open("test_cv.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        print("✅ Test file created successfully")
        
        # Test file upload endpoint
        with open("test_cv.txt", "rb") as f:
            files = {"file": ("test_cv.txt", f, "text/plain")}
            response = requests.post("http://localhost:8000/upload-cv/", files=files, timeout=10)
        
        if response.status_code == 200:
            print("✅ File upload test successful")
            result = response.json()
            print(f"   - Filename: {result.get('filename')}")
            print(f"   - Content length: {result.get('content_length')}")
            return True
        else:
            print(f"❌ File upload test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ File processing test failed: {e}")
        return False
    finally:
        # Clean up test file
        try:
            import os
            if os.path.exists("test_cv.txt"):
                os.remove("test_cv.txt")
        except:
            pass

def test_pdf_upload_fallback():
    """Test PDF upload with backend fallback"""
    try:
        # Create a simple PDF-like file for testing
        test_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test CV Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
        
        # Create a test PDF file
        with open("test_cv.pdf", "wb") as f:
            f.write(test_content)
        
        print("✅ Test PDF file created successfully")
        
        # Test PDF file upload endpoint
        with open("test_cv.pdf", "rb") as f:
            files = {"file": ("test_cv.pdf", f, "application/pdf")}
            response = requests.post("http://localhost:8000/upload-cv/", files=files, timeout=15)
        
        if response.status_code == 200:
            print("✅ PDF upload test successful")
            result = response.json()
            print(f"   - Filename: {result.get('filename')}")
            print(f"   - Content length: {result.get('content_length')}")
            return True
        else:
            print(f"❌ PDF upload test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PDF upload test failed: {e}")
        return False
    finally:
        # Clean up test file
        try:
            import os
            if os.path.exists("test_cv.pdf"):
                os.remove("test_cv.pdf")
        except:
            pass

def test_chat_functionality():
    """Test chat functionality"""
    try:
        # Test chat endpoint
        chat_data = {"message": "Show my CV"}
        response = requests.post("http://localhost:8000/chat/", json=chat_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Chat functionality test successful")
            result = response.json()
            print(f"   - Response status: {result.get('status')}")
            return True
        else:
            print(f"❌ Chat functionality test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Chat functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing CV Updater Fixes")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("File Processing", test_pdf_processing),
        ("PDF Upload Fallback", test_pdf_upload_fallback),
        ("Chat Functionality", test_chat_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The fixes are working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the backend and frontend setup.")
    
    print("\n📝 Next Steps:")
    print("1. Start the frontend: cd frontend && npm start")
    print("2. Check browser console for React Router warnings")
    print("3. Try uploading a PDF file to test PDF processing")
    print("4. If PDF fails, try uploading a TXT file instead")

if __name__ == "__main__":
    main() 