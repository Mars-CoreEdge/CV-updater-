#!/usr/bin/env python3
"""
Debug script to examine and clean CV content
"""

import requests
import re

def debug_cv_content():
    """Debug and clean CV content"""
    
    base_url = "http://localhost:8081"
    
    print("🔍 Debugging CV Content")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Backend is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it first.")
        return False
    
    # Test 2: Get current CV content
    try:
        response = requests.get(f"{base_url}/cv/current/")
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            print(f"✅ CV content retrieved successfully")
            print(f"   Content length: {len(content)} characters")
            
            # Check for emoji icons
            emoji_count = content.count('📋')
            print(f"   Emoji icons found: {emoji_count}")
            
            if emoji_count > 0:
                print("❌ Emoji icons still present - cleaning needed")
                
                # Clean the content
                cleaned_content = content.replace('📋 ', '').replace('📋', '')
                cleaned_content = re.sub(r'─+', '', cleaned_content)  # Remove underlines
                
                print(f"   Cleaned content length: {len(cleaned_content)} characters")
                
                # Show before and after
                lines = content.split('\n')
                cleaned_lines = cleaned_content.split('\n')
                
                print("\n📋 Before cleaning (first 15 lines):")
                print("-" * 40)
                for i, line in enumerate(lines[:15], 1):
                    print(f"   {i:2d}: {line}")
                
                print("\n📋 After cleaning (first 15 lines):")
                print("-" * 40)
                for i, line in enumerate(cleaned_lines[:15], 1):
                    print(f"   {i:2d}: {line}")
                
                # Try to update the CV with cleaned content
                print("\n🔄 Attempting to update CV with cleaned content...")
                try:
                    update_response = requests.post(f"{base_url}/cv/cleanup")
                    if update_response.status_code == 200:
                        print("✅ CV cleanup successful")
                    else:
                        print(f"❌ CV cleanup failed: {update_response.status_code}")
                except Exception as e:
                    print(f"❌ Error during cleanup: {e}")
            else:
                print("✅ No emoji icons found - content is clean")
                
        else:
            print(f"⚠️ No CV found (status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error debugging CV content: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ CV content debugging completed!")
    return True

if __name__ == "__main__":
    debug_cv_content() 