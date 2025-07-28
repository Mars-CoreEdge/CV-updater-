#!/usr/bin/env python3
"""
Test UPDATE operation patterns specifically
"""

def test_update_patterns():
    """Test the UPDATE operation patterns"""
    
    test_messages = [
        "Update my objective to focus on AI development",
        "Change my certification to include AWS Solutions Architect",
        "Modify my research to include blockchain applications",
        "Update my achievement to include Best Developer Award",
        "Change my leadership role to Senior Team Lead",
        "Update my volunteer work to include disaster relief",
        "Modify my language skills to include Italian",
        "Update my technologies to include GraphQL",
        "Change my interests to include rock climbing",
        "Update my references to include current manager",
        "Modify additional info to include travel availability"
    ]
    
    print("🧪 Testing UPDATE Pattern Matching")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: {message}")
        msg = message.lower()
        
        # Test each UPDATE pattern
        update_patterns = [
            ("OBJECTIVE_UPDATE", ["update", "change", "modify"], ["objective", "goal", "career objective", "professional objective"]),
            ("CERTIFICATION_UPDATE", ["update", "change", "modify"], ["certification", "license", "certificate", "credential", "training"]),
            ("RESEARCH_UPDATE", ["update", "change", "modify"], ["research", "publication", "paper", "thesis", "dissertation"]),
            ("ACHIEVEMENT_UPDATE", ["update", "change", "modify"], ["award", "honor", "achievement", "recognition", "scholarship"]),
            ("LEADERSHIP_UPDATE", ["update", "change", "modify"], ["leadership", "led", "managed", "supervised", "directed"]),
            ("VOLUNTEER_UPDATE", ["update", "change", "modify"], ["volunteer", "community service", "charity", "pro bono"]),
            ("LANGUAGE_UPDATE", ["update", "change", "modify"], ["language", "speak", "fluent in", "proficient in"]),
            ("TECHNOLOGY_UPDATE", ["update", "change", "modify"], ["tool", "technology", "software", "framework", "platform"]),
            ("INTEREST_UPDATE", ["update", "change", "modify"], ["hobby", "interest", "passion", "enjoy", "like to"]),
            ("REFERENCE_UPDATE", ["update", "change", "modify"], ["reference", "referee", "recommendation"]),
            ("ADDITIONAL_UPDATE", ["update", "change", "modify"], ["additional", "miscellaneous", "other", "extra"])
        ]
        
        matched = False
        for category, action_keywords, section_keywords in update_patterns:
            has_action = any(phrase in msg for phrase in action_keywords)
            has_section = any(phrase in msg for phrase in section_keywords)
            
            if has_action and has_section:
                print(f"   ✅ MATCHED: {category}")
                print(f"      Action keywords found: {[kw for kw in action_keywords if kw in msg]}")
                print(f"      Section keywords found: {[kw for kw in section_keywords if kw in msg]}")
                matched = True
                break
            elif has_action:
                print(f"   ⚠️ PARTIAL: {category} - Found action keywords but no section keywords")
                print(f"      Action keywords found: {[kw for kw in action_keywords if kw in msg]}")
            elif has_section:
                print(f"   ⚠️ PARTIAL: {category} - Found section keywords but no action keywords")
                print(f"      Section keywords found: {[kw for kw in section_keywords if kw in msg]}")
        
        if not matched:
            print(f"   ❌ NO MATCH - Would fall back to help message")

if __name__ == "__main__":
    test_update_patterns() 