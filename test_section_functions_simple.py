#!/usr/bin/env python3
"""
Simplified test script for section detection functions.
Tests the regex patterns and logic without importing the full backend.
"""

import re

# Define the SECTION_PATTERNS (copied from main_enhanced.py)
SECTION_PATTERNS = {
    # Objective / Goal
    "objective": [
        r"^OBJECTIVE$", r"^CAREER\s+OBJECTIVE$", r"^PROFESSIONAL\s+OBJECTIVE$", r"^EMPLOYMENT\s+OBJECTIVE$",
        r"^CAREER\s+GOAL$", r"^PERSONAL\s+OBJECTIVE$",
        r"^[_\-=\s]*OBJECTIVE[_\-=\s]*$", r"^[_\-=\s]*CAREER\s+OBJECTIVE[_\-=\s]*$", r"^[_\-=\s]*PROFESSIONAL\s+OBJECTIVE[_\-=\s]*$",
        r"^[_\-=\s]*EMPLOYMENT\s+OBJECTIVE[_\-=\s]*$", r"^[_\-=\s]*CAREER\s+GOAL[_\-=\s]*$", r"^[_\-=\s]*PERSONAL\s+OBJECTIVE[_\-=\s]*$"
    ],
    
    # Certifications & Training
    "certifications": [
        r"^CERTIFICATIONS$", r"^LICENSES$", r"^COURSES$", r"^ONLINE\s+COURSES$", r"^CERTIFICATIONS\s+&\s+LICENSES$",
        r"^CREDENTIALS$", r"^PROFESSIONAL\s+CERTIFICATIONS$", r"^TECHNICAL\s+CERTIFICATIONS$", r"^SPECIALIZED\s+TRAINING$",
        r"^TRAINING\s+&\s+DEVELOPMENT$", r"^COMPLETED\s+COURSES$",
        r"^[_\-=\s]*CERTIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*LICENSES[_\-=\s]*$", r"^[_\-=\s]*COURSES[_\-=\s]*$",
        r"^[_\-=\s]*ONLINE\s+COURSES[_\-=\s]*$", r"^[_\-=\s]*CERTIFICATIONS\s+&\s+LICENSES[_\-=\s]*$", r"^[_\-=\s]*CREDENTIALS[_\-=\s]*$",
        r"^[_\-=\s]*PROFESSIONAL\s+CERTIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*TECHNICAL\s+CERTIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*SPECIALIZED\s+TRAINING[_\-=\s]*$",
        r"^[_\-=\s]*TRAINING\s+&\s+DEVELOPMENT[_\-=\s]*$", r"^[_\-=\s]*COMPLETED\s+COURSES[_\-=\s]*$"
    ],
    
    # Research & Academic Work
    "research": [
        r"^RESEARCH$", r"^RESEARCH\s+EXPERIENCE$", r"^PUBLICATIONS$", r"^PAPERS$", r"^ACADEMIC\s+WORK$", r"^RESEARCH\s+PAPERS$",
        r"^THESES$", r"^DISSERTATIONS$", r"^CONFERENCE\s+PRESENTATIONS$", r"^PRESENTATIONS$", r"^ACADEMIC\s+CONTRIBUTIONS$",
        r"^RESEARCH\s+HIGHLIGHTS$", r"^SCHOLARLY\s+WORK$",
        r"^[_\-=\s]*RESEARCH[_\-=\s]*$", r"^[_\-=\s]*RESEARCH\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*PUBLICATIONS[_\-=\s]*$",
        r"^[_\-=\s]*PAPERS[_\-=\s]*$", r"^[_\-=\s]*ACADEMIC\s+WORK[_\-=\s]*$", r"^[_\-=\s]*RESEARCH\s+PAPERS[_\-=\s]*$",
        r"^[_\-=\s]*THESES[_\-=\s]*$", r"^[_\-=\s]*DISSERTATIONS[_\-=\s]*$", r"^[_\-=\s]*CONFERENCE\s+PRESENTATIONS[_\-=\s]*$",
        r"^[_\-=\s]*PRESENTATIONS[_\-=\s]*$", r"^[_\-=\s]*ACADEMIC\s+CONTRIBUTIONS[_\-=\s]*$", r"^[_\-=\s]*RESEARCH\s+HIGHLIGHTS[_\-=\s]*$",
        r"^[_\-=\s]*SCHOLARLY\s+WORK[_\-=\s]*$"
    ],
    
    # Awards & Achievements
    "achievements": [
        r"^AWARDS$", r"^HONORS$", r"^HONORS\s+&\s+AWARDS$", r"^ACHIEVEMENTS$", r"^NOTABLE\s+ACHIEVEMENTS$",
        r"^CAREER\s+ACHIEVEMENTS$", r"^DISTINCTIONS$", r"^RECOGNITIONS$", r"^SCHOLARSHIPS$", r"^FELLOWSHIPS$",
        r"^ACADEMIC\s+AWARDS$",
        r"^[_\-=\s]*AWARDS[_\-=\s]*$", r"^[_\-=\s]*HONORS[_\-=\s]*$", r"^[_\-=\s]*HONORS\s+&\s+AWARDS[_\-=\s]*$",
        r"^[_\-=\s]*ACHIEVEMENTS[_\-=\s]*$", r"^[_\-=\s]*NOTABLE\s+ACHIEVEMENTS[_\-=\s]*$", r"^[_\-=\s]*CAREER\s+ACHIEVEMENTS[_\-=\s]*$",
        r"^[_\-=\s]*DISTINCTIONS[_\-=\s]*$", r"^[_\-=\s]*RECOGNITIONS[_\-=\s]*$", r"^[_\-=\s]*SCHOLARSHIPS[_\-=\s]*$",
        r"^[_\-=\s]*FELLOWSHIPS[_\-=\s]*$", r"^[_\-=\s]*ACADEMIC\s+AWARDS[_\-=\s]*$"
    ],
    
    # Leadership & Activities
    "leadership": [
        r"^LEADERSHIP\s+EXPERIENCE$", r"^LEADERSHIP\s+ROLES$", r"^ACTIVITIES$", r"^STUDENT\s+ACTIVITIES$",
        r"^CAMPUS\s+INVOLVEMENT$", r"^PROFESSIONAL\s+ACTIVITIES$", r"^ORGANIZATIONAL\s+INVOLVEMENT$",
        r"^LEADERSHIP\s+&\s+INVOLVEMENT$",
        r"^[_\-=\s]*LEADERSHIP\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*LEADERSHIP\s+ROLES[_\-=\s]*$", r"^[_\-=\s]*ACTIVITIES[_\-=\s]*$",
        r"^[_\-=\s]*STUDENT\s+ACTIVITIES[_\-=\s]*$", r"^[_\-=\s]*CAMPUS\s+INVOLVEMENT[_\-=\s]*$", r"^[_\-=\s]*PROFESSIONAL\s+ACTIVITIES[_\-=\s]*$",
        r"^[_\-=\s]*ORGANIZATIONAL\s+INVOLVEMENT[_\-=\s]*$", r"^[_\-=\s]*LEADERSHIP\s+&\s+INVOLVEMENT[_\-=\s]*$"
    ],
    
    # Volunteer / Community Involvement
    "volunteer": [
        r"^VOLUNTEER\s+WORK$", r"^VOLUNTEERING$", r"^COMMUNITY\s+SERVICE$", r"^CIVIC\s+ENGAGEMENT$",
        r"^SOCIAL\s+INVOLVEMENT$", r"^COMMUNITY\s+INVOLVEMENT$", r"^CHARITABLE\s+WORK$", r"^PRO\s+BONO\s+WORK$",
        r"^[_\-=\s]*VOLUNTEER\s+WORK[_\-=\s]*$", r"^[_\-=\s]*VOLUNTEERING[_\-=\s]*$", r"^[_\-=\s]*COMMUNITY\s+SERVICE[_\-=\s]*$",
        r"^[_\-=\s]*CIVIC\s+ENGAGEMENT[_\-=\s]*$", r"^[_\-=\s]*SOCIAL\s+INVOLVEMENT[_\-=\s]*$", r"^[_\-=\s]*COMMUNITY\s+INVOLVEMENT[_\-=\s]*$",
        r"^[_\-=\s]*CHARITABLE\s+WORK[_\-=\s]*$", r"^[_\-=\s]*PRO\s+BONO\s+WORK[_\-=\s]*$"
    ],
    
    # Languages
    "languages": [
        r"^LANGUAGES$", r"^LANGUAGE\s+PROFICIENCY$", r"^SPOKEN\s+LANGUAGES$", r"^FOREIGN\s+LANGUAGES$",
        r"^[_\-=\s]*LANGUAGES[_\-=\s]*$", r"^[_\-=\s]*LANGUAGE\s+PROFICIENCY[_\-=\s]*$", r"^[_\-=\s]*SPOKEN\s+LANGUAGES[_\-=\s]*$",
        r"^[_\-=\s]*FOREIGN\s+LANGUAGES[_\-=\s]*$"
    ],
    
    # Tools & Technologies
    "technologies": [
        r"^TOOLS$", r"^TECHNOLOGIES$", r"^SOFTWARE$", r"^PROGRAMMING\s+LANGUAGES$", r"^FRAMEWORKS$", r"^PLATFORMS$",
        r"^IT\s+PROFICIENCY$", r"^SOFTWARE\s+PROFICIENCY$", r"^SYSTEMS$", r"^ENVIRONMENTS$",
        r"^[_\-=\s]*TOOLS[_\-=\s]*$", r"^[_\-=\s]*TECHNOLOGIES[_\-=\s]*$", r"^[_\-=\s]*SOFTWARE[_\-=\s]*$",
        r"^[_\-=\s]*PROGRAMMING\s+LANGUAGES[_\-=\s]*$", r"^[_\-=\s]*FRAMEWORKS[_\-=\s]*$", r"^[_\-=\s]*PLATFORMS[_\-=\s]*$",
        r"^[_\-=\s]*IT\s+PROFICIENCY[_\-=\s]*$", r"^[_\-=\s]*SOFTWARE\s+PROFICIENCY[_\-=\s]*$", r"^[_\-=\s]*SYSTEMS[_\-=\s]*$",
        r"^[_\-=\s]*ENVIRONMENTS[_\-=\s]*$"
    ],
    
    # Hobbies & Personal Interests
    "interests": [
        r"^HOBBIES$", r"^INTERESTS$", r"^PERSONAL\s+INTERESTS$", r"^ACTIVITIES\s+&\s+INTERESTS$", r"^OUTSIDE\s+INTERESTS$",
        r"^EXTRACURRICULAR\s+ACTIVITIES$", r"^LEISURE\s+INTERESTS$",
        r"^[_\-=\s]*HOBBIES[_\-=\s]*$", r"^[_\-=\s]*INTERESTS[_\-=\s]*$", r"^[_\-=\s]*PERSONAL\s+INTERESTS[_\-=\s]*$",
        r"^[_\-=\s]*ACTIVITIES\s+&\s+INTERESTS[_\-=\s]*$", r"^[_\-=\s]*OUTSIDE\s+INTERESTS[_\-=\s]*$",
        r"^[_\-=\s]*EXTRACURRICULAR\s+ACTIVITIES[_\-=\s]*$", r"^[_\-=\s]*LEISURE\s+INTERESTS[_\-=\s]*$"
    ],
    
    # Additional / Miscellaneous
    "additional": [
        r"^ADDITIONAL\s+INFORMATION$", r"^MISCELLANEOUS$", r"^ADDENDUM$", r"^ANNEXURES$", r"^SUPPLEMENTARY\s+DETAILS$",
        r"^ACCOMPLISHMENTS$", r"^CAREER\s+HIGHLIGHTS$", r"^SUMMARY\s+OF\s+QUALIFICATIONS$", r"^WORK\s+AUTHORIZATION$",
        r"^CITIZENSHIP$", r"^MILITARY\s+SERVICE$", r"^SECURITY\s+CLEARANCE$", r"^PUBLICATIONS\s+&\s+PRESENTATIONS$",
        r"^PROFESSIONAL\s+MEMBERSHIPS$", r"^AFFILIATIONS$", r"^MEMBERSHIPS$", r"^PORTFOLIOS$", r"^GITHUB$", r"^LINKEDIN$",
        r"^SOCIAL\s+LINKS$", r"^ONLINE\s+PRESENCE$",
        r"^[_\-=\s]*ADDITIONAL\s+INFORMATION[_\-=\s]*$", r"^[_\-=\s]*MISCELLANEOUS[_\-=\s]*$", r"^[_\-=\s]*ADDENDUM[_\-=\s]*$",
        r"^[_\-=\s]*ANNEXURES[_\-=\s]*$", r"^[_\-=\s]*SUPPLEMENTARY\s+DETAILS[_\-=\s]*$", r"^[_\-=\s]*ACCOMPLISHMENTS[_\-=\s]*$",
        r"^[_\-=\s]*CAREER\s+HIGHLIGHTS[_\-=\s]*$", r"^[_\-=\s]*SUMMARY\s+OF\s+QUALIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*WORK\s+AUTHORIZATION[_\-=\s]*$",
        r"^[_\-=\s]*CITIZENSHIP[_\-=\s]*$", r"^[_\-=\s]*MILITARY\s+SERVICE[_\-=\s]*$", r"^[_\-=\s]*SECURITY\s+CLEARANCE[_\-=\s]*$",
        r"^[_\-=\s]*PUBLICATIONS\s+&\s+PRESENTATIONS[_\-=\s]*$", r"^[_\-=\s]*PROFESSIONAL\s+MEMBERSHIPS[_\-=\s]*$",
        r"^[_\-=\s]*AFFILIATIONS[_\-=\s]*$", r"^[_\-=\s]*MEMBERSHIPS[_\-=\s]*$", r"^[_\-=\s]*PORTFOLIOS[_\-=\s]*$",
        r"^[_\-=\s]*GITHUB[_\-=\s]*$", r"^[_\-=\s]*LINKEDIN[_\-=\s]*$", r"^[_\-=\s]*SOCIAL\s+LINKS[_\-=\s]*$", r"^[_\-=\s]*ONLINE\s+PRESENCE[_\-=\s]*$"
    ]
}

def find_section_in_cv_simple(cv_content: str, section_name: str) -> dict:
    """
    Simplified version of find_section_in_cv function for testing.
    """
    if section_name not in SECTION_PATTERNS:
        return {'found': False}
    
    lines = cv_content.split('\n')
    patterns = SECTION_PATTERNS[section_name]
    
    for i, line in enumerate(lines):
        line_upper = line.upper().strip()
        for pattern in patterns:
            if re.match(pattern, line_upper, re.IGNORECASE):
                # Found the section header
                start_line = i
                header_line = line
                
                # Find the end of this section (next section or end of file)
                end_line = len(lines)
                for j in range(i + 1, len(lines)):
                    # Check if this line is a header for another section
                    for other_section, other_patterns in SECTION_PATTERNS.items():
                        if other_section != section_name:
                            for other_pattern in other_patterns:
                                if re.match(other_pattern, lines[j].upper().strip(), re.IGNORECASE):
                                    end_line = j
                                    break
                            if end_line != len(lines):
                                break
                    if end_line != len(lines):
                        break
                
                # Extract section content
                section_content = '\n'.join(lines[start_line:end_line])
                
                return {
                    'start_line': start_line,
                    'end_line': end_line,
                    'content': section_content,
                    'header': header_line,
                    'found': True
                }
    
    return {'found': False}

def get_section_simple(cv_content: str, section_name: str) -> str:
    """
    Simplified section extraction function.
    """
    section_info = find_section_in_cv_simple(cv_content, section_name)
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def test_section_detection():
    """Test section detection with comprehensive CV content"""
    
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
    
    # Test each section
    test_cases = [
        ("Objective", "objective"),
        ("Certifications", "certifications"),
        ("Research", "research"),
        ("Achievements", "achievements"),
        ("Leadership", "leadership"),
        ("Volunteer", "volunteer"),
        ("Languages", "languages"),
        ("Technologies", "technologies"),
        ("Interests", "interests"),
        ("Additional", "additional")
    ]
    
    results = {}
    total_tests = len(test_cases)
    passed_tests = 0
    
    for section_name, section_key in test_cases:
        print(f"\n📋 Testing {section_name} Section Detection")
        print("-" * 40)
        
        try:
            # Call the function
            result = get_section_simple(sample_cv, section_key)
            
            # Check if section was found
            if result and result.strip():
                print(f"✅ {section_name} section found!")
                print(f"📄 Content: {result[:100]}{'...' if len(result) > 100 else ''}")
                results[section_name] = "PASS"
                passed_tests += 1
            else:
                print(f"❌ {section_name} section NOT found")
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
        section_key = section_name.lower()
        for header in headers:
            test_cv = f"""
JOHN DOE
Software Engineer

{header}
Sample content for {section_name.lower()} section.

EDUCATION
Bachelor's degree
"""
            
            result = get_section_simple(test_cv, section_key)
            
            if result and "Sample content" in result:
                print(f"  ✅ {header}")
            else:
                print(f"  ❌ {header}")

if __name__ == "__main__":
    print("🚀 Starting Section Detection Function Tests")
    print("=" * 60)
    
    # Run main tests
    results = test_section_detection()
    
    # Run variant header tests
    test_variant_headers()
    
    print("\n🎯 Testing Complete!") 