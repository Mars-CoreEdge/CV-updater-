#!/usr/bin/env python3
"""
Local test for intelligent content extraction
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_extraction():
    """Test the intelligent content extraction locally"""
    print("🧠 Testing Intelligent Content Extraction (Local)")
    print("=" * 60)
    
    try:
        from main_enhanced import extract_intelligent_content
        
        # Test messages
        test_messages = [
            "I learned React and Node.js",
            "Add Python, JavaScript, and Docker to my skills",
            "I led a team of 5 developers in building microservices",
            "I graduated with a Master's in Computer Science from Stanford",
            "I built an e-commerce platform with React and Node.js",
            "Machine Learning",
            "Led development team",
            "Master's degree in AI",
            "Built a mobile app",
            "Add 'Led a team of 5 developers in building a microservices architecture' to my experience section",
            "Add 'Master of Science in Computer Science from Stanford University (2020-2022)' to my education section"
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 Test {i}: {message}")
            
            extracted_content, detected_section = extract_intelligent_content(message)
            print(f"   🔍 Extracted: '{extracted_content}'")
            print(f"   📂 Detected Section: {detected_section}")
            
            # Show improvement
            if len(extracted_content) < len(message):
                print(f"   ✅ Content shortened: {len(message)} → {len(extracted_content)} characters")
            else:
                print(f"   ⚠️ Content length: {len(extracted_content)} characters")
        
        print("\n" + "=" * 60)
        print("✅ Local extraction test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extraction() 