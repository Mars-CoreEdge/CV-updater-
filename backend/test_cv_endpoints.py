#!/usr/bin/env python3
"""
Comprehensive test script for all CV-related endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8081"

def test_endpoint(endpoint, method="GET", data=None, files=None):
    """Test a specific endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
            
        print(f"✅ {method} {endpoint}: {response.status_code}")
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            except:
                print(f"   Response: {response.text[:200]}...")
        elif response.status_code >= 400:
            print(f"   Error: {response.text}")
        return response.status_code < 400
    except Exception as e:
        print(f"❌ {method} {endpoint}: Error - {e}")
        return False

def create_test_cv():
    """Create a test CV file with the actual content"""
    cv_content = """Abuzar Asif
Phone: (+92) 3010422906
Email: Abuzarasif19@gmail.com
LinkedIn: https://www.linkedin.com/in/abuzar-asif-a50342243/
Home: Lahore (Pakistan)

ABOUT MYSELF
Results-oriented Front-End Developer with a proven track record of creating engaging, high-performance web applications. Proficient in JavaScript, React.js, and modern front-end technologies. Committed to staying updated with industry trends and best practices. Seeking a challenging role where I can contribute my skills and passion to a dynamic team.

SKILLS
Front End (Html, Css, JQuery, Bootstrap, Javascript, React js) / GitHub / Python Language - Basic knowledge / C++ / Redux toolkit / GSAP / Framer Motion / Postman / Auth with JWT / Axios

WORK EXPERIENCE
Pixarsart Studios – Lahore, Pakistan
City: Lahore | Country: Pakistan
Junior React Js Developer
[ 01/01/2025 – 03/03/2025 ]
I worked as a React.js Developer at Pixarsart, where I developed and maintained the company's official website with a focus on responsive, user-friendly design. I contributed to key projects like the GMCI Dashboard, integrating RESTful APIs and building dynamic UI components, and Elevated Iron, enhancing front-end performance and features. I collaborated closely with designers and back-end developers to ensure seamless application delivery.

Intern at Dynamic Developers – Lahore, Pakistan
City: Lahore | Country: Pakistan
Front End Website Developer
[ 10/08/2023 – 10/10/2023 ]
Developed and customized the Swift Trucking Dispatch company website and multiple mini projects using HTML, CSS, jQuery, Bootstrap, and React JS during an internship at Dynamics Developers. Acquired practical experience in building responsive and interactive web pages aligned with industry standards.

Intern at DigitsCom Technologies – Lahore, Pakistan
City: Lahore | Country: Pakistan
Web Developer
[ 01/05/2022 – 30/09/2022 ]
Developed and customized SFRA clone pages, Digiskills Clone, Saylani Welfare website, and Techlead Clone 4.0 using HTML, CSS, jQuery, and JavaScript during an internship at DigitsCom Technologies. Gained hands-on experience in creating responsive and interactive web pages following industry standards.

EDUCATION AND TRAINING
Bachelor of Science in Computer Science
University of Engineering and Technology, Lahore
[ 15/09/2020 – 15/05/2024 ]
City: Lahore | Country: Pakistan"""
    
    with open("test_cv_actual.txt", "w", encoding="utf-8") as f:
        f.write(cv_content)
    
    return "test_cv_actual.txt"

def main():
    print("🚀 Testing CV Updater Backend - All CV Endpoints")
    print("=" * 60)
    
    # Create test CV file
    test_file = create_test_cv()
    
    # Test basic endpoints
    print("\n📋 Testing Basic Endpoints:")
    test_endpoint("/")
    test_endpoint("/docs")
    
    # Test CV upload
    print("\n📤 Testing CV Upload:")
    with open(test_file, "rb") as f:
        files = {"file": (test_file, f, "text/plain")}
        test_endpoint("/upload-cv/", method="POST", files=files)
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Test CV retrieval endpoints
    print("\n📄 Testing CV Retrieval:")
    test_endpoint("/cv/current/")
    test_endpoint("/cv/enhanced/")
    test_endpoint("/cvs/")
    
    # Test PDF generation
    print("\n📄 Testing PDF Generation:")
    test_endpoint("/cv/pdf-preview")
    
    # Test chat functionality
    print("\n💬 Testing Chat Functionality:")
    test_endpoint("/chat/history/")
    
    # Test project endpoints
    print("\n🔧 Testing Project Endpoints:")
    test_endpoint("/projects/")
    test_endpoint("/projects/list")
    
    # Test CV management
    print("\n⚙️ Testing CV Management:")
    test_endpoint("/cv/cleanup", method="POST")
    test_endpoint("/cv/generate", method="POST")
    
    # Test diagnostics
    print("\n🔍 Testing Diagnostics:")
    test_endpoint("/diagnostics/db-cv-dump")
    
    print("\n" + "=" * 60)
    print("✅ CV endpoint testing completed!")
    print(f"📖 API Documentation: {BASE_URL}/docs")
    print(f"🔗 Base URL: {BASE_URL}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    main() 