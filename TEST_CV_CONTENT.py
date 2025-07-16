#!/usr/bin/env python3
"""
Test script to check the actual CV content after adding projects
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_cv_content():
    """Test the actual CV content after adding projects"""
    
    print("🔍 Testing CV content after adding projects...")
    
    # First, add projects to CV
    print("\n1. Adding projects to CV...")
    try:
        response = requests.post(f"{BASE_URL}/cv/add-projects", timeout=10)
        if response.status_code == 200:
            data = response.json()
            cv_content = data.get('cv_content', '')
            print(f"✅ Projects added to CV successfully")
            print(f"   CV length: {len(cv_content)} characters")
            
            # Show the CV content
            print(f"\n📄 CV Content Preview:")
            print("=" * 60)
            print(cv_content[:1000])  # Show first 1000 characters
            print("=" * 60)
            
            # Check for projects section
            if 'PROJECTS' in cv_content.upper():
                print("✅ 'PROJECTS' section found in CV")
            else:
                print("❌ 'PROJECTS' section NOT found in CV")
                
            # Check for project content
            if '1.' in cv_content and any(project_word in cv_content.lower() for project_word in ['react', 'website', 'app']):
                print("✅ Project content found in CV")
            else:
                print("❌ Project content NOT found in CV")
                
        else:
            print(f"❌ Failed to add projects to CV: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_cv_content() 