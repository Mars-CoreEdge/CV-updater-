#!/usr/bin/env python3
"""
Debug script to test classification logic directly for references messages.
"""

import re

def classify_message_fallback_debug(message: str, cv_content: str = None) -> dict:
    """Debug version of classify_message_fallback"""
    msg = message.lower()
    print(f"[DEBUG] classify_message_fallback: message='{message}' (lower='{msg}')")

    # Check REFERENCE_ADD explicit pattern
    print(f"[DEBUG] Checking REFERENCE_ADD explicit: add/insert/put/append in msg? {any(kw in msg for kw in ['add', 'include', 'insert', 'put', 'append'])}, reference/referee/recommendation in msg? {any(kw in msg for kw in ['reference', 'referee', 'recommendation', 'endorsement'])}")
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("reference" in msg or "referee" in msg or "recommendation" in msg or "endorsement" in msg):
        print("[DEBUG] classify_message_fallback: Detected REFERENCE_ADD (explicit)")
        return {"category": "REFERENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}

    # Check REFERENCE_ADD implicit pattern
    print(f"[DEBUG] Checking REFERENCE_ADD implicit: reference/referee/recommendation in msg? {any(kw in msg for kw in ['reference', 'referee', 'recommendation', 'endorsement'])}")
    if ("reference" in msg or "referee" in msg or "recommendation" in msg or "endorsement" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected REFERENCE_ADD (implicit)")
        return {"category": "REFERENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}

    # Check CONTACT_ADD pattern
    print(f"[DEBUG] Checking CONTACT_ADD: my email/phone/linkedin/address in msg? {any(phrase in msg for phrase in ['my email is', 'phone number', 'linkedin', 'address', 'contact me', 'reach me'])}")
    if any(phrase in msg for phrase in ["my email is", "phone number", "linkedin", "address", "contact me", "reach me"]):
        print("[DEBUG] classify_message_fallback: Detected CONTACT_ADD")
        return {"category": "CONTACT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}

    print("[DEBUG] classify_message_fallback: No specific pattern matched, falling back to OTHER")
    return {"category": "OTHER", "extracted_info": message.strip(), "operation": "READ"}

def extract_intelligent_content_debug(message: str) -> tuple[str, str]:
    """Debug version of extract_intelligent_content"""
    message_lower = message.lower().strip()
    
    # Auto-detect section based on keywords and patterns
    section_keywords = {
        "skills": ["skill", "programming", "language", "framework", "expertise", "know", "learned", "mastered"],
        "experience": ["experience", "work", "job", "employment", "position", "role", "responsibility", "led", "managed", "developed", "built", "created", "implemented"],
        "education": ["education", "degree", "university", "college", "school", "graduated", "studied", "certification", "course", "diploma", "masters", "bachelors", "phd"],
        "projects": ["project", "built", "created", "developed", "application", "website", "app", "system", "platform"],
        "contact": ["contact", "phone", "email", "linkedin", "address", "location", "portfolio", "website"],
        "objective": ["objective", "goal", "career objective", "professional objective", "aim", "target"],
        "certifications": ["certification", "certified", "license", "credential", "training", "certificate"],
        "research": ["research", "publication", "paper", "thesis", "dissertation", "study", "academic"],
        "achievements": ["achievement", "award", "recognition", "honor", "accomplishment", "success", "milestone", "scholarship"],
        "leadership": ["leadership", "led", "managed", "supervised", "directed", "team lead", "manager"],
        "volunteer": ["volunteer", "community service", "charity", "pro bono", "community work"],
        "languages": ["language", "speak", "fluent", "conversational", "native", "bilingual", "proficient in"],
        "technologies": ["tool", "software", "platform", "system", "technology", "technologies", "git", "docker", "jenkins", "jira", "confluence", "slack", "proficient with", "skilled in"],
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
    
    return content, detected_section

def test_references_classification():
    """Test classification with references messages"""
    test_messages = [
        "References available upon request",
        "Professional references from Google and Microsoft"
    ]
    
    print("🧪 Testing REFERENCES Classification")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📋 Test {i}: '{message}'")
        print("-" * 40)
        
        # Test classify_message_fallback
        print("Testing classify_message_fallback:")
        result = classify_message_fallback_debug(message)
        print(f"Classification result: {result}")
        
        if result["category"] == "REFERENCE_ADD":
            print("✅ PASS - Correctly classified as REFERENCE_ADD")
        else:
            print(f"❌ FAIL - Expected REFERENCE_ADD, got {result['category']}")
        
        # Test extract_intelligent_content
        print("\nTesting extract_intelligent_content:")
        content, detected_section = extract_intelligent_content_debug(message)
        print(f"Extracted content: '{content}'")
        print(f"Detected section: {detected_section}")
        
        if detected_section == "references":
            print("✅ PASS - Correctly detected references section")
        else:
            print(f"❌ FAIL - Expected references, got {detected_section}")

if __name__ == "__main__":
    test_references_classification() 