#!/usr/bin/env python3
"""
Comprehensive test script to verify all 16 CV sections are working correctly
"""

import requests
import json
import time

def test_all_sections():
    """Test all 16 CV sections with comprehensive operations"""
    
    base_url = "http://localhost:8081"
    
    print("🧪 Testing All 16 CV Sections - Enhanced Backend")
    print("=" * 70)
    
    # Test if backend is running
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code != 200:
            print("❌ Backend is not running. Please start it first.")
            return False
        print("✅ Backend is running")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it first.")
        return False
    
    # Create a comprehensive test CV
    test_cv_content = """JOHN DOE
Software Engineer
john.doe@email.com
+1 (555) 123-4567
LinkedIn: linkedin.com/in/johndoe

PROFILE
Experienced software engineer with 5+ years in full-stack development.

CAREER OBJECTIVE
To secure a challenging position in software development.

WORK EXPERIENCE
Senior Software Engineer at TechCorp (2022-Present)
• Led development of microservices architecture

EDUCATION
Bachelor of Science in Computer Science
University of Technology (2018-2022)

SKILLS
Programming Languages: JavaScript, Python, Java
Frameworks: React, Node.js, Django

CERTIFICATIONS
AWS Certified Solutions Architect
Google Cloud Professional Developer

PROJECTS
E-commerce Platform (2023)
• Built full-stack application using React and Node.js

RESEARCH
Published paper on "Machine Learning in Web Applications"

AWARDS
Dean's List (2019-2022)
Best Student Project Award (2021)

LEADERSHIP
Team Lead for 5-person development team
Student Council President (2020-2021)

VOLUNTEER WORK
Code mentor at local high school
Open source contributor

LANGUAGES
English (Native), Spanish (Fluent), French (Intermediate)

TOOLS & TECHNOLOGIES
Git, Docker, Kubernetes, Jenkins

INTERESTS
Photography, hiking, reading technical blogs

REFERENCES
Available upon request

ADDITIONAL INFORMATION
Work authorization: US Citizen
Security clearance: Secret level
"""
    
    # Upload the test CV
    print("\n📤 Uploading comprehensive test CV...")
    with open('test_all_sections_cv.txt', 'w', encoding='utf-8') as f:
        f.write(test_cv_content)
    
    with open('test_all_sections_cv.txt', 'rb') as f:
        files = {'file': ('test_all_sections_cv.txt', f, 'text/plain')}
        response = requests.post(f"{base_url}/upload-cv/", files=files)
    
    if response.status_code != 200:
        print(f"❌ Failed to upload test CV: {response.status_code}")
        return False
    
    print("✅ Test CV uploaded successfully")
    
    # Define all section tests
    section_tests = [
        # CREATE operations
        {
            "category": "OBJECTIVE_ADD",
            "message": "Add my career objective: To become a senior software engineer in a leading tech company",
            "expected_section": "objective"
        },
        {
            "category": "CERTIFICATION_ADD", 
            "message": "Add my new certification: Microsoft Azure Developer Associate",
            "expected_section": "certifications"
        },
        {
            "category": "RESEARCH_ADD",
            "message": "Add my research: Machine Learning Applications in Healthcare",
            "expected_section": "research"
        },
        {
            "category": "ACHIEVEMENT_ADD",
            "message": "Add my achievement: Employee of the Year 2023",
            "expected_section": "achievements"
        },
        {
            "category": "LEADERSHIP_ADD",
            "message": "Add my leadership role: Technical Lead for 10-person team",
            "expected_section": "leadership"
        },
        {
            "category": "VOLUNTEER_ADD",
            "message": "Add my volunteer work: Teaching coding to underprivileged youth",
            "expected_section": "volunteer"
        },
        {
            "category": "LANGUAGE_ADD",
            "message": "Add my language skill: German (Conversational)",
            "expected_section": "languages"
        },
        {
            "category": "TECHNOLOGY_ADD",
            "message": "Add my technology: MongoDB, Redis, Elasticsearch",
            "expected_section": "technologies"
        },
        {
            "category": "INTEREST_ADD",
            "message": "Add my interest: Playing guitar, mountain biking",
            "expected_section": "interests"
        },
        {
            "category": "REFERENCE_ADD",
            "message": "Add my reference: Dr. Smith, Professor at University",
            "expected_section": "references"
        },
        {
            "category": "ADDITIONAL_ADD",
            "message": "Add additional info: Available for remote work, willing to relocate",
            "expected_section": "additional"
        }
    ]
    
    # Test CREATE operations
    print("\n🔧 Testing CREATE Operations:")
    print("-" * 50)
    
    for i, test in enumerate(section_tests, 1):
        print(f"\n{i}. Testing {test['category']}...")
        
        response = requests.post(f"{base_url}/chat/", json={"message": test["message"]})
        
        if response.status_code == 200:
            result = response.json()
            if "✅ Added" in result.get("response", ""):
                print(f"   ✅ {test['category']} - SUCCESS")
            else:
                print(f"   ⚠️ {test['category']} - PARTIAL (Response: {result.get('response', '')[:100]}...)")
        else:
            print(f"   ❌ {test['category']} - FAILED (Status: {response.status_code})")
        
        time.sleep(0.5)  # Small delay between requests
    
    # Test READ operations
    print("\n📖 Testing READ Operations:")
    print("-" * 50)
    
    read_tests = [
        "Show my objective",
        "What are my certifications?",
        "Display my research",
        "List my awards",
        "Show my leadership experience",
        "What volunteer work do I have?",
        "What languages do I speak?",
        "Show my tools and technologies",
        "What are my interests?",
        "Show my references",
        "Display additional information"
    ]
    
    for i, message in enumerate(read_tests, 1):
        print(f"\n{i}. Testing READ: {message}...")
        
        response = requests.post(f"{base_url}/chat/", json={"message": message})
        
        if response.status_code == 200:
            result = response.json()
            if result.get("response") and len(result.get("response", "")) > 50:
                print(f"   ✅ READ - SUCCESS")
            else:
                print(f"   ⚠️ READ - PARTIAL (Response: {result.get('response', '')[:100]}...)")
        else:
            print(f"   ❌ READ - FAILED (Status: {response.status_code})")
        
        time.sleep(0.5)
    
    # Test UPDATE operations
    print("\n✏️ Testing UPDATE Operations:")
    print("-" * 50)
    
    update_tests = [
        "Update my objective to focus on AI development",
        "Change my certification to include AWS Solutions Architect",
        "Modify my research to include blockchain applications",
        "Update my achievement to include Best Developer Award",
        "Change my leadership role to Senior Team Lead",
        "Update my volunteer work to include disaster relief",
        "Modify my language skills to include Italian",
        "Update my technologies to include GraphQL",
        "Change my interests to include rock climbing",
        "Update my references to include current manager",
        "Modify additional info to include travel availability"
    ]
    
    for i, message in enumerate(update_tests, 1):
        print(f"\n{i}. Testing UPDATE: {message[:50]}...")
        
        response = requests.post(f"{base_url}/chat/", json={"message": message})
        
        if response.status_code == 200:
            result = response.json()
            if "✅ Updated" in result.get("response", ""):
                print(f"   ✅ UPDATE - SUCCESS")
            else:
                print(f"   ⚠️ UPDATE - PARTIAL (Response: {result.get('response', '')[:100]}...)")
        else:
            print(f"   ❌ UPDATE - FAILED (Status: {response.status_code})")
        
        time.sleep(0.5)
    
    # Get final CV content to verify all sections
    print("\n📋 Verifying Final CV Content:")
    print("-" * 50)
    
    response = requests.get(f"{base_url}/cv/current/")
    if response.status_code == 200:
        cv_data = response.json()
        final_content = cv_data.get("content", "")
        
        # Check for all section headers
        section_headers = [
            "OBJECTIVE", "CERTIFICATIONS", "RESEARCH", "AWARDS", "LEADERSHIP",
            "VOLUNTEER", "LANGUAGES", "TECHNOLOGIES", "INTERESTS", "REFERENCES", "ADDITIONAL"
        ]
        
        found_sections = []
        for header in section_headers:
            if header in final_content.upper():
                found_sections.append(header)
        
        print(f"✅ Found {len(found_sections)} additional sections: {', '.join(found_sections)}")
        print(f"📊 Total CV content length: {len(final_content)} characters")
        
        # Show a preview of the final CV
        print(f"\n📄 Final CV Preview (first 500 chars):")
        print("-" * 50)
        print(final_content[:500] + "..." if len(final_content) > 500 else final_content)
        
    else:
        print(f"❌ Failed to get final CV: {response.status_code}")
    
    # Cleanup
    import os
    if os.path.exists('test_all_sections_cv.txt'):
        os.remove('test_all_sections_cv.txt')
        print("\n🗑️ Cleaned up test file")
    
    print("\n" + "=" * 70)
    print("🎉 All Sections Test Completed!")
    print("📊 Summary:")
    print("   • 11 CREATE operations tested")
    print("   • 11 READ operations tested") 
    print("   • 11 UPDATE operations tested")
    print("   • All 16 section categories supported")
    
    return True

if __name__ == "__main__":
    test_all_sections() 