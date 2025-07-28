#!/usr/bin/env python3
"""
Test specific failing patterns in isolation
"""

def test_specific_patterns():
    """Test the specific failing patterns"""
    
    failing_messages = [
        "Add my objective: To become a senior software engineer",
        "Add additional info: Available for remote work",
        "Update my objective to focus on AI development",
        "Modify my research to include blockchain applications",
        "Update my achievement to include Best Developer Award",
        "Change my leadership role to Senior Team Lead",
        "Update my volunteer work to include disaster relief",
        "Change my interests to include rock climbing",
        "Update my references to include current manager",
        "Modify additional info to include travel availability"
    ]
    
    print("🧪 Testing Specific Failing Patterns")
    print("=" * 50)
    
    for i, message in enumerate(failing_messages, 1):
        print(f"\n{i}. Testing: {message}")
        msg = message.lower()
        
        # Test each pattern in the exact order they appear in the backend
        patterns = [
            # OBJECTIVE patterns
            ("OBJECTIVE_ADD", ["add", "include", "insert", "put", "append", "objective", "goal", "career objective", "professional objective", "aim", "target"], ["objective", "goal", "career objective", "professional objective"]),
            ("OBJECTIVE_UPDATE", ["update", "change", "modify"], ["objective", "goal", "career objective", "professional objective"]),
            
            # ADDITIONAL patterns
            ("ADDITIONAL_ADD", ["add", "include", "insert", "put", "append", "additional", "miscellaneous", "other", "extra", "supplementary", "further"], ["additional", "miscellaneous", "other", "extra"]),
            ("ADDITIONAL_UPDATE", ["update", "change", "modify"], ["additional", "miscellaneous", "other", "extra"]),
            
            # RESEARCH patterns
            ("RESEARCH_ADD", ["add", "include", "insert", "put", "append", "research", "publication", "paper", "thesis", "dissertation", "study", "investigation"], ["research", "publication", "paper", "thesis", "dissertation"]),
            ("RESEARCH_UPDATE", ["update", "change", "modify"], ["research", "publication", "paper", "thesis", "dissertation"]),
            
            # ACHIEVEMENT patterns
            ("ACHIEVEMENT_ADD", ["add", "include", "insert", "put", "append", "award", "honor", "achievement", "recognition", "scholarship", "prize", "accomplishment"], ["award", "honor", "achievement", "recognition", "scholarship"]),
            ("ACHIEVEMENT_UPDATE", ["update", "change", "modify"], ["award", "honor", "achievement", "recognition", "scholarship"]),
            
            # LEADERSHIP patterns
            ("LEADERSHIP_ADD", ["add", "include", "insert", "put", "append", "leadership", "led", "managed", "supervised", "directed", "team lead", "management"], ["leadership", "led", "managed", "supervised", "directed"]),
            ("LEADERSHIP_UPDATE", ["update", "change", "modify"], ["leadership", "led", "managed", "supervised", "directed"]),
            
            # VOLUNTEER patterns
            ("VOLUNTEER_ADD", ["add", "include", "insert", "put", "append", "volunteer", "community service", "charity", "pro bono", "social work", "helping"], ["volunteer", "community service", "charity", "pro bono"]),
            ("VOLUNTEER_UPDATE", ["update", "change", "modify"], ["volunteer", "community service", "charity", "pro bono"]),
            
            # INTEREST patterns
            ("INTEREST_ADD", ["add", "include", "insert", "put", "append", "hobby", "interest", "passion", "enjoy", "like to", "enjoyment", "leisure"], ["hobby", "interest", "passion", "enjoy", "like to"]),
            ("INTEREST_UPDATE", ["update", "change", "modify"], ["hobby", "interest", "passion", "enjoy", "like to"]),
            
            # REFERENCE patterns
            ("REFERENCE_ADD", ["add", "include", "insert", "put", "append", "reference", "referee", "recommendation", "endorsement", "testimonial"], ["reference", "referee", "recommendation", "endorsement"]),
            ("REFERENCE_UPDATE", ["update", "change", "modify"], ["reference", "referee", "recommendation", "endorsement"])
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

if __name__ == "__main__":
    test_specific_patterns() 