#!/usr/bin/env python3
"""
🧪 Test All CV Sections Fix
Tests if all CV sections are properly added to the PDF
"""

import requests
import time

API_BASE_URL = "http://localhost:8081"

def test_all_sections():
    """Test all CV sections functionality"""
    
    print("🧪 Testing All CV Sections Fix")
    print("=" * 60)
    
    # Test cases for all sections
    test_cases = {
        "contact": [
            "My email is john.doe@example.com",
            "Phone: +1-555-123-4567"
        ],
        "objective": [
            "My career objective is to become a senior software engineer",
            "I aim to lead development teams and deliver innovative solutions"
        ],
        "experience": [
            "I worked as a Software Engineer at Google for 5 years",
            "Senior Developer at Microsoft from 2020 to 2023"
        ],
        "education": [
            "Bachelor's degree in Computer Science from MIT",
            "Master of Science in Data Science from Stanford"
        ],
        "skills": [
            "I am skilled in Python, JavaScript, and C++",
            "Proficient in React, Node.js, and MongoDB"
        ],
        "certifications": [
            "AWS Certified Solutions Architect",
            "Microsoft Azure certification"
        ],
        "projects": [
            "Built a React e-commerce website",
            "Developed a machine learning project for image recognition"
        ],
        "research": [
            "Published research paper on AI ethics",
            "Conducted study on blockchain technology"
        ],
        "achievements": [
            "Received Best Developer Award",
            "Won hackathon competition"
        ],
        "leadership": [
            "Led a team of 10 developers",
            "Managed software development projects"
        ],
        "volunteer": [
            "Volunteered at local coding bootcamp",
            "Community service at tech education center"
        ],
        "languages": [
            "Speak English, Spanish, and French",
            "Fluent in German and Italian"
        ],
        "technologies": [
            "Proficient with Git, Docker, and Jenkins",
            "Skilled in Jira, Confluence, and Slack"
        ],
        "interests": [
            "Hobbies: coding, reading, hiking",
            "Enjoy playing guitar and photography"
        ],
        "references": [
            "References available upon request",
            "Professional references from Google and Microsoft"
        ],
        "additional": [
            "Additional information: Work authorization in US",
            "Miscellaneous: Open source contributor"
        ]
    }
    
    results = {}
    total_tests = 0
    passed_tests = 0
    
    # Test each section
    for section, messages in test_cases.items():
        print(f"\n📋 Testing {section.upper()} Section:")
        print("-" * 50)
        
        section_passed = 0
        section_total = len(messages)
        
        for i, message in enumerate(messages, 1):
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
                    
                    print(f"   Response: {response_text[:150]}...")
                    
                    # Check if the response indicates the correct section
                    if section.lower() in response_text.lower():
                        print(f"   ✅ PASS - Correctly added to {section} section")
                        section_passed += 1
                        passed_tests += 1
                    else:
                        print(f"   ❌ FAIL - Wrong section or no section detected")
                        print(f"   Expected: {section}")
                else:
                    print(f"   ❌ ERROR - HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ ERROR - {str(e)}")
            
            total_tests += 1
            time.sleep(1)  # Small delay between tests
        
        # Section summary
        section_pass_rate = (section_passed / section_total) * 100
        results[section] = {
            'passed': section_passed,
            'total': section_total,
            'pass_rate': section_pass_rate
        }
        
        print(f"\n📊 {section.upper()} Results: {section_passed}/{section_total} ({section_pass_rate:.1f}%)")
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    overall_pass_rate = (passed_tests / total_tests) * 100
    print(f"Overall: {passed_tests}/{total_tests} tests passed ({overall_pass_rate:.1f}%)")
    
    print("\n📋 Section Breakdown:")
    for section, result in results.items():
        status = "✅" if result['pass_rate'] == 100 else "⚠️" if result['pass_rate'] >= 50 else "❌"
        print(f"{status} {section.upper()}: {result['passed']}/{result['total']} ({result['pass_rate']:.1f}%)")
    
    if overall_pass_rate == 100:
        print("\n🎉 SUCCESS! All sections working perfectly!")
    elif overall_pass_rate >= 80:
        print(f"\n👍 Good progress! {overall_pass_rate:.1f}% Pass Rate")
    else:
        print(f"\n⚠️ Needs improvement. {overall_pass_rate:.1f}% Pass Rate")
    
    return overall_pass_rate

if __name__ == "__main__":
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            test_all_sections()
        else:
            print("❌ Backend is not responding properly")
    except Exception as e:
        print(f"❌ Backend is not running: {e}")
        print("Please start the backend first: cd backend && python main_enhanced.py") 