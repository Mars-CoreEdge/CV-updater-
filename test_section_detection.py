#!/usr/bin/env python3
"""
Test script to verify improved section detection
"""

import requests
import re

def test_section_detection():
    """Test the improved section detection logic"""
    
    base_url = "http://localhost:8081"
    
    print("🧪 Testing Improved Section Detection")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Backend is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it first.")
        return False
    
    # Test 2: Check current CV content for sections
    try:
        response = requests.get(f"{base_url}/cv/current/")
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            print(f"✅ CV content retrieved successfully")
            print(f"   Content length: {len(content)} characters")
            
            # Look for potential section headers
            lines = content.split('\n')
            section_keywords = [
                'PROFILE', 'SUMMARY', 'SKILLS', 'WORK EXPERIENCE', 'EXPERIENCE', 
                'EDUCATION', 'PROJECTS', 'PROFESSIONAL SKILLS', 'TECHNICAL SKILLS', 
                'CONTACT', 'OBJECTIVE', 'QUALIFICATIONS', 'ACHIEVEMENTS', 'CERTIFICATIONS',
                'LANGUAGES', 'INTERESTS', 'REFERENCES', 'AWARDS', 'PUBLICATIONS'
            ]
            
            print("\n🔍 Looking for section headers in content:")
            print("-" * 40)
            
            found_sections = []
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if line_stripped:
                    clean_line = re.sub(r'[_\-\s]+', ' ', line_stripped).strip().upper()
                    for keyword in section_keywords:
                        if keyword in clean_line and len(clean_line) < 50:
                            found_sections.append({
                                'line_number': i,
                                'original': line_stripped,
                                'clean': clean_line,
                                'keyword': keyword
                            })
                            break
            
            if found_sections:
                print(f"✅ Found {len(found_sections)} potential section headers:")
                for section in found_sections:
                    print(f"   Line {section['line_number']:2d}: '{section['original']}'")
                    print(f"        Clean: '{section['clean']}'")
                    print(f"        Keyword: {section['keyword']}")
                    print()
            else:
                print("❌ No section headers found in content")
                print("   This might indicate the content needs better formatting")
                
            # Show a sample of the content structure
            print("\n📋 Content structure sample (first 20 lines):")
            print("-" * 40)
            for i, line in enumerate(lines[:20], 1):
                if line.strip():
                    print(f"   {i:2d}: {line.strip()}")
                else:
                    print(f"   {i:2d}: [empty line]")
                    
        else:
            print(f"⚠️ No CV found (status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error testing section detection: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ Section detection test completed!")
    return True

if __name__ == "__main__":
    test_section_detection() 