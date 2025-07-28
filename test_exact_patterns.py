#!/usr/bin/env python3
"""
Test exact failing patterns in isolation
"""

def test_exact_patterns():
    """Test the exact failing patterns"""
    
    failing_messages = [
        "Add my objective: To become a senior software engineer in a leading tech company",
        "Add my interest: Playing guitar, mountain biking",
        "Add additional info: Available for remote work",
        "Update my objective to focus on AI development",
        "Modify my research to include blockchain applications",
        "Update my achievement to include Best Developer Award",
        "Change my leadership role to Senior Team Lead",
        "Change my interests to include rock climbing",
        "Update my references to include current manager",
        "Modify additional info to include travel availability"
    ]
    
    print("🧪 Testing Exact Failing Patterns")
    print("=" * 50)
    
    for i, message in enumerate(failing_messages, 1):
        print(f"\n{i}. Testing: {message}")
        msg = message.lower()
        
        # Test each pattern in the exact order they appear in the backend
        patterns = [
            # UPDATE patterns (should be checked first)
            ("OBJECTIVE_UPDATE", ["update", "change", "modify"], ["objective", "goal", "career objective", "professional objective"]),
            ("RESEARCH_UPDATE", ["update", "change", "modify"], ["research", "publication", "paper", "thesis", "dissertation"]),
            ("ACHIEVEMENT_UPDATE", ["update", "change", "modify"], ["award", "honor", "achievement", "recognition", "scholarship"]),
            ("LEADERSHIP_UPDATE", ["update", "change", "modify"], ["leadership", "led", "managed", "supervised", "directed"]),
            ("INTEREST_UPDATE", ["update", "change", "modify"], ["hobby", "interest", "passion", "enjoy", "like to"]),
            ("REFERENCE_UPDATE", ["update", "change", "modify"], ["reference", "referee", "recommendation", "endorsement"]),
            ("ADDITIONAL_UPDATE", ["update", "change", "modify"], ["additional", "miscellaneous", "other", "extra"]),
            
            # ADD patterns (should be checked after UPDATE)
            ("OBJECTIVE_ADD", ["add", "include", "insert", "put", "append"], ["objective", "goal", "career objective", "professional objective"]),
            ("INTEREST_ADD", ["add", "include", "insert", "put", "append"], ["hobby", "interest", "passion", "enjoy", "like to"]),
            ("ADDITIONAL_ADD", ["add", "include", "insert", "put", "append"], ["additional", "miscellaneous", "other", "extra"])
        ]
        
        matched = False
        for category, action_keywords, section_keywords in patterns:
            has_action = any(phrase in msg for phrase in action_keywords)
            has_section = any(phrase in msg for phrase in section_keywords)
            
            if has_action and has_section:
                print(f"   ✅ MATCHED: {category}")
                print(f"      Action keywords found: {[kw for kw in action_keywords if kw in msg]}")
                print(f"      Section keywords found: {[kw for kw in section_keywords if kw in msg]}")
                matched = True
                break
        
        if not matched:
            print(f"   ❌ NO MATCH - Would fall back to help message")
            # Debug what keywords are found
            all_action_keywords = ["add", "include", "insert", "put", "append", "update", "change", "modify"]
            all_section_keywords = ["objective", "goal", "career objective", "professional objective", "hobby", "interest", "passion", "enjoy", "like to", "additional", "miscellaneous", "other", "extra", "research", "publication", "paper", "thesis", "dissertation", "award", "honor", "achievement", "recognition", "scholarship", "leadership", "led", "managed", "supervised", "directed", "reference", "referee", "recommendation", "endorsement"]
            
            found_actions = [kw for kw in all_action_keywords if kw in msg]
            found_sections = [kw for kw in all_section_keywords if kw in msg]
            
            print(f"      Found action keywords: {found_actions}")
            print(f"      Found section keywords: {found_sections}")

if __name__ == "__main__":
    test_exact_patterns() 