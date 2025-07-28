#!/usr/bin/env python3
"""
Simple test for classification patterns
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
    
    # Define the patterns from the backend (updated)
    update_patterns = [
        (["update objective", "change goal", "modify objective", "objective to", "goal to"], "OBJECTIVE_UPDATE"),
        (["update certification", "change license", "modify credential", "certification to", "license to"], "CERTIFICATION_UPDATE"),
        (["update research", "change publication", "modify paper", "research to", "publication to"], "RESEARCH_UPDATE"),
        (["update award", "change achievement", "modify honor", "achievement to", "award to"], "ACHIEVEMENT_UPDATE"),
        (["update leadership", "change management", "modify role", "leadership to", "role to"], "LEADERSHIP_UPDATE"),
        (["update volunteer", "change service", "modify charity", "volunteer to", "service to", "volunteer work to"], "VOLUNTEER_UPDATE"),
        (["update language", "change language skill", "modify language", "language to", "language skill to", "language skills to"], "LANGUAGE_UPDATE"),
        (["update tool", "change technology", "modify software", "technology to", "tool to", "technologies to"], "TECHNOLOGY_UPDATE"),
        (["update hobby", "change interest", "modify passion", "interest to", "hobby to", "interests to"], "INTEREST_UPDATE"),
        (["update reference", "change referee", "modify recommendation", "reference to", "referee to", "references to"], "REFERENCE_UPDATE"),
        (["update additional", "change miscellaneous", "modify other", "additional to", "miscellaneous to", "additional info to"], "ADDITIONAL_UPDATE")
    ]
    
    print("🧪 Testing UPDATE Pattern Matching (Updated)")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: {message}")
        msg = message.lower()
        
        matched = False
        for patterns, category in update_patterns:
            if any(phrase in msg for phrase in patterns):
                print(f"   ✅ MATCHED: {category}")
                matched = True
                break
        
        if not matched:
            print(f"   ❌ NO MATCH - Would fall back to help message")

if __name__ == "__main__":
    test_update_patterns() 