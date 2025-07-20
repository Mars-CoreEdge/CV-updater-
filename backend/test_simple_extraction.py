#!/usr/bin/env python3
"""
Simple test for project extraction
"""

from project_extractor import extract_and_format_projects

def test_simple_extraction():
    """Test simple project extraction"""
    
    # The exact CV content from the test
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
    
    print("🧪 Testing Simple Project Extraction")
    print("=" * 50)
    
    print(f"📄 CV content length: {len(cv_content)}")
    print(f"📄 CV content preview: {cv_content[:200]}...")
    
    # Check if PROJECTS keyword exists
    if 'PROJECTS' in cv_content.upper():
        print("✅ 'PROJECTS' keyword found in CV")
    else:
        print("❌ 'PROJECTS' keyword NOT found in CV")
    
    # Test extraction
    try:
        extracted_projects = extract_and_format_projects(cv_content)
        print(f"🔍 Extracted {len(extracted_projects)} projects")
        
        for i, project in enumerate(extracted_projects, 1):
            print(f"  Project {i}: {project.get('title', 'N/A')}")
            print(f"    Description: {project.get('description', 'N/A')}")
            print(f"    Technologies: {project.get('technologies', [])}")
        
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_extraction() 