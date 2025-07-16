#!/usr/bin/env python3
"""
Test script to show the full CV content and search for projects section
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_full_cv():
    """Test the full CV content to find projects section"""
    
    print("🔍 Testing full CV content...")
    
    # Add projects to CV
    print("\n1. Adding projects to CV...")
    try:
        response = requests.post(f"{BASE_URL}/cv/add-projects", timeout=10)
        if response.status_code == 200:
            data = response.json()
            cv_content = data.get('cv_content', '')
            print(f"✅ Projects added to CV successfully")
            print(f"   CV length: {len(cv_content)} characters")
            
            # Show the full CV content
            print(f"\n📄 FULL CV Content:")
            print("=" * 80)
            print(cv_content)
            print("=" * 80)
            
            # Search for projects section
            print(f"\n🔍 Searching for projects section...")
            
            # Check for different variations of projects section
            projects_variations = [
                'PROJECTS',
                'projects',
                '_____________________________ PROJECTS _____________________________',
                'PROJECT',
                'project'
            ]
            
            found_variations = []
            for variation in projects_variations:
                if variation in cv_content:
                    found_variations.append(variation)
                    print(f"✅ Found: '{variation}'")
                else:
                    print(f"❌ Not found: '{variation}'")
            
            # Check for project content
            print(f"\n🔍 Searching for project content...")
            project_indicators = ['1.', '2.', '3.', 'React', 'Website', 'Technologies:', 'Description:']
            found_indicators = []
            for indicator in project_indicators:
                if indicator in cv_content:
                    found_indicators.append(indicator)
                    print(f"✅ Found: '{indicator}'")
                else:
                    print(f"❌ Not found: '{indicator}'")
            
            # Show the last 500 characters (where projects should be)
            print(f"\n📄 Last 500 characters of CV (where projects should be):")
            print("=" * 80)
            print(cv_content[-500:])
            print("=" * 80)
                
        else:
            print(f"❌ Failed to add projects to CV: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_full_cv() 