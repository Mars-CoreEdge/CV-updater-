#!/usr/bin/env python3
"""
Test OpenAI API key functionality
"""

import os
import openai
import requests
from datetime import datetime

# Load .env file if it exists
def load_env_file():
    """Load environment variables from .env file"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Loaded environment variables from .env file")

def test_openai_key():
    """Test if OpenAI API key is working"""
    print("🔍 Testing OpenAI API Key...")
    print("=" * 50)
    
    # Check if API key is set (backend uses VITE_OPENAI_API_KEY)
    api_key = os.getenv('VITE_OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key environment variable is not set")
        print("   Please set your OpenAI API key:")
        print("   - Windows: set VITE_OPENAI_API_KEY=your_key_here")
        print("   - Linux/Mac: export VITE_OPENAI_API_KEY=your_key_here")
        print("   - Or create a .env file in the backend directory with:")
        print("     VITE_OPENAI_API_KEY=your_key_here")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...{api_key[-4:]}")
    
    # Test 1: Basic API connection
    try:
        print("\n🧪 Test 1: Testing API connection...")
        client = openai.OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello! Please respond with 'API is working' if you can see this message."}
            ],
            max_tokens=50
        )
        
        if response.choices and response.choices[0].message.content:
            print("✅ API connection successful!")
            print(f"   Response: {response.choices[0].message.content}")
        else:
            print("❌ API connection failed - no response received")
            return False
            
    except openai.AuthenticationError:
        print("❌ Authentication failed - invalid API key")
        return False
    except openai.RateLimitError:
        print("❌ Rate limit exceeded - API key is valid but quota exceeded")
        return False
    except openai.APIError as e:
        print(f"❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test 2: Check API key details
    try:
        print("\n🧪 Test 2: Checking API key details...")
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Get usage information
        usage_response = requests.get(
            'https://api.openai.com/v1/usage',
            headers=headers
        )
        
        if usage_response.status_code == 200:
            usage_data = usage_response.json()
            print("✅ API key details retrieved successfully")
            print(f"   Usage data available: {len(usage_data)} fields")
        else:
            print(f"⚠️ Could not retrieve usage data (status: {usage_response.status_code})")
            
    except Exception as e:
        print(f"⚠️ Could not check API key details: {e}")
    
    # Test 3: Test with CV-related prompt
    try:
        print("\n🧪 Test 3: Testing CV-related functionality...")
        client = openai.OpenAI(api_key=api_key)
        
        test_cv_content = """
        John Doe
        Software Engineer
        
        SKILLS:
        - Python, JavaScript, React
        - AWS, Docker, Git
        
        EXPERIENCE:
        - Software Engineer at Tech Corp (2020-2023)
        - Junior Developer at Startup Inc (2018-2020)
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful CV assistant. Analyze the CV content and provide a brief summary."},
                {"role": "user", "content": f"Please analyze this CV and provide a 2-sentence summary:\n\n{test_cv_content}"}
            ],
            max_tokens=100
        )
        
        if response.choices and response.choices[0].message.content:
            print("✅ CV analysis test successful!")
            print(f"   Analysis: {response.choices[0].message.content}")
        else:
            print("❌ CV analysis test failed")
            return False
            
    except Exception as e:
        print(f"❌ CV analysis test error: {e}")
        return False
    
    print("\n🎉 All tests passed! Your OpenAI API key is working correctly.")
    print("   You can now use the AI chat features in the CV application.")
    return True

def check_environment_setup():
    """Check if environment is properly set up"""
    print("\n🔧 Environment Setup Check:")
    print("-" * 30)
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️ .env file not found")
    
    # Check for requirements
    required_packages = ['openai', 'requests']
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} package available")
        except ImportError:
            print(f"❌ {package} package not found")
    
    # Check API key format
    api_key = os.getenv('VITE_OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
    if api_key:
        if api_key.startswith('sk-') and len(api_key) > 20:
            print("✅ API key format looks correct")
        else:
            print("⚠️ API key format may be incorrect (should start with 'sk-')")

if __name__ == "__main__":
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load .env file first
    load_env_file()
    print()
    
    check_environment_setup()
    print()
    
    success = test_openai_key()
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n✅ OpenAI API key is working! You can use AI features.")
    else:
        print("\n❌ OpenAI API key is not working. Please check your setup.")
        print("\n📋 Troubleshooting steps:")
        print("1. Verify your API key is correct")
        print("2. Check your OpenAI account has credits")
        print("3. Ensure the API key has the right permissions")
        print("4. Try setting the environment variable again") 