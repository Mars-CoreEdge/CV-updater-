#!/usr/bin/env python3
"""
Setup script for OpenAI API key
"""

import os
import sys

def setup_openai_key():
    """Help user set up OpenAI API key"""
    
    print("🔧 OpenAI API Key Setup")
    print("=" * 50)
    
    # Check if key already exists
    existing_key = os.getenv("OPENAI_API_KEY")
    if existing_key:
        print(f"✅ OpenAI API key already set: {existing_key[:10]}...{existing_key[-4:]}")
        return True
    
    print("❌ No OpenAI API key found.")
    print("\n📋 To get an OpenAI API key:")
    print("1. Go to https://platform.openai.com/")
    print("2. Sign up or log in")
    print("3. Go to 'API Keys' section")
    print("4. Create a new API key")
    print("5. Copy the key (starts with 'sk-')")
    
    print("\n🔑 Enter your OpenAI API key (or press Enter to skip):")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("⚠️ No API key provided. OpenAI features will not work.")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. Should start with 'sk-'")
        return False
    
    # Set environment variable for current session
    os.environ["OPENAI_API_KEY"] = api_key
    print(f"✅ API key set for current session: {api_key[:10]}...{api_key[-4:]}")
    
    # Create .env file for future sessions
    try:
        with open('backend/.env', 'w') as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print("✅ Created backend/.env file for persistent storage")
    except Exception as e:
        print(f"⚠️ Could not create .env file: {e}")
        print("   You'll need to set the API key again next time")
    
    return True

def test_openai_functionality():
    """Test if OpenAI is working"""
    
    print("\n🧪 Testing OpenAI Functionality...")
    print("=" * 50)
    
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ No API key available")
            return False
        
        client = OpenAI(api_key=api_key)
        
        # Test simple request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'OpenAI is working!'"}],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI test successful: {result}")
        
        # Test LinkedIn blog generation
        print("\n📝 Testing LinkedIn blog generation...")
        
        project_data = {
            "title": "Test Project",
            "description": "A test project for verification",
            "technologies": ["Python", "React", "Node.js"],
            "duration": "2 weeks",
            "highlights": ["Built responsive UI", "Implemented API", "Added authentication"]
        }
        
        # Import the blog generation function
        sys.path.append('backend')
        from main_enhanced import generate_linkedin_blog
        
        blog_content = generate_linkedin_blog(project_data)
        print(f"✅ LinkedIn blog generation successful!")
        print(f"   Blog length: {len(blog_content)} characters")
        print(f"   Preview: {blog_content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CV Updater - OpenAI Setup")
    print("=" * 60)
    
    # Setup API key
    key_setup = setup_openai_key()
    
    if key_setup:
        # Test functionality
        functionality_working = test_openai_functionality()
        
        print("\n" + "=" * 60)
        print("📊 SETUP SUMMARY")
        print("=" * 60)
        print(f"API Key Setup: {'✅ SUCCESS' if key_setup else '❌ FAILED'}")
        print(f"Functionality Test: {'✅ SUCCESS' if functionality_working else '❌ FAILED'}")
        
        if key_setup and functionality_working:
            print("\n🎉 Setup complete! OpenAI and LinkedIn blog generation are ready to use.")
            print("\n💡 You can now:")
            print("   • Use AI-powered CV updates")
            print("   • Generate LinkedIn blog posts for projects")
            print("   • Get intelligent responses in chat")
        else:
            print("\n⚠️ Setup incomplete. Some features may not work properly.")
    else:
        print("\n⚠️ OpenAI setup skipped. AI features will not be available.")
        print("   You can still use basic CV management features.") 