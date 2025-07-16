#!/usr/bin/env python3

import os
import traceback

# Test basic import
try:
    from openai import OpenAI
    print("✅ OpenAI library imported successfully")
    print(f"OpenAI version: {OpenAI.__module__}")
except ImportError as e:
    print(f"❌ Failed to import OpenAI: {e}")
    exit(1)

# Test API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY environment variable not set")
    print("💡 Set it with: export OPENAI_API_KEY=your_key_here")
    exit(1)

print(f"API Key: {api_key[:25]}...")

# Test client initialization with detailed error handling
try:
    print("🔧 Attempting OpenAI client initialization...")
    print("🔧 Calling OpenAI(api_key=api_key)...")
    
    # Try most basic initialization
    client = OpenAI(api_key=api_key)
    print("✅ OpenAI client created successfully!")
    
    # Test a simple API call
    print("🧪 Testing basic API call...")
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Try with mini first (cheaper/more accessible)
        messages=[{"role": "user", "content": "Say 'Working' in one word."}],
        max_tokens=5,
        temperature=0
    )
    
    result = response.choices[0].message.content.strip()
    print(f"✅ Basic API Response: {result}")
    
    # Now try GPT-4o
    print("🧪 Testing GPT-4o specifically...")
    response_4o = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Say 'GPT-4o Working' in exactly those words."}],
        max_tokens=10,
        temperature=0
    )
    
    result_4o = response_4o.choices[0].message.content.strip()
    print(f"✅ GPT-4o Response: {result_4o}")
    
    print("🎉 ALL TESTS PASSED! GPT-4o is working!")
    
except Exception as e:
    print(f"❌ Detailed error information:")
    print(f"Error type: {type(e)}")
    print(f"Error message: {e}")
    print(f"Error args: {e.args}")
    print("\n🔍 Full traceback:")
    traceback.print_exc()
    
    # Specific error analysis
    error_str = str(e).lower()
    print(f"\n💡 Error analysis:")
    if "authentication" in error_str or "unauthorized" in error_str:
        print("   → Authentication issue: Invalid API key")
    elif "model" in error_str and "gpt-4o" in error_str:
        print("   → Model access issue: Account doesn't have GPT-4o access")
    elif "quota" in error_str or "billing" in error_str:
        print("   → Billing issue: No credits or billing not setup")
    elif "proxies" in error_str:
        print("   → Configuration issue: Conflicting OpenAI setup")
    elif "init" in error_str:
        print("   → Initialization issue: Library version problem")
    else:
        print("   → Unknown issue: Check full traceback above")

print("\n" + "=" * 50)
print("Debug test completed.") 