#!/usr/bin/env python3
"""
🧪 Comprehensive Test for All CV Sections
Tests if content is correctly classified and added to the right sections
"""

import requests
import json
import time

# Test data for each section
test_cases = [
    # Education tests
    {
        "section": "education",
        "prompts": [
            "I have done MSCS from NUST",
            "Bachelor's degree in Computer Science from MIT",
            "Master of Science in Data Science from Stanford University"
        ],
        "expected_content": ["Mscs From Nust", "Bachelor'S Degree In Computer Science From Mit", "Master Of Science In Data Science From Stanford University"]
    },
    
    # Experience tests
    {
        "section": "experience", 
        "prompts": [
            "I worked as a Software Engineer at Google",
            "Senior Developer at Microsoft for 3 years",
            "Full Stack Developer at Amazon Web Services"
        ],
        "expected_content": ["Software Engineer At Google", "Senior Developer At Microsoft", "Full Stack Developer At Amazon Web Services"]
    },
    
    # Skills tests
    {
        "section": "skills",
        "prompts": [
            "I am skilled in Python, JavaScript, and C++",
            "Proficient in React, Node.js, and MongoDB",
            "Technologies: AWS, Docker, Kubernetes"
        ],
        "expected_content": ["Python, Javascript, And C++", "React, Node.Js, And Mongodb", "Aws, Docker, Kubernetes"]
    },
    
    # Certifications tests
    {
        "section": "certifications",
        "prompts": [
            "AWS Certified Solutions Architect",
            "Completed certification in Google Cloud Platform",
            "Microsoft Azure certification"
        ],
        "expected_content": ["Aws Certified Solutions Architect", "Google Cloud Platform", "Microsoft Azure Certification"]
    },
    
    # Projects tests
    {
        "section": "projects",
        "prompts": [
            "Built a React e-commerce website",
            "Developed a machine learning project for image recognition",
            "Created a mobile app using React Native"
        ],
        "expected_content": ["React E-Commerce Website", "Machine Learning Project For Image Recognition", "Mobile App Using React Native"]
    },
    
    # Research tests
    {
        "section": "research",
        "prompts": [
            "Published research paper on AI ethics",
            "Conducted study on blockchain technology",
            "Thesis on computer vision applications"
        ],
        "expected_content": ["Research Paper On Ai Ethics", "Study On Blockchain Technology", "Thesis On Computer Vision Applications"]
    },
    
    # Achievements tests
    {
        "section": "achievements",
        "prompts": [
            "Received Best Developer Award",
            "Won hackathon competition",
            "Earned scholarship for academic excellence"
        ],
        "expected_content": ["Best Developer Award", "Hackathon Competition", "Scholarship For Academic Excellence"]
    },
    
    # Leadership tests
    {
        "section": "leadership",
        "prompts": [
            "Led a team of 10 developers",
            "Managed software development projects",
            "Supervised junior developers"
        ],
        "expected_content": ["Team Of 10 Developers", "Software Development Projects", "Junior Developers"]
    },
    
    # Volunteer tests
    {
        "section": "volunteer",
        "prompts": [
            "Volunteered at local coding bootcamp",
            "Community service at tech education center",
            "Charity work for digital literacy"
        ],
        "expected_content": ["Local Coding Bootcamp", "Tech Education Center", "Digital Literacy"]
    },
    
    # Languages tests
    {
        "section": "languages",
        "prompts": [
            "Speak English, Spanish, and French",
            "Fluent in German and Italian",
            "Bilingual in English and Chinese"
        ],
        "expected_content": ["English, Spanish, And French", "German And Italian", "English And Chinese"]
    },
    
    # Tools tests
    {
        "section": "tools",
        "prompts": [
            "Proficient with Git, Docker, and Jenkins",
            "Skilled in Jira, Confluence, and Slack",
            "Tools: VS Code, Postman, Figma"
        ],
        "expected_content": ["Git, Docker, And Jenkins", "Jira, Confluence, And Slack", "Vs Code, Postman, Figma"]
    },
    
    # Hobbies tests
    {
        "section": "hobbies",
        "prompts": [
            "Hobbies: coding, reading, hiking",
            "Enjoy playing guitar and photography",
            "Passionate about chess and cooking"
        ],
        "expected_content": ["Coding, Reading, Hiking", "Playing Guitar And Photography", "Chess And Cooking"]
    },
    
    # References tests
    {
        "section": "references",
        "prompts": [
            "References available upon request",
            "Contact references from previous employers",
            "Professional references from Google and Microsoft"
        ],
        "expected_content": ["Available Upon Request", "From Previous Employers", "From Google And Microsoft"]
    },
    
    # Additional tests
    {
        "section": "additional",
        "prompts": [
            "Additional information: Work authorization in US",
            "Miscellaneous: Open source contributor",
            "Other details: Available for remote work"
        ],
        "expected_content": ["Work Authorization In Us", "Open Source Contributor", "Available For Remote Work"]
    }
]

def test_section_classification():
    """Test if content is correctly classified into the right sections"""
    
    print("🧪 Comprehensive CV Section Classification Test")
    print("=" * 70)
    
    API_BASE_URL = "http://localhost:8081"
    
    # First, check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/test", timeout=5)
        if response.status_code != 200:
            print("❌ Backend is not responding properly")
            return
        print("✅ Backend is running")
    except requests.exceptions.RequestException:
        print("❌ Backend is not running. Please start the backend first.")
        return
    
    total_tests = 0
    passed_tests = 0
    
    for section_test in test_cases:
        section_name = section_test["section"]
        prompts = section_test["prompts"]
        expected_contents = section_test["expected_content"]
        
        print(f"\n📋 Testing {section_name.upper()} Section:")
        print("-" * 50)
        
        for i, (prompt, expected_content) in enumerate(zip(prompts, expected_contents)):
            total_tests += 1
            
            print(f"\n{i+1}. Testing: '{prompt}'")
            print(f"   Expected: {section_name} → '{expected_content}'")
            
            try:
                # Send chat request
                response = requests.post(
                    f"{API_BASE_URL}/chat/",
                    json={"message": prompt},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    # Check if the response indicates the correct section
                    section_correct = False
                    content_found = False
                    
                    # Check for section indicators in response
                    section_indicators = {
                        "education": ["education", "academic", "degree", "university"],
                        "experience": ["experience", "worked", "job", "position"],
                        "skills": ["skills", "skilled", "technologies"],
                        "certifications": ["certification", "certified", "license"],
                        "projects": ["project", "built", "developed"],
                        "research": ["research", "paper", "study", "thesis"],
                        "achievements": ["achievement", "award", "honor"],
                        "leadership": ["leadership", "led", "managed"],
                        "volunteer": ["volunteer", "community", "charity"],
                        "languages": ["language", "speak", "fluent"],
                        "tools": ["tools", "software", "platforms"],
                        "hobbies": ["hobby", "interest", "enjoy"],
                        "references": ["reference", "contact", "available"],
                        "additional": ["additional", "miscellaneous", "other"]
                    }
                    
                    response_lower = response_text.lower()
                    expected_indicators = section_indicators.get(section_name, [])
                    
                    for indicator in expected_indicators:
                        if indicator in response_lower:
                            section_correct = True
                            break
                    
                    # Check if expected content is mentioned
                    if expected_content.lower() in response_lower:
                        content_found = True
                    
                    print(f"   Response: {response_text[:100]}...")
                    
                    if section_correct and content_found:
                        print(f"   ✅ PASS - Correctly classified as {section_name}")
                        passed_tests += 1
                    else:
                        print(f"   ❌ FAIL")
                        if not section_correct:
                            print(f"      Section mismatch: Expected {section_name}, response doesn't indicate correct section")
                        if not content_found:
                            print(f"      Content not found: Expected '{expected_content}' in response")
                
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request failed: {e}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 Final Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! All sections are working correctly!")
    elif passed_tests >= total_tests * 0.8:
        print("👍 Most tests passed! Sections are working well with minor issues.")
    else:
        print("⚠️  Many tests failed. There are significant issues with section classification.")

def test_specific_issues():
    """Test specific problematic cases"""
    
    print("\n🔍 Testing Specific Problematic Cases")
    print("=" * 50)
    
    API_BASE_URL = "http://localhost:8081"
    
    # Test cases that were previously problematic
    problematic_cases = [
        ("chinese language", "languages"),
        ("I speak Chinese", "languages"),
        ("Python programming", "skills"),
        ("JavaScript development", "skills"),
        ("AWS certification", "certifications"),
        ("React project", "projects"),
        ("Research paper", "research"),
        ("Team leadership", "leadership"),
        ("Volunteer work", "volunteer"),
        ("Git tools", "tools"),
        ("Hobby: reading", "hobbies"),
        ("References available", "references")
    ]
    
    for prompt, expected_section in problematic_cases:
        print(f"\nTesting: '{prompt}' → Expected: {expected_section}")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/",
                json={"message": prompt},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                
                # Check if response mentions the correct section
                response_lower = response_text.lower()
                section_mentioned = expected_section in response_lower
                
                if section_mentioned:
                    print(f"   ✅ Correctly classified as {expected_section}")
                else:
                    print(f"   ❌ Incorrectly classified (expected {expected_section})")
                    print(f"   Response: {response_text[:100]}...")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_section_classification()
    test_specific_issues() 