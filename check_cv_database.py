#!/usr/bin/env python3
"""
Check CV database and ensure we're working with the correct CV
"""

import requests

def check_cv_database():
    """Check CV database and list all CVs"""
    
    base_url = "http://localhost:8081"
    
    print("🗄️ Checking CV Database")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Backend is running: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it first.")
        return False
    
    # Test 2: List all CVs
    try:
        response = requests.get(f"{base_url}/cvs/")
        if response.status_code == 200:
            data = response.json()
            cvs = data.get('cvs', [])
            print(f"✅ Found {len(cvs)} CVs in database")
            
            for i, cv in enumerate(cvs, 1):
                print(f"\n📄 CV {i}:")
                print(f"   ID: {cv.get('id')}")
                print(f"   Title: {cv.get('title', 'N/A')}")
                print(f"   Filename: {cv.get('filename', 'N/A')}")
                print(f"   Active: {cv.get('is_active', False)}")
                print(f"   Created: {cv.get('created_at', 'N/A')}")
                print(f"   Updated: {cv.get('updated_at', 'N/A')}")
                
        else:
            print(f"❌ Failed to get CVs: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking CV database: {e}")
        return False
    
    # Test 3: Get current CV content
    try:
        response = requests.get(f"{base_url}/cv/current/")
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            filename = data.get('filename', 'N/A')
            print(f"\n📋 Current CV:")
            print(f"   Filename: {filename}")
            print(f"   Content length: {len(content)} characters")
            
            # Check for emoji icons
            emoji_count = content.count('📋')
            print(f"   Emoji icons found: {emoji_count}")
            
            if emoji_count > 0:
                print("❌ Emoji icons still present in current CV")
                
                # Try to regenerate the CV
                print("\n🔄 Attempting to regenerate CV...")
                try:
                    regenerate_response = requests.post(f"{base_url}/cv/generate")
                    if regenerate_response.status_code == 200:
                        print("✅ CV regeneration successful")
                        
                        # Check again
                        response = requests.get(f"{base_url}/cv/current/")
                        if response.status_code == 200:
                            data = response.json()
                            content = data.get('content', '')
                            emoji_count = content.count('📋')
                            print(f"   Emoji icons after regeneration: {emoji_count}")
                    else:
                        print(f"❌ CV regeneration failed: {regenerate_response.status_code}")
                except Exception as e:
                    print(f"❌ Error during regeneration: {e}")
            else:
                print("✅ No emoji icons found in current CV")
                
        else:
            print(f"⚠️ No current CV found (status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Error getting current CV: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ CV database check completed!")
    return True

if __name__ == "__main__":
    check_cv_database() 