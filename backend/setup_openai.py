#!/usr/bin/env python3
"""
Setup script for OpenAI API key
"""

import os
import getpass

def setup_openai_key():
    """Interactive setup for OpenAI API key"""
    print("🔧 OpenAI API Key Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ Found existing {env_file} file")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'VITE_OPENAI_API_KEY' in content:
                print("✅ OpenAI API key is already configured")
                return True
    else:
        print(f"📝 Creating new {env_file} file")
    
    print("\n📋 To get your OpenAI API key:")
    print("1. Go to https://platform.openai.com/api-keys")
    print("2. Sign in or create an account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key (starts with 'sk-')")
    print("5. Paste it below\n")
    
    # Get API key from user
    api_key = getpass.getpass("Enter your OpenAI API key (will be hidden): ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. Should start with 'sk-'")
        return False
    
    # Write to .env file
    try:
        with open(env_file, 'w') as f:
            f.write(f"VITE_OPENAI_API_KEY={api_key}\n")
            f.write("PORT=8081\n")
            f.write("HOST=0.0.0.0\n")
            f.write("DATABASE_URL=sqlite:///cv_updater.db\n")
        
        print(f"✅ API key saved to {env_file}")
        print("🔒 The file has been created with your API key")
        
        # Test the key
        print("\n🧪 Testing the API key...")
        os.environ['VITE_OPENAI_API_KEY'] = api_key
        
        # Import and run the test
        try:
            from test_openai_key import test_openai_key
            success = test_openai_key()
            if success:
                print("\n🎉 Setup complete! Your OpenAI API key is working.")
                return True
            else:
                print("\n❌ API key test failed. Please check your key.")
                return False
        except ImportError:
            print("⚠️ Could not import test module, but key is saved")
            return True
            
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False

def check_current_setup():
    """Check current OpenAI setup"""
    print("🔍 Current OpenAI Setup Status")
    print("=" * 35)
    
    # Check environment variable
    api_key = os.getenv('VITE_OPENAI_API_KEY')
    if api_key:
        print(f"✅ Environment variable set: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("❌ Environment variable not set")
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
        with open('.env', 'r') as f:
            content = f.read()
            if 'VITE_OPENAI_API_KEY' in content:
                print("✅ API key found in .env file")
            else:
                print("❌ API key not found in .env file")
    else:
        print("❌ .env file not found")
    
    # Test if it works
    if api_key:
        print("\n🧪 Testing API key...")
        try:
            import openai
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            print("✅ API key is working!")
            return True
        except Exception as e:
            print(f"❌ API key test failed: {e}")
            return False
    else:
        print("❌ No API key to test")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'check':
        check_current_setup()
    else:
        print("Choose an option:")
        print("1. Setup new API key")
        print("2. Check current setup")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == '1':
            setup_openai_key()
        elif choice == '2':
            check_current_setup()
        else:
            print("Invalid choice") 