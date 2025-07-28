#!/usr/bin/env python3
"""
Test CREATE operation patterns
"""

def test_create_patterns():
    """Test the CREATE operation patterns"""
    
    test_messages = [
        "Add my objective: To become a senior software engineer in a leading tech company",
        "Add my certification: Microsoft Azure Developer Associate",
        "Add my research: Machine Learning Applications in Healthcare",
        "Add my achievement: Employee of the Year 2023",
        "Add my leadership role: Technical Lead for 10-person team",
        "Add my volunteer work: Teaching coding to underprivileged youth",
        "Add my language skill: German (Conversational)",
        "Add my technology: MongoDB, Redis, Elasticsearch",
        "Add my interest: Playing guitar, mountain biking",
        "Add my reference: Dr. Smith, Professor at University",
        "Add additional info: Available for remote work"
    ]
    
    # Current patterns from backend
    create_patterns = [
        (["objective", "goal", "career objective", "professional objective"], ["add", "include", "insert", "put"], "OBJECTIVE_ADD"),
        (["certification", "license", "certificate", "credential", "training"], ["add", "include", "insert", "put"], "CERTIFICATION_ADD"),
        (["research", "publication", "paper", "thesis", "dissertation"], ["add", "include", "insert", "put"], "RESEARCH_ADD"),
        (["award", "honor", "achievement", "recognition", "scholarship"], ["add", "include", "insert", "put"], "ACHIEVEMENT_ADD"),
        (["leadership", "led", "managed", "supervised", "directed"], ["add", "include", "insert", "put"], "LEADERSHIP_ADD"),
        (["volunteer", "community service", "charity", "pro bono"], ["add", "include", "insert", "put"], "VOLUNTEER_ADD"),
        (["language", "speak", "fluent in", "proficient in"], ["add", "include", "insert", "put"], "LANGUAGE_ADD"),
        (["tool", "technology", "software", "framework", "platform"], ["add", "include", "insert", "put"], "TECHNOLOGY_ADD"),
        (["hobby", "interest", "passion", "enjoy", "like to"], ["add", "include", "insert", "put"], "INTEREST_ADD"),
        (["reference", "referee", "recommendation"], ["add", "include", "insert", "put"], "REFERENCE_ADD"),
        (["additional", "miscellaneous", "other", "extra"], ["add", "include", "insert", "put"], "ADDITIONAL_ADD")
    ]
    
    print("🧪 Testing CREATE Pattern Matching")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: {message}")
        msg = message.lower()
        
        matched = False
        for section_keywords, action_keywords, category in create_patterns:
            has_section = any(phrase in msg for phrase in section_keywords)
            has_action = any(phrase in msg for phrase in action_keywords)
            
            if has_section and has_action:
                print(f"   ✅ MATCHED: {category}")
                print(f"      Section keywords found: {[kw for kw in section_keywords if kw in msg]}")
                print(f"      Action keywords found: {[kw for kw in action_keywords if kw in msg]}")
                matched = True
                break
            elif has_section:
                print(f"   ⚠️ PARTIAL: Found section keywords but no action keywords")
                print(f"      Section keywords found: {[kw for kw in section_keywords if kw in msg]}")
            elif has_action:
                print(f"   ⚠️ PARTIAL: Found action keywords but no section keywords")
                print(f"      Action keywords found: {[kw for kw in action_keywords if kw in msg]}")
        
        if not matched:
            print(f"   ❌ NO MATCH - Would fall back to help message")

if __name__ == "__main__":
    test_create_patterns() 