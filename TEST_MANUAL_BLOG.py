#!/usr/bin/env python3
"""
Manual test to see full LinkedIn blog content
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_manual_blog():
    """Test LinkedIn blog generation manually"""
    
    print("🧪 Manual LinkedIn Blog Test")
    print("=" * 60)
    
    # Test the working command
    command = "Generate a LinkedIn post"
    
    print(f"Testing command: '{command}'")
    print("-" * 60)
    
    try:
        response = requests.post(f"{BASE_URL}/chat/", 
                               json={"message": command}, 
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            print("📝 FULL RESPONSE:")
            print("=" * 60)
            print(response_text)
            print("=" * 60)
            
            # Extract blog content
            if 'LinkedIn Blog Post Generated Successfully' in response_text:
                lines = response_text.split('\n')
                blog_start = False
                blog_content = []
                
                for line in lines:
                    if 'Blog Content:' in line:
                        blog_start = True
                        continue
                    elif blog_start and line.strip() and not line.startswith('**'):
                        if 'Tips for posting:' in line:
                            break
                        blog_content.append(line)
                
                if blog_content:
                    blog_text = '\n'.join(blog_content).strip()
                    print(f"\n📊 Blog Statistics:")
                    print(f"   Length: {len(blog_text)} characters")
                    print(f"   Words: {len(blog_text.split())} words")
                    print(f"   Lines: {len(blog_content)} lines")
                    
                    # Check for key elements
                    has_emoji = any(char in blog_text for char in ['🚀', '💡', '🛠️', '⏱️', '🎯', '💬'])
                    has_hashtags = '#' in blog_text
                    has_technologies = any(tech in blog_text for tech in ['React', 'Python', 'AI', 'API'])
                    
                    print(f"\n📋 Content Analysis:")
                    print(f"   Has emojis: {'✅' if has_emoji else '❌'}")
                    print(f"   Has hashtags: {'✅' if has_hashtags else '❌'}")
                    print(f"   Mentions technologies: {'✅' if has_technologies else '❌'}")
                    
            else:
                print("❌ No blog content found in response")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_manual_blog() 