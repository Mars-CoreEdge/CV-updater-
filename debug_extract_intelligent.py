#!/usr/bin/env python3
"""
Debug script to test extract_intelligent_content function directly.
"""

import re

def extract_intelligent_content_debug(message: str) -> tuple[str, str]:
    """
    Debug version of extract_intelligent_content to see what's happening.
    """
    message_lower = message.lower().strip()
    
    # Auto-detect section based on keywords and patterns
    section_keywords = {
        "skills": ["skill", "technology", "programming", "language", "framework", "tool", "software", "expertise", "proficient", "know", "learned", "mastered"],
        "experience": ["experience", "work", "job", "employment", "position", "role", "responsibility", "led", "managed", "developed", "built", "created", "implemented"],
        "education": ["education", "degree", "university", "college", "school", "graduated", "studied", "certification", "course", "diploma", "masters", "bachelors", "phd"],
        "projects": ["project", "built", "created", "developed", "application", "website", "app", "system", "platform", "tool", "software"],
        "contact": ["contact", "phone", "email", "linkedin", "address", "location", "portfolio", "website"],
        "objective": ["objective", "goal", "career objective", "professional objective", "aim", "target"],
        "certifications": ["certification", "certified", "license", "credential", "training", "certificate"],
        "research": ["research", "publication", "paper", "thesis", "dissertation", "study", "academic"],
        "achievements": ["achievement", "award", "recognition", "honor", "accomplishment", "success", "milestone", "scholarship"],
        "leadership": ["leadership", "led", "managed", "supervised", "directed", "team lead", "manager"],
        "volunteer": ["volunteer", "community service", "charity", "pro bono", "community work"],
        "languages": ["language", "speak", "fluent", "conversational", "native", "bilingual", "proficient in"],
        "technologies": ["tool", "software", "platform", "system", "technology", "technologies", "git"],
        "interests": ["interest", "hobby", "passion", "enjoy", "like", "love", "favorite"],
        "references": ["reference", "referee", "recommendation", "endorsement"],
        "additional": ["additional", "miscellaneous", "other", "extra"]
    }
    
    # Count keyword matches for each section
    section_scores = {}
    for section, keywords in section_keywords.items():
        score = sum(1 for keyword in keywords if keyword in message_lower)
        section_scores[section] = score
        if score > 0:
            print(f"  {section}: {score} matches")
    
    # Find the section with highest score
    detected_section = max(section_scores.items(), key=lambda x: x[1])[0] if section_scores else "skills"
    
    print(f"  Highest score: {detected_section} with {section_scores.get(detected_section, 0)} matches")
    
    # Extract main content (simplified version)
    content = message.strip()
    
    # Remove common prefixes
    prefixes_to_remove = [
        "add", "include", "put", "insert", "add to", "include in", "put in", "insert in",
        "add to my", "include in my", "put in my", "insert in my",
        "add to the", "include in the", "put in the", "insert in the",
        "add to my skills", "add to my experience", "add to my education", "add to my projects",
        "add to skills", "add to experience", "add to education", "add to projects",
        "add skills", "add experience", "add education", "add projects",
        "add to contact", "add to profile", "add to achievements", "add to languages", "add to interests",
        "add '", "add \"", "include '", "include \"", "put '", "put \"", "insert '", "insert \"",
        "complete my project of", "i have completed my", "i completed my", "i graduated with", "i graduated from",
        "i learned", "i am proficient in", "i have experience in", "i led", "i managed", "i developed",
        "i built", "i created", "i designed", "i worked on", "i studied", "i have", "i am", "i can"
    ]
    
    # Remove prefixes (try multiple times to catch nested prefixes)
    for _ in range(3):  # Try up to 3 times
        original_content = content
        for prefix in prefixes_to_remove:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
                break
        if content == original_content:
            break  # No more prefixes found
    
    # Clean up extra whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    
    return content, detected_section

def test_extract_intelligent():
    """Test extract_intelligent_content with objective messages"""
    test_messages = [
        "My career objective is to become a senior software engineer",
        "I aim to lead development teams and deliver innovative solutions"
    ]
    
    print("🧪 Testing extract_intelligent_content")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📋 Test {i}: '{message}'")
        print("-" * 40)
        
        content, detected_section = extract_intelligent_content_debug(message)
        print(f"Extracted content: '{content}'")
        print(f"Detected section: {detected_section}")
        
        if detected_section == "objective":
            print("✅ PASS - Correctly detected objective section")
        else:
            print(f"❌ FAIL - Expected objective, got {detected_section}")

if __name__ == "__main__":
    test_extract_intelligent() 