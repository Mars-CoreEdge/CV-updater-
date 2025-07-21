#!/usr/bin/env python3
"""
Test script for PDF generation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_enhanced import generate_cv_pdf
from io import BytesIO

def test_pdf_generation():
    """Test PDF generation with sample data"""
    
    # Sample CV content
    sample_cv = """
JOHN DOE
john.doe@email.com | +1-555-123-4567 | linkedin.com/in/johndoe

PROFILE SUMMARY
Experienced software developer with 5+ years in web development.

SKILLS
• JavaScript, React, Node.js
• Python, Django, FastAPI
• MongoDB, PostgreSQL
• AWS, Docker

EXPERIENCE
Software Developer | Tech Corp | 2020-2023
• Developed web applications using React and Node.js
• Implemented RESTful APIs

EDUCATION
Bachelor of Computer Science | University of Technology | 2016-2020
"""

    # Sample projects
    sample_projects = [
        {
            "title": "E-commerce Platform",
            "description": "Built a full-stack e-commerce platform",
            "duration": "Jan 2023 - Mar 2023",
            "technologies": ["React", "Node.js", "MongoDB"],
            "highlights": ["Implemented user authentication", "Built payment integration"]
        },
        {
            "title": "Task Management App",
            "description": "Created a collaborative task management application",
            "duration": "Apr 2023 - Jun 2023",
            "technologies": ["React", "Express", "PostgreSQL"],
            "highlights": ["Real-time updates", "Team collaboration features"]
        }
    ]
    
    try:
        print("🔄 Testing PDF generation...")
        
        # Test with projects
        pdf_buffer = generate_cv_pdf(sample_cv, sample_projects)
        
        if pdf_buffer and pdf_buffer.getvalue():
            print("✅ PDF generated successfully!")
            print(f"📄 PDF size: {len(pdf_buffer.getvalue())} bytes")
            
            # Save test PDF
            with open("test_cv_with_projects.pdf", "wb") as f:
                f.write(pdf_buffer.getvalue())
            print("💾 Test PDF saved as 'test_cv_with_projects.pdf'")
            
        else:
            print("❌ PDF generation failed - empty buffer")
            return False
            
        # Test without projects
        pdf_buffer_no_projects = generate_cv_pdf(sample_cv, [])
        
        if pdf_buffer_no_projects and pdf_buffer_no_projects.getvalue():
            print("✅ PDF generation without projects successful!")
            
            # Save test PDF
            with open("test_cv_no_projects.pdf", "wb") as f:
                f.write(pdf_buffer_no_projects.getvalue())
            print("💾 Test PDF saved as 'test_cv_no_projects.pdf'")
            
        else:
            print("❌ PDF generation without projects failed")
            return False
            
        print("🎉 All PDF generation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ PDF generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1) 