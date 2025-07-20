#!/usr/bin/env python3
"""
Test script for project extraction functionality
"""

from project_extractor import extract_and_format_projects

def test_project_extraction():
    """Test the project extraction with sample CV content"""
    
    # Sample CV content with projects
    sample_cv = """
    JOHN DOE
    Software Developer
    john.doe@email.com | +1-555-0123
    
    PROFILE
    Experienced software developer with 5+ years in web development.
    
    SKILLS
    JavaScript, Python, React, Node.js, PostgreSQL
    
    EXPERIENCE
    Senior Developer at TechCorp (2020-2023)
    - Led development of multiple web applications
    - Mentored junior developers
    
    PROJECTS
    E-Commerce Platform
    [2023 - Present]
    - Built full-stack e-commerce solution with React, Node.js, and PostgreSQL
    - Implemented user authentication, payment processing, and inventory management
    - Deployed on AWS with Docker containers and CI/CD pipeline
    - Technologies: React, Node.js, PostgreSQL, AWS, Docker
    
    Task Management App
    [2022]
    - Developed collaborative task management application with real-time updates
    - Features include user roles, file sharing, and progress tracking
    - Integrated with Google Calendar and Slack APIs
    - Technologies: Vue.js, Express, MongoDB, Socket.io
    
    Weather Dashboard
    [2021]
    - Created responsive weather dashboard using OpenWeather API
    - Implemented location-based weather forecasts
    - Technologies: JavaScript, HTML5, CSS3, OpenWeather API
    
    EDUCATION
    Bachelor of Computer Science, University of Technology (2018)
    """
    
    print("Testing project extraction...")
    print("=" * 50)
    
    try:
        # Extract projects
        projects = extract_and_format_projects(sample_cv)
        
        print(f"✅ Successfully extracted {len(projects)} projects:")
        print()
        
        for i, project in enumerate(projects, 1):
            print(f"Project {i}: {project['title']}")
            print(f"  Duration: {project.get('duration', 'N/A')}")
            print(f"  Description: {project.get('description', 'N/A')}")
            print(f"  Technologies: {', '.join(project.get('technologies', []))}")
            print(f"  Highlights: {len(project.get('highlights', []))} items")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during project extraction: {e}")
        return False

if __name__ == "__main__":
    success = test_project_extraction()
    if success:
        print("✅ Project extraction test completed successfully!")
    else:
        print("❌ Project extraction test failed!") 