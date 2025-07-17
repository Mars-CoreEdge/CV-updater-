#!/usr/bin/env python3
"""
Test CV reorganization and section placement
"""

import requests
import json

def test_cv_reorganization():
    """Test CV reorganization with scattered content"""
    
    # Test CV content similar to the problematic one provided
    test_cv_content = """PROFESSIONAL CV
Accomplished Full Stack Developer with 1 years of experience contributing to
outstanding success in the software development industry. Confident in ability to
effectively build responsive web applications and optimize performance for
scalability. Comfortable collaborating with others and working independently in a
variety of settings including agile team environments and remote development
projects. Committed to lifelong learning and contributing to team success. |
Duration: June 2025 | Bachelor of Science in Computer Science - 3.4 | Institution:
UET Lahore (2024) | 1. E-commerce | Duration: 3 months | - Increased sales by
50%
____________________________________________________________
Profile Summary
__________________________________________________
Skills
__________________________________________________
Technical Skills:
__________________________________________________
• React.js
• Node.js
• MongoDB
• Express.js
Professional Skills:
__________________________________________________
• Python
• FastAPI
• Langraph
Work Experience
__________________________________________________
Full Stack Developer at Core Edge Solutions
• Contributed to outstanding success in the software development industry by
building responsive web applications and optimizing performance for scalability.
- Collaborated With Team Members And Worked
Independently In Agile Team Environments And
Remote Development Projects.
__________________________________________________
Education
__________________________________________________
Projects
__________________________________________________
Description: Developed a web app for creating, updating, and managing tasks
with deadlines and status tracking.
• Built the front-end using React.js, JavaScript, HTML, CSS, and Bootstrap for a
responsive UI.
• Created REST APIs with FastAPI and integrated Supabase for database and
user authentication.
• Managed code with GitHub and ensured smooth deployment and
performance.
Technologies: React.js, Node.js
Key Highlights:
Generated on July 17, 2025 | CV Updater Platform"""
    
    try:
        # Test the CV reorganization by uploading this content
        print("🧪 Testing CV reorganization with scattered content...")
        
        # Create a test file-like object
        from io import BytesIO
        test_file = BytesIO(test_cv_content.encode('utf-8'))
        test_file.name = "test_cv.txt"
        
        # Test upload with the problematic CV content
        files = {'file': ('test_cv.txt', test_file, 'text/plain')}
        data = {'extracted_text': test_cv_content}
        
        response = requests.post(
            "http://localhost:8081/upload-cv/",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CV upload successful!")
            print(f"📄 Filename: {result.get('filename', 'N/A')}")
            print(f"📊 Status: {result.get('status', 'N/A')}")
            
            # Now test getting the current CV to see if it's properly organized
            cv_response = requests.get("http://localhost:8081/cv/current/")
            
            if cv_response.status_code == 200:
                cv_result = cv_response.json()
                cv_content = cv_result.get('content', '')
                
                if cv_content:
                    print(f"📝 CV Content Length: {len(cv_content)} characters")
                    
                    # Check for proper section organization
                    print("\n📋 Section Organization Check:")
                    
                    sections_to_check = [
                        "PROFILE SUMMARY",
                        "SKILLS", 
                        "WORK EXPERIENCE",
                        "EDUCATION",
                        "PROJECTS"
                    ]
                    
                    for section in sections_to_check:
                        if section in cv_content:
                            print(f"✅ {section} - Found")
                        else:
                            print(f"❌ {section} - Missing")
                    
                    # Check for scattered content that should be organized
                    print("\n🔍 Content Placement Check:")
                    
                    # Check if skills are properly placed
                    if "• React.js" in cv_content and "SKILLS" in cv_content:
                        skills_section_start = cv_content.find("SKILLS")
                        react_js_pos = cv_content.find("• React.js")
                        if react_js_pos > skills_section_start:
                            print("✅ Skills properly placed under SKILLS section")
                        else:
                            print("❌ Skills not properly placed under SKILLS section")
                    
                    # Check if experience is properly placed
                    if "Full Stack Developer at Core Edge Solutions" in cv_content and "WORK EXPERIENCE" in cv_content:
                        exp_section_start = cv_content.find("WORK EXPERIENCE")
                        job_pos = cv_content.find("Full Stack Developer at Core Edge Solutions")
                        if job_pos > exp_section_start:
                            print("✅ Experience properly placed under WORK EXPERIENCE section")
                        else:
                            print("❌ Experience not properly placed under WORK EXPERIENCE section")
                    
                    # Check if projects are properly placed
                    if "Description: Developed a web app" in cv_content and "PROJECTS" in cv_content:
                        proj_section_start = cv_content.find("PROJECTS")
                        proj_desc_pos = cv_content.find("Description: Developed a web app")
                        if proj_desc_pos > proj_section_start:
                            print("✅ Projects properly placed under PROJECTS section")
                        else:
                            print("❌ Projects not properly placed under PROJECTS section")
                    
                    # Show a preview of the reorganized CV
                    print(f"\n📄 Reorganized CV Preview (first 800 characters):")
                    print("-" * 50)
                    print(cv_content[:800])
                    print("-" * 50)
                    
                    # Check for proper line breaks and structure
                    lines = cv_content.split('\n')
                    print(f"\n📊 Structure Analysis:")
                    print(f"Total lines: {len(lines)}")
                    print(f"Lines with bullet points: {len([l for l in lines if l.strip().startswith('•')])}")
                    print(f"Lines with section headers: {len([l for l in lines if '_____' in l and any(section in l for section in sections_to_check)])}")
                    
                else:
                    print("❌ No CV content retrieved")
                    
            else:
                print(f"❌ Failed to retrieve CV: {cv_response.status_code}")
                print(f"Error: {cv_response.text}")
                
        else:
            print(f"❌ CV upload failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on port 8081.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_cv_reorganization() 