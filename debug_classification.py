#!/usr/bin/env python3
"""
Debug script to test classification logic directly.
"""

import re

def classify_message_fallback_debug(message: str, cv_content: str = None) -> dict:
    """Debug version of classify_message_fallback"""
    msg = message.lower()
    print(f"[DEBUG] classify_message_fallback: message='{message}' (lower='{msg}')")

    # SPECIFIC ADD OPERATIONS - Check these FIRST before any other patterns
    print(f"[DEBUG] UPDATED CODE VERSION - Checking OBJECTIVE_ADD: add/insert/put/append in msg? {any(kw in msg for kw in ['add', 'include', 'insert', 'put', 'append'])}, objective/goal in msg? {any(kw in msg for kw in ['objective', 'goal', 'career objective', 'professional objective'])}")
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("objective" in msg or "goal" in msg or "career objective" in msg or "professional objective" in msg):
        print("[DEBUG] classify_message_fallback: Detected OBJECTIVE_ADD")
        return {"category": "OBJECTIVE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    
    # IMPLICIT ADD OPERATIONS - For messages without explicit "add" words
    if ("objective" in msg or "goal" in msg or "career objective" in msg or "professional objective" in msg or "aim" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected OBJECTIVE_ADD (implicit)")
        return {"category": "OBJECTIVE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    
    # If no specific pattern matches, return help
    print("[DEBUG] classify_message_fallback: No pattern matched, returning CV_HELP")
    return {"category": "CV_HELP", "extracted_info": message.strip(), "operation": "READ"}

def test_classification():
    """Test classification with objective messages"""
    test_messages = [
        "My career objective is to become a senior software engineer",
        "I aim to lead development teams and deliver innovative solutions"
    ]
    
    print("🧪 Testing Classification Logic")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📋 Test {i}: '{message}'")
        print("-" * 40)
        
        result = classify_message_fallback_debug(message)
        print(f"Result: {result}")
        
        if result.get("category") == "OBJECTIVE_ADD":
            print("✅ PASS - Correctly classified as OBJECTIVE_ADD")
        else:
            print(f"❌ FAIL - Expected OBJECTIVE_ADD, got {result.get('category')}")

if __name__ == "__main__":
    test_classification() 