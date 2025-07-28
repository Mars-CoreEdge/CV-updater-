#!/usr/bin/env python3
"""
Test classification order to identify conflicts
"""

def test_classification_order():
    """Test the classification order to find conflicts"""
    
    test_messages = [
        "Add my objective: To become a senior software engineer",
        "Add my certification: Microsoft Azure Developer Associate",
        "Add my research: Machine Learning Applications",
        "Add my achievement: Employee of the Year 2023",
        "Add my leadership role: Technical Lead",
        "Add my volunteer work: Teaching coding",
        "Add my language skill: German",
        "Add my technology: MongoDB",
        "Add my interest: Playing guitar",
        "Add my reference: Dr. Smith",
        "Add additional info: Available for remote work"
    ]
    
    print("🧪 Testing Classification Order")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: {message}")
        msg = message.lower()
        
        # Test each pattern in order
        patterns = [
            ("OBJECTIVE_ADD", ["objective", "goal", "career objective", "professional objective"], ["add", "include", "insert", "put"]),
            ("CERTIFICATION_ADD", ["certification", "license", "certificate", "credential", "training"], ["add", "include", "insert", "put"]),
            ("RESEARCH_ADD", ["research", "publication", "paper", "thesis", "dissertation"], ["add", "include", "insert", "put"]),
            ("ACHIEVEMENT_ADD", ["award", "honor", "achievement", "recognition", "scholarship"], ["add", "include", "insert", "put"]),
            ("LEADERSHIP_ADD", ["leadership", "led", "managed", "supervised", "directed"], ["add", "include", "insert", "put"]),
            ("VOLUNTEER_ADD", ["volunteer", "community service", "charity", "pro bono"], ["add", "include", "insert", "put"]),
            ("LANGUAGE_ADD", ["language", "speak", "fluent in", "proficient in"], ["add", "include", "insert", "put"]),
            ("TECHNOLOGY_ADD", ["tool", "technology", "software", "framework", "platform"], ["add", "include", "insert", "put"]),
            ("INTEREST_ADD", ["hobby", "interest", "passion", "enjoy", "like to"], ["add", "include", "insert", "put"]),
            ("REFERENCE_ADD", ["reference", "referee", "recommendation"], ["add", "include", "insert", "put"]),
            ("ADDITIONAL_ADD", ["additional", "miscellaneous", "other", "extra"], ["add", "include", "insert", "put"]),
            # Legacy patterns that might interfere
            ("EDUCATION_ADD (LEGACY)", ["degree", "certification", "education"], []),
        ]
        
        matched = False
        for category, section_keywords, action_keywords in patterns:
            has_section = any(phrase in msg for phrase in section_keywords)
            has_action = len(action_keywords) == 0 or any(phrase in msg for phrase in action_keywords)
            
            if has_section and has_action:
                print(f"   ✅ MATCHED: {category}")
                matched = True
                break
            elif has_section:
                print(f"   ⚠️ PARTIAL: {category} - Found section keywords but no action keywords")
        
        if not matched:
            print(f"   ❌ NO MATCH - Would fall back to help message")

if __name__ == "__main__":
    test_classification_order() 