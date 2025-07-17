#!/usr/bin/env python3
"""
Test script to check if OpenAI key is working
"""

import os
import sys

# Add backend to path
sys.path.append('backend')

def test_openai_connection():
    """Test if OpenAI key is working"""
    
    print("🔍 Testing OpenAI Connection...")
    print("=" * 50)
    
    # Check environment variable
    api_key = os.getenv("VITE_OPENAI_API_KEY")
    if not api_key:
        print("❌ VITE_OPENAI_API_KEY environment variable not set")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ VITE_OPENAI_API_KEY format is invalid (should start with 'sk-')")
        return False
    
    print(f"✅ VITE_OPENAI_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test OpenAI client
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello, OpenAI is working!'"}],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API test successful!")
        print(f"   Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_linkedin_blog_generation():
    """Test LinkedIn blog generation functionality"""
    
    print("\n🔍 Testing LinkedIn Blog Generation...")
    print("=" * 50)
    
    try:
        from openai import OpenAI
        import os
        
        api_key = os.getenv("VITE_OPENAI_API_KEY")
        if not api_key:
            print("❌ No OpenAI API key available")
            return False
        
        client = OpenAI(api_key=api_key)
        
        # Sample project data
        project_data = {
            "title": "React E-Commerce Website",
            "description": "A modern e-commerce platform built with React and Node.js",
            "technologies": ["React", "Node.js", "MongoDB", "Express"],
            "duration": "3 months",
            "highlights": [
                "Implemented responsive design",
                "Integrated payment gateway",
                "Built admin dashboard"
            ]
        }
        
        # Test blog generation
        prompt = f"""Create a professional LinkedIn blog post about this project:

Project Details:
- Title: {project_data.get('title', 'Project')}
- Description: {project_data.get('description', '')}
- Technologies: {', '.join(project_data.get('technologies', []))}
- Duration: {project_data.get('duration', '')}
- Highlights: {'; '.join(project_data.get('highlights', []))}

Create an engaging LinkedIn post that:
1. Starts with an attention-grabbing hook
2. Explains the project's purpose and impact
3. Highlights technical challenges overcome
4. Mentions key technologies used
5. Includes relevant hashtags
6. Ends with a call to action or reflection
7. Uses emojis appropriately
8. Keeps it professional but engaging
9. Length: 200-300 words

Make it sound personal and authentic, as if the developer is sharing their experience."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        blog_content = response.choices[0].message.content.strip()
        print(f"✅ LinkedIn blog generation successful!")
        print(f"   Blog length: {len(blog_content)} characters")
        print(f"   Preview: {blog_content[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ LinkedIn blog generation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 OpenAI and LinkedIn Blog Testing")
    print("=" * 60)
    
    # Test OpenAI connection
    openai_working = test_openai_connection()
    
    # Test LinkedIn blog generation
    blog_working = test_linkedin_blog_generation()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"OpenAI Connection: {'✅ WORKING' if openai_working else '❌ FAILED'}")
    print(f"LinkedIn Blog Generation: {'✅ WORKING' if blog_working else '❌ FAILED'}")
    
    if openai_working and blog_working:
        print("\n🎉 All tests passed! OpenAI and LinkedIn blog generation are working.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.") 