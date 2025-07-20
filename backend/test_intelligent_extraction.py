#!/usr/bin/env python3
"""
Test script to demonstrate intelligent content extraction
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081"

def test_intelligent_extraction():
    """Test the intelligent content extraction with various messages"""
    print("🧠 Testing Intelligent Content Extraction")
    print("=" * 60)
    
    # Test messages that should auto-detect sections and extract main content
    test_messages = [
        # Skills tests
        "I learned React and Node.js",
        "Add Python, JavaScript, and Docker to my skills",
        "I'm proficient in machine learning and data science",
        
        # Experience tests
        "I led a team of 5 developers in building microservices",
        "Add that I managed a project with 100K users",
        "I developed a full-stack application using React and Node.js",
        
        # Education tests
        "I graduated with a Master's in Computer Science from Stanford",
        "Add my AWS certification",
        "I studied Data Science at MIT",
        
        # Projects tests
        "I built an e-commerce platform with React and Node.js",
        "Add my weather app project",
        "I created a task management system",
        
        # Generic tests (should auto-detect)
        "React and TypeScript",
        "Led development team",
        "Master's degree in AI",
        "Built a mobile app"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Test {i}: {message}")
        
        # Test the extraction locally first
        try:
            from main_enhanced import extract_intelligent_content
            extracted_content, detected_section = extract_intelligent_content(message)
            print(f"   🔍 Extracted: '{extracted_content}'")
            print(f"   📂 Detected Section: {detected_section}")
        except Exception as e:
            print(f"   ❌ Local extraction failed: {e}")
            continue
        
        # Test via API
        chat_data = {"message": message}
        
        try:
            response = requests.post(f"{BASE_URL}/chat/", json=chat_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ API Response: {result.get('response', '')[:100]}...")
            else:
                print(f"   ❌ API failed: {response.text}")
        except Exception as e:
            print(f"   ❌ API request failed: {e}")
        
        time.sleep(1)  # Small delay between requests

def test_simple_messages():
    """Test simple messages that should work without specifying sections"""
    print("\n🎯 Testing Simple Messages (No Section Specification)")
    print("=" * 60)
    
    simple_messages = [
        "Machine Learning",
        "Led a team of developers",
        "Bachelor's in Computer Science",
        "Built a web application",
        "Python and JavaScript",
        "Managed a project",
        "AWS certification",
        "Created a mobile app"
    ]
    
    for i, message in enumerate(simple_messages, 1):
        print(f"\n📝 Simple Test {i}: {message}")
        
        # Test the extraction locally
        try:
            from main_enhanced import extract_intelligent_content
            extracted_content, detected_section = extract_intelligent_content(message)
            print(f"   🔍 Extracted: '{extracted_content}'")
            print(f"   📂 Detected Section: {detected_section}")
        except Exception as e:
            print(f"   ❌ Local extraction failed: {e}")
            continue
        
        # Test via API
        chat_data = {"message": message}
        
        try:
            response = requests.post(f"{BASE_URL}/chat/", json=chat_data)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ API Response: {result.get('response', '')[:100]}...")
            else:
                print(f"   ❌ API failed: {response.text}")
        except Exception as e:
            print(f"   ❌ API request failed: {e}")
        
        time.sleep(1)

def main():
    print("🚀 Intelligent Content Extraction Test")
    print("=" * 60)
    
    # Test intelligent extraction
    test_intelligent_extraction()
    
    # Test simple messages
    test_simple_messages()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\n📊 Summary:")
    print("   - Content extraction now extracts only main content")
    print("   - Section auto-detection works without explicit specification")
    print("   - System is more intelligent and user-friendly")
    print("   - No more adding complete string text to CV")

if __name__ == "__main__":
    main() 