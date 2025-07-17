#!/usr/bin/env python3
"""
Test Enter key and multi-line input functionality
"""

import requests
import json

def test_multi_line_input():
    """Test CV builder with multi-line input and special characters"""
    
    # Test data with multi-line content and special characters
    test_cv_data = {
        "personal_info": {
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-234-567-8900",
            "address": "New York, NY, USA",
            "linkedin": "https://linkedin.com/in/johndoe",
            "website": "https://johndoe.com"
        },
        "profile_summary": """Passionate AI Researcher with expertise in machine learning and data science.

• Led multiple research projects in computer vision
• Published 5 papers in top-tier conferences
• Mentored 10+ junior researchers
• Specialized in deep learning and neural networks""",
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
                "description": """Leading AI research projects and developing machine learning models.

• Improved model accuracy by 25% through innovative algorithms
• Led team of 5 researchers across multiple projects
• Published 3 research papers in top conferences
• Implemented new training methodologies""",
                "achievements": [
                    "Improved model accuracy by 25%",
                    "Led team of 5 researchers",
                    "Published 3 research papers"
                ]
            }
        ],
        "education": [
            {
                "degree": "Master of Science in Computer Science",
                "institution": "MIT",
                "year": "2021",
                "grade": "3.9 GPA"
            }
        ],
        "projects": [
            {
                "title": "AI Chatbot for CV Editing",
                "description": """Built an intelligent chatbot that helps users edit and improve their CVs using natural language processing.

• Implemented advanced NLP algorithms for text understanding
• Created user-friendly interface with real-time feedback
• Integrated multiple AI models for comprehensive analysis
• Achieved 95% user satisfaction rate""",
                "duration": "6 months",
                "technologies": ["Python", "OpenAI API", "React", "Node.js"],
                "highlights": [
                    "Improved CV quality by 30%",
                    "Processed 1000+ CVs",
                    "Achieved 95% user satisfaction"
                ]
            }
        ]
    }
    
    try:
        # Test the CV builder endpoint
        print("🧪 Testing CV Builder with multi-line input and special characters...")
        
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
                
                # Check for multi-line content
                print("\n📋 Multi-line Content Check:")
                if "• Led multiple research projects" in cv_content:
                    print("✅ Multi-line profile summary - Found")
                else:
                    print("❌ Multi-line profile summary - Missing")
                
                if "• Improved model accuracy by 25%" in cv_content:
                    print("✅ Multi-line experience description - Found")
                else:
                    print("❌ Multi-line experience description - Missing")
                
                if "• Implemented advanced NLP algorithms" in cv_content:
                    print("✅ Multi-line project description - Found")
                else:
                    print("❌ Multi-line project description - Missing")
                
                # Check for special characters
                special_chars = ["C++", "AI Researcher", "Data Science @ MIT", "Python 3.8+", "Docker & Kubernetes"]
                print("\n🔤 Special Characters Check:")
                for char in special_chars:
                    if char in cv_content:
                        print(f"✅ '{char}' - Found")
                    else:
                        print(f"❌ '{char}' - Missing")
                
                # Show a preview of the generated CV
                print(f"\n📄 CV Preview (first 800 characters):")
                print("-" * 50)
                print(cv_content[:800])
                print("-" * 50)
                
                # Check for proper line breaks
                lines = cv_content.split('\n')
                print(f"\n📊 Line Analysis:")
                print(f"Total lines: {len(lines)}")
                print(f"Lines with bullet points: {len([l for l in lines if l.strip().startswith('•')])}")
                print(f"Empty lines: {len([l for l in lines if not l.strip()])}")
                
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
    test_multi_line_input() 