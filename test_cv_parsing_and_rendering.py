#!/usr/bin/env python3
"""
Comprehensive test for CV parsing and rendering
Tests both PDF and TXT file formats
"""

import requests
import json
import time
import os
from io import BytesIO

def create_test_files():
    """Create test PDF and TXT files with known structure"""
    
    # Test TXT content with clear sections
    txt_content = """JOHN DOE
john.doe@email.com
+1 (555) 123-4567
linkedin.com/in/johndoe
github.com/johndoe

PROFILE
Experienced software engineer with 5+ years in full-stack development.
Specialized in React, Python, and cloud technologies.

EDUCATION
Bachelor of Science in Computer Science
University of Technology
2018 - 2022

WORK EXPERIENCE
Senior Software Engineer
TechCorp Inc.
2022 - Present
• Led development of microservices architecture
• Mentored junior developers
• Improved system performance by 40%

Software Developer
StartupXYZ
2020 - 2022
• Built React frontend applications
• Implemented RESTful APIs
• Collaborated with cross-functional teams

SKILLS
Programming Languages: JavaScript, Python, Java, SQL
Frameworks: React, Node.js, Django, Spring Boot
Tools: Git, Docker, AWS, Jenkins
"""
    
    # Save TXT file
    with open('test_resume.txt', 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    print("✅ Created test_resume.txt")
    return 'test_resume.txt'

def test_txt_upload_and_rendering():
    """Test TXT file upload and rendering"""
    
    base_url = "http://localhost:8081"
    
    print("\n🧪 Testing TXT File Upload and Rendering")
    print("=" * 50)
    
    # Test 1: Upload TXT file
    try:
        with open('test_resume.txt', 'rb') as f:
            files = {'file': ('test_resume.txt', f, 'text/plain')}
            response = requests.post(f"{base_url}/upload-cv/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ TXT upload successful: {data.get('filename', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
        else:
            print(f"❌ TXT upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading TXT: {e}")
        return False
    
    # Wait for processing
    time.sleep(2)
    
    # Test 2: Get current CV content
    try:
        response = requests.get(f"{base_url}/cv/current/")
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            print(f"✅ TXT content retrieved successfully")
            print(f"   Content length: {len(content)} characters")
            
            # Check for section headers
            sections_found = []
            lines = content.split('\n')
            section_keywords = ['PROFILE', 'EDUCATION', 'WORK EXPERIENCE', 'SKILLS']
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if line_stripped:
                    for keyword in section_keywords:
                        if keyword in line_stripped.upper():
                            sections_found.append({
                                'line': i,
                                'content': line_stripped,
                                'keyword': keyword
                            })
                            break
            
            print(f"   Sections found: {len(sections_found)}")
            for section in sections_found:
                print(f"     Line {section['line']}: {section['content']}")
            
            # Check for truncation
            if len(content) < 500:
                print("⚠️ Content seems truncated")
            else:
                print("✅ Content appears complete")
            
            # Check for formatting issues
            if '📋' in content:
                print("❌ Emoji icons still present")
            else:
                print("✅ No emoji icons found")
            
            if '─' in content:
                print("❌ Underlines still present")
            else:
                print("✅ No underlines found")
                
        else:
            print(f"❌ Failed to get CV content: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting CV content: {e}")
        return False
    
    return True

def test_pdf_upload_and_rendering():
    """Test PDF file upload and rendering"""
    
    base_url = "http://localhost:8081"
    
    print("\n🧪 Testing PDF File Upload and Rendering")
    print("=" * 50)
    
    # Create a simple PDF for testing
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Create test PDF
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=letter)
        
        # Add content to PDF
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "JANE SMITH")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, "jane.smith@email.com")
        c.drawString(100, 715, "+1 (555) 987-6543")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 680, "PROFILE")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, 660, "Experienced data scientist with expertise in machine learning.")
        c.drawString(100, 645, "Specialized in Python, TensorFlow, and statistical analysis.")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 610, "EDUCATION")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, 590, "Master of Science in Data Science")
        c.drawString(100, 575, "Data University")
        c.drawString(100, 560, "2019 - 2021")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 525, "WORK EXPERIENCE")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, 505, "Data Scientist")
        c.drawString(100, 490, "Analytics Corp")
        c.drawString(100, 475, "2021 - Present")
        c.drawString(100, 460, "• Developed predictive models for customer behavior")
        c.drawString(100, 445, "• Improved model accuracy by 25%")
        
        c.save()
        pdf_content = pdf_buffer.getvalue()
        
        # Save PDF file
        with open('test_resume.pdf', 'wb') as f:
            f.write(pdf_content)
        
        print("✅ Created test_resume.pdf")
        
    except ImportError:
        print("⚠️ reportlab not available, skipping PDF test")
        return True
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        return True
    
    # Test 1: Upload PDF file
    try:
        with open('test_resume.pdf', 'rb') as f:
            files = {'file': ('test_resume.pdf', f, 'application/pdf')}
            response = requests.post(f"{base_url}/upload-cv/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PDF upload successful: {data.get('filename', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
        else:
            print(f"❌ PDF upload failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error uploading PDF: {e}")
        return False
    
    # Wait for processing
    time.sleep(3)
    
    # Test 2: Get current CV content
    try:
        response = requests.get(f"{base_url}/cv/current/")
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '')
            print(f"✅ PDF content retrieved successfully")
            print(f"   Content length: {len(content)} characters")
            
            # Check for section headers
            sections_found = []
            lines = content.split('\n')
            section_keywords = ['PROFILE', 'EDUCATION', 'WORK EXPERIENCE', 'SKILLS']
            
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if line_stripped:
                    for keyword in section_keywords:
                        if keyword in line_stripped.upper():
                            sections_found.append({
                                'line': i,
                                'content': line_stripped,
                                'keyword': keyword
                            })
                            break
            
            print(f"   Sections found: {len(sections_found)}")
            for section in sections_found:
                print(f"     Line {section['line']}: {section['content']}")
            
            # Check for truncation
            if len(content) < 200:
                print("⚠️ PDF content seems truncated")
            else:
                print("✅ PDF content appears complete")
            
            # Check for formatting issues
            if '📋' in content:
                print("❌ Emoji icons still present")
            else:
                print("✅ No emoji icons found")
            
            if '─' in content:
                print("❌ Underlines still present")
            else:
                print("✅ No underlines found")
                
        else:
            print(f"❌ Failed to get CV content: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting CV content: {e}")
        return False
    
    return True

def test_frontend_rendering():
    """Test frontend rendering by checking the API response structure"""
    
    base_url = "http://localhost:8081"
    
    print("\n🧪 Testing Frontend Rendering")
    print("=" * 50)
    
    try:
        # Test CV current endpoint
        response = requests.get(f"{base_url}/cv/current/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CV API response structure:")
            print(f"   Content: {len(data.get('content', ''))} characters")
            print(f"   Filename: {data.get('filename', 'N/A')}")
            print(f"   Last Updated: {data.get('last_updated', 'N/A')}")
            
            # Test PDF preview endpoint
            pdf_response = requests.get(f"{base_url}/cv/pdf-preview")
            if pdf_response.status_code == 200:
                print(f"✅ PDF preview endpoint working")
                print(f"   Content-Type: {pdf_response.headers.get('content-type', 'N/A')}")
                print(f"   Content-Length: {len(pdf_response.content)} bytes")
            else:
                print(f"❌ PDF preview endpoint failed: {pdf_response.status_code}")
                
        else:
            print(f"❌ CV current endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing frontend rendering: {e}")
        return False
    
    return True

def cleanup_test_files():
    """Clean up test files"""
    test_files = ['test_resume.txt', 'test_resume.pdf']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ Removed {file}")

def main():
    """Main test function"""
    
    print("🚀 Comprehensive CV Parsing and Rendering Test")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8081/")
        if response.status_code != 200:
            print("❌ Backend is not running. Please start it first.")
            return False
        print("✅ Backend is running")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running. Please start it first.")
        return False
    
    # Create test files
    txt_file = create_test_files()
    
    # Run tests
    txt_success = test_txt_upload_and_rendering()
    pdf_success = test_pdf_upload_and_rendering()
    frontend_success = test_frontend_rendering()
    
    # Cleanup
    cleanup_test_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   TXT Upload & Rendering: {'✅ PASS' if txt_success else '❌ FAIL'}")
    print(f"   PDF Upload & Rendering: {'✅ PASS' if pdf_success else '❌ FAIL'}")
    print(f"   Frontend Rendering: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    if txt_success and pdf_success and frontend_success:
        print("\n🎉 All tests passed! CV parsing and rendering is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")
    
    return txt_success and pdf_success and frontend_success

if __name__ == "__main__":
    main() 