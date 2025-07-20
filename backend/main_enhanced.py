from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
import PyPDF2
import docx2txt
from dotenv import load_dotenv
import os
import requests
import re
import psycopg2
from fpdf import FPDF
from io import BytesIO
import json
import threading
from contextlib import contextmanager
from typing import List, Optional
from datetime import datetime

# Import database connection
try:
    from db import get_db_cursor
    USE_SUPABASE = False  # Temporarily using SQLite
    print("✅ Using SQLite database (temporary)")
except ImportError:
    print("❌ ERROR: db.py not found. Please ensure the database configuration file exists.")
    raise ImportError("Database configuration file (db.py) is required")

# Enhanced Section Detection Patterns - Updated for simple CV format
SECTION_PATTERNS = {
    "contact": [
        r"^CONTACT\s+INFORMATION$",
        r"^CONTACT$",
        r"^PERSONAL\s+INFORMATION$",
        r"^DETAILS$",
        r"^[_\-=\s]*CONTACT\s+INFORMATION[_\-=\s]*$",
        r"^[_\-=\s]*CONTACT[_\-=\s]*$",
        r"^[_\-=\s]*PERSONAL\s+INFORMATION[_\-=\s]*$",
        r"^[_\-=\s]*DETAILS[_\-=\s]*$"
    ],
    "profile": [
        r"^ABOUT\s+MYSELF$",
        r"^ABOUT\s+ME$",
        r"^PROFILE$",
        r"^PROFILE\s+SUMMARY$",
        r"^SUMMARY$",
        r"^PERSONAL\s+PROFILE$",
        r"^OBJECTIVE$",
        r"^CAREER\s+OBJECTIVE$",
        r"^[_\-=\s]*ABOUT\s+MYSELF[_\-=\s]*$",
        r"^[_\-=\s]*ABOUT\s+ME[_\-=\s]*$",
        r"^[_\-=\s]*PROFILE[_\-=\s]*$",
        r"^[_\-=\s]*PROFILE\s+SUMMARY[_\-=\s]*$",
        r"^[_\-=\s]*SUMMARY[_\-=\s]*$",
        r"^[_\-=\s]*PERSONAL\s+PROFILE[_\-=\s]*$",
        r"^[_\-=\s]*OBJECTIVE[_\-=\s]*$",
        r"^[_\-=\s]*CAREER\s+OBJECTIVE[_\-=\s]*$"
    ],
    "skills": [
        r"^SKILLS$",
        r"^TECHNICAL\s+SKILLS$",
        r"^PROFESSIONAL\s+SKILLS$",
        r"^CORE\s+SKILLS$",
        r"^COMPETENCIES$",
        r"^EXPERTISE$",
        r"^[_\-=\s]*SKILLS[_\-=\s]*$",
        r"^[_\-=\s]*TECHNICAL\s+SKILLS[_\-=\s]*$",
        r"^[_\-=\s]*PROFESSIONAL\s+SKILLS[_\-=\s]*$",
        r"^[_\-=\s]*CORE\s+SKILLS[_\-=\s]*$",
        r"^[_\-=\s]*COMPETENCIES[_\-=\s]*$",
        r"^[_\-=\s]*EXPERTISE[_\-=\s]*$"
    ],
    "experience": [
        r"^WORK\s+EXPERIENCE$",
        r"^EXPERIENCE$",
        r"^PROFESSIONAL\s+EXPERIENCE$",
        r"^EMPLOYMENT\s+HISTORY$",
        r"^CAREER\s+HISTORY$",
        r"^WORK\s+HISTORY$",
        r"^[_\-=\s]*WORK\s+EXPERIENCE[_\-=\s]*$",
        r"^[_\-=\s]*EXPERIENCE[_\-=\s]*$",
        r"^[_\-=\s]*PROFESSIONAL\s+EXPERIENCE[_\-=\s]*$",
        r"^[_\-=\s]*EMPLOYMENT\s+HISTORY[_\-=\s]*$",
        r"^[_\-=\s]*CAREER\s+HISTORY[_\-=\s]*$",
        r"^[_\-=\s]*WORK\s+HISTORY[_\-=\s]*$"
    ],
    "education": [
        r"^EDUCATION\s+AND\s+TRAINING$",
        r"^EDUCATION$",
        r"^EDUCATIONAL\s+BACKGROUND$",
        r"^EDUCATION\s+&\s+QUALIFICATIONS$",
        r"^ACADEMIC\s+BACKGROUND$",
        r"^QUALIFICATIONS$",
        r"^ACADEMIC\s+QUALIFICATIONS$",
        r"^EDUCATION\s+&\s+TRAINING$",
        r"^[_\-=\s]*EDUCATION\s+AND\s+TRAINING[_\-=\s]*$",
        r"^[_\-=\s]*EDUCATION[_\-=\s]*$",
        r"^[_\-=\s]*EDUCATIONAL\s+BACKGROUND[_\-=\s]*$",
        r"^[_\-=\s]*EDUCATION\s+&\s+QUALIFICATIONS[_\-=\s]*$",
        r"^[_\-=\s]*ACADEMIC\s+BACKGROUND[_\-=\s]*$",
        r"^[_\-=\s]*QUALIFICATIONS[_\-=\s]*$",
        r"^[_\-=\s]*ACADEMIC\s+QUALIFICATIONS[_\-=\s]*$",
        r"^[_\-=\s]*EDUCATION\s+&\s+TRAINING[_\-=\s]*$"
    ],
    "certifications": [
        r"^CERTIFICATIONS$",
        r"^CERTIFICATES$",
        r"^CERTIFICATE$",
        r"^[_\-=\s]*CERTIFICATIONS[_\-=\s]*$",
        r"^[_\-=\s]*CERTIFICATES[_\-=\s]*$",
        r"^[_\-=\s]*CERTIFICATE[_\-=\s]*$"
    ],
    "projects": [
        r"^PROJECTS$",
        r"^PROJECT\s+EXPERIENCE$",
        r"^KEY\s+PROJECTS$",
        r"^SELECTED\s+PROJECTS$",
        r"^PORTFOLIO$",
        r"^[_\-=\s]*PROJECTS[_\-=\s]*$",
        r"^[_\-=\s]*PROJECT\s+EXPERIENCE[_\-=\s]*$",
        r"^[_\-=\s]*KEY\s+PROJECTS[_\-=\s]*$",
        r"^[_\-=\s]*SELECTED\s+PROJECTS[_\-=\s]*$",
        r"^[_\-=\s]*PORTFOLIO[_\-=\s]*$"
    ],
    "achievements": [
        r"^ACHIEVEMENTS$",
        r"^AWARDS$",
        r"^HONORS$",
        r"^RECOGNITIONS$",
        r"^[_\-=\s]*ACHIEVEMENTS[_\-=\s]*$",
        r"^[_\-=\s]*AWARDS[_\-=\s]*$",
        r"^[_\-=\s]*HONORS[_\-=\s]*$",
        r"^[_\-=\s]*RECOGNITIONS[_\-=\s]*$"
    ],
    "languages": [
        r"^LANGUAGES$",
        r"^LANGUAGE\s+SKILLS$",
        r"^[_\-=\s]*LANGUAGES[_\-=\s]*$",
        r"^[_\-=\s]*LANGUAGE\s+SKILLS[_\-=\s]*$"
    ],
    "interests": [
        r"^INTERESTS$",
        r"^HOBBIES$",
        r"^PERSONAL\s+INTERESTS$",
        r"^[_\-=\s]*INTERESTS[_\-=\s]*$",
        r"^[_\-=\s]*HOBBIES[_\-=\s]*$",
        r"^[_\-=\s]*PERSONAL\s+INTERESTS[_\-=\s]*$"
    ]
}

# Load .env from the backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

def find_section_in_cv(cv_content: str, section_name: str) -> dict:
    """
    Find a specific section in CV content using robust regex patterns.
    Returns dict with start, end, content, and header info.
    """
    if section_name not in SECTION_PATTERNS:
        return None
    
    lines = cv_content.split('\n')
    patterns = SECTION_PATTERNS[section_name]
    
    for i, line in enumerate(lines):
        line_upper = line.upper().strip()
        for pattern in patterns:
            if re.match(pattern, line_upper, re.IGNORECASE):
                # Found the section header
                start_line = i
                header_line = line
                
                # Find the end of this section (next section or end of file)
                end_line = len(lines)
                for j in range(i + 1, len(lines)):
                    # Check if this line is a header for another section
                    for other_section, other_patterns in SECTION_PATTERNS.items():
                        if other_section != section_name:
                            for other_pattern in other_patterns:
                                if re.match(other_pattern, lines[j].upper().strip(), re.IGNORECASE):
                                    end_line = j
                                    break
                            if end_line != len(lines):
                                break
                    if end_line != len(lines):
                        break
                
                # Extract section content
                section_content = '\n'.join(lines[start_line:end_line])
                
                return {
                    'start_line': start_line,
                    'end_line': end_line,
                    'start_pos': cv_content.find(line),
                    'end_pos': cv_content.find('\n'.join(lines[:end_line])) + len('\n'.join(lines[:end_line])),
                    'content': section_content,
                    'header': header_line,
                    'found': True
                }
    
    # If not found with exact patterns, try fuzzy matching
    for i, line in enumerate(lines):
        line_upper = line.upper().strip()
        # Check if line contains the section name (fuzzy match)
        if section_name.upper() in line_upper and len(line_upper) < 50:
            # Found a potential section header
            start_line = i
            header_line = line
            
            # Find the end of this section (next section or end of file)
            end_line = len(lines)
            for j in range(i + 1, len(lines)):
                # Check if this line is a header for another section
                for other_section, other_patterns in SECTION_PATTERNS.items():
                    if other_section != section_name:
                        for other_pattern in other_patterns:
                            if re.match(other_pattern, lines[j].upper().strip(), re.IGNORECASE):
                                end_line = j
                                break
                        if end_line != len(lines):
                            break
                if end_line != len(lines):
                    break
            
            # Extract section content
            section_content = '\n'.join(lines[start_line:end_line])
            
            return {
                'start_line': start_line,
                'end_line': end_line,
                'start_pos': cv_content.find(line),
                'end_pos': cv_content.find('\n'.join(lines[:end_line])) + len('\n'.join(lines[:end_line])),
                'content': section_content,
                'header': header_line,
                'found': True
            }
    
    return {'found': False}

def insert_content_in_section_enhanced(cv_content: str, section_name: str, new_content: str, insert_mode: str = "append") -> str:
    """
    Insert content into a specific CV section with enhanced logic.
    
    Args:
        cv_content: Full CV content
        section_name: Name of section to update
        new_content: Content to insert
        insert_mode: "append", "prepend", or "replace"
    
    Returns:
        Updated CV content
    """
    section_info = find_section_in_cv(cv_content, section_name)
    lines = cv_content.split('\n')
    
    if section_info and section_info['found']:
        # Section exists - insert content appropriately
        start_line = section_info['start_line']
        end_line = section_info['end_line']
        
        if insert_mode == "replace":
            # Replace entire section content
            new_section_lines = [lines[start_line]]  # Keep header
            new_section_lines.extend(new_content.split('\n'))
            lines = lines[:start_line] + new_section_lines + lines[end_line:]
        elif insert_mode == "prepend":
            # Add content at beginning of section (after header)
            new_section_lines = [lines[start_line]]  # Keep header
            new_section_lines.extend(new_content.split('\n'))
            new_section_lines.extend(lines[start_line + 1:end_line])
            lines = lines[:start_line] + new_section_lines + lines[end_line:]
        else:  # append
            # Add content at end of section
            new_section_lines = lines[start_line:end_line]
            new_section_lines.extend(new_content.split('\n'))
            lines = lines[:start_line] + new_section_lines + lines[end_line:]
    else:
        # Section doesn't exist - create it
        # Find a good position to insert (after profile/summary, before experience)
        insert_position = len(lines)
        
        # Try to insert after profile/summary
        profile_info = find_section_in_cv(cv_content, "profile")
        if profile_info and profile_info['found']:
            insert_position = profile_info['end_line']
        else:
            # Try to insert after first few lines (name, contact info)
            for i in range(min(10, len(lines))):
                if re.match(r'^[_\-=\s]*[A-Z][A-Z\s&]+[_\-=\s]*$', lines[i].upper().strip()):
                    insert_position = i
                    break
        
        # Create section header
        section_header = f"___________________________ {section_name.upper()} ___________________________"
        new_section_lines = [section_header] + new_content.split('\n')
        
        lines = lines[:insert_position] + [''] + new_section_lines + lines[insert_position:]
    
    return '\n'.join(lines)

def generate_enhanced_pdf(cv_content: str) -> BytesIO:
    """
    Generate a well-formatted PDF from CV content with enhanced styling.
    """
    # Clean the CV content before generating PDF
    cv_content = clean_cv_text(cv_content)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set fonts (fallback to default if custom fonts not available)
    try:
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
        use_custom_font = True
    except:
        use_custom_font = False
    
    # Parse CV content
    lines = cv_content.split('\n')
    
    # Extract name and title (first few lines)
    name = ""
    title = ""
    contact_info = []
    
    for i, line in enumerate(lines[:10]):
        line = line.strip()
        if line and not re.match(r'^[_\-=\s]*[A-Z][A-Z\s&]+[_\-=\s]*$', line):
            if not name:
                name = line
            elif not title and len(line) < 50:
                title = line
            elif '@' in line or re.match(r'^[\+]?[0-9\-\s\(\)]+$', line) or 'www.' in line:
                contact_info.append(line)
    
    # Header section
    if name:
        if use_custom_font:
            pdf.set_font('DejaVu', 'B', 20)
        else:
            pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, name, ln=True, align='C')
    
    if title:
        if use_custom_font:
            pdf.set_font('DejaVu', '', 14)
        else:
            pdf.set_font('Arial', '', 14)
        pdf.cell(0, 8, title, ln=True, align='C')
    
    # Contact info
    if contact_info:
        if use_custom_font:
            pdf.set_font('DejaVu', '', 10)
        else:
            pdf.set_font('Arial', '', 10)
        for contact in contact_info:
            pdf.cell(0, 6, contact, ln=True, align='C')
    
    pdf.ln(10)
    
    # Process sections
    current_section = None
    section_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header
        is_header = False
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, line.upper(), re.IGNORECASE):
                    # Process previous section
                    if current_section and section_content:
                        _write_section_to_pdf(pdf, current_section, section_content, use_custom_font)
                    
                    # Start new section
                    current_section = section_name
                    section_content = []
                    is_header = True
                    break
            if is_header:
                break
        
        if not is_header and current_section:
            section_content.append(line)
    
    # Process last section
    if current_section and section_content:
        _write_section_to_pdf(pdf, current_section, section_content, use_custom_font)
    
    # Return PDF as bytes
    pdf_bytes = BytesIO()
    pdf.output(pdf_bytes, 'S')
    pdf_bytes.seek(0)
    return pdf_bytes

def _write_section_to_pdf(pdf, section_name: str, content_lines: list, use_custom_font: bool = False):
    """Helper function to write a section to PDF with proper formatting."""
    # Section header
    if use_custom_font:
        pdf.set_font('DejaVu', 'B', 14)
    else:
        pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, section_name.upper(), ln=True, fill=True)
    pdf.ln(2)
    
    # Section content
    if use_custom_font:
        pdf.set_font('DejaVu', '', 10)
    else:
        pdf.set_font('Arial', '', 10)
    
    for line in content_lines:
        if line.strip():
            # Check if this looks like a bullet point or subheading
            if line.strip().startswith('•') or line.strip().startswith('-'):
                pdf.cell(10, 6, '', ln=False)  # Indent
                pdf.cell(0, 6, line.strip(), ln=True)
            elif re.match(r'^[A-Z][A-Za-z\s]+:', line.strip()):
                # Subheading (like "Company: ", "Duration: ")
                if use_custom_font:
                    pdf.set_font('DejaVu', 'B', 10)
                else:
                    pdf.set_font('Arial', 'B', 10)
                pdf.cell(0, 6, line.strip(), ln=True)
                if use_custom_font:
                    pdf.set_font('DejaVu', '', 10)
                else:
                    pdf.set_font('Arial', '', 10)
            else:
                pdf.cell(0, 6, line.strip(), ln=True)
    
    pdf.ln(5)

# Advanced PDF Processing Libraries
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("PyMuPDF not available")

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    print("pdfplumber not available")

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_bytes
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("OCR libraries not available")

import json
from typing import List, Optional
import os
import re
from datetime import datetime
from fastapi.responses import Response

# OpenAI setup
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    print("OpenAI library not available")
    HAS_OPENAI = False
    OpenAI = None

# Initialize OpenAI client with API key
OPENAI_API_KEY = os.getenv("VITE_OPENAI_API_KEY")

if not HAS_OPENAI:
    print("⚠️  Warning: OpenAI library not installed. Chat features will not work.")
    openai_client = None
elif not OPENAI_API_KEY or not OPENAI_API_KEY.startswith('sk-'):
    print("⚠️  Warning: OpenAI API key not set or invalid. Chat features will not work.")
    print("💡 Set VITE_OPENAI_API_KEY environment variable with your API key")
    openai_client = None
else:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        openai_client = None

app = FastAPI(title="CV Updater Chatbot with OpenAI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str

class CVResponse(BaseModel):
    content: str
    filename: str
    last_updated: Optional[str] = None

# Database setup
def init_db():
    # SQLite setup (temporary)
    try:
        cursor, conn = get_db_cursor()
        
        # Create tables if they don't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS cvs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL DEFAULT 'Untitled CV',
            filename TEXT NOT NULL,
            original_content TEXT NOT NULL,
            current_content TEXT NOT NULL,
            is_active BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            message_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS cv_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            update_type TEXT NOT NULL,
            content TEXT NOT NULL,
            original_message TEXT NOT NULL,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS manual_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ SQLite database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise Exception(f"Failed to initialize database: {e}")

def init_sqlite_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('cv_updater.db', timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS cvs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL DEFAULT 'Untitled CV',
        filename TEXT NOT NULL,
        original_content TEXT NOT NULL,
        current_content TEXT NOT NULL,
        is_active BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        message_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS cv_updates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        update_type TEXT NOT NULL,
        content TEXT NOT NULL,
        original_message TEXT NOT NULL,
        processed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS manual_projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Check if 'processed' column exists in cv_updates table and add it if not
    try:
        cursor.execute("PRAGMA table_info(cv_updates)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'processed' not in columns:
            cursor.execute("ALTER TABLE cv_updates ADD COLUMN processed BOOLEAN DEFAULT FALSE")
            print("Added 'processed' column to cv_updates table")
    except Exception as e:
        print(f"Note: {e}")
    
    # Add new columns if they don't exist
    try:
        cursor.execute("PRAGMA table_info(cvs)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'title' not in columns:
            cursor.execute("ALTER TABLE cvs ADD COLUMN title TEXT NOT NULL DEFAULT 'Untitled CV'")
            print("Added 'title' column to cvs table")
        if 'is_active' not in columns:
            cursor.execute("ALTER TABLE cvs ADD COLUMN is_active BOOLEAN DEFAULT FALSE")
            print("Added 'is_active' column to cvs table")
            
            # Set the most recent CV as active if no CV is marked as active
            cursor.execute("SELECT COUNT(*) FROM cvs WHERE is_active = TRUE")
            active_count = cursor.fetchone()[0]
            if active_count == 0:
                cursor.execute("UPDATE cvs SET is_active = TRUE WHERE id = (SELECT id FROM cvs ORDER BY updated_at DESC LIMIT 1)")
                print("Set most recent CV as active")
    except Exception as e:
        print(f"Note: {e}")
    
    conn.commit()
    conn.close()
    print("✅ SQLite database initialized successfully")

init_db()

import threading
import time
from contextlib import contextmanager

# Global database lock
db_lock = threading.RLock()

def get_db_connection():
    """Get database connection with proper error handling"""
    try:
        # Try to use the imported get_db_cursor from db.py
        from db import get_db_cursor
        # This will return a connection from the db.py module
        return None  # For now, we'll use SQLite fallback
    except ImportError:
        # Fallback to SQLite
        import sqlite3
        conn = sqlite3.connect('cv_updater.db', timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

@contextmanager
def get_db_cursor_context():
    """Context manager for database cursor with proper connection handling"""
    cursor = None
    conn = None
    try:
        import sqlite3
        conn = sqlite3.connect('cv_updater.db', timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.cursor()
        yield cursor, conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database operation error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def extract_text_from_file(file: UploadFile) -> str:
    """Enhanced file text extraction with better error handling and validation"""
    try:
        content = file.file.read()
        print(f"📄 Processing file: {file.filename} ({len(content)} bytes)")
        
        if not content:
            raise HTTPException(status_code=400, detail="File is empty or corrupted")
        
        if file.filename.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(content)
        elif file.filename.lower().endswith('.docx'):
            extracted_text = docx2txt.process(BytesIO(content))
        elif file.filename.lower().endswith('.txt'):
            # Handle different encodings for text files
            try:
                extracted_text = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    extracted_text = content.decode('latin-1')
                except UnicodeDecodeError:
                    extracted_text = content.decode('utf-8', errors='ignore')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please use PDF, DOCX, or TXT files.")
        
        # Clean up Unicode characters and normalize text
        extracted_text = clean_cv_text(extracted_text)
        
        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from file. Please check the file content.")
        
        print(f"✅ Successfully extracted {len(extracted_text)} characters from {file.filename}")
        return extracted_text.strip()
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Error extracting text from {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

def clean_cv_text(text: str) -> str:
    """Clean and normalize CV text by removing problematic Unicode characters"""
    import unicodedata
    
    # Remove or replace problematic Unicode characters
    cleaned_text = text
    
    # Replace common Unicode icons with text equivalents
    unicode_replacements = {
        '\uf1ad': '',  # Remove problematic Unicode character
        '\uf0f1': 'Phone: ',  # Phone icon
        '\uf0e0': 'Email: ',  # Email icon
        '\uf08c': 'LinkedIn: ',  # LinkedIn icon
        '\uf3c5': 'Home: ',  # Home icon
        '\uf1ad': '',  # Building/company icon
        '\uf0b1': '',  # Other problematic characters
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2022': '•',  # Bullet point
        '\u2026': '...',  # Ellipsis
    }
    
    for unicode_char, replacement in unicode_replacements.items():
        cleaned_text = cleaned_text.replace(unicode_char, replacement)
    
    # Remove other problematic Unicode characters that can't be encoded in latin-1
    cleaned_text = ''.join(char for char in cleaned_text if ord(char) < 256 or char in '•')
    
    # Normalize Unicode characters
    cleaned_text = unicodedata.normalize('NFKC', cleaned_text)
    
    # Clean up extra whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    
    return cleaned_text.strip()

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Enhanced PDF text extraction with multiple fallback methods"""
    
    # Method 1: Try PyMuPDF (fastest and most accurate)
    if HAS_PYMUPDF:
        try:
            text = extract_text_with_pymupdf(pdf_content)
            if text and text.strip():
                print("✅ Text extracted successfully with PyMuPDF")
                return text
        except Exception as e:
            print(f"PyMuPDF extraction failed: {e}")
    
    # Method 2: Try pdfplumber (good for complex layouts)
    if HAS_PDFPLUMBER:
        try:
            text = extract_text_with_pdfplumber(pdf_content)
            if text and text.strip():
                print("✅ Text extracted successfully with pdfplumber")
                return text
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")
    
    # Method 3: Try PyPDF2 (basic fallback)
    try:
        text = extract_text_with_pypdf2(pdf_content)
        if text and text.strip():
            print("✅ Text extracted successfully with PyPDF2")
            return text
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")
    
    # Method 4: Try OCR as last resort (for scanned PDFs)
    if HAS_OCR:
        try:
            text = extract_text_with_ocr(pdf_content)
            if text and text.strip():
                print("✅ Text extracted successfully with OCR")
                return text
        except Exception as e:
            print(f"OCR extraction failed: {e}")
    
    # If all methods fail
    raise HTTPException(
        status_code=400, 
        detail="Could not extract text from PDF. The file might be corrupted, password-protected, or contain only images. Please try converting to TXT format."
    )

def extract_text_with_pymupdf(pdf_content: bytes) -> str:
    """Extract text using PyMuPDF (fitz)"""
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    text = ""
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text += page.get_text() + "\n"
    
    doc.close()
    return text.strip()

def extract_text_with_pdfplumber(pdf_content: bytes) -> str:
    """Extract text using pdfplumber"""
    text = ""
    
    with pdfplumber.open(BytesIO(pdf_content)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    return text.strip()

def extract_text_with_pypdf2(pdf_content: bytes) -> str:
    """Extract text using PyPDF2 (basic fallback)"""
    pdf_reader = PyPDF2.PdfFileReader(BytesIO(pdf_content))
    text = ""
    
    for page_num in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page_num)
        text += page.extractText() + "\n"
    
    return text.strip()

def extract_text_with_ocr(pdf_content: bytes) -> str:
    """Extract text using OCR (for scanned PDFs)"""
    # Convert PDF to images
    images = convert_from_bytes(pdf_content)
    text = ""
    
    for i, image in enumerate(images):
        # Use pytesseract to extract text from each page image
        page_text = pytesseract.image_to_string(image)
        if page_text.strip():
            text += f"--- Page {i+1} ---\n{page_text}\n"
    
    return text.strip()

def classify_message(message: str, cv_content: str = None) -> dict:
    if not openai_client:
        # Fallback to pattern matching if OpenAI is not available
        return classify_message_fallback(message, cv_content)
        
    try:
        cv_context = ""
        if cv_content:
            # Provide CV context to the AI
            cv_context = f"\n\nCurrent CV Content Preview:\n{cv_content[:500]}..."
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"""You are a CV assistant with full CRUD capabilities. Classify messages to perform Create, Read, Update, Delete operations on CV content:

=== CREATE OPERATIONS ===
SKILL_ADD: adding new skills ("I learned", "I know", "add skill", "skilled in")
EXPERIENCE_ADD: adding work experience ("I worked", "I was employed", "job at", "worked as")
EDUCATION_ADD: adding education ("I studied", "graduated from", "degree in", "certification in")
PROJECT_ADD: adding new project ("I built", "I created", "I developed", "project called")
CONTACT_ADD: adding contact info ("my email is", "phone number", "linkedin", "address")

=== READ OPERATIONS ===
CV_SHOW: show full CV ("show cv", "display cv", "my cv", "current cv")
SKILL_SHOW: show skills ("what skills", "my skills", "list skills", "show skills")
EXPERIENCE_SHOW: show experience ("what experience", "my jobs", "work history", "employment")
EDUCATION_SHOW: show education ("my education", "degrees", "qualifications", "academic")
PROJECT_SHOW: show projects ("my projects", "what projects", "list projects", "portfolio")
CONTACT_SHOW: show contact info ("my contact", "contact details", "how to reach")

=== UPDATE OPERATIONS ===
SKILL_UPDATE: modify existing skills ("update skill", "change skill", "modify skill")
EXPERIENCE_UPDATE: modify work experience ("update job", "change experience", "modify work")
EDUCATION_UPDATE: modify education ("update degree", "change education", "modify qualification")
PROJECT_UPDATE: modify project ("update project", "change project", "modify project")
CONTACT_UPDATE: modify contact info ("update contact", "change email", "new phone")

=== DELETE OPERATIONS ===
SKILL_DELETE: remove skills ("remove skill", "delete skill", "don't have skill")
EXPERIENCE_DELETE: remove experience ("remove job", "delete experience", "wasn't employed")
EDUCATION_DELETE: remove education ("remove degree", "delete education", "didn't study")
PROJECT_DELETE: remove project ("remove project", "delete project", "didn't build")
CONTACT_DELETE: remove contact info ("remove contact", "delete email", "no phone")

=== UTILITY OPERATIONS ===
CV_GENERATE: generate updated CV ("generate cv", "create cv", "make cv", "build cv")
CV_CLEANUP: clean duplicate sections ("clean cv", "fix duplicates", "organize cv")
LINKEDIN_BLOG: generate LinkedIn blog post ("linkedin blog", "create blog", "write blog", "generate post", "social media post")
CV_HELP: show available commands ("help", "what can you do", "commands", "how to use")
OTHER: general conversation

Extract specific information and identify target items by keywords, names, or descriptions.
Return JSON: {{"category": "CATEGORY", "extracted_info": "specific details", "target_item": "what to modify/delete", "target_section": "SECTION_NAME", "operation": "CREATE|READ|UPDATE|DELETE"}}{cv_context}"""},
                {"role": "user", "content": message}
            ],
            temperature=0.1,
            max_tokens=200
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI classification failed: {e}")
        return classify_message_fallback(message, cv_content)

def classify_message_fallback(message: str, cv_content: str = None) -> dict:
    """Enhanced fallback classification with full CRUD support and better education detection"""
    msg = message.lower()
    print(f"[DEBUG] classify_message_fallback: message='{message}'")

    # EDUCATION ADD/UPDATE - expanded patterns
    education_add_phrases = [
        "add", "include", "insert", "put", "append", "enroll", "study", "degree", "certification", "course", "program", "school", "university", "college", "phd", "master", "bachelor"
    ]
    if any(kw in msg for kw in education_add_phrases) and ("education" in msg or "degree" in msg or "phd" in msg or "master" in msg or "bachelor" in msg or "university" in msg or "college" in msg):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_ADD")
        return {"category": "EDUCATION_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("education" in msg or "degree" in msg or "phd" in msg or "master" in msg or "bachelor" in msg or "university" in msg or "college" in msg):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_UPDATE")
        return {"category": "EDUCATION_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    
    # READ OPERATIONS
    if any(phrase in msg for phrase in ["show cv", "display cv", "my cv", "current cv"]):
        print("[DEBUG] classify_message_fallback: Detected CV_SHOW")
        return {"category": "CV_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["what skills", "my skills", "list skills", "show skills"]):
        print("[DEBUG] classify_message_fallback: Detected SKILL_SHOW")
        return {"category": "SKILL_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["what experience", "my jobs", "work history", "employment"]):
        print("[DEBUG] classify_message_fallback: Detected EXPERIENCE_SHOW")
        return {"category": "EXPERIENCE_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my education", "degrees", "qualifications", "academic"]):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_SHOW")
        return {"category": "EDUCATION_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my projects", "what projects", "list projects", "portfolio"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_SHOW")
        return {"category": "PROJECT_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my contact", "contact details", "how to reach"]):
        print("[DEBUG] classify_message_fallback: Detected CONTACT_SHOW")
        return {"category": "CONTACT_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    
    # DELETE OPERATIONS
    elif any(phrase in msg for phrase in ["remove skill", "delete skill", "don't have skill"]):
        print("[DEBUG] classify_message_fallback: Detected SKILL_DELETE")
        return {"category": "SKILL_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove job", "delete experience", "wasn't employed"]):
        print("[DEBUG] classify_message_fallback: Detected EXPERIENCE_DELETE")
        return {"category": "EXPERIENCE_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove degree", "delete education", "didn't study"]):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_DELETE")
        return {"category": "EDUCATION_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove project", "delete project", "didn't build"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_DELETE")
        return {"category": "PROJECT_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove contact", "delete email", "no phone"]):
        print("[DEBUG] classify_message_fallback: Detected CONTACT_DELETE")
        return {"category": "CONTACT_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    
    # UPDATE OPERATIONS
    elif any(phrase in msg for phrase in ["update skill", "change skill", "modify skill"]):
        print("[DEBUG] classify_message_fallback: Detected SKILL_UPDATE")
        return {"category": "SKILL_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    elif any(phrase in msg for phrase in ["update job", "change experience", "modify work"]):
        print("[DEBUG] classify_message_fallback: Detected EXPERIENCE_UPDATE")
        return {"category": "EXPERIENCE_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    elif any(phrase in msg for phrase in ["update degree", "change education", "modify qualification"]):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_UPDATE")
        return {"category": "EDUCATION_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    elif any(phrase in msg for phrase in ["update project", "change project", "modify project"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_UPDATE")
        return {"category": "PROJECT_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    elif any(phrase in msg for phrase in ["update contact", "change email", "new phone"]):
        print("[DEBUG] classify_message_fallback: Detected CONTACT_UPDATE")
        return {"category": "CONTACT_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    
    # CREATE OPERATIONS
    elif any(phrase in msg for phrase in ["i learned", "i know", "add skill", "skilled in"]):
        print("[DEBUG] classify_message_fallback: Detected SKILL_ADD")
        return {"category": "SKILL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["i worked", "i was employed", "job at", "worked as"]):
        print("[DEBUG] classify_message_fallback: Detected EXPERIENCE_ADD")
        return {"category": "EXPERIENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["i studied", "graduated from", "degree in", "certification in"]):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_ADD")
        return {"category": "EDUCATION_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["i built", "i created", "i developed", "project called"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_ADD")
        return {"category": "PROJECT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["my email is", "phone number", "linkedin", "address"]):
        print("[DEBUG] classify_message_fallback: Detected CONTACT_ADD")
        return {"category": "CONTACT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    
    # UTILITY OPERATIONS - LinkedIn blog should be checked FIRST with more specific patterns
    elif any(phrase in msg for phrase in ["linkedin blog", "linkedin post", "generate linkedin", "create linkedin", "write linkedin"]):
        print("[DEBUG] classify_message_fallback: Detected LINKEDIN_BLOG")
        return {"category": "LINKEDIN_BLOG", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["generate a linkedin", "create a linkedin", "write a linkedin", "generate linkedin post", "create linkedin post", "write linkedin post"]):
        print("[DEBUG] classify_message_fallback: Detected LINKEDIN_BLOG")
        return {"category": "LINKEDIN_BLOG", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["generate blog", "create blog", "write blog"]) and not any(phrase in msg for phrase in ["contact", "email", "phone", "address"]):
        print("[DEBUG] classify_message_fallback: Detected LINKEDIN_BLOG")
        return {"category": "LINKEDIN_BLOG", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["generate cv", "create cv", "make cv", "build cv"]):
        print("[DEBUG] classify_message_fallback: Detected CV_GENERATE")
        return {"category": "CV_GENERATE", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["clean cv", "fix duplicates", "organize cv"]):
        print("[DEBUG] classify_message_fallback: Detected CV_CLEANUP")
        return {"category": "CV_CLEANUP", "extracted_info": message.strip(), "operation": "UPDATE"}
    elif any(phrase in msg for phrase in ["help", "what can you do", "commands", "how to use"]):
        print("[DEBUG] classify_message_fallback: Detected CV_HELP")
        return {"category": "CV_HELP", "extracted_info": message.strip(), "operation": "READ"}
    
    # LEGACY SUPPORT (backward compatibility)
    elif any(phrase in msg for phrase in ["skill", "learned", "achieved"]):
        print("[DEBUG] classify_message_fallback: Detected SKILL_ADD")
        return {"category": "SKILL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["worked", "job", "experience"]):
        print("[DEBUG] classify_message_fallback: Detected EXPERIENCE_ADD")
        return {"category": "EXPERIENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["degree", "certification", "education"]):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_ADD")
        return {"category": "EDUCATION_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["project", "built", "developed", "created", "app", "website", "system"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_ADD")
        return {"category": "PROJECT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    
    # Check for LinkedIn blog commands more broadly (catch-all)
    elif any(phrase in msg for phrase in ["linkedin", "blog", "post", "social media"]):
        print("[DEBUG] classify_message_fallback: Detected LINKEDIN_BLOG")
        return {"category": "LINKEDIN_BLOG", "extracted_info": message.strip(), "operation": "CREATE"}
    
    print("[DEBUG] classify_message_fallback: Detected OTHER")
    return {"category": "OTHER", "extracted_info": message.strip(), "operation": "READ"}

def update_cv_section_smart(cv_content: str, section_name: str, update_info: str) -> str:
    """Update a specific section of the CV using OpenAI without creating new sections"""
    try:
        # Find the existing section in the CV
        sections = parse_cv_sections(cv_content)
        
        if section_name.lower() not in sections:
            # Don't create new sections, just return original CV
            return cv_content
            
        # Use OpenAI to intelligently update the specific section
        prompt = f"""You are updating a specific section of a CV. 

Current CV Content:
{cv_content}

Target Section: {section_name}
Update Information: {update_info}

Instructions:
1. Find the existing {section_name} section in the CV
2. Update ONLY that section with the new information
3. DO NOT create new sections
4. Maintain the original formatting and structure
5. Add the new information naturally to the existing section
6. Return the complete updated CV

Updated CV:"""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        updated_cv = response.choices[0].message.content.strip()
        
        # Validate that the response is a complete CV
        if len(updated_cv) < len(cv_content) * 0.8:
            # If the response is too short, fall back to manual section update
            return update_cv_section_manual(cv_content, section_name, update_info)
        
        return updated_cv
        
    except Exception as e:
        print(f"OpenAI section update failed: {e}")
        # Fallback to manual section update
        return update_cv_section_manual(cv_content, section_name, update_info)

def update_cv_section_manual(cv_content: str, section_name: str, update_info: str) -> str:
    """Manual fallback for updating CV sections"""
    sections = parse_cv_sections(cv_content)
    
    # Map section names to standardized names
    section_mapping = {
        'skills': ['skills', 'technical skills', 'core competencies', 'technologies'],
        'experience': ['work experience', 'experience', 'professional experience', 'employment history'],
        'education': ['education', 'educational background', 'academic background', 'qualifications']
    }
    
    # Find the correct section
    target_section = None
    for standard_name, variations in section_mapping.items():
        if section_name.lower() in variations:
            for variation in variations:
                if variation in sections:
                    target_section = variation
                    break
        if target_section:
            break
    
    if not target_section:
        return cv_content
    
    # Get section info
    section_info = sections[target_section]
    lines = cv_content.split('\n')
    
    # Add new content at the end of the section
    insert_position = section_info['end_line']
    
    # Format the new content based on section type
    if 'skill' in section_name.lower():
        new_content = f"• {update_info}"
    elif 'experience' in section_name.lower():
        new_content = f"• {update_info}"
    elif 'education' in section_name.lower():
        formatted_education = extract_education_from_message(update_info)
        new_content = f"• {formatted_education}"
    else:
        new_content = f"• {update_info}"
    
    # Insert the new content
    lines.insert(insert_position, new_content)
    
    return '\n'.join(lines)

def extract_projects_from_cv(cv_content: str) -> list:
    """Extract projects from the 'Projects' section of the CV text."""
    projects_section = extract_section_from_cv(cv_content, 'projects')
    if not projects_section:
        print("[DEBUG] No 'Projects' section found in CV.")
    return []
    # Try to split by lines and look for project-like entries
    lines = projects_section.split('\n')
    projects = []
    current_project = ''
    for line in lines:
        line = line.strip()
        # Heuristic: new project if line starts with number, bullet, or is all caps
        if re.match(r"^(\d+\.|[-•*])\s+", line) or (line.isupper() and len(line) > 5):
            if current_project:
                projects.append(current_project.strip())
                print(f"[DEBUG] Parsed project:\n{current_project.strip()}\n---END PROJECT---")
            current_project = line
        else:
            current_project += '\n' + line
    if current_project:
        projects.append(current_project.strip())
        print(f"[DEBUG] Parsed project:\n{current_project.strip()}\n---END PROJECT---")
    print(f"[DEBUG] Total projects extracted: {len(projects)}")
    return projects

def extract_projects_fallback(cv_content: str) -> List[dict]:
    """Fallback method - now returns empty list to prevent automatic project creation"""
    # No longer automatically create projects from CV content
    return []

def extract_project_from_message(message: str) -> dict:
    """Extract project details from chat message using AI or patterns"""
    try:
        prompt = f"""Extract project information from this message and return as JSON:
        
        Message: {message}
        
        Extract:
        - title: project name
        - description: what the project does
        - technologies: array of tech stack mentioned
        - duration: any timeframe mentioned
        - highlights: key achievements or features
        
        Return JSON format: {{"title": "", "description": "", "technologies": [], "duration": "", "highlights": []}}
        If information is missing, use reasonable defaults."""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        if result_text.startswith('```json'):
            result_text = result_text[7:-3]
        elif result_text.startswith('```'):
            result_text = result_text[3:-3]
        
        return json.loads(result_text)
    except:
        # Fallback pattern extraction
        return extract_project_from_message_fallback(message)

def extract_project_from_message_fallback(message: str) -> dict:
    """Fallback method to extract project info using patterns"""
    
    msg_lower = message.lower()
    
    # Extract title (look for project names)
    title_patterns = [
        r'(?:built|created|developed|made)\s+(?:a\s+)?(.+?)(?:\s+using|\s+with|\s+in|\s+for|\.|\,|$)',
        r'project\s+(?:called\s+)?(.+?)(?:\s+using|\s+with|\s+in|\s+for|\.|\,|$)',
        r'working\s+on\s+(.+?)(?:\s+using|\s+with|\s+in|\s+for|\.|\,|$)'
    ]
    
    title = "New Project"
    for pattern in title_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            title = match.group(1).strip().title()
            break
    
    # Extract technologies
    tech_patterns = [
        r'react\.?js', r'javascript', r'html', r'css', r'bootstrap', r'tailwind',
        r'fastapi', r'python', r'django', r'flask', r'supabase', r'firebase',
        r'node\.?js', r'express', r'mongodb', r'sql', r'postgresql', r'mysql',
        r'vue\.?js', r'angular', r'typescript', r'next\.?js', r'nuxt',
        r'docker', r'aws', r'azure', r'git', r'github', r'gitlab'
    ]
    
    technologies = []
    for pattern in tech_patterns:
        if re.search(pattern, msg_lower):
            tech_name = pattern.replace(r'\.?', '').replace(r'\\', '').title()
            if tech_name not in technologies:
                technologies.append(tech_name)
    
    # Extract duration/timeline
    duration_patterns = [
        r'(\d+)\s+(?:weeks?|months?|days?)',
        r'(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}',
        r'(?:last|this|next)\s+(?:week|month|year)',
        r'recently|currently|ongoing'
    ]
    
    duration = ""
    for pattern in duration_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            duration = match.group(0).title()
            break
    
    return {
        "title": title,
        "description": f"Project developed using {', '.join(technologies[:3]) if technologies else 'modern technologies'}",
        "technologies": technologies,
        "duration": duration or "Recent",
        "highlights": [
            "Implemented core functionality",
            "Developed user interface",
            "Added responsive design"
        ]
    }

def extract_education_from_message(message: str) -> str:
    """Extract and format education from chat message"""
    try:
        prompt = f"""Extract education information from this message and format it properly:
        
        Message: {message}
        
        Format the education as: "[Degree] [Status/Year], from [University/Institution]"
        
        Examples:
        - "Master of Computer Science Graduated in 2023, from Stanford University"
        - "Bachelor of Engineering Pursuing, from MIT"
        - "PhD in Data Science Expected 2025, from Harvard University"
        
        Extract and format only the education, no bullet points or extra text."""
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=200
        )
        
        result = response.choices[0].message.content.strip()
        return result
    except:
        # Fallback pattern extraction
        return extract_education_fallback(message)

def extract_education_fallback(message: str) -> str:
    """Fallback method to extract and format education"""
    msg_lower = message.lower()
    
    # Extract degree type
    degree_patterns = {
        r'masters?|ms|m\.s\.': 'Master',
        r'bachelors?|bs|b\.s\.|undergraduate': 'Bachelor',
        r'phd|doctorate|doctoral': 'PhD',
        r'mba': 'MBA',
        r'certification|certificate|cert': 'Certification'
    }
    
    degree_type = "Degree"
    for pattern, degree in degree_patterns.items():
        if re.search(pattern, msg_lower):
            degree_type = degree
            break
    
    # Extract field/subject
    field_patterns = [
        r'in\s+([^,\.]+?)(?:\s+from|\s+at|$)',
        r'of\s+([^,\.]+?)(?:\s+from|\s+at|$)',
        r'degree\s+([^,\.]+?)(?:\s+from|\s+at|$)'
    ]
    
    # Set default field based on degree type - only if degree type was actually detected
    if degree_type == "MBA":
        field = "Business Administration"
    elif degree_type == "Certification":
        field = "Technology"  # Will be overridden if specific field found
    elif degree_type != "Degree":  # Only set default if we found a specific degree type
        field = "Computer Science"
    else:
        field = ""  # Don't set a default field if no degree type was detected
    
    for pattern in field_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            extracted_field = match.group(1).strip().title()
            # Clean up common field variations
            if extracted_field.lower() in ['cs', 'comp sci', 'computer sci']:
                field = "Computer Science"
            elif extracted_field.lower() in ['data sci', 'ds']:
                field = "Data Science"
            elif extracted_field.lower() in ['aws', 'amazon web services']:
                field = "AWS"
            else:
                field = extracted_field
            break
    
    # Extract university/institution
    university_patterns = [
        r'from\s+(stanford\s+university|harvard\s+university|mit|stanford|harvard|princeton|yale|columbia|berkeley|ucla|caltech|carnegie\s+mellon)',
        r'from\s+([^,\.]+?)\s+university',
        r'from\s+([^,\.]+?)\s+institute',
        r'from\s+([^,\.]+?)\s+college',
        r'from\s+([^,\.0-9]+?)(?:\s+in\s+\d{4}|$)',
        r'at\s+([^,\.]+?)(?:\s+university|\s+institute|\s+college|$)',
        r'university\s+of\s+([^,\.]+)',
    ]
    
    university = "University"
    for pattern in university_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            university = match.group(1).strip().title()
            # Handle special cases
            if university.lower() in ['mit', 'stanford', 'harvard', 'princeton', 'yale', 'columbia', 'berkeley', 'ucla', 'caltech']:
                if university.lower() == 'mit':
                    university = "MIT"
                elif university.lower() == 'ucla':
                    university = "UCLA"
                elif university.lower() == 'berkeley':
                    university = "UC Berkeley"
                elif university.lower() == 'caltech':
                    university = "Caltech"
                else:
                    university = university.title()
            elif not university.lower().endswith(('university', 'institute', 'college', 'school')):
                if 'business' in university.lower() or 'management' in university.lower():
                    university += " School"
                else:
                    university += " University"
            break
    
    # Extract year/status
    year_patterns = [
        r'(\d{4})',
        r'(graduated|completed|finished)',
        r'(pursuing|current|ongoing)',
        r'(expected|will graduate)'
    ]
    
    status = "Completed"
    for pattern in year_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            if match.group(1).isdigit():
                status = f"Graduated in {match.group(1)}"
            elif match.group(1) in ['pursuing', 'current', 'ongoing']:
                status = "Pursuing"
            elif match.group(1) in ['expected', 'will graduate']:
                status = "Expected"
            else:
                status = "Graduated"
            break
    
    # Only format education if we have meaningful information
    if degree_type == "Degree" and not field and university == "University":
        # If we couldn't extract meaningful information, return the original message
        return message.strip()
    
    # Format the education entry
    if degree_type == "Certification":
        return f"{degree_type} in {field} {status}, from {university}"
    else:
        return f"{degree_type} of {field} {status}, from {university}"

# ===== NEW CRUD HELPER FUNCTIONS =====

def extract_intelligent_content(message: str) -> tuple[str, str]:
    """
    Intelligently extract main content and auto-detect section from a message.
    Returns (extracted_content, detected_section)
    """
    message_lower = message.lower().strip()
    
    # Auto-detect section based on keywords and patterns
    section_keywords = {
        "skills": ["skill", "technology", "programming", "language", "framework", "tool", "software", "expertise", "proficient", "know", "learned", "mastered"],
        "experience": ["experience", "work", "job", "employment", "position", "role", "responsibility", "led", "managed", "developed", "built", "created", "implemented"],
        "education": ["education", "degree", "university", "college", "school", "graduated", "studied", "certification", "course", "diploma", "masters", "bachelors", "phd"],
        "projects": ["project", "built", "created", "developed", "application", "website", "app", "system", "platform", "tool", "software"],
        "contact": ["contact", "phone", "email", "linkedin", "address", "location", "portfolio", "website"],
        "profile": ["profile", "summary", "about", "objective", "introduction", "background", "overview"],
        "achievements": ["achievement", "award", "recognition", "honor", "accomplishment", "success", "milestone"],
        "languages": ["language", "speak", "fluent", "conversational", "native", "bilingual"],
        "interests": ["interest", "hobby", "passion", "enjoy", "like", "love", "favorite"]
    }
    
    # Count keyword matches for each section
    section_scores = {}
    for section, keywords in section_keywords.items():
        score = sum(1 for keyword in keywords if keyword in message_lower)
        section_scores[section] = score
    
    # Find the section with highest score
    detected_section = max(section_scores.items(), key=lambda x: x[1])[0] if section_scores else "skills"
    
    # If no clear section detected, try to infer from content patterns
    if section_scores[detected_section] == 0:
        if any(word in message_lower for word in ["add", "include", "put", "insert"]):
            # Look for section names in the message
            for section in section_keywords.keys():
                if section in message_lower:
                    detected_section = section
                    break
    
    # Extract main content (remove common prefixes and section references)
    content = message.strip()
    
    # Remove common prefixes more aggressively
    prefixes_to_remove = [
        "add", "include", "put", "insert", "add to", "include in", "put in", "insert in",
        "add to my", "include in my", "put in my", "insert in my",
        "add to the", "include in the", "put in the", "insert in the",
        "add to my skills", "add to my experience", "add to my education", "add to my projects",
        "add to skills", "add to experience", "add to education", "add to projects",
        "add skills", "add experience", "add education", "add projects",
        "add to contact", "add to profile", "add to achievements", "add to languages", "add to interests",
        "add '", "add \"", "include '", "include \"", "put '", "put \"", "insert '", "insert \"",
        "complete my project of", "i have completed my", "i completed my", "i graduated with", "i graduated from",
        "i learned", "i am proficient in", "i have experience in", "i led", "i managed", "i developed",
        "i built", "i created", "i designed", "i worked on", "i studied", "i have", "i am", "i can"
    ]
    
    # Remove prefixes (try multiple times to catch nested prefixes)
    for _ in range(3):  # Try up to 3 times
        original_content = content
        for prefix in prefixes_to_remove:
            if content.lower().startswith(prefix.lower()):
                content = content[len(prefix):].strip()
                break
        if content == original_content:
            break  # No more prefixes found
    
    # Also remove "to my [section] section" patterns
    section_patterns = ["to my skills section", "to my experience section", "to my education section", 
                       "to my projects section", "to my contact section", "to my profile section",
                       "to my skills", "to my experience", "to my education", "to my projects"]
    for pattern in section_patterns:
        if content.lower().endswith(pattern.lower()):
            content = content[:-len(pattern)].strip()
            break
    
    # Remove quotes if present (handle both single and double quotes)
    if content.startswith("'") and content.endswith("'"):
        content = content[1:-1]
    elif content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
    elif content.startswith("'") and content.endswith("'"):
        content = content[1:-1]
    elif content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
    
    # Remove any remaining quote patterns
    content = re.sub(r"^['\"]\s*", "", content)  # Remove leading quotes
    content = re.sub(r"\s*['\"]$", "", content)  # Remove trailing quotes
    
    # Clean up extra whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    
    # If content is still too long, try to extract the most important part
    if len(content) > 100:
        # For skills, extract individual items
        if detected_section == "skills":
            content = extract_skills_content(content)
        # For experience, extract the main action/achievement
        elif detected_section == "experience":
            content = extract_experience_content(content)
        # For education, extract the degree/institution
        elif detected_section == "education":
            content = extract_education_content(content)
        # For projects, extract the project name/description
        elif detected_section == "projects":
            content = extract_project_content(content)
    
    return content, detected_section

def extract_skills_content(content: str) -> str:
    """Extract individual skills from content"""
    # Remove common prefixes more aggressively
    content = re.sub(r'^(i learned|i know|i am proficient in|i can|i have experience in|i am skilled in|i have|i am|i can do|i know how to)\s*', '', content, flags=re.IGNORECASE)
    
    # Split by common separators
    separators = [',', 'and', '&', '+', ';', '|', 'also', 'including']
    parts = [content]
    
    for sep in separators:
        new_parts = []
        for part in parts:
            new_parts.extend(part.split(sep))
        parts = new_parts
    
    # Clean and filter parts
    skills = []
    for part in parts:
        skill = part.strip()
        if skill and len(skill) > 1 and len(skill.split()) <= 4:
            # Capitalize properly
            skill = skill.title()
            skills.append(skill)
    
    return ', '.join(skills[:5])  # Limit to 5 skills

def extract_experience_content(content: str) -> str:
    """Extract main experience/achievement from content"""
    # Remove common prefixes more aggressively
    content = re.sub(r'^(i led|i managed|i developed|i built|i created|i implemented|i designed|i worked on|i was responsible for|i have|i am|i can)\s*', '', content, flags=re.IGNORECASE)
    
    # Look for key action phrases
    action_patterns = [
        r'(led|managed|developed|built|created|implemented|designed|architected|optimized|improved|increased|reduced|delivered|completed|achieved)\s+[^,.]*',
        r'responsible\s+for\s+[^,.]*',
        r'worked\s+on\s+[^,.]*',
        r'helped\s+[^,.]*',
        r'assisted\s+with\s+[^,.]*'
    ]
    
    for pattern in action_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            result = match.group(0).strip()
            # Limit to key concepts (avoid long descriptions)
            if len(result.split()) > 8:
                words = result.split()[:8]
                result = ' '.join(words)
            return result
    
    # If no pattern found, take the first meaningful phrase
    phrases = re.split(r'[.!?,]', content)
    for phrase in phrases:
        phrase = phrase.strip()
        if len(phrase.split()) <= 8 and len(phrase) > 3:
            return phrase
    
    return content

def extract_education_content(content: str) -> str:
    """Extract education information from content"""
    # Remove common prefixes more aggressively
    content = re.sub(r'^(i graduated|i completed|i have|i earned|i studied|i have completed|i am|i was)\s*', '', content, flags=re.IGNORECASE)
    
    # Look for degree and institution patterns
    degree_patterns = [
        r'(bachelor|master|phd|mba|certification)\s+(?:of|in)\s+[^,]*',
        r'(degree|diploma|certificate)\s+(?:in|of)\s+[^,]*',
        r'graduated\s+(?:from|with)\s+[^,]*',
        r'studied\s+[^,]*'
    ]
    
    for pattern in degree_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            result = match.group(0).strip()
            # Format as "Degree in Field from University"
            if 'from' in result.lower():
                return result
            elif 'in' in result.lower():
                return result
            else:
                return result
    
    # If no pattern found, extract key education info
    words = content.split()
    if len(words) >= 3:
        # Look for degree + field + university pattern
        for i in range(len(words) - 2):
            if any(degree in words[i].lower() for degree in ['bachelor', 'master', 'phd', 'mba', 'certification']):
                if i + 2 < len(words):
                    return f"{words[i].title()} in {' '.join(words[i+1:i+3])}"
    
    # Fallback: take first meaningful phrase
    phrases = re.split(r'[.!?,]', content)
    for phrase in phrases:
        phrase = phrase.strip()
        if len(phrase.split()) <= 6 and len(phrase) > 3:
            return phrase
    
    return content

def extract_project_content(content: str) -> str:
    """Extract project information from content"""
    # Remove common prefixes more aggressively
    content = re.sub(r'^(i built|i created|i developed|i designed|i made|my project|project called|application for|complete my project of|i have completed)\s*', '', content, flags=re.IGNORECASE)
    
    # Look for project patterns
    project_patterns = [
        r'(built|created|developed|designed)\s+[^,.]*',
        r'project\s+(?:called|named)\s+[^,.]*',
        r'application\s+(?:for|that)\s+[^,.]*',
        r'website\s+(?:for|that)\s+[^,.]*',
        r'system\s+(?:for|that)\s+[^,.]*',
        r'(todo|task|e-commerce|weather|chat|blog|portfolio|dashboard)\s+[^,.]*'
    ]
    
    for pattern in project_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            result = match.group(0).strip()
            # Limit to key concepts
            if len(result.split()) > 6:
                words = result.split()[:6]
                result = ' '.join(words)
            return result
    
    # If no pattern found, extract key project info
    words = content.split()
    if len(words) >= 2:
        # Look for project type + technology pattern
        for i in range(len(words) - 1):
            if any(tech in words[i+1].lower() for tech in ['react', 'node', 'python', 'java', 'javascript', 'vue', 'angular']):
                return f"{words[i].title()} in {words[i+1].title()}"
    
    # Fallback: take first meaningful phrase
    phrases = re.split(r'[.!?,]', content)
    for phrase in phrases:
        phrase = phrase.strip()
        if len(phrase.split()) <= 6 and len(phrase) > 2:
            return phrase
    
    return content

def extract_main_keywords_from_message(message: str, section_type: str) -> str:
    """Extract main keywords for skills, experience, education, or projects from message."""
    clean_message = message.lower().strip()
    if section_type == 'skills':
        clean_message = re.sub(r'^(i learned|i know|add skill|skilled in|i have|i can)\s*', '', clean_message).strip()
        separators = [',', 'and', '&', '+', ';', '|']
    elif section_type == 'experience':
        clean_message = re.sub(r'^(i worked|i was employed|job at|worked as|i had a job)\s*', '', clean_message).strip()
        separators = [',', 'and', '&', '+', ';', '|']
    elif section_type == 'education':
        clean_message = re.sub(r'^(i studied|graduated from|degree in|certification in|i have a degree in)\s*', '', clean_message).strip()
        separators = [',', 'and', '&', '+', ';', '|']
    elif section_type == 'projects':
        clean_message = re.sub(r'^(i built|i created|i developed|project called|my project|i made)\s*', '', clean_message).strip()
        separators = [',', 'and', '&', '+', ';', '|']
    else:
        separators = [',', 'and', '&', '+', ';', '|']
    
    keywords = []
    parts = [clean_message]
    for sep in separators:
        new_parts = []
        for part in parts:
            new_parts.extend(part.split(sep))
        parts = new_parts
    for part in parts:
        keyword = part.strip().title()
        if keyword and len(keyword) > 1 and len(keyword.split()) <= 3:
            keywords.append(keyword)
    return ', '.join(keywords)

def create_cv_item(cv_content: str, section_type: str, item_info: str) -> tuple[str, str]:
    """Create/add new item to CV section - APPENDS to existing content"""
    try:
        sections = parse_cv_sections(cv_content)
        cv_lines = cv_content.split('\n')
        new_items = []
        if section_type.lower() in ['skills', 'experience', 'education', 'projects']:
            extracted_keywords = extract_main_keywords_from_message(item_info, section_type.lower())
            keywords_list = [s.strip() for s in extracted_keywords.split(',') if s.strip()]
            for keyword in keywords_list:
                new_items.append(f"• {keyword}")
        elif section_type.lower() == 'contact':
            contact_text = extract_contact_from_message(item_info)
            new_items.append(f"• {contact_text}")
        else:
            new_items.append(f"• {item_info}")
        # Find the target section
        target_section = None
        for section_name in sections.keys():
            if section_type.lower() in section_name.lower():
                target_section = section_name
                break
        if not target_section:
            # If section doesn't exist, create new section
            updated_cv = smart_section_integration(cv_content, section_type.lower(), new_items)
            return updated_cv, f"✅ Added new {section_type.lower()} section with your input!"
        # Otherwise, append to existing section
            section_info = sections[target_section]
            insert_position = section_info['end_line']
        for i, item in enumerate(new_items):
            cv_lines.insert(insert_position + i, item)
            updated_cv = '\n'.join(cv_lines)
        return updated_cv, f"✅ Added to {section_type.lower()} section!"
    except Exception as e:
        print(f"Error creating CV item: {e}")
        return cv_content, f"❌ Failed to add to {section_type.lower()} section: {str(e)}"

def read_cv_section(cv_content: str, section_type: str) -> str:
    """Read and display specific CV section"""
    try:
        if section_type.lower() == 'full' or section_type.lower() == 'cv':
            return f"📋 **Your Complete CV:**\n\n{cv_content[:1500]}{'...' if len(cv_content) > 1500 else ''}"
        
        # Extract specific section
        section_content = extract_section_from_cv(cv_content, section_type.lower())
        
        if section_content and len(section_content.strip()) > 10:
            return f"📝 **Your {section_type.title()} Section:**\n\n{section_content}"
        else:
            # Search for relevant content with keywords
            section_keywords = {
                'skills': ['skill', 'technology', 'programming', 'language', 'framework', 'tool'],
                'experience': ['work', 'job', 'position', 'company', 'role', 'responsibilities', 'employed'],
                'education': ['education', 'degree', 'university', 'college', 'school', 'certification', 'course'],
                'projects': ['project', 'built', 'developed', 'created', 'app', 'website', 'system'],
                'contact': ['email', 'phone', 'linkedin', 'address', 'contact']
            }
            
            keywords = section_keywords.get(section_type.lower(), [])
            relevant_lines = []
            
            for line in cv_content.split('\n'):
                if any(keyword in line.lower() for keyword in keywords) and len(line.strip()) > 5:
                    relevant_lines.append(line.strip())
            
            if relevant_lines:
                return f"📝 **{section_type.title()}-related content found:**\n\n" + "\n".join(relevant_lines[:5])
            else:
                return f"📭 No {section_type.lower()} information found in your CV. You can add some by telling me about your {section_type.lower()}!"
        
    except Exception as e:
        print(f"Error reading CV section: {e}")
        return f"❌ Error reading {section_type} section: {str(e)}"

def update_cv_item(cv_content: str, section_type: str, update_info: str) -> tuple[str, str]:
    """Update existing item in CV section - MODIFIES existing content, doesn't replace"""
    try:
        sections = parse_cv_sections(cv_content)
        cv_lines = cv_content.split('\n')
        target_section = None
        for section_name in sections.keys():
            if section_type.lower() in section_name.lower():
                target_section = section_name
                break
        if not target_section:
            # If section doesn't exist, treat as CREATE operation
            return create_cv_item(cv_content, section_type, update_info)
        # Check if update_info specifies what to update
        if any(keyword in update_info.lower() for keyword in ['add', 'include', 'with']):
            # This is actually an ADD operation to existing section
            print(f"🔄 Treating UPDATE as ADD operation for {section_type}")
            return create_cv_item(cv_content, section_type, update_info)
        # Use the main keyword extraction for update as well
        extracted_keywords = extract_main_keywords_from_message(update_info, section_type.lower())
        keywords_list = [s.strip() for s in extracted_keywords.split(',') if s.strip()]
        if not keywords_list:
            return cv_content, f"❌ No valid keywords found to update {section_type.lower()} section."
        # For now, just append as new items (can be improved to replace existing in future)
        for i, keyword in enumerate(keywords_list):
            cv_lines.insert(sections[target_section]['end_line'] + i, f"• {keyword}")
        updated_cv = '\n'.join(cv_lines)
        return updated_cv, f"✅ Updated {section_type.lower()} section with new keywords!"
    except Exception as e:
        print(f"Error updating CV item: {e}")
        return cv_content, f"❌ Failed to update {section_type.lower()} section: {str(e)}"

def delete_cv_item(cv_content: str, section_type: str, item_info: str) -> tuple[str, str]:
    """Delete item from CV section"""
    try:
        sections = parse_cv_sections(cv_content)
        cv_lines = cv_content.split('\n')
        
        # Find section
        section_key = None
        for key in sections.keys():
            if section_type.lower() in key.lower():
                section_key = key
                break
        
        if not section_key:
            return cv_content, f"❌ {section_type.title()} section not found in CV."
        
        section_info = sections[section_key]
        
        # Extract keywords from item_info to identify what to delete
        delete_keywords = item_info.lower().split()
        lines_to_remove = []
        
        # Find lines in the section that match the deletion criteria
        for i in range(section_info['content_start'], section_info['end_line'] + 1):
            if i < len(cv_lines):
                line = cv_lines[i].lower()
                # Check if any delete keywords match the line content
                if any(keyword in line for keyword in delete_keywords if len(keyword) > 2):
                    lines_to_remove.append(i)
        
        if lines_to_remove:
            # Remove lines in reverse order to maintain indices
            for line_idx in reversed(lines_to_remove):
                removed_content = cv_lines[line_idx]
                del cv_lines[line_idx]
            
            updated_cv = '\n'.join(cv_lines)
            return updated_cv, f"✅ Successfully removed {len(lines_to_remove)} item(s) from {section_type.lower()} section. The matching content has been deleted from your CV."
        else:
            return cv_content, f"⚠️ No matching {section_type.lower()} items found to delete. Please be more specific about what you want to remove."
        
    except Exception as e:
        print(f"Error deleting CV item: {e}")
        return cv_content, f"❌ Failed to delete {section_type.lower()} item: {str(e)}"

def extract_skills_from_message(message: str) -> str:
    """Extract skills from message, returning only main skill words, not the whole string."""
    # Remove common prefixes
    clean_message = re.sub(r'^(i learned|i know|add skill|skilled in|i have|i can)\s*', '', message.lower()).strip()
    # Split on common separators and clean up
    skills = []
    separators = [',', 'and', '&', '+', ';', '|']
    parts = [clean_message]
    for sep in separators:
        new_parts = []
        for part in parts:
            new_parts.extend(part.split(sep))
        parts = new_parts
    for part in parts:
        skill = part.strip().title()
        # Only add if it's a single word or short phrase (not the whole message)
        if skill and len(skill) > 1 and len(skill.split()) <= 3:
            skills.append(skill)
    # Only return joined skills, never the whole message
    return ', '.join(skills)

def extract_experience_from_message(message: str) -> str:
    """Extract work experience from message"""
    # Basic formatting for experience
    clean_message = re.sub(r'^(i worked|i was employed|job at|worked as|i had a job)\s*', '', message.lower()).strip()
    return clean_message.title()

def extract_contact_from_message(message: str) -> str:
    """Extract contact information from message"""
    clean_message = re.sub(r'^(my email is|phone number|my phone|contact|address)\s*', '', message.lower()).strip()
    return clean_message

def clean_duplicate_project_sections(cv_content: str) -> str:
    """Remove all project sections and additional sections"""
    lines = cv_content.split('\n')
    cleaned_lines = []
    skip_section = False
    
    for line in lines:
        line_upper = line.upper().strip()
        
        # Check if this is any project section or additional section
        if (line_upper.startswith('ADDITIONAL') or 
            (line_upper.isupper() and 'PROJECT' in line_upper)):
            skip_section = True
            continue
        
        # Check if we're starting a new non-project section
        if (line_upper.isupper() and 
            any(keyword in line_upper for keyword in 
                ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'CERTIFICATION']) and
            'PROJECT' not in line_upper and
            not line_upper.startswith('ADDITIONAL')):
            skip_section = False
        
        # Check for "Generated on" footer - stop skipping after it
        if 'Generated on' in line:
            skip_section = False
        
        if not skip_section:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def smart_section_integration(cv_content: str, section_type: str, new_content: List[str]) -> str:
    """Intelligently integrate new content into appropriate sections - APPENDS to existing sections"""
    try:
        sections = parse_cv_sections(cv_content)
        cv_lines = cv_content.split('\n')
        
        # Find the target section (flexible matching)
        target_section = None
        for section_name in sections.keys():
            if section_type.lower() in section_name.lower():
                target_section = section_name
                break
        
        if target_section:
            # APPEND to existing section
            section_info = sections[target_section]
            insert_position = section_info['end_line']
            
            # Find the last non-empty line in the section
            while (insert_position > section_info['content_start'] and 
                   insert_position < len(cv_lines) and 
                   not cv_lines[insert_position].strip()):
                insert_position -= 1
            
            # Insert new content after the last content line
            for i, content_line in enumerate(new_content):
                cv_lines.insert(insert_position + 1 + i, content_line)
                
            print(f"📝 Appended {len(new_content)} items to existing {target_section} section")
            
        else:
            # Create new section at appropriate location
            section_headers = {
                'skills': 'SKILLS',
                'experience': 'WORK EXPERIENCE', 
                'education': 'EDUCATION',
                'projects': 'PROJECTS',
                'contact': 'CONTACT INFORMATION'
            }
            
            header = section_headers.get(section_type, section_type.upper())
            full_content = [f"\n{header}"] + new_content + [""]
            
            # Determine best insertion point based on standard CV order
            cv_order = ['skills', 'experience', 'education', 'projects', 'contact']
            current_index = cv_order.index(section_type) if section_type in cv_order else len(cv_order)
            
            # Find insertion point based on existing sections
            insert_pos = len(cv_lines)
            
            # Look for next section in order
            for i in range(current_index + 1, len(cv_order)):
                next_section_type = cv_order[i]
                for section_name in sections.keys():
                    if next_section_type in section_name.lower():
                        insert_pos = sections[section_name]['start_line']
                        break
                if insert_pos < len(cv_lines):
                    break
            
            # Insert new section
            for i, line in enumerate(reversed(full_content)):
                cv_lines.insert(insert_pos, line)
                
            print(f"📝 Created new {header} section with {len(new_content)} items")
        
        return '\n'.join(cv_lines)
        
    except Exception as e:
        print(f"Error in smart section integration: {e}")
        return cv_content

def generate_cv_with_projects(cursor=None, conn=None) -> str:
    """Generate updated CV with all projects properly integrated"""
    try:
        # Use provided cursor or create new connection
        if cursor is None:
            with get_db_cursor_context() as (cursor, conn):
                return _generate_cv_with_projects_internal(cursor, conn)
        else:
            return _generate_cv_with_projects_internal(cursor, conn)
        
    except Exception as e:
        print(f"Error generating CV with projects: {e}")
        return "Error generating updated CV"

def _generate_cv_with_projects_internal(cursor, conn) -> str:
    """Internal implementation of CV generation with projects"""
    # Get active CV
    cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
    cv_row = cursor.fetchone()
    if not cv_row:
        # If no active CV, get the most recent one
        cursor.execute("SELECT current_content FROM cvs ORDER BY updated_at DESC LIMIT 1")
        cv_row = cursor.fetchone()
    
    if not cv_row:
        return "No CV found. Please upload a CV first."
    
    original_cv = cv_row[0]
    
    # Clean up any existing duplicate sections first
    original_cv = clean_duplicate_project_sections(original_cv)
    
    # Get manual projects from database
    cursor.execute("SELECT project_data FROM manual_projects ORDER BY created_at ASC")
    manual_projects = cursor.fetchall()
    
    new_projects = []
    for project_row in manual_projects:
        try:
            project_data = json.loads(project_row[0])
            new_projects.append(project_data)
        except:
            pass
    
    # If no manually added projects, remove any existing projects section and return original CV
    if not new_projects:
        # Clean up any existing projects section
        if 'projects' in sections:
            # Remove the projects section entirely
            start_line = sections['projects']['start_line']
            end_line = sections['projects']['end_line']
            del cv_lines[start_line:end_line + 1]
            return '\n'.join(cv_lines)
        return original_cv
    
    # Parse CV sections
    sections = parse_cv_sections(original_cv)
    cv_lines = original_cv.split('\n')
    
    # Only use manually added projects (no extraction from CV content)
    all_projects = new_projects.copy()
    
    if not all_projects:
        return original_cv
    
    # Generate properly formatted projects content
    projects_content = []
    for i, project in enumerate(all_projects, 1):
        # Format each project consistently
        title = project.get('title', f'Project {i}')
        duration = project.get('duration', '')
        description = project.get('description', '')
        technologies = project.get('technologies', [])
        highlights = project.get('highlights', [])
        
        # Project title with number
        projects_content.append(f"{i}. {title}")
        
        # Duration if available
        if duration:
            projects_content.append(f"   Duration: {duration}")
        
        # Description if available
        if description:
            projects_content.append(f"   Description: {description}")
        
        # Technologies if available
        if technologies:
            tech_str = ', '.join(technologies) if isinstance(technologies, list) else str(technologies)
            projects_content.append(f"   Technologies: {tech_str}")
        
        # Key highlights if available
        if highlights:
            projects_content.append("   Key Highlights:")
            if isinstance(highlights, list):
                for highlight in highlights:
                    projects_content.append(f"   • {highlight}")
            else:
                projects_content.append(f"   • {highlights}")
        
        # Empty line between projects
        projects_content.append("")
    
    # First, clean up any existing project content to prevent duplicates
    print(f"📝 Cleaning up existing project content...")
    
    # Remove only old project content, not the header
    new_cv_lines = []
    in_projects_section = False
    for line in cv_lines:
        if 'PROJECTS' in line.upper():
            in_projects_section = True
            new_cv_lines.append(line)
            continue
        if in_projects_section:
            # If we hit a new section or an empty line, stop skipping
            if (line.strip() == '' or (line.isupper() and len(line.strip()) > 3)):
                in_projects_section = False
                new_cv_lines.append(line)
            # Otherwise, skip old project content
            continue
        new_cv_lines.append(line)
    cv_lines = new_cv_lines

    # Now add the projects section with proper header if not present
    if not any('PROJECTS' in line.upper() for line in cv_lines):
        print(f"📝 Adding projects section with header")
        projects_header = "\n_____________________________ PROJECTS _____________________________\n"
        cv_lines.append(projects_header)
    else:
        print(f"📝 Projects section header already present")

    # Always append the new projects content after the header
    # Find the header index
    for idx, line in enumerate(cv_lines):
        if 'PROJECTS' in line.upper():
            insert_idx = idx + 1
            break
    else:
        insert_idx = len(cv_lines)
    # Remove anything after the header (old projects)
    cv_lines = cv_lines[:insert_idx]
    # Add new projects content
    cv_lines.extend(projects_content)
    print(f"📝 Inserted {len(projects_content)} project lines after header")
    
    updated_cv = '\n'.join(cv_lines)
    
    # Final cleanup to remove any remaining duplicates
    updated_cv = clean_duplicate_project_sections(updated_cv)
    
    # Update in database
    cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
    
    return updated_cv

def extract_existing_projects_from_cv(cv_content: str, sections: dict) -> List[dict]:
    """No longer extract existing projects from CV - only use manually added projects"""
    # Return empty list to prevent automatic project extraction
    return []

def extract_section_from_cv(cv_content: str, section_name: str) -> str:
    """Extract a section from the CV text by section header (case-insensitive, robust, supports many variations)."""
    # Build a robust regex for the requested section
    section_patterns = {
        'education': [
            r'[_\-\s]*EDUCATION[_\-\s]*',
            r'[_\-\s]*EDUCATIONAL\s+BACKGROUND[_\-\s]*',
            r'[_\-\s]*ACADEMIC\s+BACKGROUND[_\-\s]*',
            r'[_\-\s]*QUALIFICATIONS[_\-\s]*'
        ],
        'experience': [
            r'[_\-\s]*EXPERIENCE[_\-\s]*',
            r'[_\-\s]*WORK\s+EXPERIENCE[_\-\s]*',
            r'[_\-\s]*PROFESSIONAL\s+EXPERIENCE[_\-\s]*',
            r'[_\-\s]*EMPLOYMENT\s+HISTORY[_\-\s]*',
            r'[_\-\s]*CAREER\s+HISTORY[_\-\s]*'
        ],
        'skills': [
            r'[_\-\s]*SKILLS[_\-\s]*',
            r'[_\-\s]*TECHNICAL\s+SKILLS[_\-\s]*',
            r'[_\-\s]*CORE\s+COMPETENCIES[_\-\s]*',
            r'[_\-\s]*TECHNOLOGIES[_\-\s]*',
            r'[_\-\s]*TECHNICAL\s+COMPETENCIES[_\-\s]*'
        ],
        'projects': [
            r'[_\-\s]*PROJECTS[_\-\s]*',
            r'[_\-\s]*PERSONAL\s+PROJECTS[_\-\s]*',
            r'[_\-\s]*PORTFOLIO[_\-\s]*',
            r'[_\-\s]*SELECTED\s+PROJECTS?[_\-\s]*',
            r'[_\-\s]*MAJOR\s+PROJECTS?[_\-\s]*',
            r'[_\-\s]*PROJECT\s+EXPERIENCE[_\-\s]*',
            r'[_\-\s]*PROFESSIONAL\s+PROJECTS?[_\-\s]*',
            r'[_\-\s]*TECHNICAL\s+PROJECTS?[_\-\s]*',
            r'[_\-\s]*PROJECTS?\s+AND\s+ACHIEVEMENTS[_\-\s]*',
            r'[_\-\s]*PROJECTS?\s+PORTFOLIO[_\-\s]*',
            r'[_\-\s]*PROJECTS?\s+SUMMARY[_\-\s]*'
        ]
    }
    patterns = section_patterns.get(section_name.lower(), [rf'[_\-\s]*{section_name.upper()}[_\-\s]*'])
    for pat in patterns:
        regex = re.compile(rf'^{pat}$\n*([\s\S]*?)(?=^[_\-\s]*[A-Z][A-Z\s&]+[_\-\s]*$|$)', re.IGNORECASE | re.MULTILINE)
        match = regex.search(cv_content)
        if match:
            section_text = match.group(1).strip()
            print(f"[DEBUG] Extracted section '{section_name}':\n{section_text[:500]}\n---END SECTION---")
            return section_text
    print(f"[DEBUG] No section header found for '{section_name}' (tried {len(patterns)} patterns).")
    return ''

def parse_cv_sections(cv_content: str) -> dict:
    """Parse CV content to identify sections and their positions"""
    
    sections = {}
    cv_lines = cv_content.split('\n')
    
    # Enhanced section headers patterns to handle various formats
    section_patterns = {
        'profile': [
            r'^\s*PROFILE\s+SUMMARY\s*$', r'^\s*PROFILE\s*$', r'^\s*SUMMARY\s*$', r'^\s*ABOUT\s+ME\s*$',
            r'^\s*OBJECTIVE\s*$', r'^\s*PROFESSIONAL\s+SUMMARY\s*$', r'^\s*CAREER\s+OBJECTIVE\s*$',
            r'^\s*_+\s*PROFILE\s+SUMMARY\s*_+\s*$', r'^\s*_+\s*PROFILE\s*_+\s*$'
        ],
        'skills': [
            r'^\s*SKILLS?\s*$', r'^\s*TECHNICAL\s+SKILLS?\s*$', r'^\s*CORE\s+COMPETENCIES\s*$',
            r'^\s*TECHNOLOGIES\s*$', r'^\s*TECHNICAL\s+COMPETENCIES\s*$', r'^\s*PROFESSIONAL\s+SKILLS?\s*$',
            r'^\s*_+\s*SKILLS?\s*_+\s*$', r'^\s*_+\s*TECHNICAL\s+SKILLS?\s*_+\s*$'
        ],
        'experience': [
            r'^\s*WORK\s+EXPERIENCE\s*$', r'^\s*EXPERIENCE\s*$', r'^\s*PROFESSIONAL\s+EXPERIENCE\s*$',
            r'^\s*EMPLOYMENT\s+HISTORY\s*$', r'^\s*CAREER\s+HISTORY\s*$', r'^\s*WORK\s+HISTORY\s*$',
            r'^\s*_+\s*WORK\s+EXPERIENCE\s*_+\s*$', r'^\s*_+\s*EXPERIENCE\s*_+\s*$'
        ],
        'education': [
            r'^\s*EDUCATION\s*$', r'^\s*EDUCATIONAL\s+BACKGROUND\s*$', r'^\s*ACADEMIC\s+BACKGROUND\s*$',
            r'^\s*QUALIFICATIONS\s*$', r'^\s*ACADEMIC\s+QUALIFICATIONS\s*$', r'^\s*DEGREES\s*$',
            r'^\s*_+\s*EDUCATION\s*_+\s*$', r'^\s*_+\s*EDUCATIONAL\s+BACKGROUND\s*_+\s*$'
        ],
        'projects': [
            r'^\s*PROJECTS?\s*$', r'^\s*KEY\s+PROJECTS?\s*$', r'^\s*NOTABLE\s+PROJECTS?\s*$',
            r'^\s*PERSONAL\s+PROJECTS?\s*$', r'^\s*PORTFOLIO\s*$', r'^\s*SELECTED\s+PROJECTS?\s*$',
            r'^\s*MAJOR\s+PROJECTS?\s*$', r'^\s*PROJECT\s+EXPERIENCE\s*$', r'^\s*PROFESSIONAL\s+PROJECTS?\s*$',
            r'^\s*_+\s*PROJECTS?\s*_+\s*$'
        ]
    }
    
    for i, line in enumerate(cv_lines):
        line_upper = line.upper().strip()
        
        # Check for section headers with enhanced pattern matching
        for section_type, patterns in section_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line_upper, re.IGNORECASE):
                    sections[section_type] = {
                        'start_line': i,
                        'header': line.strip(),
                        'content_start': i + 1
                    }
                    break
            if section_type in sections:
                    break
    
    # Find section end positions
    section_names = list(sections.keys())
    for i, section_name in enumerate(section_names):
        if i < len(section_names) - 1:
            # Next section starts where this one ends
            next_section = sections[section_names[i + 1]]
            sections[section_name]['end_line'] = next_section['start_line'] - 1
        else:
            # Last section goes to end of document
            sections[section_name]['end_line'] = len(cv_lines) - 1
    
    return sections

def insert_content_in_section(cv_lines: List[str], section_info: dict, new_content: List[str]) -> List[str]:
    """Insert new content at the end of a specific section"""
    if not section_info:
        return cv_lines
    
    insert_position = section_info['end_line']
    
    # Find the last non-empty line in the section
    while insert_position > section_info['content_start'] and not cv_lines[insert_position].strip():
        insert_position -= 1
    
    # Insert new content after the last content line
    for i, content_line in enumerate(reversed(new_content)):
        cv_lines.insert(insert_position + 1, content_line)
    
    return cv_lines

def enhance_cv_with_openai(original_cv: str, updates: List[tuple]) -> str:
    try:
        skills = [u[1] for u in updates if u[0] == "skill"]
        experiences = [u[1] for u in updates if u[0] == "experience"]
        education = [u[1] for u in updates if u[0] == "education"]
        
        # Use smart section integration for each type of update
        updated_cv = original_cv
        
        # Add skills to skills section
        if skills:
            skill_content = [f"• {skill}" for skill in skills]
            updated_cv = smart_section_integration(updated_cv, 'skills', skill_content)
        
        # Add experience to experience section
        if experiences:
            exp_content = []
            for exp in experiences:
                exp_content.extend([f"• {exp}", ""])
            updated_cv = smart_section_integration(updated_cv, 'experience', exp_content)
        
        # Add education to education section
        if education:
            edu_content = []
            for edu in education:
                formatted_edu = extract_education_from_message(edu)
                # Only add if it's properly formatted
                if formatted_edu != edu.strip() or any(word in edu.lower() for word in ['degree', 'university', 'college', 'certification', 'phd', 'master', 'bachelor']):
                    edu_content.append(f"• {formatted_edu}")
            
            if edu_content:
                updated_cv = smart_section_integration(updated_cv, 'education', edu_content)
        
        return updated_cv
        
    except Exception as e:
        print(f"OpenAI enhancement failed: {e}, using smart fallback")
        # Smart fallback that inserts in correct sections
        return enhance_cv_smart_fallback(original_cv, updates)

def enhance_cv_smart_fallback(original_cv: str, updates: List[tuple]) -> str:
    """Intelligent fallback that inserts content in appropriate sections"""
    skills = [u[1] for u in updates if u[0] == "skill"]
    experiences = [u[1] for u in updates if u[0] == "experience"]
    education = [u[1] for u in updates if u[0] == "education"]
    
    # If no updates provided, return original CV unchanged
    if not skills and not experiences and not education:
        return original_cv
    
    # Parse the CV to find sections
    sections = parse_cv_sections(original_cv)
    cv_lines = original_cv.split('\n')
    
    # Insert skills
    if skills:
        if 'skills' in sections:
            # Add to existing skills section
            new_skills = [f"• {skill}" for skill in skills]
            cv_lines = insert_content_in_section(cv_lines, sections['skills'], new_skills)
        else:
            # Create new skills section at appropriate location
            skills_header = "\nSKILLS"
            skills_content = [skills_header] + [f"• {skill}" for skill in skills] + [""]
            
            # Try to insert after personal info but before experience
            insert_pos = 10 if len(cv_lines) > 10 else len(cv_lines) // 3
            for i, line in enumerate(reversed(skills_content)):
                cv_lines.insert(insert_pos, line)
    
    # Insert experience
    if experiences:
        if 'experience' in sections:
            # Add to existing experience section
            new_exp = []
            for exp in experiences:
                new_exp.extend([f"• {exp}", ""])
            cv_lines = insert_content_in_section(cv_lines, sections['experience'], new_exp)
        else:
            # Create new experience section
            exp_header = "\nWORK EXPERIENCE"
            exp_content = [exp_header] + [f"• {exp}" for exp in experiences] + [""]
            
            # Insert after skills or personal info
            insert_pos = sections.get('skills', {}).get('end_line', len(cv_lines) // 2)
            for i, line in enumerate(reversed(exp_content)):
                cv_lines.insert(insert_pos + 1, line)
    
    # Insert education
    if education:
        if 'education' in sections:
            # Add to existing education section with proper formatting
            new_edu = []
            for edu in education:
                formatted_edu = extract_education_from_message(edu)
                new_edu.append(f"• {formatted_edu}")
            cv_lines = insert_content_in_section(cv_lines, sections['education'], new_edu)
        else:
            # Create new education section at the end
            edu_header = "\nEDUCATION"
            formatted_education = []
            for edu in education:
                formatted_edu = extract_education_from_message(edu)
                formatted_education.append(f"• {formatted_edu}")
            edu_content = [edu_header] + formatted_education + [""]
            
            # Insert at end but before any projects section
            insert_pos = sections.get('projects', {}).get('start_line', len(cv_lines))
            for i, line in enumerate(reversed(edu_content)):
                cv_lines.insert(insert_pos, line)
    
    return '\n'.join(cv_lines)

@app.get("/")
async def root():
    return {"message": "CV Updater Chatbot API with OpenAI"}

@app.post("/upload-cv/")
async def upload_cv(
    file: UploadFile = File(...),
    extracted_text: str = Form(None)
):
    """Enhanced CV upload with better error handling and validation"""
    try:
        print(f"🔄 Starting upload process for: {file.filename}")
        
        # Use extracted_text if provided, else extract from file
        cv_text = extracted_text or extract_text_from_file(file)
        
        if not cv_text or len(cv_text.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="The uploaded file doesn't contain enough readable text. Please ensure your CV has substantial content."
            )
        
        with get_db_cursor_context() as (cursor, conn):
            # Generate a title from filename
            title = file.filename.replace('.pdf', '').replace('.docx', '').replace('.txt', '').replace('_', ' ').title()
            
            # Clear all existing projects when new CV is uploaded
            cursor.execute("DELETE FROM manual_projects")
            print("🗑️ Cleared existing projects")
            
            # Set all other CVs as inactive
            cursor.execute("UPDATE cvs SET is_active = FALSE")
            print("🔄 Set other CVs as inactive")
            
            # Insert new CV as active
            cursor.execute('''INSERT INTO cvs (title, filename, original_content, current_content, is_active) 
                             VALUES (?, ?, ?, ?, TRUE)''', 
                          (title, file.filename, cv_text, cv_text))
            
            print(f"✅ Successfully stored CV in database. Content length: {len(cv_text)} characters")
            
            # Verify the CV was stored correctly
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            stored_cv = cursor.fetchone()
            
            if stored_cv and len(stored_cv[0]) > 0:
                print("✅ CV content verified in database - chat system will have full access")
            else:
                print("⚠️ Warning: CV might not be properly stored")
            
            # Extract and insert projects from CV
            extracted_projects = extract_projects_from_cv(stored_cv[0])
            print(f"🔍 Extracted {len(extracted_projects)} projects from CV.")
            for project in extracted_projects:
                cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", (json.dumps(project),))
            print(f"✅ Inserted {len(extracted_projects)} projects into manual_projects table.")
        
        return JSONResponse(status_code=200, content={
            "message": f"✅ CV uploaded successfully! Chat system now has full access to your {len(cv_text)} character CV content.", 
            "filename": file.filename,
            "title": title,
            "content_length": len(cv_text),
            "status": "ready_for_chat"
        })
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute("INSERT INTO chat_messages (message, message_type) VALUES (?, ?)", 
                          (request.message, "user"))
        
            # Get current CV content for context with enhanced debugging
            cursor.execute("SELECT current_content, filename FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if cv_row:
                cv_content, filename = cv_row
                print(f"📋 Chat accessing CV: {filename} ({len(cv_content) if cv_content else 0} characters)")
            else:
                cv_content = None
                print("⚠️ No active CV found in database")
            
            classification = classify_message(request.message, cv_content)
            category = classification.get("category", "OTHER")
            extracted_info = classification.get("extracted_info")
            operation = classification.get("operation", "READ")
            target_item = classification.get("target_item", "")
            
            response_text = ""
            cv_updated = False
            
            # Ensure we have CV content for most operations
            if not cv_content and category not in ["CV_HELP", "OTHER"]:
                response_text = "📄 Please upload a CV first so I can perform operations on your CV content!"
            
            # ===== CREATE OPERATIONS =====
            elif category in ["SKILL_ADD", "EXPERIENCE_ADD", "EDUCATION_ADD", "PROJECT_ADD", "PROFILE_ADD", "CONTACT_ADD"]:
                if cv_content:
                    # Use intelligent content extraction to get main content and auto-detect section
                    extracted_content, detected_section = extract_intelligent_content(request.message)
                    
                    # Override detected section with explicit category if available
                    section_map = {
                        "SKILL_ADD": "skills",
                        "EXPERIENCE_ADD": "experience", 
                        "EDUCATION_ADD": "education",
                        "PROJECT_ADD": "projects",
                        "PROFILE_ADD": "profile",
                        "CONTACT_ADD": "contact"
                    }
                    section_type = section_map.get(category, detected_section)
                    
                    print(f"[DIAG] Incoming {category}. Original message: {request.message}")
                    print(f"[DIAG] Extracted content: {extracted_content}")
                    print(f"[DIAG] Detected section: {detected_section}, Using section: {section_type}")
                    print(f"[DIAG] CV before update (excerpt): {cv_content[cv_content.lower().find(section_type):][:500] if section_type in cv_content.lower() else cv_content[:500]}")
                    
                    # Use the extracted content instead of the full message
                    updated_cv = insert_content_in_section_enhanced(cv_content, section_type, extracted_content, "append")
                    
                    print(f"[DIAG] CV after update (excerpt): {updated_cv[updated_cv.lower().find(section_type):][:500] if section_type in updated_cv.lower() else updated_cv[:500]}")
                    if updated_cv != cv_content:
                        cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
                        cv_updated = True
                        print(f"[DIAG] DB updated with new {section_type} section.")
                        # Extract and return the updated section
                        updated_section = extract_section_from_cv(updated_cv, section_type)
                        response_text = f"✅ Added '{extracted_content}' to {section_type} section! Your CV has been updated.\n\n**Updated {section_type.title()} Section:**\n{updated_section}"
                    else:
                        print(f"[DIAG] No changes made to {section_type} section.")
                        response_text = f"⚠️ No changes made to your {section_type} section."
                    
                    if category == "PROJECT_ADD":
                        try:
                            project_data = extract_project_from_message(extracted_content)
                            cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", (json.dumps(project_data),))
                        except:
                            pass
            
            # ===== READ OPERATIONS =====
            elif category in ["CV_SHOW", "SKILL_SHOW", "EXPERIENCE_SHOW", "EDUCATION_SHOW", "PROJECT_SHOW", "CONTACT_SHOW"]:
                if cv_content:
                    section_map = {
                        "CV_SHOW": "cv",
                        "SKILL_SHOW": "skills",
                        "EXPERIENCE_SHOW": "experience",
                        "EDUCATION_SHOW": "education",
                        "PROJECT_SHOW": "projects",
                        "CONTACT_SHOW": "contact"
                    }
                    
                    section_type = section_map.get(category, "cv")
                    response_text = read_cv_section(cv_content, section_type)
                    
                    # For projects, also check the projects database
                    if category == "PROJECT_SHOW":
                        cursor.execute("SELECT project_data FROM manual_projects ORDER BY created_at DESC")
                        projects = cursor.fetchall()
                        if projects:
                            response_text += f"\n\n🗄️ **Projects Database ({len(projects)} projects):**\n"
                            for i, (project_json,) in enumerate(projects[:3], 1):
                                try:
                                    project = json.loads(project_json)
                                    response_text += f"{i}. {project.get('title', 'Untitled')}\n"
                                except:
                                    pass
                            if len(projects) > 3:
                                response_text += f"... and {len(projects) - 3} more projects"
            
            # ===== UPDATE OPERATIONS =====
            elif category in ["SKILL_UPDATE", "EXPERIENCE_UPDATE", "EDUCATION_UPDATE", "PROJECT_UPDATE", "PROFILE_UPDATE", "CONTACT_UPDATE"]:
                if cv_content:
                    # Use intelligent content extraction to get main content and auto-detect section
                    extracted_content, detected_section = extract_intelligent_content(request.message)
                    
                    # Override detected section with explicit category if available
                    section_map = {
                        "SKILL_UPDATE": "skills",
                        "EXPERIENCE_UPDATE": "experience",
                        "EDUCATION_UPDATE": "education", 
                        "PROJECT_UPDATE": "projects",
                        "PROFILE_UPDATE": "profile",
                        "CONTACT_UPDATE": "contact"
                    }
                    section_type = section_map.get(category, detected_section)
                    
                    print(f"[DIAG] Incoming {category}. Original message: {request.message}")
                    print(f"[DIAG] Extracted content: {extracted_content}")
                    print(f"[DIAG] Detected section: {detected_section}, Using section: {section_type}")
                    print(f"[DIAG] CV before update (excerpt): {cv_content[cv_content.lower().find(section_type):][:500] if section_type in cv_content.lower() else cv_content[:500]}")
                    
                    # Use the extracted content instead of the full message
                    updated_cv = insert_content_in_section_enhanced(cv_content, section_type, extracted_content, "append")
                    
                    print(f"[DIAG] CV after update (excerpt): {updated_cv[updated_cv.lower().find(section_type):][:500] if section_type in updated_cv.lower() else updated_cv[:500]}")
                    if updated_cv != cv_content:
                        cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
                        cv_updated = True
                        print(f"[DIAG] DB updated with new {section_type} section.")
                        updated_section = extract_section_from_cv(updated_cv, section_type)
                        response_text = f"✅ Updated {section_type} section with '{extracted_content}'! Your CV has been updated.\n\n**Updated {section_type.title()} Section:**\n{updated_section}"
                    else:
                        print(f"[DIAG] No changes made to {section_type} section.")
                        response_text = f"⚠️ No changes made to your {section_type} section."
            
            # ===== DELETE OPERATIONS =====
            elif category in ["SKILL_DELETE", "EXPERIENCE_DELETE", "EDUCATION_DELETE", "PROJECT_DELETE", "CONTACT_DELETE"]:
                if cv_content:
                    section_map = {
                        "SKILL_DELETE": "skills",
                        "EXPERIENCE_DELETE": "experience",
                        "EDUCATION_DELETE": "education",
                        "PROJECT_DELETE": "projects", 
                        "CONTACT_DELETE": "contact"
                    }
                    
                    section_type = section_map.get(category, "skills")
                    updated_cv, response_text = delete_cv_item(cv_content, section_type, extracted_info)
                    
                    if updated_cv != cv_content:
                        cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
                        cv_updated = True
                        response_text += f" The changes are now visible in your CV."
                    
                    # Also handle project database deletion
                    if category == "PROJECT_DELETE":
                        id_match = re.search(r'\b(\d+)\b', extracted_info)
                        if id_match:
                            project_id = int(id_match.group(1))
                            cursor.execute("DELETE FROM manual_projects WHERE id = ?", (project_id,))
                            if cursor.rowcount > 0:
                                response_text += f" Also removed project ID {project_id} from database."
            
            # ===== UTILITY OPERATIONS =====
            elif category == "CV_GENERATE":
                updated_cv = generate_cv_with_projects(cursor, conn)
                response_text = "✅ Successfully generated your enhanced CV with all projects and updates included! Your CV has been updated and is now ready for viewing. Check the CV panel to see your updated content."
                cv_updated = True
                
            elif category == "CV_CLEANUP":
                response_text = "🧹 Cleaning up duplicate sections in your CV..."
                cleaned_cv = clean_duplicate_project_sections(generate_cv_with_projects(cursor, conn))
                cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (cleaned_cv,))
                response_text += " ✅ CV cleaned up successfully! Your CV is now free of duplicate sections."
                cv_updated = True
                
            elif category == "LINKEDIN_BLOG":
                # Get all projects from database
                cursor.execute("SELECT id, project_data FROM manual_projects ORDER BY created_at DESC")
                projects = cursor.fetchall()
                
                if not projects:
                    response_text = "❌ No projects found. Please add some projects first before generating a LinkedIn blog post."
                else:
                    # Use the most recent project for blog generation
                    project_id, project_json = projects[0]
                    try:
                        project_data = json.loads(project_json)
                        
                        # Generate LinkedIn blog post
                        if openai_client:
                            blog_content = generate_linkedin_blog(project_data)
                        else:
                            blog_content = generate_linkedin_blog_fallback(project_data)
                        
                        response_text = f"""📝 **LinkedIn Blog Post Generated Successfully!**

**Project:** {project_data.get('title', 'Project')}

**Blog Content:**
{blog_content}

**💡 Tips for posting:**
• Copy the content above
• Paste it into LinkedIn
• Add relevant hashtags if needed
• Tag relevant technologies/companies
• Engage with comments

**🎯 Ready to share your project with the world!**"""
                        
                    except Exception as e:
                        response_text = f"❌ Error generating LinkedIn blog: {str(e)}"
                
            elif category == "CV_HELP":
                response_text = """🤖 **AI CV Assistant - Full CRUD Commands**

    ✨ **CREATE (Add New Items):**
    • "I learned Python, React, and Docker" - Add skills
    • "I worked as Senior Developer at TechCorp" - Add experience  
    • "I studied Computer Science at MIT" - Add education
    • "I built a React e-commerce app" - Add project
    • "My email is john@example.com" - Add contact info

    📖 **READ (Show Information):**
    • "Show my skills" / "What skills do I have?" - Display skills
    • "Show my experience" / "My work history" - Display experience
    • "Show my education" / "My qualifications" - Display education
    • "Show my projects" / "My portfolio" - Display projects
    • "Show my CV" / "Display my complete CV" - Show full CV

    ✏️ **UPDATE (Modify Existing):**
    • "Update my skills section with Node.js" - Modify skills
    • "Change my experience at TechCorp" - Modify experience
    • "Update my education details" - Modify education
    • "Modify my React project" - Update projects

    🗑️ **DELETE (Remove Items):**
    • "Remove Python skill" / "Delete JavaScript" - Remove skills
    • "Remove job at OldCorp" / "Delete experience" - Remove experience
    • "Remove degree" / "Delete education entry" - Remove education
    • "Remove project 1" / "Delete React app" - Remove projects

    🔧 **UTILITY COMMANDS:**
    • "Generate CV" - Create updated CV with all changes
    • "Clean CV" - Remove duplicate sections and organize
    • "LinkedIn Blog" / "Create Blog" - Generate LinkedIn post for your latest project
    • "Help" - Show this command list

    💬 **Natural Language Support:**
    Just talk naturally! I understand commands like:
    • "I don't have JavaScript skill anymore"
    • "Actually, I didn't work at that company"
    • "Add Node.js to my technical skills"
    • "What programming languages do I know?"

    🎯 **Pro Tips:**
    • All changes are saved automatically
    • Use "Generate CV" to see final result
    • Be specific when updating/deleting items
    • I can understand various ways of saying the same thing!"""
            
            else:
                response_text = """👋 I'm your AI CV Assistant with full CRUD capabilities! 
                
    I can **Create**, **Read**, **Update**, and **Delete** any part of your CV.
    
    Try commands like:
    • "I learned Python and React" 
    • "Show my skills"
    • "Remove JavaScript skill"
    • "Update my experience"
    
    Say **"help"** for complete command list! 😊"""
        
            # Add operation details to response for debugging
            debug_info = f"\n\n🔍 **Operation Details:** {category} ({operation})"
            print(f"💬 Chat Operation: {category} | Operation: {operation} | CV Updated: {cv_updated}")
            
            cursor.execute("INSERT INTO chat_messages (message, message_type) VALUES (?, ?)", 
                          (response_text, "bot"))
            
            return ChatResponse(response=response_text, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/cv/current/", response_model=CVResponse)
async def get_current_cv():
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Get the active CV with current content (includes all updates)
            cursor.execute("SELECT filename, current_content, updated_at FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                # If no active CV, get the most recent one
                cursor.execute("SELECT filename, current_content, updated_at FROM cvs ORDER BY updated_at DESC LIMIT 1")
                cv_row = cursor.fetchone()
            
            if not cv_row:
                raise HTTPException(status_code=404, detail="No CV found. Please upload a CV first.")
            
            filename, current_content, updated_at = cv_row
            
            # Format the current CV for better display (this includes all updates)
            formatted_cv = format_cv_for_display(current_content)
            
            return CVResponse(content=formatted_cv, filename=filename, last_updated=updated_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def format_cv_for_display(cv_content: str) -> str:
    """Format CV content for clean display in the frontend"""
    try:
        # First, reorganize the CV content to ensure proper section placement
        reorganized_cv = reorganize_cv_content(cv_content)
        
        lines = reorganized_cv.strip().split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append("")
                continue
            
            # Check if this is a section header (with underscores or all caps)
            is_header = (
                ('_____' in line and any(keyword in line.upper() for keyword in 
                    ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 
                     'PROJECTS', 'ACHIEVEMENTS', 'CERTIFICATIONS', 'CONTACT'])) or
                (line.isupper() and len(line) > 3 and any(keyword in line.upper() for keyword in 
                    ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 
                     'PROJECTS', 'ACHIEVEMENTS', 'CERTIFICATIONS', 'CONTACT']))
            )
            
            if is_header:
                # Add some spacing before section headers
                if formatted_lines and formatted_lines[-1] != "":
                    formatted_lines.append("")
                # Clean up the header (remove underscores, format nicely)
                clean_header = line.replace('_', '').strip()
                formatted_lines.append(f"📋 {clean_header}")
                formatted_lines.append("─" * (len(clean_header) + 5))  # Add underline
            else:
                # Clean up bullet points and formatting
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    formatted_lines.append(f"  • {line[1:].strip()}")
                else:
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
        
    except Exception as e:
        print(f"Error formatting CV for display: {e}")
        return cv_content  # Return original if formatting fails

# New CV Management Endpoints
@app.get("/cvs/")
async def list_all_cvs():
    """Get list of all CVs with metadata"""
    try:
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute('''SELECT id, title, filename, created_at, updated_at, is_active 
                             FROM cvs ORDER BY updated_at DESC''')
            cvs = cursor.fetchall()
            
            cv_list = []
            for cv in cvs:
                cv_id, title, filename, created_at, updated_at, is_active = cv
                cv_list.append({
                    "id": cv_id,
                    "title": title,
                    "filename": filename,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "is_active": bool(is_active)
                })
            
            return {"cvs": cv_list, "total_count": len(cv_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/cvs/{cv_id}")
async def get_cv_by_id(cv_id: int):
    """Get specific CV by ID"""
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        cursor.execute('''SELECT id, title, filename, current_content, created_at, updated_at, is_active 
                         FROM cvs WHERE id = ?''', (cv_id,))
        cv_row = cursor.fetchone()
        conn.close()
        
        if not cv_row:
            raise HTTPException(status_code=404, detail="CV not found")
        
        cv_id, title, filename, content, created_at, updated_at, is_active = cv_row
        
        return {
            "id": cv_id,
            "title": title,
            "filename": filename,
            "content": content,
            "created_at": created_at,
            "updated_at": updated_at,
            "is_active": bool(is_active)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

class CVUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

@app.put("/cvs/{cv_id}")
async def update_cv(cv_id: int, cv_data: CVUpdateRequest):
    """Update CV title and/or content"""
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Check if CV exists
        cursor.execute("SELECT id FROM cvs WHERE id = ?", (cv_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Update fields that are provided
        update_fields = []
        params = []
        
        if cv_data.title is not None:
            update_fields.append("title = ?")
            params.append(cv_data.title)
            
        if cv_data.content is not None:
            update_fields.append("current_content = ?")
            params.append(cv_data.content)
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(cv_id)
            
            query = f"UPDATE cvs SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return {"message": "CV updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/cvs/{cv_id}")
async def delete_cv(cv_id: int):
    """Delete a CV"""
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Check if CV exists
        cursor.execute("SELECT is_active FROM cvs WHERE id = ?", (cv_id,))
        cv_row = cursor.fetchone()
        
        if not cv_row:
            raise HTTPException(status_code=404, detail="CV not found")
        
        was_active = cv_row[0]
        
        # Delete the CV
        cursor.execute("DELETE FROM cvs WHERE id = ?", (cv_id,))
        
        # If the deleted CV was active, make the most recent CV active
        if was_active:
            cursor.execute('''UPDATE cvs SET is_active = TRUE 
                             WHERE id = (SELECT id FROM cvs ORDER BY updated_at DESC LIMIT 1)''')
        
        conn.commit()
        conn.close()
        
        return {"message": "CV deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/cvs/{cv_id}/activate")
async def activate_cv(cv_id: int):
    """Set a CV as the active one"""
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Check if CV exists
        cursor.execute("SELECT id FROM cvs WHERE id = ?", (cv_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="CV not found")
        
        # Set all CVs as inactive
        cursor.execute("UPDATE cvs SET is_active = FALSE")
        
        # Set the specified CV as active
        cursor.execute("UPDATE cvs SET is_active = TRUE WHERE id = ?", (cv_id,))
        
        conn.commit()
        conn.close()
        
        return {"message": "CV activated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/cvs/{cv_id}/download")
async def download_cv_by_id(cv_id: int):
    """Download a specific CV as PDF"""
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        cursor.execute('''SELECT title, current_content FROM cvs WHERE id = ?''', (cv_id,))
        cv_row = cursor.fetchone()
        conn.close()
        
        if not cv_row:
            raise HTTPException(status_code=404, detail="CV not found")
        
        title, content = cv_row
        
        # Format CV with AI for better structure
        formatted_content = format_cv_with_ai(content)
        
        # Generate PDF file
        pdf_buffer = generate_cv_pdf(formatted_content, [])
        pdf_content = pdf_buffer.getvalue()
        
        # Generate filename from title and determine file type
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Determine file type based on content
        try:
            # Try to decode as text to see if it's a text file
            pdf_content.decode('utf-8')
            # If successful, it's a text file
            filename = f"{safe_title}_{timestamp}.txt"
            media_type = "text/plain"
            content_type = "text/plain; charset=utf-8"
        except UnicodeDecodeError:
            # If decode fails, it's binary PDF content
            filename = f"{safe_title}_{timestamp}.pdf"
            media_type = "application/pdf"
            content_type = "application/pdf"
        
        return Response(
            content=pdf_content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Content-Length": str(len(pdf_content)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Content-Type": content_type,
                "X-Content-Type-Options": "nosniff"
            }
        )
        
    except Exception as e:
        print(f"Error generating CV document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading CV: {str(e)}")

@app.get("/chat/history/")
async def get_chat_history():
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, message, message_type, created_at FROM chat_messages ORDER BY created_at")
        messages = cursor.fetchall()
        conn.close()
        return [{"id": msg[0], "message": msg[1], "type": msg[2], "timestamp": msg[3]} for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

class ProjectRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    duration: Optional[str] = ""
    technologies: List[str] = []
    highlights: List[str] = []

@app.get("/projects/")
async def get_projects():
    try:
        with get_db_cursor_context() as (cursor, conn):
            # First check for manually created projects - INCLUDE ID!
            cursor.execute("SELECT id, project_data FROM manual_projects ORDER BY created_at DESC")
            manual_projects = cursor.fetchall()
            
            projects = []
            for project_row in manual_projects:
                try:
                    project_id = project_row[0]
                    project_data = json.loads(project_row[1])
                    # Add the ID to the project data
                    project_data['id'] = project_id
                    projects.append(project_data)
                except:
                    pass
            
            # Only return manual projects from database to ensure deleted projects are excluded
            # Note: We skip CV extraction to avoid showing deleted projects
            
            return {"projects": projects, "total_count": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

class ChatProjectRequest(BaseModel):
    message: str

@app.post("/projects/create-from-chat")
async def create_project_from_chat(request: ChatProjectRequest):
    """Create a project from natural language chat input"""
    try:
        # Extract project data from chat message
        project_data = extract_project_from_chat_message(request.message)
        
        if not project_data.get('title'):
            return {
                "success": False,
                "message": "Could not extract project information from your message. Please provide more details like: 'Create a React e-commerce website project using React, Node.js, and MongoDB'",
                "project": None
            }

        with get_db_cursor_context() as (cursor, conn):
            # Create manual_projects table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS manual_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", 
                          (json.dumps(project_data),))
            project_id = cursor.lastrowid
            
            return {
                "success": True,
                "message": f"Successfully created project '{project_data['title']}'",
                "project": {**project_data, "id": project_id}
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating project: {str(e)}",
            "project": None
        }

def extract_project_from_chat_message(message: str) -> dict:
    """Extract project information from a natural language message"""
    import re
    
    project_data = {
        "title": "",
        "description": "",
        "technologies": [],
        "duration": "",
        "highlights": []
    }
    
    message_lower = message.lower()
    
    # Extract title patterns - improved to handle more natural language
    title_patterns = [
        r"create\s+(?:a\s+)?(.+?)\s+project",
        r"add\s+(?:a\s+)?(.+?)\s+project", 
        r"new\s+(.+?)\s+project",
        r"build\s+(?:a\s+)?(.+?)\s+(?:project|app|website|system)",
        r"make\s+(?:a\s+)?(.+?)\s+(?:project|app|website|system)",
        r"i\s+(?:have\s+)?(?:created|built|made|developed)\s+(?:a\s+|an\s+)?(.+?)(?:\s+project|\s+app|\s+website|\s+system|$)",
        r"(?:created|built|made|developed)\s+(?:a\s+|an\s+)?(.+?)(?:\s+project|\s+app|\s+website|\s+system|$)"
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, message_lower)
        if match:
            title = match.group(1).strip()
            # Clean up common words
            title = re.sub(r'\b(using|with|that|which|for)\b.*', '', title).strip()
            project_data["title"] = title.title()
            break
    
    # Fallback: if no title found but message contains project-related keywords
    if not project_data["title"] and any(keyword in message_lower for keyword in ['project', 'website', 'app', 'system', 'created', 'built']):
        # Try to extract key nouns as potential project names
        import re
        words = message_lower.split()
        potential_titles = []
        
        # Look for common project types
        project_types = ['website', 'app', 'application', 'system', 'platform', 'tool', 'dashboard', 'portal', 'api', 'service']
        for ptype in project_types:
            if ptype in message_lower:
                # Look for adjectives before the project type
                pattern = r'(\w+\s+)?' + ptype
                match = re.search(pattern, message_lower)
                if match:
                    potential_titles.append(f"{match.group(1) or ''}{ptype}".strip())
        
        if potential_titles:
            project_data["title"] = potential_titles[0].title()
        else:
            project_data["title"] = "New Project"
    
    # Extract technologies
    tech_keywords = [
        'react', 'vue', 'angular', 'javascript', 'typescript',
        'node', 'express', 'python', 'django', 'flask', 'fastapi',
        'mongodb', 'mysql', 'postgresql', 'sqlite', 'redis',
        'aws', 'firebase', 'docker', 'kubernetes', 'jenkins',
        'html', 'css', 'sass', 'bootstrap', 'tailwind',
        'git', 'github', 'gitlab', 'api', 'rest', 'graphql'
    ]
    
    found_technologies = []
    for tech in tech_keywords:
        if tech.lower() in message_lower:
            found_technologies.append(tech.title())
    
    project_data["technologies"] = found_technologies
    
    # Generate description
    if project_data["title"]:
        tech_text = f" using {', '.join(found_technologies[:3])}" if found_technologies else ""
        project_data["description"] = f"A {project_data['title']} project{tech_text}. Built with modern development practices and clean code architecture."
    
    # Extract duration if mentioned
    duration_patterns = [
        r"(\d+)\s+(month|week|day)s?",
        r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}",
        r"\d{4}\s*-\s*\d{4}"
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, message_lower)
        if match:
            project_data["duration"] = match.group(0)
            break
    
    # Add some default highlights if technologies are found
    if found_technologies:
        highlights = []
        if 'react' in [t.lower() for t in found_technologies]:
            highlights.append("Built responsive user interface with React components")
        if any(db in [t.lower() for t in found_technologies] for db in ['mongodb', 'mysql', 'postgresql']):
            highlights.append("Implemented robust data storage and retrieval")
        if any(backend in [t.lower() for t in found_technologies] for backend in ['node', 'python', 'django', 'flask']):
            highlights.append("Developed RESTful API endpoints")
        if any(cloud in [t.lower() for t in found_technologies] for cloud in ['aws', 'firebase']):
            highlights.append("Deployed application to cloud platform")
        
        project_data["highlights"] = highlights[:3]  # Limit to 3 highlights
    
    return project_data

@app.post("/projects/create")
async def create_project(project: ProjectRequest):
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Create manual_projects table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS manual_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            project_data = {
                "title": project.title,
                "description": project.description,
                "duration": project.duration,
                "technologies": project.technologies,
                "highlights": project.highlights
            }
            
            cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", 
                          (json.dumps(project_data),))
            project_id = cursor.lastrowid
            
            # Add ID to returned project data
            project_with_id = {**project_data, "id": project_id}
            return {"message": "Project created successfully", "project": project_with_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/projects/clear-all")
async def clear_all_projects():
    """Clear all projects from the database"""
    try:
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute("DELETE FROM manual_projects")
            return {"message": "All projects cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/projects/list")
async def list_projects_with_ids():
    try:
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute("SELECT id, project_data FROM manual_projects ORDER BY created_at DESC")
            manual_projects = cursor.fetchall()
            
            projects = []
            for project_row in manual_projects:
                try:
                    project_data = json.loads(project_row[1])
                    project_data['id'] = project_row[0]
                    projects.append(project_data)
                except:
                    pass
            
            return {"projects": projects, "total_count": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/projects/blog")
async def generate_project_blog_by_title():
    """Generate a LinkedIn blog post for a project by title (for chatbot)"""
    try:
        from fastapi import Request
        
        request_body = await request.json() if hasattr(request, 'json') else {}
        project_title = request_body.get('project_title', '').lower()
        
        with get_db_cursor() as (cursor, conn):
            # Get all projects and find by title
            cursor.execute("SELECT id, project_data FROM manual_projects")
            projects = cursor.fetchall()
            
            matching_project = None
            for project_id, project_json in projects:
                try:
                    project_data = json.loads(project_json)
                    if project_title in project_data.get('title', '').lower():
                        matching_project = project_data
                        break
                except:
                    continue
        
        if not matching_project:
            return {
                "message": "Project not found",
                "blog_content": "I couldn't find a project with that title. Please check the project name and try again.",
                "project_title": project_title
            }
        
        # Generate blog post
        blog_content = generate_linkedin_blog(matching_project)
        
        return {
            "message": "LinkedIn blog generated successfully",
            "blog_content": blog_content,
            "project_title": matching_project.get('title', 'Project')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating blog: {str(e)}")

@app.put("/projects/{project_id}")
async def update_project(project_id: int, project: ProjectRequest):
    try:
        with get_db_cursor() as (cursor, conn):
            project_data = {
                "title": project.title,
                "description": project.description,
                "duration": project.duration,
                "technologies": project.technologies,
                "highlights": project.highlights
            }
            
            cursor.execute("UPDATE manual_projects SET project_data = ? WHERE id = ?", 
                          (json.dumps(project_data), project_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
            
            # Add ID to returned project data
            project_with_id = {**project_data, "id": project_id}
            return {"message": "Project updated successfully", "project": project_with_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    try:
        with get_db_cursor() as (cursor, conn):
            cursor.execute("DELETE FROM manual_projects WHERE id = ?", (project_id,))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return {"message": "Project deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/cv/cleanup")
async def cleanup_cv():
    """Clean up duplicate sections in the CV"""
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Get current active CV
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                # If no active CV, get the most recent one
                cursor.execute("SELECT current_content FROM cvs ORDER BY updated_at DESC LIMIT 1")
                cv_row = cursor.fetchone()
            
            if not cv_row:
                raise HTTPException(status_code=404, detail="No CV found. Please upload a CV first.")
            
            current_cv = cv_row[0]
            
            # Clean up duplicate sections
            cleaned_cv = clean_duplicate_project_sections(current_cv)
            
            # Regenerate with proper formatting using existing cursor
            cleaned_cv = generate_cv_with_projects(cursor, conn)
            
            # Update in database
            cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (cleaned_cv,))
            
            return {"message": "CV cleaned up successfully! All duplicate sections removed.", "cv_content": cleaned_cv}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up CV: {str(e)}")

@app.post("/cv/generate")
async def generate_updated_cv():
    try:
        with get_db_cursor_context() as (cursor, conn):
            updated_cv = generate_cv_with_projects(cursor, conn)
            return {"message": "CV generated successfully", "cv_content": updated_cv}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/cv/add-projects")
async def add_projects_to_cv():
    """Add all projects to the current CV"""
    try:
        with get_db_cursor() as (cursor, conn):
            # Check if there's an active CV
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                # If no active CV, get the most recent one
                cursor.execute("SELECT current_content FROM cvs ORDER BY updated_at DESC LIMIT 1")
                cv_row = cursor.fetchone()
            
            if not cv_row:
                # No CV exists, create a basic CV with projects
                basic_cv = "PROFESSIONAL CV\n\nPROJECTS\n"
                cursor.execute('''INSERT INTO cvs (title, filename, original_content, current_content, is_active) 
                                 VALUES (?, ?, ?, ?, TRUE)''', 
                              ("Generated CV", "generated_cv.txt", basic_cv, basic_cv))
                print("📄 Created basic CV for projects")
            
            # Generate CV with all projects included
            updated_cv = generate_cv_with_projects(cursor, conn)
            
            # Update the active CV in the database
            cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
            
            return {
                "success": True,
                "message": "All projects successfully added to your CV!",
                "cv_content": updated_cv
            }
    except Exception as e:
        print(f"Error adding projects to CV: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding projects to CV: {str(e)}")

@app.get("/cv/enhanced/", response_model=CVResponse)
async def get_enhanced_cv():
    """Get CV with all enhancements and projects included"""
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Get the active CV
            cursor.execute("SELECT filename, current_content, updated_at FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                # If no active CV, get the most recent one
                cursor.execute("SELECT filename, current_content, updated_at FROM cvs ORDER BY updated_at DESC LIMIT 1")
                cv_row = cursor.fetchone()
            
            if not cv_row:
                raise HTTPException(status_code=404, detail="No CV found. Please upload a CV first.")
            
            filename, current_content, updated_at = cv_row
            
            # Apply any pending updates
            cursor.execute("SELECT update_type, content FROM cv_updates WHERE processed = FALSE ORDER BY created_at")
            updates = cursor.fetchall()
            
            if updates:
                enhanced_cv = enhance_cv_with_openai(current_content, updates)
                cursor.execute("UPDATE cv_updates SET processed = TRUE")
                cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (enhanced_cv,))
            else:
                enhanced_cv = current_content
            
            # Generate CV with all projects and enhancements
            enhanced_cv = generate_cv_with_projects(cursor, conn)
            
            # Format with AI for better presentation
            formatted_cv = format_cv_with_ai(enhanced_cv)
            
            cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (formatted_cv,))
            
            return CVResponse(content=formatted_cv, filename=filename, last_updated=updated_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def generate_linkedin_blog(project_data: dict) -> str:
    """Generate a LinkedIn blog post for a specific project"""
    try:
        prompt = f"""Create a professional LinkedIn blog post about this project:

Project Details:
- Title: {project_data.get('title', 'Project')}
- Description: {project_data.get('description', '')}
- Technologies: {', '.join(project_data.get('technologies', []))}
- Duration: {project_data.get('duration', '')}
- Highlights: {'; '.join(project_data.get('highlights', []))}

Create an engaging LinkedIn post that:
1. Starts with an attention-grabbing hook
2. Explains the project's purpose and impact
3. Highlights technical challenges overcome
4. Mentions key technologies used
5. Includes relevant hashtags
6. Ends with a call to action or reflection
7. Uses emojis appropriately
8. Keeps it professional but engaging
9. Length: 200-300 words

Make it sound personal and authentic, as if the developer is sharing their experience."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating LinkedIn blog with OpenAI: {e}")
        # Fallback blog generation
        return generate_linkedin_blog_fallback(project_data)

def generate_linkedin_blog_fallback(project_data: dict) -> str:
    """Fallback method to generate LinkedIn blog post"""
    title = project_data.get('title', 'My Latest Project')
    description = project_data.get('description', 'An amazing project I worked on')
    technologies = project_data.get('technologies', [])
    duration = project_data.get('duration', 'Recently')
    highlights = project_data.get('highlights', [])
    
    tech_text = f" using {', '.join(technologies[:3])}" if technologies else ""
    highlights_text = "\n".join([f"✅ {highlight}" for highlight in highlights[:3]]) if highlights else ""
    
    blog_post = f"""🚀 Excited to share my latest project: {title}!

{description}{tech_text}.

💡 What I accomplished:
{highlights_text if highlights_text else "✅ Successfully delivered a functional solution"}

🛠️ Tech Stack:
{' | '.join(technologies) if technologies else 'Modern web technologies'}

⏱️ Timeline: {duration}

This project challenged me to think creatively and implement best practices in software development. Each obstacle was an opportunity to learn and grow as a developer.

The experience reinforced my passion for creating solutions that make a real impact. I'm grateful for the opportunity to work with cutting-edge technologies and deliver meaningful results.

What's your favorite part about building new projects? I'd love to hear about your latest achievements! 💬

#WebDevelopment #SoftwareDeveloper #TechInnovation #Programming #ProjectManagement #Development"""

    return blog_post

@app.post("/projects/{project_id}/blog")
async def generate_project_blog(project_id: int):
    """Generate a LinkedIn blog post for a specific project"""
    try:
        with get_db_cursor() as (cursor, conn):
            # Get project data
            cursor.execute("SELECT project_data FROM manual_projects WHERE id = ?", (project_id,))
            project_row = cursor.fetchone()
            
            if not project_row:
                raise HTTPException(status_code=404, detail="Project not found")
            
            project_data = json.loads(project_row[0])
            
            # Generate blog post
            blog_content = generate_linkedin_blog(project_data)
            
            return {
                "message": "LinkedIn blog generated successfully",
                "blog_content": blog_content,
                "project_title": project_data.get('title', 'Project')
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating blog: {str(e)}")

class CVBuilderRequest(BaseModel):
    personal_info: dict
    profile_summary: str
    skills: dict
    experience: List[dict]
    education: List[dict]
    projects: List[dict]

@app.post("/cv/create-from-builder")
async def create_cv_from_builder(cv_data: CVBuilderRequest):
    """Create a new CV from the CV Builder data"""
    try:
        # Generate CV text from structured data
        cv_text = generate_cv_text_from_data(cv_data.dict())
        
        # Generate title from personal info
        personal_info = cv_data.personal_info
        title = f"{personal_info.get('full_name', 'Professional')} CV"
        filename = f"cv_builder_{personal_info.get('full_name', 'professional').lower().replace(' ', '_')}.txt"
        
        # Store in database
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Set all other CVs as inactive
        cursor.execute("UPDATE cvs SET is_active = FALSE")
        
        # Insert new CV as active
        cursor.execute('''INSERT INTO cvs (title, filename, original_content, current_content, is_active) 
                         VALUES (?, ?, ?, ?, TRUE)''', 
                      (title, filename, cv_text, cv_text))
        
        # Store projects separately
        for project in cv_data.projects:
            project_json = json.dumps(project)
            cursor.execute('INSERT INTO manual_projects (project_data) VALUES (?)', (project_json,))
        
        conn.commit()
        conn.close()
        
        return {
            "message": "CV created successfully from CV Builder",
            "cv_content": cv_text,
            "title": title,
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error creating CV from builder: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating CV: {str(e)}")

def generate_cv_text_from_data(cv_data: dict) -> str:
    """Generate formatted CV text from structured data"""
    cv_text = ""
    
    # Personal Information
    personal = cv_data.get('personal_info', {})
    cv_text += f"{personal.get('full_name', '')}\n"
    cv_text += f"{personal.get('phone', '')}\n"
    cv_text += f"{personal.get('email', '')} {personal.get('address', '')}\n"
    if personal.get('linkedin'):
        cv_text += f"{personal.get('linkedin')}\n"
    if personal.get('website'):
        cv_text += f"{personal.get('website')}\n"
    
    # Profile Summary
    profile_summary = cv_data.get('profile_summary', '')
    if profile_summary:
        cv_text += f"\n_____________________________ PROFILE SUMMARY _____________________________\n"
        cv_text += f"{profile_summary}\n"
    
    # Skills
    skills = cv_data.get('skills', {})
    technical_skills = skills.get('technical', [])
    professional_skills = skills.get('professional', [])
    
    if technical_skills or professional_skills:
        cv_text += f"\n_____________________________ SKILLS _____________________________\n"
        if technical_skills:
            cv_text += f"Technical Skills:\n"
            for skill in technical_skills:
                cv_text += f"• {skill}\n"
        if professional_skills:
            cv_text += f"Professional Skills:\n"
            for skill in professional_skills:
                cv_text += f"• {skill}\n"
    
    # Work Experience
    experience = cv_data.get('experience', [])
    if experience:
        cv_text += f"\n_____________________________ WORK EXPERIENCE _____________________________\n"
        for exp in experience:
            cv_text += f"{exp.get('job_title', '')} at {exp.get('company', '')}\n"
            cv_text += f"Duration: {exp.get('duration', '')}\n"
            if exp.get('description'):
                cv_text += f"Description: {exp.get('description')}\n"
            if exp.get('achievements'):
                cv_text += f"Achievements:\n"
                for achievement in exp.get('achievements', []):
                    cv_text += f"• {achievement}\n"
            cv_text += "\n"
    
    # Education
    education = cv_data.get('education', [])
    if education:
        cv_text += f"\n_____________________________ EDUCATION _____________________________\n"
        for edu in education:
            cv_text += f"{edu.get('degree', '')}"
            if edu.get('grade'):
                cv_text += f" - {edu.get('grade')}"
            cv_text += f"\nInstitution: {edu.get('institution', '')}"
            if edu.get('year'):
                cv_text += f" ({edu.get('year')})"
            cv_text += "\n\n"
    
    # Projects
    projects = cv_data.get('projects', [])
    if projects:
        cv_text += f"\n_____________________________ PROJECTS _____________________________\n"
        for i, project in enumerate(projects, 1):
            cv_text += f"{i}. {project.get('title', '')}\n"
            if project.get('duration'):
                cv_text += f"   Duration: {project.get('duration')}\n"
            if project.get('description'):
                cv_text += f"   Description: {project.get('description')}\n"
            if project.get('technologies'):
                cv_text += f"   Technologies: {', '.join(project.get('technologies', []))}\n"
            if project.get('highlights'):
                cv_text += f"   Key Highlights:\n"
                for highlight in project.get('highlights', []):
                    cv_text += f"   • {highlight}\n"
            cv_text += "\n"
    
    return cv_text

class BlogRequest(BaseModel):
    project_title: str

@app.post("/blog/generate")
async def generate_blog_post(request: BlogRequest):
    """Generate a LinkedIn blog post for a project by title"""
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Get all projects and find by title
        cursor.execute("SELECT id, project_data FROM manual_projects")
        projects = cursor.fetchall()
        
        matching_project = None
        for project_id, project_json in projects:
            try:
                project_data = json.loads(project_json)
                project_title = project_data.get('title', '').lower()
                search_title = request.project_title.lower()
                
                # Try exact match first, then partial match
                if search_title == project_title or search_title in project_title or project_title in search_title:
                    matching_project = project_data
                    break
            except:
                continue
        
        # If no match found and we have projects, use the first one
        if not matching_project and projects:
            try:
                project_data = json.loads(projects[0][1])
                matching_project = project_data
            except:
                pass
        
        conn.close()
        
        if not matching_project:
            return {
                "success": False,
                "message": "Project not found",
                "blog_content": f"I couldn't find a project matching '{request.project_title}'. Please check the project name and try again.",
                "project_title": request.project_title
            }
        
        # Generate blog post
        blog_content = generate_linkedin_blog(matching_project)
        
        return {
            "success": True,
            "message": "LinkedIn blog generated successfully",
            "blog_content": blog_content,
            "project_title": matching_project.get('title', 'Project')
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": "Error generating blog",
            "blog_content": f"Sorry, I encountered an error while generating the blog: {str(e)}",
            "project_title": request.project_title
        }

def format_cv_with_ai(cv_content: str) -> str:
    """Use AI to format CV content into well-structured sections"""
    try:
        prompt = f"""Format this CV content into a professional, well-structured format with clear sections. Organize the content properly and ensure consistent formatting.

CV Content:
{cv_content}

Please format the CV with:
1. Clear section headers (PROFILE SUMMARY, SKILLS, WORK EXPERIENCE, EDUCATION, PROJECTS)
2. Consistent bullet points and formatting
3. Proper spacing between sections
4. Professional language and structure
5. Remove any duplicate sections or content
6. Ensure all content is relevant and well-organized
7. Place all content under the correct section headers
8. Remove any scattered or misplaced content

Return only the formatted CV content, no additional commentary."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        formatted_content = response.choices[0].message.content.strip()
        return formatted_content
        
    except Exception as e:
        print(f"AI formatting failed: {e}")
        return reorganize_cv_content(cv_content)  # Use fallback reorganization

def reorganize_cv_content(cv_content: str) -> str:
    """Reorganize CV content to ensure proper section placement"""
    try:
        lines = cv_content.split('\n')
        organized_sections = {
            'personal_info': [],
            'profile_summary': [],
            'skills': [],
            'experience': [],
            'education': [],
            'projects': []
        }
        
        current_section = 'personal_info'
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect section headers with more flexible patterns
            if (re.search(r'PROFILE\s+SUMMARY', line_stripped, re.IGNORECASE) or 
                re.search(r'^\s*_+\s*PROFILE\s*_+\s*$', line_stripped, re.IGNORECASE)):
                current_section = 'profile_summary'
                continue
            elif (re.search(r'^\s*_+\s*SKILLS?\s*_+\s*$', line_stripped, re.IGNORECASE) or
                  re.search(r'TECHNICAL\s+SKILLS?', line_stripped, re.IGNORECASE) or
                  re.search(r'PROFESSIONAL\s+SKILLS?', line_stripped, re.IGNORECASE)):
                current_section = 'skills'
                continue
            elif (re.search(r'^\s*_+\s*WORK\s+EXPERIENCE\s*_+\s*$', line_stripped, re.IGNORECASE) or
                  re.search(r'^\s*_+\s*EXPERIENCE\s*_+\s*$', line_stripped, re.IGNORECASE) or
                  re.search(r'^\s*WORK\s+EXPERIENCE\s*$', line_stripped, re.IGNORECASE)):
                current_section = 'experience'
                continue
            elif (re.search(r'^\s*_+\s*EDUCATION\s*_+\s*$', line_stripped, re.IGNORECASE) or
                  re.search(r'^\s*_+\s*EDUCATIONAL\s*_+\s*$', line_stripped, re.IGNORECASE) or
                  re.search(r'^\s*EDUCATION\s*$', line_stripped, re.IGNORECASE)):
                current_section = 'education'
                continue
            elif (re.search(r'^\s*_+\s*PROJECTS?\s*_+\s*$', line_stripped, re.IGNORECASE) or
                  re.search(r'^\s*PROJECTS?\s*$', line_stripped, re.IGNORECASE)):
                current_section = 'projects'
                continue
            
            # Add content to current section (include non-empty lines)
            if line_stripped and current_section:
                organized_sections[current_section].append(line_stripped)
        
        # Rebuild CV with proper structure
        rebuilt_cv = []
        
        # Personal info (first few lines)
        if organized_sections['personal_info']:
            rebuilt_cv.extend(organized_sections['personal_info'][:5])  # Name, contact info
            rebuilt_cv.append('')
        
        # Profile Summary
        if organized_sections['profile_summary']:
            rebuilt_cv.append('_____________________________ PROFILE SUMMARY _____________________________')
            rebuilt_cv.extend(organized_sections['profile_summary'])
            rebuilt_cv.append('')
        
        # Skills
        if organized_sections['skills']:
            rebuilt_cv.append('_____________________________ SKILLS _____________________________')
            rebuilt_cv.extend(organized_sections['skills'])
            rebuilt_cv.append('')
        
        # Work Experience
        if organized_sections['experience']:
            rebuilt_cv.append('_____________________________ WORK EXPERIENCE _____________________________')
            rebuilt_cv.extend(organized_sections['experience'])
            rebuilt_cv.append('')
        
        # Education
        if organized_sections['education']:
            rebuilt_cv.append('_____________________________ EDUCATION _____________________________')
            rebuilt_cv.extend(organized_sections['education'])
            rebuilt_cv.append('')
        
        # Projects
        if organized_sections['projects']:
            rebuilt_cv.append('_____________________________ PROJECTS _____________________________')
            rebuilt_cv.extend(organized_sections['projects'])
            rebuilt_cv.append('')
        
        result = '\n'.join(rebuilt_cv)
        
        # If no sections were found, return original content
        if len(result.strip()) < 100:
            print("Warning: CV reorganization resulted in very short content, returning original")
            return cv_content
            
        return result
        
    except Exception as e:
        print(f"CV reorganization failed: {e}")
        return cv_content

def generate_cv_pdf(cv_content: str, projects: List[dict]) -> BytesIO:
    """Generate a modern, professional PDF using ReportLab 4.4.2"""
    buffer = BytesIO()
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
        from reportlab.lib.colors import HexColor, black, white, Color
        from reportlab.lib.units import inch, cm, mm
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        
        # Create PDF document with modern margins
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=25*mm, leftMargin=25*mm,
                              topMargin=30*mm, bottomMargin=25*mm)
        
        # Get default styles
        styles = getSampleStyleSheet()
        
        # Modern color scheme
        primary_color = HexColor('#1a365d')      # Dark blue
        accent_color = HexColor('#3182ce')       # Blue
        secondary_color = HexColor('#4a5568')    # Gray
        light_gray = HexColor('#f7fafc')         # Light gray
        success_color = HexColor('#38a169')      # Green
        warning_color = HexColor('#d69e2e')      # Yellow
        
        # Enhanced typography styles for ReportLab 4.4.2
        header_style = ParagraphStyle(
            'ModernHeader',
            parent=styles['Heading1'],
            fontSize=32,
            spaceAfter=35,
            alignment=TA_CENTER,
            textColor=primary_color,
            fontName='Helvetica-Bold',
            spaceBefore=0,
            leading=38
        )
        
        section_style = ParagraphStyle(
            'ModernSection',
            parent=styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=30,
            textColor=primary_color,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            leftIndent=0,
            leading=22
        )
        
        body_style = ParagraphStyle(
            'ModernBody',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            fontName='Helvetica',
            textColor=HexColor('#2d3748'),
            leading=16,
            firstLineIndent=0
        )
        
        bullet_style = ParagraphStyle(
            'ModernBullet',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            leftIndent=20,
            fontName='Helvetica',
            textColor=HexColor('#2d3748'),
            leading=16,
            firstLineIndent=0
        )
        
        contact_style = ParagraphStyle(
            'ModernContact',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=5,
            alignment=TA_CENTER,
            fontName='Helvetica',
            textColor=secondary_color,
            leading=16
        )
        
        # Enhanced styles for different content types
        job_title_style = ParagraphStyle(
            'JobTitle',
            parent=styles['Normal'],
            fontSize=14,
            spaceAfter=4,
            fontName='Helvetica-Bold',
            textColor=accent_color,
            leading=18
        )
        
        company_style = ParagraphStyle(
            'Company',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=2,
            fontName='Helvetica-Bold',
            textColor=secondary_color,
            leading=16
        )
        
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            fontName='Helvetica',
            textColor=secondary_color,
            leading=14,
            alignment=TA_RIGHT
        )
        
        skill_style = ParagraphStyle(
            'Skill',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=4,
            fontName='Helvetica',
            textColor=HexColor('#2d3748'),
            leading=16,
            leftIndent=20
        )
        
        # Build PDF content
        story = []
        
        # Parse CV content
        lines = cv_content.split('\n')
        
        # Extract name and contact info
        name = "PROFESSIONAL CV"
        contact_info = []
        sections = []
        current_section = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Skip formatting artifacts
            if line.startswith('📋') or '─' in line or line.startswith('='):
                continue
                
            # First non-empty line is usually the name
            if i == 0 and not any(keyword in line.upper() for keyword in ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS']):
                name = line.upper()
            elif '@' in line or 'http' in line or any(char.isdigit() for char in line):
                # Contact information
                contact_info.append(line)
            elif (line.isupper() and len(line) > 3) or any(keyword in line.upper() for keyword in 
                ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS', 'ABOUT']):
                # Section header
                if current_section:
                    sections.append(current_section)
                current_section = [line]
            else:
                if current_section:
                    current_section.append(line)
                else:
                    sections.append([line])
        
        if current_section:
            sections.append(current_section)
        
        # Add modern header with name
        story.append(Paragraph(name, header_style))
        
        # Add contact information in a clean format
        if contact_info:
            contact_text = " | ".join(contact_info)
            story.append(Paragraph(contact_text, contact_style))
        
        story.append(Spacer(1, 25))
        
        # Add a professional divider
        divider_style = ParagraphStyle(
            'Divider',
            parent=styles['Normal'],
            fontSize=2,
            spaceAfter=25,
            spaceBefore=25,
            alignment=TA_CENTER,
            textColor=accent_color
        )
        story.append(Paragraph("_" * 60, divider_style))
        
        # Process sections with enhanced formatting
        for section in sections:
            if not section:
                continue
                
            section_title = section[0]
            section_content = section[1:] if len(section) > 1 else []
            
            # Add section header with enhanced styling
            section_text = section_title.replace('_', ' ').title()
            story.append(Paragraph(section_text, section_style))
            
            # Add subtle underline for section
            underline_style = ParagraphStyle(
                'Underline',
                parent=styles['Normal'],
                fontSize=1,
                spaceAfter=20,
                spaceBefore=0,
                alignment=TA_LEFT,
                textColor=accent_color
            )
            story.append(Paragraph("_" * 50, underline_style))
            
            # Process section content with smart formatting
            for line in section_content:
                line = line.strip()
                if not line:
                    continue
                
                # Handle different content types
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    # Bullet points
                    clean_line = line[1:].strip()
                    if clean_line:
                        story.append(Paragraph(f"• {clean_line}", bullet_style))
                        
                elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                    # Numbered list
                    story.append(Paragraph(line, bullet_style))
                    
                elif '|' in line and len(line.split('|')) >= 2:
                    # Job entries with company and date
                    parts = line.split('|')
                    if len(parts) >= 3:
                        job_title = parts[0].strip()
                        company = parts[1].strip()
                        date = parts[2].strip()
                        
                        # Create a table for job entries
                        job_data = [[job_title, date]]
                        job_table = Table(job_data, colWidths=[doc.width*0.7, doc.width*0.3])
                        job_table.setStyle(TableStyle([
                            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (0, 0), 14),
                            ('TEXTCOLOR', (0, 0), (0, 0), accent_color),
                            ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
                            ('FONTSIZE', (1, 0), (1, 0), 11),
                            ('TEXTCOLOR', (1, 0), (1, 0), secondary_color),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ]))
                        story.append(job_table)
                        
                        # Add company name
                        if company:
                            story.append(Paragraph(company, company_style))
                        story.append(Spacer(1, 8))
                        
                    else:
                        story.append(Paragraph(line, body_style))
                        
                elif ':' in line and len(line.split(':')) == 2:
                    # Key-value pairs
                    key, value = line.split(':', 1)
                    if key.strip() and value.strip():
                        story.append(Paragraph(f"<b>{key.strip()}:</b> {value.strip()}", body_style))
                    else:
                        story.append(Paragraph(line, body_style))
                        
                else:
                    # Regular content
                    if line and not line.startswith('Generated on'):
                        story.append(Paragraph(line, body_style))
            
            # Add spacing between sections
            story.append(Spacer(1, 15))
        
        # Add modern footer with enhanced styling
        story.append(Spacer(1, 40))
        footer_style = ParagraphStyle(
            'ModernFooter',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=secondary_color,
            fontName='Helvetica',
            leading=12
        )
        
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y')} | CV Updater Platform"
        story.append(Paragraph(footer_text, footer_style))
        
        # Build PDF with enhanced error handling
        try:
            doc.build(story)
            buffer.seek(0)
            print("✅ Modern professional PDF generated successfully with ReportLab 4.4.2")
            return buffer
        except Exception as build_error:
            print(f"PDF build error: {build_error}")
            # Fallback to simpler build
            simple_story = [Paragraph(name, header_style)]
            simple_story.append(Spacer(1, 20))
            simple_story.append(Paragraph(cv_content, body_style))
            doc.build(simple_story)
            buffer.seek(0)
            return buffer
        
    except ImportError as import_error:
        print(f"ReportLab import error: {import_error}")
        print("ReportLab not available, using enhanced text fallback")
        return generate_cv_text_fallback_enhanced(cv_content, buffer)
    except Exception as e:
        print(f"ReportLab PDF generation failed: {e}, using enhanced text fallback")
        return generate_cv_text_fallback_enhanced(cv_content, buffer)

def generate_cv_text_fallback_enhanced(cv_content: str, buffer: BytesIO) -> BytesIO:
    """Generate enhanced formatted text file as PDF fallback"""
    try:
        # Parse CV content for better formatting
        lines = cv_content.split('\n')
        
        # Extract name and contact info
        name = "PROFESSIONAL CV"
        contact_info = []
        sections = []
        current_section = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Skip formatting artifacts
            if line.startswith('📋') or '─' in line or line.startswith('='):
                continue
                
            # First non-empty line is usually the name
            if i == 0 and not any(keyword in line.upper() for keyword in ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS']):
                name = line.upper()
            elif '@' in line or 'http' in line or any(char.isdigit() for char in line):
                # Contact information
                contact_info.append(line)
            elif (line.isupper() and len(line) > 3) or any(keyword in line.upper() for keyword in 
                ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS', 'ABOUT']):
                # Section header
                if current_section:
                    sections.append(current_section)
                current_section = [line]
            else:
                if current_section:
                    current_section.append(line)
                else:
                    sections.append([line])
        
        if current_section:
            sections.append(current_section)
        
        # Create enhanced formatted content
        formatted_content = f"""
{'='*80}
{name:^80}
{'='*80}

"""
        
        # Add contact information
        if contact_info:
            contact_text = " | ".join(contact_info)
            formatted_content += f"{contact_text:^80}\n\n"
        
        # Add sections with modern formatting
        for section in sections:
            if not section:
                continue
                
            section_title = section[0]
            section_content = section[1:] if len(section) > 1 else []
            
            # Format section header
            formatted_content += f"\n{'-'*80}\n"
            formatted_content += f"{section_title.replace('_', ' ').title():^80}\n"
            formatted_content += f"{'-'*80}\n\n"
            
            # Format section content
            for line in section_content:
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    formatted_content += f"  {line}\n"
                elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                    formatted_content += f"  {line}\n"
                elif ':' in line and len(line.split(':')) == 2:
                    key, value = line.split(':', 1)
                    if key.strip() and value.strip():
                        formatted_content += f"  {key.strip()}: {value.strip()}\n"
                    else:
                        formatted_content += f"  {line}\n"
                else:
                    formatted_content += f"  {line}\n"
        
        # Add footer
        formatted_content += f"\n{'='*80}\n"
        formatted_content += f"Generated on {datetime.now().strftime('%B %d, %Y')} | CV Updater Platform\n"
        formatted_content += f"{'='*80}\n"
        
        # Save as text content
        buffer.write(formatted_content.encode('utf-8'))
        buffer.seek(0)
        print("✅ Enhanced CV text document generated successfully")
        return buffer
            
    except Exception as e:
        print(f"Enhanced CV generation error: {e}")
        # Fallback to simple format
        return generate_cv_text_fallback(cv_content, buffer)

def generate_cv_text_fallback(cv_content: str, buffer: BytesIO) -> BytesIO:
    """Generate basic formatted text file as final fallback"""
    try:
        # Simple but clean formatting
        formatted_content = f"""
CURRICULUM VITAE
{'='*60}

{cv_content}

{'='*60}
Generated on {datetime.now().strftime('%B %d, %Y')} | CV Updater Platform
        """
        
        # Save as text content
        buffer.write(formatted_content.encode('utf-8'))
        buffer.seek(0)
        print("✅ Basic CV text document generated successfully")
        return buffer
            
    except Exception as e:
        print(f"CV generation error: {e}")
        # Minimal fallback
        try:
            buffer = BytesIO()
            simple_content = f"CURRICULUM VITAE\n\n{cv_content}\n\nGenerated on {datetime.now().strftime('%B %d, %Y')}"
            buffer.write(simple_content.encode('utf-8'))
            buffer.seek(0)
            return buffer
        except Exception as fallback_error:
            print(f"Fallback CV generation failed: {fallback_error}")
            raise HTTPException(status_code=500, detail="Could not generate CV document. Please try again.")

@app.post("/cv/download")
async def download_cv():
    """Download CV as enhanced PDF with proper formatting."""
    try:
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT current_content, filename FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                raise HTTPException(status_code=404, detail="No active CV found")
            
            cv_content, filename = cv_row
            
            # Generate enhanced PDF
            pdf_bytes = generate_enhanced_pdf(cv_content)
            
            # Create filename for download
            base_name = os.path.splitext(filename)[0] if filename else "cv"
            download_filename = f"{base_name}_updated.pdf"
            
            return Response(
                content=pdf_bytes.getvalue(),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={download_filename}"}
            )
            
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

@app.get("/cv/pdf-preview")
async def get_cv_pdf_preview():
    """Get CV as PDF for preview (not download)."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                raise HTTPException(status_code=404, detail="No active CV found")
            
            cv_content = cv_row[0]
            
            # Clean the CV content before generating PDF
            cv_content = clean_cv_text(cv_content)
            
            # Generate enhanced PDF
            pdf_bytes = generate_enhanced_pdf(cv_content)
            
            # Get the PDF content
            pdf_content = pdf_bytes.getvalue()
            
            # Check if PDF was generated successfully
            if len(pdf_content) == 0:
                print("Warning: Generated PDF is empty, using fallback")
                # Use a simple text-based fallback
                pdf_content = f"CV Content:\n\n{cv_content}".encode('utf-8')
                return Response(
                    content=pdf_content,
                    media_type="text/plain",
                    headers={"Content-Disposition": "inline; filename=cv.txt"}
                )
            
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={"Content-Disposition": "inline; filename=cv.pdf"}
            )
            
    except Exception as e:
        print(f"Error generating PDF preview: {e}")
        # Fallback to text response
        try:
            with get_db_cursor_context() as (cursor, conn):
                cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
                cv_row = cursor.fetchone()
                if cv_row:
                    cv_content = cv_row[0]
                    return Response(
                        content=cv_content.encode('utf-8'),
                        media_type="text/plain",
                        headers={"Content-Disposition": "inline; filename=cv_fallback.txt"}
                    )
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
    try:
        # Generate updated CV with all projects and pending updates
        with get_db_cursor() as (cursor, conn):
            # Get current CV content
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                # If no active CV, get the most recent one
                cursor.execute("SELECT current_content FROM cvs ORDER BY updated_at DESC LIMIT 1")
                cv_row = cursor.fetchone()
            
            if not cv_row:
                raise HTTPException(status_code=404, detail="No CV found. Please upload a CV first.")
            
            current_cv = cv_row[0]
            
            # Check for pending updates and apply them
            cursor.execute("SELECT update_type, content FROM cv_updates WHERE processed = FALSE ORDER BY created_at")
            updates = cursor.fetchall()
            
            if updates:
                # Apply pending updates
                updated_cv = enhance_cv_with_openai(current_cv, updates)
                # Mark updates as processed
                cursor.execute("UPDATE cv_updates SET processed = TRUE")
                # Update CV in database
                cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
                current_cv = updated_cv
            
            # Regenerate CV with current projects to ensure everything is up to date
            final_cv = generate_cv_with_projects(cursor, conn)
            
            # Ensure we have the most complete CV content
            if len(final_cv) > len(current_cv):
                current_cv = final_cv
            
            # Format CV with AI for better structure
            formatted_cv = format_cv_with_ai(current_cv)
            
            # Update the database with the final CV
            cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (formatted_cv,))
            
            # Generate comprehensive PDF file with all content
            pdf_buffer = generate_cv_pdf(formatted_cv, [])
            pdf_content = pdf_buffer.getvalue()
            
            # Determine file type and media type based on content
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Check if we generated an actual PDF (binary content) or text fallback
            try:
                # Try to decode as text to see if it's a text file
                pdf_content.decode('utf-8')
                # If successful, it's a text file
                filename = f"Enhanced_CV_Complete_{timestamp}.txt"
                media_type = "text/plain"
                content_type = "text/plain; charset=utf-8"
                print("📄 Serving complete CV as text file")
            except UnicodeDecodeError:
                # If decode fails, it's binary PDF content
                filename = f"Enhanced_CV_Complete_{timestamp}.pdf"
                media_type = "application/pdf"
                content_type = "application/pdf"
                print("📄 Serving complete CV as PDF file")
            
            return Response(
                content=pdf_content,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename=\"{filename}\"",
                    "Content-Length": str(len(pdf_content)),
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "Content-Type": content_type,
                    "X-Content-Type-Options": "nosniff"
                }
            )
        
    except Exception as e:
        print(f"Error generating complete CV document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading complete CV: {str(e)}")

@app.post("/diagnostics/education-update-test")
async def education_update_test():
    """Simulate an education update and return before/after CV content and update status for diagnostics."""
    try:
        with get_db_cursor() as (cursor, conn):
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            if not cv_row:
                return {"success": False, "message": "No active CV found."}
            before_cv = cv_row[0]
            test_message = "Add MSc in AI at Oxford to my education"
            print("[DIAG] Simulating education update with message:", test_message)
            updated_cv = insert_in_education_section(before_cv, test_message)
            update_made = updated_cv != before_cv
            if update_made:
                cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
                print("[DIAG] Education section updated in DB.")
            else:
                print("[DIAG] No changes made to education section.")
            return {
                "success": True,
                "test_message": test_message,
                "before_cv_excerpt": before_cv[before_cv.lower().find('education'):][:500],
                "after_cv_excerpt": updated_cv[updated_cv.lower().find('education'):][:500],
                "update_made": update_made
            }
    except Exception as e:
        print(f"[DIAG] Error in education update test: {e}")
        return {"success": False, "error": str(e)}

@app.get("/diagnostics/db-cv-dump")
async def db_cv_dump():
    """Return all rows from the cvs table for diagnostics."""
    import sqlite3
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, current_content, updated_at, is_active FROM cvs ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        result = [
            {
                "id": row[0],
                "filename": row[1],
                "current_content": row[2],
                "updated_at": row[3],
                "is_active": bool(row[4])
            }
            for row in rows
        ]
        return JSONResponse(content={"cvs": result})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Vercel handler - add this at the end of the file
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081) 