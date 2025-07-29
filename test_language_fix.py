#!/usr/bin/env python3
"""
Test to verify that Chinese language is correctly classified as languages section
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
        # Skills patterns
        'skills': {
            'keywords': ['skills', 'skilled', 'proficient', 'expertise', 'technologies', 'tools', 'frameworks'],
            'patterns': [
                r'(?:skilled|proficient|expert|knowledge)\s+(?:in\s+)?([^,\.]+)',
                r'(?:technologies?|tools?|frameworks?|skills?)\s*:\s*([^,\.]+)',
                r'(?:i\s+(?:am\s+)?(?:skilled|proficient|expert)\s+in\s+)?([^,\.]+)',
                r'([a-zA-Z\s,]+(?:python|javascript|java|c\+\+|react|node|angular|vue|sql|aws|docker|kubernetes|git|html|css|php|ruby|go|rust|swift|kotlin)[a-zA-Z\s,]*)'
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
        }
    }
    
    # Find the most likely section based on keywords
    best_section = None
    best_score = 0
    
    # First, check for specific language indicators (highest priority)
    language_indicators = ['chinese', 'english', 'spanish', 'french', 'german', 'italian', 'portuguese', 'russian', 'japanese', 'korean', 'arabic', 'hindi', 'urdu', 'bengali', 'tamil', 'telugu', 'marathi', 'gujarati', 'kannada', 'malayalam', 'punjabi', 'sindhi', 'nepali', 'thai', 'vietnamese', 'indonesian', 'malay', 'filipino', 'tagalog', 'dutch', 'swedish', 'norwegian', 'danish', 'finnish', 'polish', 'czech', 'slovak', 'hungarian', 'romanian', 'bulgarian', 'serbian', 'croatian', 'greek', 'turkish', 'hebrew', 'persian', 'farsi', 'kurdish', 'armenian', 'georgian', 'mongolian', 'tibetan', 'lao', 'cambodian', 'khmer', 'burmese', 'myanmar']
    
    # Check if the message contains specific language names
    for language in language_indicators:
        if language in message_lower:
            best_section = 'languages'
            best_score = 10  # High priority for language detection
            break
    
    # If no specific language found, check other sections
    if not best_section:
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
            cleaned = re.sub(r'^(?:i\s+(?:have\s+)?|i\s+(?:am\s+)?|my\s+|i\s+(?:worked|studied|built|developed|created|designed|implemented|designed|implemented)\s+)', '', message_lower)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            extracted_content = cleaned.title()
    
    return best_section, extracted_content

def test_language_classification():
    """Test language classification"""
    
    test_cases = [
        ("chinese language", "languages", "Chinese Language"),
        ("I speak Chinese", "languages", "Chinese"),
        ("Fluent in English", "languages", "English"),
        ("Python programming", "skills", "Python Programming"),
        ("JavaScript development", "skills", "Javascript Development"),
    ]
    
    print("🧪 Testing Language Classification Fix")
    print("=" * 50)
    
    for i, (input_text, expected_section, expected_content) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{input_text}'")
        print(f"   Expected: {expected_section} → '{expected_content}'")
        
        detected_section, extracted_content = extract_universal_cv_content(input_text)
        print(f"   Result:   {detected_section} → '{extracted_content}'")
        
        if detected_section == expected_section:
            print(f"   ✅ Section correct!")
        else:
            print(f"   ❌ Section wrong! Expected '{expected_section}', got '{detected_section}'")
        
        if expected_content.lower() in extracted_content.lower() or extracted_content.lower() in expected_content.lower():
            print(f"   ✅ Content similar!")
        else:
            print(f"   ❌ Content different! Expected '{expected_content}', got '{extracted_content}'")

if __name__ == "__main__":
    test_language_classification() 