#!/usr/bin/env python3
"""
Test the OBJECTIVE_ADD pattern logic standalone
"""

def test_objective_add_pattern():
    """Test the OBJECTIVE_ADD pattern logic"""
    
    message = "Add my objective: To become a senior software engineer in a leading tech company"
    msg = message.lower()
    
    print("🧪 Testing OBJECTIVE_ADD Pattern Logic")
    print("=" * 50)
    print(f"Original message: '{message}'")
    print(f"Lowercase message: '{msg}'")
    print()
    
    # Test the pattern logic
    action_keywords = ["add", "include", "insert", "put", "append"]
    section_keywords = ["objective", "goal", "career objective", "professional objective"]
    
    print("Testing action keywords:")
    for kw in action_keywords:
        found = kw in msg
        print(f"  '{kw}' in msg: {found}")
    
    print("\nTesting section keywords:")
    for kw in section_keywords:
        found = kw in msg
        print(f"  '{kw}' in msg: {found}")
    
    print("\nPattern logic:")
    has_action = any(kw in msg for kw in action_keywords)
    has_section = any(kw in msg for kw in section_keywords)
    
    print(f"  has_action = any(kw in msg for kw in {action_keywords}) = {has_action}")
    print(f"  has_section = any(kw in msg for kw in {section_keywords}) = {has_section}")
    print(f"  has_action AND has_section = {has_action and has_section}")
    
    if has_action and has_section:
        print("✅ PATTERN SHOULD MATCH!")
    else:
        print("❌ PATTERN SHOULD NOT MATCH!")

if __name__ == "__main__":
    test_objective_add_pattern() 