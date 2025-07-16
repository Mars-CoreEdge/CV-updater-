#!/usr/bin/env python3
"""
Test the chat interface for LinkedIn blog generation
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_chat_interface():
    """Test the chat interface for LinkedIn blog generation"""
    
    print("🧪 Chat Interface LinkedIn Blog Test")
    print("=" * 60)
    
    # Test different LinkedIn blog commands
    commands = [
        "Generate a LinkedIn post",
        "Create a LinkedIn blog post",
        "Write a blog post about my project",
        "LinkedIn blog"
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"\n{i}. Testing: '{command}'")
        print("-" * 50)
        
        try:
            response = requests.post(f"{BASE_URL}/chat/", 
                                   json={"message": command}, 
                                   timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                print(f"✅ Status: {response.status_code}")
                print(f"📝 Response Length: {len(response_text)} characters")
                
                # Check if it's a LinkedIn blog response
                if 'LinkedIn Blog Post Generated Successfully' in response_text:
                    print("🎉 SUCCESS: LinkedIn blog generated!")
                    
                    # Extract blog content
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
                        print(f"📊 Blog Content Length: {len(blog_text)} characters")
                        print(f"📄 Blog Preview: {blog_text[:100]}...")
                        
                        # Check for key elements
                        has_emoji = any(char in blog_text for char in ['🚀', '💡', '🛠️', '⏱️', '🎯', '💬'])
                        has_hashtags = '#' in blog_text
                        has_technologies = any(tech in blog_text for tech in ['React', 'Python', 'AI', 'API'])
                        
                        print(f"📋 Content Analysis:")
                        print(f"   Has emojis: {'✅' if has_emoji else '❌'}")
                        print(f"   Has hashtags: {'✅' if has_hashtags else '❌'}")
                        print(f"   Mentions technologies: {'✅' if has_technologies else '❌'}")
                        
                        return True
                    else:
                        print("❌ No blog content found in response")
                else:
                    print("❌ Not a LinkedIn blog response")
                    print(f"📄 Response preview: {response_text[:200]}...")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait a bit between requests
        time.sleep(1)
    
    return False

def test_frontend_simulation():
    """Simulate what the frontend would see"""
    
    print(f"\n🔍 Frontend Simulation Test")
    print("=" * 60)
    
    command = "Generate a LinkedIn post"
    
    try:
        response = requests.post(f"{BASE_URL}/chat/", 
                               json={"message": command}, 
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            print(f"✅ Backend Response Status: {response.status_code}")
            print(f"📝 Response Data Structure:")
            print(f"   Keys: {list(data.keys())}")
            print(f"   Response Length: {len(response_text)} characters")
            
            # Check if frontend would detect this as a blog
            if 'LinkedIn Blog Post Generated Successfully' in response_text:
                print("🎉 Frontend would detect this as a LinkedIn blog!")
                
                # Show what the frontend would display
                print(f"\n📱 What Frontend Would Show:")
                print("=" * 40)
                print(response_text)
                print("=" * 40)
                
                return True
            else:
                print("❌ Frontend would NOT detect this as a LinkedIn blog")
                print(f"📄 Response preview: {response_text[:300]}...")
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Chat Interface LinkedIn Blog Testing")
    print("=" * 60)
    
    # Test chat interface
    chat_test = test_chat_interface()
    
    # Test frontend simulation
    frontend_test = test_frontend_simulation()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Chat Interface Test: {'✅ PASS' if chat_test else '❌ FAIL'}")
    print(f"Frontend Simulation: {'✅ PASS' if frontend_test else '❌ FAIL'}")
    
    if chat_test and frontend_test:
        print("\n🎉 Chat interface is working correctly!")
        print("💡 The issue might be in the frontend display or user interaction.")
    elif chat_test:
        print("\n⚠️ Backend is working but frontend simulation failed.")
        print("💡 Check frontend code for response handling.")
    else:
        print("\n❌ Chat interface is not working properly.")
        print("💡 Check backend chat endpoint and OpenAI integration.") 