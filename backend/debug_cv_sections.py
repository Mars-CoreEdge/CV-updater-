#!/usr/bin/env python3
"""
Debug CV sections to see actual content structure
"""

import requests

def debug_cv_sections():
    """Debug CV sections to understand the structure"""
    
    try:
        # Get the current CV content
        response = requests.get("http://localhost:8081/cv/current/")
        
        if response.status_code == 200:
            cv_result = response.json()
            cv_content = cv_result.get('content', '')
            
            if cv_content:
                print("🔍 Debugging CV Content Structure:")
                print("=" * 60)
                
                lines = cv_content.split('\n')
                print(f"Total lines: {len(lines)}")
                print()
                
                print("📋 All lines with potential section headers:")
                print("-" * 40)
                
                for i, line in enumerate(lines):
                    line_stripped = line.strip()
                    if any(keyword in line_stripped.upper() for keyword in 
                           ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS']):
                        print(f"Line {i+1}: '{line_stripped}'")
                
                print()
                print("📋 Full CV content:")
                print("-" * 40)
                print(cv_content)
                print("-" * 40)
                
            else:
                print("❌ No CV content found")
                
        else:
            print(f"❌ Failed to retrieve CV: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on port 8081.")
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")

if __name__ == "__main__":
    debug_cv_sections() 