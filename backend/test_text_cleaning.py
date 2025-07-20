#!/usr/bin/env python3
"""
Test text cleaning and its effect on project extraction
"""

from main_enhanced import clean_cv_text
from project_extractor import extract_and_format_projects

def test_text_cleaning():
    """Test how text cleaning affects project extraction"""
    
    # The exact CV content
    original_cv = """JOHN DOE
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
    
    print("🧪 Testing Text Cleaning Effect on Project Extraction")
    print("=" * 60)
    
    print(f"📄 Original CV length: {len(original_cv)}")
    print(f"📄 Original CV preview: {original_cv[:200]}...")
    
    # Test extraction on original text
    print("\n1. Testing extraction on ORIGINAL text:")
    try:
        original_projects = extract_and_format_projects(original_cv)
        print(f"✅ Original text: Extracted {len(original_projects)} projects")
        for i, project in enumerate(original_projects, 1):
            print(f"  Project {i}: {project.get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ Original text extraction failed: {e}")
    
    # Clean the text
    print("\n2. Cleaning the text...")
    cleaned_cv = clean_cv_text(original_cv)
    print(f"📄 Cleaned CV length: {len(cleaned_cv)}")
    print(f"📄 Cleaned CV preview: {cleaned_cv[:200]}...")
    
    # Check if PROJECTS keyword exists in cleaned text
    if 'PROJECTS' in cleaned_cv.upper():
        print("✅ 'PROJECTS' keyword found in cleaned CV")
    else:
        print("❌ 'PROJECTS' keyword NOT found in cleaned CV")
    
    # Test extraction on cleaned text
    print("\n3. Testing extraction on CLEANED text:")
    try:
        cleaned_projects = extract_and_format_projects(cleaned_cv)
        print(f"✅ Cleaned text: Extracted {len(cleaned_projects)} projects")
        for i, project in enumerate(cleaned_projects, 1):
            print(f"  Project {i}: {project.get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ Cleaned text extraction failed: {e}")
    
    # Compare results
    print("\n4. Comparison:")
    print(f"Original text projects: {len(original_projects) if 'original_projects' in locals() else 'N/A'}")
    print(f"Cleaned text projects: {len(cleaned_projects) if 'cleaned_projects' in locals() else 'N/A'}")

if __name__ == "__main__":
    test_text_cleaning() 