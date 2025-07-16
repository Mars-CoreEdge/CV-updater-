#!/usr/bin/env python3

import os

# Test basic import
try:
    from openai import OpenAI
    print("✅ OpenAI library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import OpenAI: {e}")
    exit(1)

# Test API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY environment variable not set")
    exit(1)

print(f"API Key: {api_key[:25]}..." if api_key else "❌ No API Key")

# Test client initialization  
try:
    print("🔧 Initializing OpenAI client...")
    client = OpenAI(api_key=api_key)
    print("✅ OpenAI client created successfully")
except Exception as e:
    print(f"❌ Client initialization failed: {e}")
    print(f"Error type: {type(e)}")
    exit(1)

# Test simple API call
try:
    print("🧪 Testing GPT-4o API call...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Say 'Test successful' in exactly those words."}],
        max_tokens=10,
        temperature=0
    )
    
    result = response.choices[0].message.content.strip()
    print(f"✅ Response: {result}")
    
    if "Test successful" in result:
        print("🎉 GPT-4o API is working perfectly!")
    else:
        print("⚠️ Got response but not expected content")
        
except Exception as e:
    print(f"❌ API call failed: {e}")
    
    error_str = str(e).lower()
    if "authentication" in error_str:
        print("💡 Authentication error - API key issue")
    elif "model" in error_str:
        print("💡 Model access error - GPT-4o not available for this account")
    elif "quota" in error_str or "billing" in error_str:
        print("💡 Billing/quota issue - check OpenAI account")
    else:
        print("💡 Other error - check network/OpenAI status") 