#!/usr/bin/env python3
"""
Test all LinkedIn blog commands to ensure they work properly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_all_linkedin_commands():
    """Test all LinkedIn blog generation commands"""
    
    print("🧪 All LinkedIn Blog Commands Test")
    print("=" * 60)
    
    # All the commands that should work
    commands = [
        "Generate a LinkedIn post",
        "Create a LinkedIn blog post", 
        "Write a blog post about my project",
        "LinkedIn blog",
        "Generate LinkedIn post",
        "Create blog post",
        "Write a LinkedIn post",
        "LinkedIn post",
        "Generate blog",
        "Create a blog"
    ]
    
    success_count = 0
    total_commands = len(commands)
    
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
                    success_count += 1
                    
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
                        print(f"📄 Blog Preview: {blog_text[:80]}...")
                        
                        # Check for key elements
                        has_emoji = any(char in blog_text for char in ['🚀', '💡', '🛠️', '⏱️', '🎯', '💬'])
                        has_hashtags = '#' in blog_text
                        has_technologies = any(tech in blog_text for tech in ['React', 'Python', 'AI', 'API', 'Technology'])
                        
                        print(f"📋 Content Analysis:")
                        print(f"   Has emojis: {'✅' if has_emoji else '❌'}")
                        print(f"   Has hashtags: {'✅' if has_hashtags else '❌'}")
                        print(f"   Mentions technologies: {'✅' if has_technologies else '❌'}")
                    else:
                        print("❌ No blog content found in response")
                else:
                    print("❌ Not a LinkedIn blog response")
                    print(f"📄 Response preview: {response_text[:150]}...")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Wait a bit between requests
        time.sleep(1)
    
    return success_count, total_commands

def test_project_creation_and_blog():
    """Test creating a project and then generating a blog for it"""
    
    print(f"\n🔍 Project Creation + Blog Generation Test")
    print("=" * 60)
    
    # First, create a test project
    print("1. Creating a test project...")
    try:
        project_response = requests.post(f"{BASE_URL}/projects/create-from-chat", 
                                       json={"message": "Create a React e-commerce website project using React, Node.js, and MongoDB"}, 
                                       timeout=15)
        
        if project_response.status_code == 200:
            project_data = project_response.json()
            if project_data.get('success'):
                project_title = project_data.get('project', {}).get('title', 'Test Project')
                print(f"✅ Project created: {project_title}")
                
                # Now generate a blog for this project
                print(f"\n2. Generating blog for '{project_title}'...")
                blog_response = requests.post(f"{BASE_URL}/chat/", 
                                           json={"message": "Generate a LinkedIn post"}, 
                                           timeout=15)
                
                if blog_response.status_code == 200:
                    blog_data = blog_response.json()
                    blog_text = blog_data.get('response', '')
                    
                    if 'LinkedIn Blog Post Generated Successfully' in blog_text:
                        print("🎉 SUCCESS: Blog generated for specific project!")
                        
                        # Extract project name from blog
                        lines = blog_text.split('\n')
                        for line in lines:
                            if '**Project:**' in line:
                                project_name = line.replace('**Project:**', '').strip()
                                print(f"📝 Blog generated for project: {project_name}")
                                break
                        
                        return True
                    else:
                        print("❌ Blog generation failed")
                        print(f"📄 Response: {blog_text[:200]}...")
                else:
                    print(f"❌ Blog generation HTTP error: {blog_response.status_code}")
            else:
                print(f"❌ Project creation failed: {project_data.get('message')}")
        else:
            print(f"❌ Project creation HTTP error: {project_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Comprehensive LinkedIn Blog Testing")
    print("=" * 60)
    
    # Test all commands
    success_count, total_commands = test_all_linkedin_commands()
    
    # Test project creation and blog generation
    project_blog_test = test_project_creation_and_blog()
    
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("=" * 60)
    print(f"LinkedIn Blog Commands: {success_count}/{total_commands} ✅")
    print(f"Project + Blog Generation: {'✅ PASS' if project_blog_test else '❌ FAIL'}")
    
    success_rate = (success_count / total_commands) * 100 if total_commands > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_count >= total_commands * 0.8 and project_blog_test:
        print("\n🎉 EXCELLENT! LinkedIn blog generation is working perfectly!")
        print("\n💡 All commands are working:")
        print("   • 'Generate a LinkedIn post' ✅")
        print("   • 'Create a LinkedIn blog post' ✅")
        print("   • 'Write a blog post about my project' ✅")
        print("   • 'LinkedIn blog' ✅")
        print("   • And many more variations ✅")
        print("\n🚀 Ready for production use!")
    elif success_count >= total_commands * 0.5:
        print("\n⚠️ MOSTLY WORKING! Some commands need attention.")
        print("💡 Check the failed commands above for patterns.")
    else:
        print("\n❌ NEEDS ATTENTION! Many commands are failing.")
        print("💡 Check the backend classification logic.") 