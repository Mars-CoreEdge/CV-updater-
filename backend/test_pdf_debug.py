#!/usr/bin/env python3
"""
Debug script to test PDF generation directly
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fpdf_import():
    """Test if FPDF is working correctly"""
    print("🔍 Testing FPDF Import...")
    
    try:
        from fpdf import FPDF
        print("✅ FPDF imported successfully")
        
        # Test basic PDF creation
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Test PDF', ln=True, align='C')
        pdf.cell(0, 10, 'This is a test PDF', ln=True, align='C')
        
        # Save to bytes
        from io import BytesIO
        pdf_bytes = BytesIO()
        pdf.output(pdf_bytes, 'S')
        pdf_bytes.seek(0)
        
        content = pdf_bytes.getvalue()
        print(f"✅ Basic PDF created successfully! Size: {len(content)} bytes")
        
        # Save to file for inspection
        with open("test_basic.pdf", "wb") as f:
            f.write(content)
        print("✅ Test PDF saved as 'test_basic.pdf'")
        
        return True
        
    except Exception as e:
        print(f"❌ FPDF test failed: {e}")
        return False

def test_enhanced_pdf():
    """Test the enhanced PDF generation function"""
    print("\n🔍 Testing Enhanced PDF Generation...")
    
    try:
        from main_enhanced import generate_enhanced_pdf, clean_cv_text
        
        # Test CV content
        test_cv = """JOHN DOE
Software Engineer

CONTACT INFORMATION
Phone: (555) 123-4567
Email: john.doe@email.com

ABOUT MYSELF
Passionate software engineer with 5+ years of experience.

SKILLS
JavaScript, Python, React, Node.js

WORK EXPERIENCE
Senior Developer at TechCorp (2020-2023)
- Led development team
- Built scalable applications

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley (2016-2020)"""
        
        # Clean the CV content
        cleaned_cv = clean_cv_text(test_cv)
        print(f"✅ CV content cleaned successfully ({len(cleaned_cv)} characters)")
        
        # Generate PDF
        pdf_bytes = generate_enhanced_pdf(cleaned_cv)
        content = pdf_bytes.getvalue()
        
        print(f"✅ Enhanced PDF generated successfully! Size: {len(content)} bytes")
        
        # Save to file
        with open("test_enhanced.pdf", "wb") as f:
            f.write(content)
        print("✅ Enhanced PDF saved as 'test_enhanced.pdf'")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced PDF test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing Database Connection...")
    
    try:
        from main_enhanced import get_db_cursor_context
        
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute("SELECT COUNT(*) FROM cvs")
            count = cursor.fetchone()[0]
            print(f"✅ Database connection successful! CV count: {count}")
            
            # Get current CV
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if cv_row:
                cv_content = cv_row[0]
                print(f"✅ Current CV retrieved! Length: {len(cv_content)} characters")
                return cv_content
            else:
                print("⚠️ No active CV found in database")
                return None
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return None

def main():
    print("🚀 PDF Generation Debug Test")
    print("=" * 50)
    
    # Test 1: Basic FPDF
    if not test_fpdf_import():
        print("❌ Basic FPDF test failed - cannot proceed")
        return
    
    # Test 2: Enhanced PDF
    if not test_enhanced_pdf():
        print("❌ Enhanced PDF test failed")
        return
    
    # Test 3: Database
    cv_content = test_database_connection()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    
    if cv_content:
        print("📄 Testing PDF generation with actual CV...")
        try:
            from main_enhanced import generate_enhanced_pdf, clean_cv_text
            
            cleaned_cv = clean_cv_text(cv_content)
            pdf_bytes = generate_enhanced_pdf(cleaned_cv)
            content = pdf_bytes.getvalue()
            
            with open("actual_cv.pdf", "wb") as f:
                f.write(content)
            print(f"✅ Actual CV PDF generated! Size: {len(content)} bytes")
            print("📄 Saved as 'actual_cv.pdf'")
            
        except Exception as e:
            print(f"❌ Actual CV PDF generation failed: {e}")

if __name__ == "__main__":
    main() 