#!/usr/bin/env python3
"""
Test script for the new section detection functions.
Tests all 10 new get_<section>_section() functions with various CV formats.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from main_enhanced import (
    get_objective_section, get_certifications_section, get_research_section,
    get_achievements_section, get_leadership_section, get_volunteer_section,
    get_languages_section, get_technologies_section, get_interests_section,
    get_additional_section
)

def test_section_detection_functions():
    """Test all section detection functions with comprehensive CV content"""
    
    # Sample CV content with all sections
    sample_cv = """
JOHN DOE
Software Engineer
john.doe@email.com | +1-555-123-4567 | linkedin.com/in/johndoe

CAREER OBJECTIVE
To become a senior software engineer and lead development teams in innovative projects.

EDUCATION
Bachelor of Computer Science, Graduated in 2023, from Stanford University
Master of Software Engineering, Expected 2025, from MIT

WORK EXPERIENCE
Software Engineer at Google (2023-2024)
- Developed scalable web applications
- Led a team of 5 developers

SKILLS
Python, JavaScript, React, Node.js, AWS, Docker

CERTIFICATIONS
AWS Certified Solutions Architect - Amazon Web Services 2023
Microsoft Azure Developer - Microsoft 2022

PROJECTS
E-commerce Platform - Built using React and Node.js
Mobile App - Developed with React Native

RESEARCH
Machine Learning Ethics - Stanford University 2023
Blockchain Technology Study - MIT 2022

ACHIEVEMENTS
Best Developer Award - Tech Conference 2023
Hackathon Winner - University Competition 2022

LEADERSHIP EXPERIENCE
Team Lead - Software Development Team 2022-2023
Project Manager - Agile Development Team 6 months

VOLUNTEER WORK
Coding Instructor - Local Bootcamp 2023-2024
Community Service - Charity Organization 6 months

LANGUAGES
English - Native
Spanish - Fluent
French - Conversational

TECHNOLOGIES
Development Tools - Git, Docker, Jenkins
Project Management - Jira, Confluence, Slack

INTERESTS
Technical Interests - Coding, Reading Tech Blogs
Outdoor Activities - Hiking, Photography

ADDITIONAL INFORMATION
Work Authorization - US Citizen
Open Source - Active Contributor
Professional Memberships - IEEE Member
"""

    print("🧪 Testing Section Detection Functions")
    print("=" * 60)
    
    # Test each section function
    test_cases = [
        ("Objective", get_objective_section, "CAREER OBJECTIVE"),
        ("Certifications", get_certifications_section, "CERTIFICATIONS"),
        ("Research", get_research_section, "RESEARCH"),
        ("Achievements", get_achievements_section, "ACHIEVEMENTS"),
        ("Leadership", get_leadership_section, "LEADERSHIP EXPERIENCE"),
        ("Volunteer", get_volunteer_section, "VOLUNTEER WORK"),
        ("Languages", get_languages_section, "LANGUAGES"),
        ("Technologies", get_technologies_section, "TECHNOLOGIES"),
        ("Interests", get_interests_section, "INTERESTS"),
        ("Additional", get_additional_section, "ADDITIONAL INFORMATION")
    ]
    
    results = {}
    total_tests = len(test_cases)
    passed_tests = 0
    
    for section_name, function, expected_header in test_cases:
        print(f"\n📋 Testing {section_name} Section Detection")
        print("-" * 40)
        
        try:
            # Call the function
            result = function(sample_cv)
            
            # Check if section was found
            if result and result.strip():
                print(f"✅ {section_name} section found!")
                print(f"📄 Content: {result[:100]}{'...' if len(result) > 100 else ''}")
                results[section_name] = "PASS"
                passed_tests += 1
            else:
                print(f"❌ {section_name} section NOT found")
                print(f"🔍 Expected header: {expected_header}")
                results[section_name] = "FAIL"
                
        except Exception as e:
            print(f"❌ Error testing {section_name}: {str(e)}")
            results[section_name] = "ERROR"
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for section_name, result in results.items():
        status_icon = "✅" if result == "PASS" else "❌"
        print(f"{status_icon} {section_name}: {result}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 All section detection functions are working correctly!")
    else:
        print("⚠️  Some section detection functions need attention.")
    
    return results

def test_variant_headers():
    """Test section detection with various header formats"""
    
    print("\n🧪 Testing Variant Header Formats")
    print("=" * 60)
    
    # Test different header formats for each section
    variant_tests = [
        ("Objective", [
            "OBJECTIVE",
            "CAREER OBJECTIVE", 
            "PROFESSIONAL OBJECTIVE",
            "EMPLOYMENT OBJECTIVE",
            "CAREER GOAL"
        ]),
        ("Certifications", [
            "CERTIFICATIONS",
            "LICENSES",
            "CREDENTIALS", 
            "PROFESSIONAL CERTIFICATIONS",
            "TECHNICAL CERTIFICATIONS"
        ]),
        ("Research", [
            "RESEARCH",
            "PUBLICATIONS",
            "PAPERS",
            "ACADEMIC WORK",
            "RESEARCH PAPERS"
        ]),
        ("Achievements", [
            "ACHIEVEMENTS",
            "AWARDS",
            "HONORS",
            "NOTABLE ACHIEVEMENTS",
            "CAREER ACHIEVEMENTS"
        ]),
        ("Leadership", [
            "LEADERSHIP EXPERIENCE",
            "LEADERSHIP ROLES",
            "ACTIVITIES",
            "STUDENT ACTIVITIES",
            "CAMPUS INVOLVEMENT"
        ]),
        ("Volunteer", [
            "VOLUNTEER WORK",
            "VOLUNTEERING",
            "COMMUNITY SERVICE",
            "CIVIC ENGAGEMENT",
            "SOCIAL INVOLVEMENT"
        ]),
        ("Languages", [
            "LANGUAGES",
            "LANGUAGE PROFICIENCY",
            "SPOKEN LANGUAGES",
            "FOREIGN LANGUAGES"
        ]),
        ("Technologies", [
            "TECHNOLOGIES",
            "TOOLS",
            "SOFTWARE",
            "PROGRAMMING LANGUAGES",
            "FRAMEWORKS"
        ]),
        ("Interests", [
            "INTERESTS",
            "HOBBIES",
            "PERSONAL INTERESTS",
            "ACTIVITIES & INTERESTS",
            "OUTSIDE INTERESTS"
        ]),
        ("Additional", [
            "ADDITIONAL INFORMATION",
            "MISCELLANEOUS",
            "ADDENDUM",
            "SUPPLEMENTARY DETAILS",
            "OTHER INFO"
        ])
    ]
    
    for section_name, headers in variant_tests:
        print(f"\n📋 Testing {section_name} variants:")
        for header in headers:
            test_cv = f"""
JOHN DOE
Software Engineer

{header}
Sample content for {section_name.lower()} section.

EDUCATION
Bachelor's degree
"""
            
            # Get the appropriate function
            function_map = {
                "Objective": get_objective_section,
                "Certifications": get_certifications_section,
                "Research": get_research_section,
                "Achievements": get_achievements_section,
                "Leadership": get_leadership_section,
                "Volunteer": get_volunteer_section,
                "Languages": get_languages_section,
                "Technologies": get_technologies_section,
                "Interests": get_interests_section,
                "Additional": get_additional_section
            }
            
            function = function_map[section_name]
            result = function(test_cv)
            
            if result and "Sample content" in result:
                print(f"  ✅ {header}")
            else:
                print(f"  ❌ {header}")

if __name__ == "__main__":
    print("🚀 Starting Section Detection Function Tests")
    print("=" * 60)
    
    # Run main tests
    results = test_section_detection_functions()
    
    # Run variant header tests
    test_variant_headers()
    
    print("\n🎯 Testing Complete!") 