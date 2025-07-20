#!/usr/bin/env python3
"""
Test the complete upload and extraction process
"""

import json
import sqlite3
from project_extractor import extract_and_format_projects

def test_upload_process():
    """Test the complete upload and extraction process"""
    
    # The CV content provided by the user
    cv_content = """JOHN DOE
Software Engineer

CONTACT INFORMATION
Phone: (555) 123-4567
Email: john.doe@email.com
LinkedIn: linkedin.com/in/johndoe
Location: San Francisco, CA
Portfolio: johndoe.dev

ABOUT MYSELF
Passionate and experienced Software Engineer with 5+ years of expertise in full-stack development, specializing in React, Node.js, and cloud technologies. Proven track record of delivering scalable applications and leading development teams. Committed to writing clean, maintainable code and staying current with industry best practices.

SKILLS
Programming Languages: JavaScript, TypeScript, Python, Java, SQL
Frontend: React, Vue.js, HTML5, CSS3, Bootstrap, Tailwind CSS
Backend: Node.js, Express, Django, Spring Boot
Databases: PostgreSQL, MongoDB, MySQL, Redis
Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD, Git
Tools: VS Code, Postman, Jira, Figma, Adobe Creative Suite

WORK EXPERIENCE
Senior Software Engineer
TechCorp Inc. - San Francisco, CA
[ 01/2023 - Present ]
• Led development of microservices architecture serving 100K+ users
• Mentored 3 junior developers and conducted code reviews
• Implemented CI/CD pipeline reducing deployment time by 60%
• Collaborated with product team to define technical requirements
• Optimized database queries improving application performance by 40%

Full Stack Developer
StartupXYZ - San Francisco, CA
[ 06/2021 - 12/2022 ]
• Built responsive web applications using React and Node.js
• Integrated third-party APIs and payment gateways
• Developed RESTful APIs and GraphQL endpoints
• Worked in agile environment with 2-week sprint cycles
• Participated in product planning and user experience design

Junior Developer
Digital Solutions - San Francisco, CA
[ 01/2020 - 05/2021 ]
• Developed and maintained client websites using modern frameworks
• Collaborated with designers to implement pixel-perfect UI designs
• Debugged and fixed bugs in production applications
• Participated in daily stand-ups and sprint planning meetings
• Contributed to codebase documentation and best practices

EDUCATION AND TRAINING
Bachelor of Science in Computer Science
University of California, Berkeley
[ 2016 - 2020 ]
• GPA: 3.8/4.0
• Relevant Coursework: Data Structures, Algorithms, Software Engineering, Database Systems
• Dean's List: 2018-2020

CERTIFICATIONS
• AWS Certified Developer Associate
• Google Cloud Professional Developer
• MongoDB Certified Developer

PROJECTS
E-Commerce Platform
[ 2023 - Present ]
• Built full-stack e-commerce solution with React, Node.js, and PostgreSQL
• Implemented user authentication, payment processing, and inventory management
• Deployed on AWS with Docker containers and CI/CD pipeline
• Technologies: React, Node.js, PostgreSQL, AWS, Docker

Task Management App
[ 2022 ]
• Developed collaborative task management application with real-time updates
• Features include user roles, file sharing, and progress tracking
• Integrated with Google Calendar and Slack APIs
• Technologies: Vue.js, Express, MongoDB, Socket.io

Weather Dashboard
[ 2021 ]
• Created weather application with location-based forecasts
• Implemented responsive design and offline functionality
• Integrated multiple weather APIs for comprehensive data
• Technologies: React, OpenWeather API, PWA, Local Storage

ACHIEVEMENTS
• Employee of the Year 2023 at TechCorp Inc.
• Best Technical Implementation Award at StartupXYZ
• Published 3 technical articles on Medium
• Speaker at 2 local developer meetups
• Open source contributor with 50+ GitHub repositories

LANGUAGES
• English (Native)
• Spanish (Conversational)
• French (Basic)

INTERESTS
• Open source development
• Machine learning and AI
• Hiking and outdoor activities
• Reading technical blogs and books
• Contributing to developer communities"""
    
    print("🧪 Testing Complete Upload and Extraction Process")
    print("=" * 60)
    
    # Step 1: Extract projects
    print("\n1. Extracting projects from CV...")
    projects = extract_and_format_projects(cv_content)
    print(f"✅ Extracted {len(projects)} projects")
    
    # Step 2: Check database
    print("\n2. Checking database...")
    try:
        conn = sqlite3.connect('cv_database.db')
        cursor = conn.cursor()
        
        # Check if manual_projects table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manual_projects'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ manual_projects table exists")
            
            # Check current projects in database
            cursor.execute("SELECT COUNT(*) FROM manual_projects")
            current_count = cursor.fetchone()[0]
            print(f"Current projects in database: {current_count}")
            
            # Clear existing projects (simulate upload process)
            cursor.execute("DELETE FROM manual_projects")
            print("🗑️ Cleared existing projects")
            
            # Insert extracted projects
            for project in projects:
                cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", 
                              (json.dumps(project),))
            
            conn.commit()
            print(f"✅ Inserted {len(projects)} projects into database")
            
            # Verify projects were inserted
            cursor.execute("SELECT id, project_data FROM manual_projects ORDER BY created_at DESC")
            stored_projects = cursor.fetchall()
            
            print(f"✅ Retrieved {len(stored_projects)} projects from database:")
            for i, (project_id, project_json) in enumerate(stored_projects, 1):
                project_data = json.loads(project_json)
                print(f"  Project {i}: {project_data.get('title', 'N/A')} (ID: {project_id})")
            
        else:
            print("❌ manual_projects table does not exist")
            print("Creating table...")
            
            cursor.execute('''CREATE TABLE manual_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Insert extracted projects
            for project in projects:
                cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", 
                              (json.dumps(project),))
            
            conn.commit()
            print(f"✅ Created table and inserted {len(projects)} projects")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # Step 3: Test the /projects/list endpoint response format
    print("\n3. Testing endpoint response format...")
    try:
        conn = sqlite3.connect('cv_database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, project_data FROM manual_projects ORDER BY created_at DESC")
        manual_projects = cursor.fetchall()
        
        projects_response = []
        for project_row in manual_projects:
            try:
                project_id = project_row[0]
                project_data = json.loads(project_row[1])
                project_data['id'] = project_id
                projects_response.append(project_data)
            except:
                pass
        
        response = {"projects": projects_response, "total_count": len(projects_response)}
        print(f"✅ Endpoint response: {len(response['projects'])} projects")
        print(f"Response format: {json.dumps(response, indent=2)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Endpoint test error: {e}")

if __name__ == "__main__":
    test_upload_process() 