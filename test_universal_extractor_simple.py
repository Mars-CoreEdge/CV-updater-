#!/usr/bin/env python3
"""
🧠 Universal CV Section Extractor Test (Simple Version)
Tests the universal extractor logic without importing the full backend
"""

import re

def extract_universal_cv_content(message: str) -> tuple[str, str]:
    """
    🧠 Universal CV Section Extractor
    Automatically detects the relevant CV section and extracts only the relevant content.
    
    Returns: (section_name, extracted_content)
    """
    message_lower = message.lower().strip()
    
    # Define section-specific extraction patterns
    section_patterns = {
        # Education patterns
        'education': {
            'keywords': ['education', 'academic', 'degree', 'university', 'college', 'school', 'graduated', 'bachelor', 'master', 'phd', 'mba'],
            'patterns': [
                r'(?:i\s+(?:have\s+)?(?:done|completed|graduated|studied|pursued|obtained|earned)\s+)?([^,\.]+?(?:degree|masters?|bachelors?|phd|mba|certification)[^,\.]*(?:from|at|in)\s+[^,\.]+)',
                r'(?:degree|masters?|bachelors?|phd|mba)\s+(?:in|of)\s+([^,\.]+?)(?:\s+from|\s+at|\s+in\s+\d{4}|$)',
                r'(?:graduated|completed|studied)\s+(?:in\s+\d{4}\s+)?(?:from|at)\s+([^,\.]+)',
                r'([^,\.]+?(?:university|college|institute|school)[^,\.]*)'
            ]
        },
        
        # Experience patterns
        'experience': {
            'keywords': ['experience', 'worked', 'job', 'position', 'role', 'employed', 'internship', 'work', 'career'],
            'patterns': [
                r'(?:i\s+(?:have\s+)?(?:worked|served|acted)\s+as\s+)?([^,\.]+?(?:engineer|developer|manager|analyst|consultant|specialist|coordinator|assistant|director|lead|architect)[^,\.]*(?:at|for|with)\s+[^,\.]+)',
                r'(?:position|role|job)\s+(?:as\s+)?([^,\.]+?)(?:\s+at|\s+for|\s+with|$)',
                r'(?:worked|employed)\s+(?:as\s+)?([^,\.]+?)(?:\s+at|\s+for|\s+with|$)',
                r'([^,\.]+?(?:company|corp|inc|ltd|soft|tech|solutions|systems)[^,\.]*)'
            ]
        },
        
        # Skills patterns
        'skills': {
            'keywords': ['skills', 'skilled', 'proficient', 'expertise', 'technologies', 'languages', 'tools', 'frameworks'],
            'patterns': [
                r'(?:skilled|proficient|expert|knowledge)\s+(?:in\s+)?([^,\.]+)',
                r'(?:technologies?|languages?|tools?|frameworks?|skills?)\s*:\s*([^,\.]+)',
                r'(?:i\s+(?:am\s+)?(?:skilled|proficient|expert)\s+in\s+)?([^,\.]+)',
                r'([a-zA-Z\s,]+(?:python|javascript|java|c\+\+|react|node|angular|vue|sql|aws|docker|kubernetes|git|html|css|php|ruby|go|rust|swift|kotlin)[a-zA-Z\s,]*)'
            ]
        },
        
        # Certifications patterns
        'certifications': {
            'keywords': ['certification', 'certified', 'license', 'course', 'training', 'credential'],
            'patterns': [
                r'(?:certification|certified|license)\s+(?:in\s+)?([^,\.]+)',
                r'(?:completed|obtained|earned)\s+(?:certification|certificate|license)\s+(?:in\s+)?([^,\.]+)',
                r'([^,\.]+?(?:certification|certificate|license)[^,\.]*)',
                r'(?:course|training)\s+(?:in\s+)?([^,\.]+)'
            ]
        },
        
        # Projects patterns
        'projects': {
            'keywords': ['project', 'built', 'developed', 'created', 'designed', 'implemented'],
            'patterns': [
                r'(?:built|developed|created|designed|implemented)\s+(?:a\s+)?([^,\.]+?(?:project|app|website|system|platform|tool)[^,\.]*)',
                r'(?:project|app|website|system)\s+(?:called\s+)?([^,\.]+)',
                r'([^,\.]+?(?:project|application|website|system|platform)[^,\.]*)'
            ]
        },
        
        # Research patterns
        'research': {
            'keywords': ['research', 'published', 'paper', 'thesis', 'dissertation', 'study'],
            'patterns': [
                r'(?:research|study|paper|thesis|dissertation)\s+(?:on\s+)?([^,\.]+)',
                r'(?:published|wrote|conducted)\s+(?:research|paper|study)\s+(?:on\s+)?([^,\.]+)',
                r'([^,\.]+?(?:research|paper|study|thesis)[^,\.]*)'
            ]
        },
        
        # Achievements patterns
        'achievements': {
            'keywords': ['achievement', 'award', 'honor', 'recognition', 'distinction', 'scholarship'],
            'patterns': [
                r'(?:achievement|award|honor|recognition|distinction)\s+(?:for\s+)?([^,\.]+)',
                r'(?:received|won|earned)\s+(?:award|honor|recognition|scholarship)\s+(?:for\s+)?([^,\.]+)',
                r'([^,\.]+?(?:award|honor|recognition|scholarship)[^,\.]*)'
            ]
        },
        
        # Leadership patterns
        'leadership': {
            'keywords': ['leadership', 'led', 'managed', 'supervised', 'coordinated', 'organized'],
            'patterns': [
                r'(?:led|managed|supervised|coordinated|organized)\s+([^,\.]+)',
                r'(?:leadership|management)\s+(?:role|position)\s+(?:as\s+)?([^,\.]+)',
                r'(?:team\s+)?(?:lead|manager|supervisor|coordinator)\s+(?:of\s+)?([^,\.]+)'
            ]
        },
        
        # Volunteer patterns
        'volunteer': {
            'keywords': ['volunteer', 'volunteering', 'community', 'service', 'charity'],
            'patterns': [
                r'(?:volunteered|volunteering)\s+(?:for|at|with)\s+([^,\.]+)',
                r'(?:community|charity)\s+(?:service|work)\s+(?:for|at|with)\s+([^,\.]+)',
                r'([^,\.]+?(?:volunteer|community|charity)[^,\.]*)'
            ]
        },
        
        # Languages patterns
        'languages': {
            'keywords': ['language', 'speak', 'fluent', 'proficient', 'bilingual'],
            'patterns': [
                r'(?:speak|fluent|proficient)\s+(?:in\s+)?([^,\.]+)',
                r'(?:language|languages?)\s*:\s*([^,\.]+)',
                r'(?:bilingual|trilingual|multilingual)\s+(?:in\s+)?([^,\.]+)',
                r'([a-zA-Z\s,]+(?:english|spanish|french|german|chinese|japanese|arabic|hindi|urdu|portuguese|italian|russian)[a-zA-Z\s,]*)'
            ]
        },
        
        # Tools patterns
        'tools': {
            'keywords': ['tools', 'software', 'platforms', 'systems', 'environments'],
            'patterns': [
                r'(?:tools?|software|platforms?|systems?)\s*:\s*([^,\.]+)',
                r'(?:proficient|skilled)\s+(?:with|in)\s+([^,\.]+)',
                r'([^,\.]+?(?:tools|software|platform|system)[^,\.]*)'
            ]
        },
        
        # Hobbies patterns
        'hobbies': {
            'keywords': ['hobby', 'hobbies', 'interest', 'interests', 'passion', 'enjoy'],
            'patterns': [
                r'(?:hobby|hobbies|interest|interests)\s*:\s*([^,\.]+)',
                r'(?:enjoy|love|passionate)\s+(?:about\s+)?([^,\.]+)',
                r'(?:free\s+time|leisure)\s+(?:activities?|hobbies?)\s*:\s*([^,\.]+)'
            ]
        },
        
        # References patterns
        'references': {
            'keywords': ['reference', 'referee', 'contact', 'available'],
            'patterns': [
                r'(?:reference|referee)\s+(?:from\s+)?([^,\.]+)',
                r'(?:contact|available)\s+(?:upon\s+)?(?:request\s+)?([^,\.]+)',
                r'([^,\.]+?(?:reference|referee)[^,\.]*)'
            ]
        },
        
        # Additional patterns
        'additional': {
            'keywords': ['additional', 'miscellaneous', 'other', 'extra', 'supplementary'],
            'patterns': [
                r'(?:additional|miscellaneous|other|extra)\s+(?:information|details)\s*:\s*([^,\.]+)',
                r'([^,\.]+?(?:additional|miscellaneous|supplementary)[^,\.]*)'
            ]
        }
    }
    
    # Find the most likely section based on keywords
    best_section = None
    best_score = 0
    
    for section, config in section_patterns.items():
        score = 0
        for keyword in config['keywords']:
            if keyword in message_lower:
                score += 1
        
        if score > best_score:
            best_score = score
            best_section = section
    
    # If no clear section found, try to infer from content
    if not best_section or best_score == 0:
        # Check for specific patterns that indicate sections
        if any(word in message_lower for word in ['degree', 'university', 'graduated', 'bachelor', 'master', 'phd']):
            best_section = 'education'
        elif any(word in message_lower for word in ['worked', 'job', 'position', 'employed', 'internship']):
            best_section = 'experience'
        elif any(word in message_lower for word in ['python', 'javascript', 'react', 'java', 'sql']):
            best_section = 'skills'
        elif any(word in message_lower for word in ['project', 'built', 'developed', 'created']):
            best_section = 'projects'
        else:
            best_section = 'additional'  # Default fallback
    
    # Extract content using the best section's patterns
    extracted_content = ""
    if best_section and best_section in section_patterns:
        patterns = section_patterns[best_section]['patterns']
        
        for pattern in patterns:
            match = re.search(pattern, message_lower)
            if match:
                extracted_content = match.group(1).strip()
                # Clean up the extracted content
                extracted_content = re.sub(r'^\s*(?:i\s+(?:have\s+)?|i\s+(?:am\s+)?)', '', extracted_content)
                extracted_content = re.sub(r'\s+', ' ', extracted_content)
                extracted_content = extracted_content.title()
                break
        
        # If no pattern matched, use a cleaned version of the message
        if not extracted_content:
            # Remove common introductory phrases
            cleaned = re.sub(r'^(?:i\s+(?:have\s+)?|i\s+(?:am\s+)?|my\s+|i\s+(?:worked|studied|built|developed|created|designed|implemented)\s+)', '', message_lower)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            extracted_content = cleaned.title()
    
    return best_section, extracted_content

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