#!/usr/bin/env python3
"""
Debug script to test classification logic
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the classification function
from main_enhanced import classify_message_fallback

def test_classification():
    """Test classification for UPDATE operations"""
    
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
    
    print("🧪 Testing Classification Logic")
    print("=" * 50)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: {message}")
        result = classify_message_fallback(message)
        print(f"   Category: {result.get('category')}")
        print(f"   Operation: {result.get('operation')}")
        
        if result.get('category') == 'OTHER':
            print(f"   ❌ FAILED - Falling back to help message")
        elif 'UPDATE' in result.get('category', ''):
            print(f"   ✅ SUCCESS - Correctly classified as UPDATE")
        else:
            print(f"   ⚠️ PARTIAL - Classified as {result.get('category')}")

if __name__ == "__main__":
    test_classification() 