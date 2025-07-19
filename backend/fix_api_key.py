#!/usr/bin/env python3

def fix_api_key_security():
    """Remove hardcoded API keys and fix security issues"""
    
    with open('main_enhanced.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the incomplete OpenAI API key line
    content = content.replace(
        "if not os.getenv('OPENAI_API_KEY'):\n    os.environ['OPENAI_API_KEY'] ",
        """if not os.getenv('OPENAI_API_KEY'):
    print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
    print("   Please set your OpenAI API key as an environment variable")
    print("   Example: export OPENAI_API_KEY='your-api-key-here'")"""
    )
    
    # Write the fixed content back
    with open('main_enhanced.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed API key security issue in main_enhanced.py")

if __name__ == "__main__":
    fix_api_key_security() 