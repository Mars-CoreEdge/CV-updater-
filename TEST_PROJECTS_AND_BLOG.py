#!/usr/bin/env python3
"""
Comprehensive test script for projects and LinkedIn blog functionality
"""

import requests
import json
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000"

def test_backend_connection():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running on http://localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_projects_endpoint():
    """Test projects endpoint"""
    try:
        print("\n🔍 Testing projects endpoint...")
        response = requests.get(f"{BASE_URL}/projects/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            projects = data.get('projects', [])
            print(f"✅ Projects endpoint working - Found {len(projects)} projects")
            
            if projects:
                print("📋 Current projects:")
                for i, project in enumerate(projects, 1):
                    print(f"  {i}. {project.get('title', 'Untitled')}")
            else:
                print("📭 No projects found")
            
            return True
        else:
            print(f"❌ Projects endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Projects endpoint error: {e}")
        return False

def test_project_creation():
    """Test creating a project via chat"""
    try:
        print("\n🔍 Testing project creation...")
        
        # Test project creation via chat
        chat_message = "Create a React e-commerce website project using React, Node.js, and MongoDB"
        
        response = requests.post(f"{BASE_URL}/projects/create-from-chat", 
                               json={"message": chat_message}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Project created successfully: {data['project']['title']}")
                print(f"   Technologies: {data['project'].get('technologies', [])}")
                return True
            else:
                print(f"❌ Project creation failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Project creation endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Project creation error: {e}")
        return False

def test_linkedin_blog_generation():
    """Test LinkedIn blog generation"""
    try:
        print("\n🔍 Testing LinkedIn blog generation...")
        
        # First, get existing projects
        response = requests.get(f"{BASE_URL}/projects/", timeout=10)
        if response.status_code != 200:
            print("❌ Cannot get projects for blog test")
            return False
            
        projects = response.json().get('projects', [])
        
        if not projects:
            print("📭 No projects available for blog generation test")
            return False
        
        # Test blog generation for the first project
        project_title = projects[0].get('title', 'Test Project')
        
        response = requests.post(f"{BASE_URL}/blog/generate", 
                               json={"project_title": project_title}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                blog_content = data.get('blog_content', '')
                print(f"✅ LinkedIn blog generated successfully for '{data['project_title']}'")
                print(f"   Blog length: {len(blog_content)} characters")
                print(f"   Preview: {blog_content[:100]}...")
                return True
            else:
                print(f"❌ Blog generation failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ Blog generation endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Blog generation error: {e}")
        return False

def test_cv_with_projects():
    """Test CV generation with projects"""
    try:
        print("\n🔍 Testing CV generation with projects...")
        
        response = requests.post(f"{BASE_URL}/cv/add-projects", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Projects successfully added to CV")
                cv_content = data.get('cv_content', '')
                print(f"   CV length: {len(cv_content)} characters")
                
                # Check if projects section exists in CV
                if 'PROJECTS' in cv_content.upper() or 'projects' in cv_content.lower():
                    print("✅ Projects section found in CV")
                    return True
                else:
                    print("⚠️ Projects section not found in CV content")
                    return False
            else:
                print(f"❌ Adding projects to CV failed: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ CV with projects endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ CV with projects error: {e}")
        return False

def test_database_tables():
    """Test if required database tables exist"""
    try:
        print("\n🔍 Testing database tables...")
        
        # Test if we can get projects (this will fail if table doesn't exist)
        response = requests.get(f"{BASE_URL}/projects/", timeout=10)
        
        if response.status_code == 200:
            print("✅ manual_projects table exists and is accessible")
            return True
        else:
            print(f"❌ manual_projects table issue - status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Database table test error: {e}")
        return False

def cleanup_test_data():
    """Clean up any test data created"""
    try:
        print("\n🧹 Cleaning up test data...")
        
        # Get all projects
        response = requests.get(f"{BASE_URL}/projects/", timeout=10)
        if response.status_code == 200:
            projects = response.json().get('projects', [])
            
            # Delete test projects (those with "Test" in title)
            for project in projects:
                if 'test' in project.get('title', '').lower():
                    try:
                        delete_response = requests.delete(f"{BASE_URL}/projects/{project['id']}", timeout=5)
                        if delete_response.status_code == 200:
                            print(f"   🗑️ Deleted test project: {project['title']}")
                    except:
                        pass
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Projects and LinkedIn Blog Functionality")
    print("=" * 60)
    
    # Test backend connection
    if not test_backend_connection():
        print("\n❌ Backend is not running. Please start it first:")
        print("   cd backend && python main_enhanced.py")
        sys.exit(1)
    
    # Test database tables
    if not test_database_tables():
        print("\n❌ Database tables are not properly set up")
        sys.exit(1)
    
    # Test projects endpoint
    projects_working = test_projects_endpoint()
    
    # Test project creation
    creation_working = test_project_creation()
    
    # Test LinkedIn blog generation
    blog_working = test_linkedin_blog_generation()
    
    # Test CV with projects
    cv_working = test_cv_with_projects()
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    results = {
        "Backend Connection": True,
        "Database Tables": True,
        "Projects Endpoint": projects_working,
        "Project Creation": creation_working,
        "LinkedIn Blog Generation": blog_working,
        "CV with Projects": cv_working
    }
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Projects and LinkedIn blog functionality is working correctly.")
    else:
        print("❌ SOME TESTS FAILED. Check the issues above and fix them.")
        
        if not projects_working:
            print("\n🔧 PROJECTS ISSUE FIXES:")
            print("1. Check if manual_projects table exists in database")
            print("2. Verify backend is running on http://localhost:8000")
            print("3. Check backend logs for errors")
            
        if not blog_working:
            print("\n🔧 LINKEDIN BLOG ISSUE FIXES:")
            print("1. Ensure OpenAI API key is set (VITE_OPENAI_API_KEY environment variable)")
            print("2. Check if projects exist before generating blogs")
            print("3. Verify blog generation endpoints are working")
            
        if not cv_working:
            print("\n🔧 CV WITH PROJECTS ISSUE FIXES:")
            print("1. Ensure you have an active CV uploaded")
            print("2. Check if projects are being added to CV generation")
            print("3. Verify CV update endpoints are working")

if __name__ == "__main__":
    main() 