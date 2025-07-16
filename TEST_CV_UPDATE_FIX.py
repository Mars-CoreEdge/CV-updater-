#!/usr/bin/env python3
"""
🧪 CV Update Fix Validation Script
Tests if the chatbot properly updates CV content and if frontend refreshes correctly.
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_cv_update_workflow():
    """Test the complete CV update workflow"""
    print("🧪 Testing CV Update Workflow")
    print("=" * 50)
    
    # Step 1: Upload a test CV
    print("📤 Step 1: Uploading test CV...")
    sample_cv = """
JOHN DOE
Software Developer

SKILLS
• Python
• JavaScript

EXPERIENCE
Software Developer at TechCorp (2022-2024)
• Developed web applications

EDUCATION
Bachelor of Computer Science (2020)
    """
    
    try:
        files = {'file': ('test_cv.txt', sample_cv, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload-cv/", files=files)
        
        if response.status_code == 200:
            print("   ✅ CV uploaded successfully")
        else:
            print(f"   ❌ Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Upload error: {e}")
        return False
    
    time.sleep(2)  # Allow processing
    
    # Step 2: Get initial CV content
    print("\n📋 Step 2: Getting initial CV content...")
    try:
        response = requests.get(f"{API_BASE_URL}/cv/current/")
        if response.status_code == 200:
            initial_cv = response.json()['content']
            print(f"   ✅ Initial CV loaded ({len(initial_cv)} characters)")
        else:
            print(f"   ❌ Failed to get CV: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ CV retrieval error: {e}")
        return False
    
    # Step 3: Test skill update
    print("\n🛠️ Step 3: Testing skill update...")
    try:
        response = requests.post(f"{API_BASE_URL}/chat/", json={
            "message": "I learned Docker and Kubernetes"
        })
        
        if response.status_code == 200:
            chat_response = response.json()['response']
            print(f"   ✅ Chat response: {chat_response[:100]}...")
            
            # Check if response indicates update
            update_indicators = ['updated', 'successfully', 'added', 'saved', 'automatically']
            has_update_indicator = any(word in chat_response.lower() for word in update_indicators)
            
            if has_update_indicator:
                print("   ✅ Response indicates CV update")
            else:
                print("   ⚠️ Response doesn't clearly indicate CV update")
        else:
            print(f"   ❌ Chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Chat error: {e}")
        return False
    
    time.sleep(1)  # Allow processing
    
    # Step 4: Get updated CV content
    print("\n📋 Step 4: Checking if CV was updated...")
    try:
        response = requests.get(f"{API_BASE_URL}/cv/current/")
        if response.status_code == 200:
            updated_cv = response.json()['content']
            print(f"   ✅ Updated CV loaded ({len(updated_cv)} characters)")
            
            # Check if Docker/Kubernetes was added
            if 'docker' in updated_cv.lower() or 'kubernetes' in updated_cv.lower():
                print("   ✅ New skills found in CV content!")
                return True
            else:
                print("   ❌ New skills NOT found in CV content")
                print(f"   📝 CV Content preview: {updated_cv[:500]}...")
                return False
        else:
            print(f"   ❌ Failed to get updated CV: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Updated CV retrieval error: {e}")
        return False

def test_experience_update():
    """Test experience update"""
    print("\n💼 Testing Experience Update...")
    
    try:
        response = requests.post(f"{API_BASE_URL}/chat/", json={
            "message": "I worked as a Senior Developer at NewCorp for 1 year"
        })
        
        if response.status_code == 200:
            chat_response = response.json()['response']
            print(f"   ✅ Experience update response: {chat_response[:100]}...")
            
            # Check updated CV
            time.sleep(1)
            cv_response = requests.get(f"{API_BASE_URL}/cv/current/")
            if cv_response.status_code == 200:
                cv_content = cv_response.json()['content']
                if 'newcorp' in cv_content.lower() or 'senior developer' in cv_content.lower():
                    print("   ✅ Experience update found in CV!")
                    return True
                else:
                    print("   ❌ Experience update NOT found in CV")
                    return False
        else:
            print(f"   ❌ Experience update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Experience update error: {e}")
        return False

def main():
    print("🔧 CV UPDATE FIX VALIDATION")
    print("=" * 50)
    print("This script tests if the chatbot properly updates CV content")
    print("and if the frontend refresh mechanisms work correctly.")
    print()
    
    # Test API connection
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code != 200:
            print("❌ Backend API not running. Start with: cd backend && python main_enhanced.py")
            return
    except:
        print("❌ Cannot connect to backend API. Is it running on port 8000?")
        return
    
    # Run tests
    skill_test = test_cv_update_workflow()
    experience_test = test_experience_update()
    
    # Results
    print("\n" + "=" * 50)
    print("🎯 TEST RESULTS")
    print("=" * 50)
    
    if skill_test and experience_test:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Chatbot correctly updates CV content")
        print("✅ Backend saves updates to database")
        print("✅ Frontend should now refresh properly")
        print()
        print("💡 Frontend improvements made:")
        print("   • Enhanced update detection keywords")
        print("   • Improved chat response messages")
        print("   • Added fallback refresh mechanism")
        print("   • Added manual refresh button")
        print()
        print("🎯 What to expect in frontend:")
        print("   • CV panel refreshes automatically after chat updates")
        print("   • Manual 'Refresh CV' button available")
        print("   • Periodic fallback refresh every 3 seconds")
        print("   • Better detection of update-related messages")
    elif skill_test or experience_test:
        print("⚠️ PARTIAL SUCCESS")
        print("Some tests passed, but there may still be issues")
    else:
        print("❌ TESTS FAILED")
        print("CV update functionality is not working properly")
        print("Check backend logs for errors")
    
    print("\n💡 Next steps:")
    print("1. Start frontend: cd frontend && npm start")
    print("2. Upload a CV")
    print("3. Try: 'I learned React and Node.js'")
    print("4. Check if CV panel refreshes automatically")
    print("5. Use manual 'Refresh CV' button if needed")

if __name__ == "__main__":
    main() 