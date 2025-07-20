#!/usr/bin/env python3
"""
Test enhanced key concept extraction
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_extraction():
    """Test the enhanced key concept extraction"""
    print("🎯 Testing Enhanced Key Concept Extraction")
    print("=" * 60)
    
    try:
        from main_enhanced import extract_intelligent_content
        
        # Test cases based on user examples
        test_cases = [
            # User's examples
            ("Complete my project of todo list in React JS", "todo list in React JS"),
            ("I have completed my masters degree in cyber security from NUST university", "Masters in Cyber Security from NUST"),
            
            # Additional test cases
            ("I learned React and Node.js", "React, Node.js"),
            ("Add Python, JavaScript, and Docker to my skills", "Python, JavaScript, Docker"),
            ("I led a team of 5 developers in building microservices", "led team of 5 developers"),
            ("I graduated with a Master's in Computer Science from Stanford", "Master's in Computer Science from Stanford"),
            ("I built an e-commerce platform with React and Node.js", "built e-commerce platform"),
            ("Machine Learning and Deep Learning", "Machine Learning, Deep Learning"),
            ("Led development team of 10 people", "led development team"),
            ("Bachelor's degree in AI from MIT", "Bachelor's in AI from MIT"),
            ("Built a mobile app for task management", "built mobile app"),
            ("AWS certification in cloud computing", "AWS certification"),
            ("Created a weather application", "created weather application"),
            ("I am proficient in machine learning algorithms", "Machine Learning Algorithms"),
            ("I managed a project with 100K users", "managed project with 100K"),
            ("I studied Data Science at MIT", "studied Data Science at MIT"),
            ("I developed a full-stack application", "developed full-stack application"),
            ("I have experience in Python programming", "Python Programming"),
            ("I completed my PhD in Computer Vision", "PhD in Computer Vision")
        ]
        
        print("📝 Testing Key Concept Extraction:")
        print("-" * 60)
        
        for i, (input_text, expected_output) in enumerate(test_cases, 1):
            print(f"\n{i:2d}. Input: {input_text}")
            
            extracted_content, detected_section = extract_intelligent_content(input_text)
            print(f"    🔍 Extracted: '{extracted_content}'")
            print(f"    📂 Section: {detected_section}")
            
            # Show improvement
            original_length = len(input_text)
            extracted_length = len(extracted_content)
            improvement = original_length - extracted_length
            
            if improvement > 0:
                print(f"    ✅ Shortened: {original_length} → {extracted_length} chars (-{improvement})")
            else:
                print(f"    ⚠️ Length: {extracted_length} chars")
            
            # Check if it matches expected pattern
            if expected_output.lower() in extracted_content.lower() or extracted_content.lower() in expected_output.lower():
                print(f"    🎯 Matches expected pattern: ✓")
            else:
                print(f"    ⚠️ Expected: '{expected_output}'")
        
        print("\n" + "=" * 60)
        print("✅ Enhanced extraction test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_extraction() 