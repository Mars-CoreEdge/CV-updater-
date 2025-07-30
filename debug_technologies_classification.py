#!/usr/bin/env python3
"""
Debug script to test classification logic directly for technologies messages.
"""

import re

def classify_message_fallback_debug(message: str, cv_content: str = None) -> dict:
    """Debug version of classify_message_fallback"""
    msg = message.lower()
    print(f"[DEBUG] classify_message_fallback: message='{message}' (lower='{msg}')")

    # Check TECHNOLOGY_ADD explicit pattern
    print(f"[DEBUG] Checking TECHNOLOGY_ADD explicit: add/insert/put/append in msg? {any(kw in msg for kw in ['add', 'include', 'insert', 'put', 'append'])}, tool/technology/software in msg? {any(kw in msg for kw in ['tool', 'technology', 'technologies', 'software', 'platform', 'system'])}")
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("tool" in msg or "technology" in msg or "technologies" in msg or "software" in msg or "platform" in msg or "system" in msg):
        print("[DEBUG] classify_message_fallback: Detected TECHNOLOGY_ADD (explicit)")
        return {"category": "TECHNOLOGY_ADD", "extracted_info": message.strip(), "operation": "CREATE"}

    # Check TECHNOLOGY_ADD implicit pattern
    print(f"[DEBUG] Checking TECHNOLOGY_ADD implicit: tool/software/platform/system/git/proficient with/skilled in in msg? {any(kw in msg for kw in ['tool', 'software', 'platform', 'system', 'git', 'proficient with', 'skilled in'])}")
    if ("tool" in msg or "software" in msg or "platform" in msg or "system" in msg or "git" in msg or "proficient with" in msg or "skilled in" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected TECHNOLOGY_ADD (implicit)")
        return {"category": "TECHNOLOGY_ADD", "extracted_info": message.strip(), "operation": "CREATE"}

    # Check SKILL_ADD pattern
    print(f"[DEBUG] Checking SKILL_ADD: add/insert/put/append in msg? {any(kw in msg for kw in ['add', 'include', 'insert', 'put', 'append'])}, skill/programming/language in msg? {any(kw in msg for kw in ['skill', 'programming', 'language', 'framework', 'expertise', 'know', 'learned', 'mastered'])}")
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("skill" in msg or "programming" in msg or "language" in msg or "framework" in msg or "expertise" in msg or "know" in msg or "learned" in msg or "mastered" in msg):
        print("[DEBUG] classify_message_fallback: Detected SKILL_ADD")
        return {"category": "SKILL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}

    # Check SKILL_ADD implicit pattern
    print(f"[DEBUG] Checking SKILL_ADD implicit: skill/programming/language in msg? {any(kw in msg for kw in ['skill', 'programming', 'language', 'framework', 'expertise', 'know', 'learned', 'mastered'])}")
    if ("skill" in msg or "programming" in msg or "language" in msg or "framework" in msg or "expertise" in msg or "know" in msg or "learned" in msg or "mastered" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected SKILL_ADD (implicit)")
        return {"category": "SKILL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}

    print("[DEBUG] classify_message_fallback: No specific pattern matched, falling back to CV_HELP")
    return {"category": "CV_HELP", "extracted_info": message.strip(), "operation": "READ"}

def test_technologies_classification():
    """Test classification with technologies messages"""
    test_messages = [
        "Proficient with Git, Docker, and Jenkins",
        "Skilled in Jira, Confluence, and Slack"
    ]
    
    print("🧪 Testing TECHNOLOGIES Classification")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📋 Test {i}: '{message}'")
        print("-" * 40)
        
        result = classify_message_fallback_debug(message)
        print(f"Classification result: {result}")
        
        if result["category"] == "TECHNOLOGY_ADD":
            print("✅ PASS - Correctly classified as TECHNOLOGY_ADD")
        else:
            print(f"❌ FAIL - Expected TECHNOLOGY_ADD, got {result['category']}")

if __name__ == "__main__":
    test_technologies_classification() 