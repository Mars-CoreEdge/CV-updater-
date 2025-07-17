#!/usr/bin/env python3
"""
Test CV Builder functionality
"""

import requests
import json

def test_cv_builder():
    """Test CV builder with special characters and section placement"""
    
    # Test data with special characters and spaces
    test_cv_data = {
        "personal_info": {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-234-567-8900",
            "address": "New York, NY, USA",
            "linkedin": "https://linkedin.com/in/johndoe",
            "website": "https://johndoe.com"
        },
        "profile_summary": "Passionate AI Researcher with expertise in machine learning and data science.",
        "skills": {
            "technical": [
                "C++",
                "AI Researcher",
                "Data Science @ MIT",
                "Python 3.8+",
                "React.js",
                "Node.js",
                "MongoDB",
                "Docker & Kubernetes"
            ],
            "professional": [
                "Team Leadership",
                "Project Management",
                "Agile/Scrum",
                "Technical Writing",
                "Problem Solving"
            ]
        },
        "experience": [
            {
                "job_title": "Senior AI Researcher",
                "company": "TechCorp Inc.",
                "duration": "Jan 2023 - Present",
                "description": "Leading AI research projects and developing machine learning models.",
                "achievements": [
                    "Improved model accuracy by 25%",
                    "Led team of 5 researchers",
                    "Published 3 research papers"
                ]
            },
            {
                "job_title": "Data Scientist",
                "company": "DataCorp Ltd.",
                "duration": "Mar 2021 - Dec 2022",
                "description": "Developed predictive models and data analysis solutions.",
                "achievements": [
                    "Built recommendation system",
                    "Reduced processing time by 40%"
                ]
            }
        ],
        "education": [
            {
                "degree": "Master of Science in Computer Science",
                "institution": "MIT",
                "year": "2021",
                "grade": "3.9 GPA"
            },
            {
                "degree": "Bachelor of Science in Mathematics",
                "institution": "Stanford University",
                "year": "2019",
                "grade": "3.8 GPA"
            }
        ],
        "projects": [
            {
                "title": "AI Chatbot for CV Editing",
                "description": "Built an intelligent chatbot that helps users edit and improve their CVs using natural language processing.",
                "duration": "6 months",
                "technologies": ["Python", "OpenAI API", "React", "Node.js"],
                "highlights": [
                    "Improved CV quality by 30%",
                    "Processed 1000+ CVs",
                    "Achieved 95% user satisfaction"
                ]
            },
            {
                "title": "E-commerce Platform",
                "description": "Developed a full-stack e-commerce solution with payment integration and inventory management.",
                "duration": "4 months",
                "technologies": ["React", "Node.js", "MongoDB", "Stripe API"],
                "highlights": [
                    "Increased sales by 40%",
                    "Reduced checkout time by 50%",
                    "Integrated 3 payment gateways"
                ]
            }
        ]
    }
    
    try:
        # Test the CV builder endpoint
        print("🧪 Testing CV Builder with special characters...")
        
        response = requests.post(
            "http://localhost:8081/cv/create-from-builder",
            json=test_cv_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ CV Builder test successful!")
            print(f"📄 CV Title: {result.get('title', 'N/A')}")
            print(f"📊 Status: {result.get('status', 'N/A')}")
            
            # Check if CV content was generated
            cv_content = result.get('cv_content', '')
            if cv_content:
                print(f"📝 CV Content Length: {len(cv_content)} characters")
                
                # Check for sections
                sections_to_check = [
                    "PROFILE SUMMARY",
                    "SKILLS", 
                    "WORK EXPERIENCE",
                    "EDUCATION",
                    "PROJECTS"
                ]
                
                print("\n📋 Section Placement Check:")
                for section in sections_to_check:
                    if section in cv_content:
                        print(f"✅ {section} - Found")
                    else:
                        print(f"❌ {section} - Missing")
                
                # Check for special characters
                special_chars = ["C++", "AI Researcher", "Data Science @ MIT", "Python 3.8+"]
                print("\n🔤 Special Characters Check:")
                for char in special_chars:
                    if char in cv_content:
                        print(f"✅ '{char}' - Found")
                    else:
                        print(f"❌ '{char}' - Missing")
                
                # Show a preview of the generated CV
                print(f"\n📄 CV Preview (first 500 characters):")
                print("-" * 50)
                print(cv_content[:500])
                print("-" * 50)
                
            else:
                print("❌ No CV content generated")
                
        else:
            print(f"❌ CV Builder test failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Make sure it's running on port 8081.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_cv_builder() 