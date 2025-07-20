#!/usr/bin/env python3
"""
Test script to verify section detection with the demo CV
"""

import requests
import json

BASE_URL = "http://localhost:8081"

def test_section_detection():
    """Test section detection with the current CV"""
    print("🔍 Testing Section Detection")
    print("=" * 50)
    
    # Get current CV
    response = requests.get(f"{BASE_URL}/cv/current/")
    if response.status_code != 200:
        print("❌ Failed to get current CV")
        return
    
    cv_content = response.json().get('content', '')
    print(f"✅ Retrieved CV content ({len(cv_content)} characters)")
    
    # Test each section
    sections_to_test = [
        "contact", "profile", "skills", "experience", 
        "education", "certifications", "projects", 
        "achievements", "languages", "interests"
    ]
    
    for section in sections_to_test:
        print(f"\n📋 Testing section: {section.upper()}")
        
        # Test chat with section-specific query
        chat_data = {
            "message": f"Add a new item to my {section} section"
        }
        
        response = requests.post(f"{BASE_URL}/chat/", json=chat_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Chat response: {result.get('response', '')[:100]}...")
        else:
            print(f"   ❌ Chat failed: {response.text}")
    
    print("\n" + "=" * 50)
    print("✅ Section detection testing completed!")

def test_specific_section_update():
    """Test updating a specific section"""
    print("\n🔄 Testing Specific Section Update")
    print("=" * 50)
    
    # Test adding to skills section
    chat_data = {
        "message": "Add 'Machine Learning' to my skills section"
    }
    
    response = requests.post(f"{BASE_URL}/chat/", json=chat_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Skills update response: {result.get('response', '')}")
        
        # Get updated CV
        cv_response = requests.get(f"{BASE_URL}/cv/current/")
        if cv_response.status_code == 200:
            updated_cv = cv_response.json().get('content', '')
            print(f"✅ Updated CV retrieved ({len(updated_cv)} characters)")
            
            # Check if skills section contains the new item
            if "Machine Learning" in updated_cv:
                print("✅ Successfully added 'Machine Learning' to skills section!")
            else:
                print("❌ 'Machine Learning' not found in updated CV")
        else:
            print(f"❌ Failed to get updated CV: {cv_response.text}")
    else:
        print(f"❌ Skills update failed: {response.text}")

def test_education_section():
    """Test education section specifically"""
    print("\n🎓 Testing Education Section")
    print("=" * 50)
    
    chat_data = {
        "message": "Add 'Master of Science in Computer Science from Stanford University (2020-2022)' to my education section"
    }
    
    response = requests.post(f"{BASE_URL}/chat/", json=chat_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Education update response: {result.get('response', '')}")
        
        # Get updated CV
        cv_response = requests.get(f"{BASE_URL}/cv/current/")
        if cv_response.status_code == 200:
            updated_cv = cv_response.json().get('content', '')
            if "Stanford University" in updated_cv:
                print("✅ Successfully added Stanford education to education section!")
            else:
                print("❌ Stanford education not found in updated CV")
        else:
            print(f"❌ Failed to get updated CV: {cv_response.text}")
    else:
        print(f"❌ Education update failed: {response.text}")

def main():
    print("🚀 CV Section Detection and Update Testing")
    print("=" * 60)
    
    # Test basic section detection
    test_section_detection()
    
    # Test specific section updates
    test_specific_section_update()
    test_education_section()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("🔗 API Documentation: http://localhost:8081/docs")

if __name__ == "__main__":
    main() 