#!/usr/bin/env python3
"""
Final test script to show the complete project extraction results
"""

from project_extractor import extract_and_format_projects

# Sample CV content
sample_cv = """
PROFESSIONAL CV
Massachusetts Institute of Technology (MIT), 2022 – 2024 | GPA: 3.9/4.0 | Indian
Institute of Technology (IIT) Bombay, 2018 – 2022 | GPA: 8.7/10 | Google,
Mountain View, CA — Summer 2023 | Improved processing speed by 30% through
optimization | Startup Inc., Remote — Jan 2022 to June 2023 | Achieved 85%
accuracy using natural language processing and clustering algorithms
____________________________________________________________
Profile
__________________________________________________
Enthusiastic And Detail-Oriented Software
Engineer With A Strong Foundation In Backend
Development, Artificial Intelligence, And Cloud
Infrastructure. Passionate About Building Impactful
Technology And Solving Real-World Problems.
Quick Learner, Effective Communicator, And A
Proactive Team Player.
__________________________________________________
Skills
__________________________________________________
Programming Languages: JavaScript, Python, TypeScript, SQL
Web Technologies: React, Node.js, Express.js, Next.js
Databases: PostgreSQL, Supabase, MongoDB
Tools & Platforms: Git, Docker, AWS, Vercel, Firebase
Soft Skills: Communication, Collaboration, Problem
Solving
__________________________________________________
Education
__________________________________________________
Master of Science in Computer Science
Specialized in Artificial Intelligence and Machine Learning
Bachelor of Technology in Computer Engineering
Minor in Data Science
Experience
__________________________________________________
Software Engineer Intern
Built a scalable data pipeline using Python and Apache Beam
Backend Developer
Developed and maintained RESTful APIs using Node.js
Integrated PostgreSQL and Supabase for dynamic data storage
Projects
__________________________________________________
AI-Powered Resume Builder
Built a chatbot interface to edit resumes dynamically via prompts
Integrated Supabase for real-time backend operations
JobMatch
A machine learning project to match users with ideal job roles based on their CV
Open Source Contributor
Contributed to the React Hook Form open source project
Improved documentation and created reusable form components
Generated on July 21, 2025 | CV Updater Platform
"""

def test_final_extraction():
    print("🎯 FINAL PROJECT EXTRACTION TEST")
    print("=" * 60)
    
    # Extract projects
    projects = extract_and_format_projects(sample_cv)
    
    print(f"✅ Successfully extracted {len(projects)} projects!")
    print()
    
    for i, project in enumerate(projects, 1):
        print(f"📋 PROJECT {i}: {project.get('title', 'N/A')}")
        print(f"   📝 Description: {project.get('description', 'N/A')}")
        print(f"   🛠️  Technologies: {', '.join(project.get('technologies', [])) if project.get('technologies') else 'N/A'}")
        print(f"   ⭐ Highlights: {len(project.get('highlights', []))} items")
        for j, highlight in enumerate(project.get('highlights', []), 1):
            print(f"      {j}. {highlight}")
        print(f"   ⏱️  Duration: {project.get('duration', 'N/A')}")
        print(f"   👤 Role: {project.get('role', 'N/A')}")
        print(f"   🆔 ID: {project.get('id', 'N/A')}")
        print("-" * 50)
    
    # Validation
    expected_projects = ["AI-Powered Resume Builder", "JobMatch", "Open Source Contributor"]
    extracted_titles = [p.get('title', '') for p in projects]
    
    print("\n🔍 VALIDATION RESULTS:")
    print("=" * 30)
    all_found = True
    for expected in expected_projects:
        if expected in extracted_titles:
            print(f"✅ Found: {expected}")
        else:
            print(f"❌ Missing: {expected}")
            all_found = False
    
    if all_found:
        print("\n🎉 SUCCESS: All expected projects were extracted!")
    else:
        print("\n⚠️  WARNING: Some expected projects were missing.")
    
    print(f"\n📊 SUMMARY: {len(projects)} projects extracted from CV")
    return projects

if __name__ == "__main__":
    test_final_extraction() 