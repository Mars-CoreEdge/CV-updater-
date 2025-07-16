#!/usr/bin/env python3
"""
Test script to verify LinkedIn blog generation works in chat
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_linkedin_blog_chat():
    """Test LinkedIn blog generation through chat interface"""
    
    print("🧪 Testing LinkedIn Blog Generation in Chat")
    print("=" * 60)
    
    # First, create a test project
    print("\n1. Creating a test project...")
    try:
        project_data = {
            "title": "AI-Powered CV Assistant",
            "description": "A modern web application that helps users create and manage professional CVs using AI",
            "technologies": ["React", "Python", "FastAPI", "OpenAI", "SQLite"],
            "duration": "3 months",
            "highlights": [
                "Implemented AI-powered CV analysis and suggestions",
                "Built responsive React frontend with modern UI/UX",
                "Developed RESTful API with FastAPI and Python",
                "Integrated OpenAI GPT-4 for intelligent content generation",
                "Added LinkedIn blog post generation feature"
            ]
        }
        
        response = requests.post(f"{BASE_URL}/projects/create", json=project_data, timeout=10)
        if response.status_code == 200:
            print("✅ Test project created successfully")
        else:
            print(f"❌ Failed to create test project: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating test project: {e}")
        return False
    
    # Test LinkedIn blog generation through chat
    print("\n2. Testing LinkedIn blog generation via chat...")
    
    chat_commands = [
        "Create a LinkedIn blog post for my latest project",
        "Generate a LinkedIn post",
        "Write a blog post about my project",
        "LinkedIn blog",
        "Create blog"
    ]
    
    for i, command in enumerate(chat_commands, 1):
        print(f"\n   Testing command {i}: '{command}'")
        try:
            response = requests.post(f"{BASE_URL}/chat/", 
                                   json={"message": command}, 
                                   timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                if 'LinkedIn Blog Post Generated Successfully' in response_text:
                    print(f"   ✅ SUCCESS - Blog generated!")
                    
                    # Extract and show blog content
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
                        print(f"   📝 Blog length: {len(blog_text)} characters")
                        print(f"   📄 Preview: {blog_text[:150]}...")
                    
                    return True
                else:
                    print(f"   ❌ FAILED - No blog generated")
                    print(f"   Response: {response_text[:200]}...")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return False

def test_project_specific_blog():
    """Test blog generation for specific project"""
    
    print("\n3. Testing project-specific blog generation...")
    
    try:
        # Get all projects
        response = requests.get(f"{BASE_URL}/projects/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            
            if projects:
                project = projects[0]  # Use first project
                project_title = project.get('title', 'Project')
                
                print(f"   Using project: {project_title}")
                
                # Test blog generation for specific project
                blog_response = requests.post(f"{BASE_URL}/blog/generate", 
                                            json={"project_title": project_title}, 
                                            timeout=15)
                
                if blog_response.status_code == 200:
                    blog_data = blog_response.json()
                    if blog_data.get('success'):
                        blog_content = blog_data.get('blog_content', '')
                        print(f"   ✅ Project-specific blog generated!")
                        print(f"   📝 Blog length: {len(blog_content)} characters")
                        print(f"   📄 Preview: {blog_content[:150]}...")
                        return True
                    else:
                        print(f"   ❌ Blog generation failed: {blog_data.get('message')}")
                else:
                    print(f"   ❌ HTTP Error: {blog_response.status_code}")
            else:
                print("   ❌ No projects found")
        else:
            print(f"   ❌ Failed to get projects: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 LinkedIn Blog Chat Testing")
    print("=" * 60)
    
    # Test basic blog generation
    basic_test = test_linkedin_blog_chat()
    
    # Test project-specific blog
    specific_test = test_project_specific_blog()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Basic Chat Blog Generation: {'✅ PASS' if basic_test else '❌ FAIL'}")
    print(f"Project-Specific Blog: {'✅ PASS' if specific_test else '❌ FAIL'}")
    
    if basic_test or specific_test:
        print("\n🎉 LinkedIn blog generation is working!")
        print("\n💡 You can now use these commands in chat:")
        print("   • 'Create a LinkedIn blog post'")
        print("   • 'Generate a LinkedIn post'")
        print("   • 'Write a blog post about my project'")
        print("   • 'LinkedIn blog'")
    else:
        print("\n⚠️ LinkedIn blog generation is not working properly.")
        print("   Check if OpenAI API key is set and working.") 