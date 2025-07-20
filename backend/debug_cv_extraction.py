#!/usr/bin/env python3
"""
Debug script for CV project extraction
"""

from project_extractor import extract_and_format_projects, find_projects_section, split_project_blocks, is_project_title

def debug_cv_extraction():
    """Debug the CV extraction with the provided CV content"""
    
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
    
    print("🔍 Debugging CV Project Extraction")
    print("=" * 60)
    
    # Step 1: Find the projects section
    print("\n1. Finding PROJECTS section...")
    projects_section = find_projects_section(cv_content)
    
    if projects_section:
        print(f"✅ Found projects section ({len(projects_section)} characters)")
        print("Projects section content:")
        print("-" * 40)
        print(projects_section)
        print("-" * 40)
        
        # Step 2: Split into project blocks
        print("\n2. Splitting into project blocks...")
        project_blocks = split_project_blocks(projects_section)
        
        print(f"✅ Found {len(project_blocks)} project blocks")
        
        # Step 3: Test project title detection
        print("\n3. Testing project title detection...")
        lines = projects_section.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                is_title = is_project_title(line)
                print(f"Line {i+1}: '{line}' -> {'TITLE' if is_title else 'NOT TITLE'}")
        
        # Step 4: Extract and format projects
        print("\n4. Extracting and formatting projects...")
        projects = extract_and_format_projects(cv_content)
        
        print(f"✅ Extracted {len(projects)} projects:")
        for i, project in enumerate(projects, 1):
            print(f"\nProject {i}:")
            print(f"  Title: {project.get('title', 'N/A')}")
            print(f"  Duration: {project.get('duration', 'N/A')}")
            print(f"  Description: {project.get('description', 'N/A')}")
            print(f"  Technologies: {', '.join(project.get('technologies', []))}")
            print(f"  Highlights: {len(project.get('highlights', []))} items")
            if project.get('highlights'):
                for highlight in project['highlights'][:2]:  # Show first 2 highlights
                    print(f"    - {highlight}")
        
    else:
        print("❌ No projects section found!")
        
        # Try to find any mention of projects
        if 'PROJECTS' in cv_content.upper():
            print("⚠️ 'PROJECTS' keyword found but section not extracted")
            # Find the line with PROJECTS
            lines = cv_content.split('\n')
            for i, line in enumerate(lines):
                if 'PROJECTS' in line.upper():
                    print(f"Found 'PROJECTS' on line {i+1}: '{line}'")
                    # Show next few lines
                    print("Next few lines:")
                    for j in range(i+1, min(i+10, len(lines))):
                        print(f"  {j+1}: {lines[j]}")
                    break
        else:
            print("❌ No 'PROJECTS' keyword found in CV")

if __name__ == "__main__":
    debug_cv_extraction() 