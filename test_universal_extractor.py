#!/usr/bin/env python3
"""
🧠 Universal CV Section Extractor Test
Tests the new universal extractor with various input examples
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the function from main_enhanced.py
from main_enhanced import extract_universal_cv_content

def test_universal_extractor():
    """Test the universal CV section extractor with various examples"""
    
    test_cases = [
        # Education examples
        ("I have done MSCS from NUST", "education", "Mscs From Nust"),
        ("I graduated with a Bachelor's degree in Computer Science from MIT", "education", "Bachelor'S Degree In Computer Science From Mit"),
        ("Master of Science in Data Science from Stanford University", "education", "Master Of Science In Data Science From Stanford University"),
        
        # Experience examples
        ("I worked as a Software Engineer at Google", "experience", "Software Engineer At Google"),
        ("Senior Developer at Microsoft for 3 years", "experience", "Senior Developer At Microsoft"),
        ("Full Stack Developer at Amazon Web Services", "experience", "Full Stack Developer At Amazon Web Services"),
        
        # Skills examples
        ("I am skilled in Python, JavaScript, and C++", "skills", "Python, Javascript, And C++"),
        ("Proficient in React, Node.js, and MongoDB", "skills", "React, Node.Js, And Mongodb"),
        ("Technologies: AWS, Docker, Kubernetes", "skills", "Aws, Docker, Kubernetes"),
        
        # Certifications examples
        ("AWS Certified Solutions Architect", "certifications", "Aws Certified Solutions Architect"),
        ("Completed certification in Google Cloud Platform", "certifications", "Google Cloud Platform"),
        ("Microsoft Azure certification", "certifications", "Microsoft Azure Certification"),
        
        # Projects examples
        ("Built a React e-commerce website", "projects", "React E-Commerce Website"),
        ("Developed a machine learning project for image recognition", "projects", "Machine Learning Project For Image Recognition"),
        ("Created a mobile app using React Native", "projects", "Mobile App Using React Native"),
        
        # Research examples
        ("Published research paper on AI ethics", "research", "Research Paper On Ai Ethics"),
        ("Conducted study on blockchain technology", "research", "Study On Blockchain Technology"),
        ("Thesis on computer vision applications", "research", "Thesis On Computer Vision Applications"),
        
        # Achievements examples
        ("Received Best Developer Award", "achievements", "Best Developer Award"),
        ("Won hackathon competition", "achievements", "Hackathon Competition"),
        ("Earned scholarship for academic excellence", "achievements", "Scholarship For Academic Excellence"),
        
        # Leadership examples
        ("Led a team of 10 developers", "leadership", "Team Of 10 Developers"),
        ("Managed software development projects", "leadership", "Software Development Projects"),
        ("Supervised junior developers", "leadership", "Junior Developers"),
        
        # Volunteer examples
        ("Volunteered at local coding bootcamp", "volunteer", "Local Coding Bootcamp"),
        ("Community service at tech education center", "volunteer", "Tech Education Center"),
        ("Charity work for digital literacy", "volunteer", "Digital Literacy"),
        
        # Languages examples
        ("Speak English, Spanish, and French", "languages", "English, Spanish, And French"),
        ("Fluent in German and Italian", "languages", "German And Italian"),
        ("Bilingual in English and Chinese", "languages", "English And Chinese"),
        
        # Tools examples
        ("Proficient with Git, Docker, and Jenkins", "tools", "Git, Docker, And Jenkins"),
        ("Skilled in Jira, Confluence, and Slack", "tools", "Jira, Confluence, And Slack"),
        ("Tools: VS Code, Postman, Figma", "tools", "Vs Code, Postman, Figma"),
        
        # Hobbies examples
        ("Hobbies: coding, reading, hiking", "hobbies", "Coding, Reading, Hiking"),
        ("Enjoy playing guitar and photography", "hobbies", "Playing Guitar And Photography"),
        ("Passionate about chess and cooking", "hobbies", "Chess And Cooking"),
        
        # References examples
        ("References available upon request", "references", "Available Upon Request"),
        ("Contact references from previous employers", "references", "From Previous Employers"),
        ("Professional references from Google and Microsoft", "references", "From Google And Microsoft"),
        
        # Additional examples
        ("Additional information: Work authorization in US", "additional", "Work Authorization In Us"),
        ("Miscellaneous: Open source contributor", "additional", "Open Source Contributor"),
        ("Other details: Available for remote work", "additional", "Available For Remote Work")
    ]
    
    print("🧠 Universal CV Section Extractor Test")
    print("=" * 60)
    
    passed = 0
    total = len(test_cases)
    
    for i, (input_text, expected_section, expected_content) in enumerate(test_cases, 1):
        print(f"\n{i:2d}. Testing: '{input_text}'")
        print(f"    Expected: {expected_section} → '{expected_content}'")
        
        try:
            detected_section, extracted_content = extract_universal_cv_content(input_text)
            print(f"    Result:   {detected_section} → '{extracted_content}'")
            
            # Check if section matches (allowing for some flexibility)
            section_match = (detected_section == expected_section or 
                           detected_section in expected_section or 
                           expected_section in detected_section)
            
            # Check if content is reasonably similar (allowing for case differences)
            content_similar = (extracted_content.lower() == expected_content.lower() or
                             expected_content.lower() in extracted_content.lower() or
                             extracted_content.lower() in expected_content.lower())
            
            if section_match and content_similar:
                print(f"    ✅ PASS")
                passed += 1
            else:
                print(f"    ❌ FAIL")
                if not section_match:
                    print(f"       Section mismatch: expected '{expected_section}', got '{detected_section}'")
                if not content_similar:
                    print(f"       Content mismatch: expected '{expected_content}', got '{extracted_content}'")
                    
        except Exception as e:
            print(f"    ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Universal extractor is working perfectly!")
    elif passed >= total * 0.8:
        print("👍 Most tests passed! Universal extractor is working well!")
    else:
        print("⚠️  Many tests failed. Universal extractor needs improvement.")

if __name__ == "__main__":
    test_universal_extractor() 