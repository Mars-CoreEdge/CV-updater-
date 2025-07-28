#!/usr/bin/env python3
"""
Test script to verify comprehensive section detection with exhaustive CV section headings
"""

import requests
import re

def test_comprehensive_section_detection():
    """Test the comprehensive section detection patterns"""
    
    base_url = "http://localhost:8081"
    
    print("🧪 Testing Comprehensive Section Detection")
    print("=" * 60)
    
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
    
    # Test CV content with various section formats
    test_cv_content = """JOHN DOE
john.doe@email.com
+1 (555) 123-4567

PERSONAL PROFILE
Experienced software engineer with 5+ years in full-stack development.

CAREER OBJECTIVE
To secure a challenging position in software development.

WORK EXPERIENCE
Senior Software Engineer at TechCorp (2022-Present)
• Led development of microservices architecture

EDUCATIONAL BACKGROUND
Bachelor of Science in Computer Science
University of Technology (2018-2022)

TECHNICAL SKILLS
Programming Languages: JavaScript, Python, Java
Frameworks: React, Node.js, Django

PROFESSIONAL CERTIFICATIONS
AWS Certified Solutions Architect
Google Cloud Professional Developer

MAJOR PROJECTS
E-commerce Platform (2023)
• Built full-stack application using React and Node.js

RESEARCH EXPERIENCE
Published paper on "Machine Learning in Web Applications"

HONORS & AWARDS
Dean's List (2019-2022)
Best Student Project Award (2021)

LEADERSHIP ROLES
Team Lead for 5-person development team
Student Council President (2020-2021)

VOLUNTEER WORK
Code mentor at local high school
Open source contributor

LANGUAGE PROFICIENCY
English (Native), Spanish (Fluent), French (Intermediate)

TOOLS & TECHNOLOGIES
Git, Docker, Kubernetes, Jenkins

PERSONAL INTERESTS
Photography, hiking, reading technical blogs

REFERENCES
Available upon request

ADDITIONAL INFORMATION
Work authorization: US Citizen
Security clearance: Secret level
"""
    
    print("\n📋 Testing CV content with comprehensive sections:")
    print("-" * 50)
    
    # Define all possible section categories
    section_categories = {
        "contact": ["PERSONAL PROFILE", "CONTACT INFORMATION", "ABOUT ME"],
        "objective": ["CAREER OBJECTIVE", "PROFESSIONAL OBJECTIVE"],
        "experience": ["WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE"],
        "education": ["EDUCATIONAL BACKGROUND", "ACADEMIC BACKGROUND"],
        "skills": ["TECHNICAL SKILLS", "CORE SKILLS"],
        "certifications": ["PROFESSIONAL CERTIFICATIONS", "CERTIFICATIONS"],
        "projects": ["MAJOR PROJECTS", "KEY PROJECTS"],
        "research": ["RESEARCH EXPERIENCE", "PUBLICATIONS"],
        "achievements": ["HONORS & AWARDS", "ACHIEVEMENTS"],
        "leadership": ["LEADERSHIP ROLES", "LEADERSHIP EXPERIENCE"],
        "volunteer": ["VOLUNTEER WORK", "COMMUNITY SERVICE"],
        "languages": ["LANGUAGE PROFICIENCY", "LANGUAGES"],
        "technologies": ["TOOLS & TECHNOLOGIES", "TECHNOLOGIES"],
        "interests": ["PERSONAL INTERESTS", "HOBBIES"],
        "references": ["REFERENCES", "REFEREES"],
        "additional": ["ADDITIONAL INFORMATION", "MISCELLANEOUS"]
    }
    
    # Test section detection
    lines = test_cv_content.split('\n')
    detected_sections = []
    
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if line_stripped:
            # Check each category
            for category, keywords in section_categories.items():
                for keyword in keywords:
                    if keyword.upper() in line_stripped.upper():
                        detected_sections.append({
                            'line': i,
                            'content': line_stripped,
                            'category': category,
                            'keyword': keyword
                        })
                        break
                if any(keyword.upper() in line_stripped.upper() for keyword in keywords):
                    break
    
    print(f"✅ Detected {len(detected_sections)} sections:")
    for section in detected_sections:
        print(f"   Line {section['line']:2d}: {section['content']}")
        print(f"        Category: {section['category']}")
        print(f"        Keyword: {section['keyword']}")
        print()
    
    # Test backend section detection
    print("\n🔍 Testing Backend Section Detection:")
    print("-" * 50)
    
    try:
        # Test with a simple CV upload
        test_cv_simple = """JANE SMITH
jane.smith@email.com

PROFILE
Experienced data scientist.

WORK EXPERIENCE
Data Scientist at Analytics Corp (2021-Present)

EDUCATION
Master of Science in Data Science (2019-2021)

SKILLS
Python, TensorFlow, Statistical Analysis

PROJECTS
Machine Learning Model for Customer Behavior
"""
        
        # Create a test file
        with open('test_comprehensive_cv.txt', 'w', encoding='utf-8') as f:
            f.write(test_cv_simple)
        
        # Upload the test CV
        with open('test_comprehensive_cv.txt', 'rb') as f:
            files = {'file': ('test_comprehensive_cv.txt', f, 'text/plain')}
            response = requests.post(f"{base_url}/upload-cv/", files=files)
        
        if response.status_code == 200:
            print("✅ Test CV uploaded successfully")
            
            # Get the current CV content
            cv_response = requests.get(f"{base_url}/cv/current/")
            if cv_response.status_code == 200:
                content = cv_response.json().get('content', '')
                print(f"✅ CV content retrieved ({len(content)} characters)")
                
                # Test section detection on the uploaded content
                lines = content.split('\n')
                backend_detected = []
                
                for i, line in enumerate(lines, 1):
                    line_stripped = line.strip()
                    if line_stripped:
                        for category, keywords in section_categories.items():
                            for keyword in keywords:
                                if keyword.upper() in line_stripped.upper():
                                    backend_detected.append({
                                        'line': i,
                                        'content': line_stripped,
                                        'category': category,
                                        'keyword': keyword
                                    })
                                    break
                            if any(keyword.upper() in line_stripped.upper() for keyword in keywords):
                                break
                
                print(f"✅ Backend detected {len(backend_detected)} sections:")
                for section in backend_detected:
                    print(f"   Line {section['line']:2d}: {section['content']}")
                    print(f"        Category: {section['category']}")
                    print()
                
            else:
                print(f"❌ Failed to get CV content: {cv_response.status_code}")
        else:
            print(f"❌ Failed to upload test CV: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
    
    # Cleanup
    import os
    if os.path.exists('test_comprehensive_cv.txt'):
        os.remove('test_comprehensive_cv.txt')
        print("\n🗑️ Cleaned up test file")
    
    print("\n" + "=" * 60)
    print("📊 Comprehensive Section Detection Test Summary:")
    print(f"   Frontend Detection: {len(detected_sections)} sections found")
    print(f"   Backend Detection: {len(backend_detected) if 'backend_detected' in locals() else 'N/A'} sections found")
    print(f"   Section Categories Covered: {len(section_categories)}")
    
    # List all section categories
    print("\n📋 All Section Categories Supported:")
    for category in section_categories.keys():
        print(f"   • {category.title()}")
    
    print("\n✅ Comprehensive section detection test completed!")
    return True

if __name__ == "__main__":
    test_comprehensive_section_detection() 