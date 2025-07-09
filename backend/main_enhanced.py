from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3
import PyPDF2
import docx2txt
from io import BytesIO
import openai
import json
from typing import List, Optional
import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, blue, darkblue
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
from fastapi.responses import Response

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY") 
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
    conn = sqlite3.connect('cv_updater.db', timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
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

init_db()

import threading
import time
from contextlib import contextmanager

# Global database lock
db_lock = threading.RLock()

def get_db_connection():
    """Get database connection with proper timeout and error handling"""
    try:
        conn = sqlite3.connect('cv_updater.db', timeout=60.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")  # Enable WAL mode for better concurrency
        conn.execute("PRAGMA synchronous=NORMAL")  # Better performance
        conn.execute("PRAGMA cache_size=10000")   # Larger cache
        conn.execute("PRAGMA temp_store=memory")  # Use memory for temp tables
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

@contextmanager
def get_db_cursor():
    """Context manager for database operations with automatic cleanup"""
    conn = None
    cursor = None
    try:
        with db_lock:  # Use threading lock
            conn = get_db_connection()
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
    content = file.file.read()
    
    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfFileReader(BytesIO(content))
        text = ""
        for page_num in range(pdf_reader.getNumPages()):
            text += pdf_reader.getPage(page_num).extractText() + "\n"
        return text
    elif file.filename.endswith('.docx'):
        return docx2txt.process(BytesIO(content))
    elif file.filename.endswith('.txt'):
        return content.decode('utf-8')
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

def classify_message(message: str) -> dict:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """Classify messages:
                CV_REQUEST: user wants updated CV ("give me", "show", "updated cv", "generate cv")
                SKILL_UPDATE: adding skills ("learned", "skill", "achieved")
                EXPERIENCE_UPDATE: work experience ("worked", "job", "position")
                EDUCATION_UPDATE: education ("degree", "certification", "course")
                PROJECT_ADD: adding new project ("project", "built", "developed", "created app")
                PROJECT_MODIFY: modifying existing project ("update project", "change project", "modify")
                PROJECT_DELETE: deleting project ("remove project", "delete project")
                PROJECT_LIST: listing projects ("show projects", "list projects", "my projects")
                CV_CLEANUP: user wants to clean up duplicate sections in CV ("clean", "cleanup", "fix", "duplicate", "remove duplicate")
                OTHER: general conversation
                Return JSON: {"category": "CATEGORY", "extracted_info": "info"}"""},
                {"role": "user", "content": message}
            ],
            temperature=0.1,
            max_tokens=150
        )
        return json.loads(response.choices[0].message.content)
    except:
        msg = message.lower()
        # Enhanced pattern matching
        if any(phrase in msg for phrase in ["give me", "updated cv", "show cv", "generate cv", "create cv"]):
            return {"category": "CV_REQUEST", "extracted_info": None}
        elif any(phrase in msg for phrase in ["clean", "cleanup", "fix", "duplicate", "remove duplicate"]):
            return {"category": "CV_CLEANUP", "extracted_info": None}
        elif any(phrase in msg for phrase in ["skill", "learned", "achieved"]):
            return {"category": "SKILL_UPDATE", "extracted_info": message.strip()}
        elif any(phrase in msg for phrase in ["worked", "job", "experience"]):
            return {"category": "EXPERIENCE_UPDATE", "extracted_info": message.strip()}
        elif any(phrase in msg for phrase in ["degree", "certification", "education"]):
            return {"category": "EDUCATION_UPDATE", "extracted_info": message.strip()}
        elif any(phrase in msg for phrase in ["project", "built", "developed", "created", "app", "website", "system"]):
            if any(word in msg for word in ["remove", "delete"]):
                return {"category": "PROJECT_DELETE", "extracted_info": message.strip()}
            elif any(word in msg for word in ["update", "modify", "change", "edit"]):
                return {"category": "PROJECT_MODIFY", "extracted_info": message.strip()}
            elif any(word in msg for word in ["show", "list", "display"]):
                return {"category": "PROJECT_LIST", "extracted_info": message.strip()}
            else:
                return {"category": "PROJECT_ADD", "extracted_info": message.strip()}
        else:
            return {"category": "OTHER", "extracted_info": message.strip()}

def extract_projects_from_cv(cv_content: str) -> List[dict]:
    try:
        prompt = f"""Extract all projects from this CV and return them as a JSON array. Each project should be an object with:
- title: project name
- description: brief description of the project
- technologies: array of technologies used
- duration: timeframe or date
- highlights: array of key achievements/features

CV Content:
{cv_content}

Return ONLY a valid JSON array of projects. If no projects found, return an empty array []."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500
        )
        
        projects_text = response.choices[0].message.content.strip()
        # Clean up the response to ensure it's valid JSON
        if projects_text.startswith('```json'):
            projects_text = projects_text[7:-3]
        elif projects_text.startswith('```'):
            projects_text = projects_text[3:-3]
        
        projects = json.loads(projects_text)
        return projects if isinstance(projects, list) else []
    except Exception as e:
        print(f"Error extracting projects with OpenAI: {e}")
        # Fallback: Pattern-based extraction
        return extract_projects_fallback(cv_content)

def extract_projects_fallback(cv_content: str) -> List[dict]:
    """Fallback method to extract projects using pattern matching"""
    
    projects = []
    cv_lower = cv_content.lower()
    
    # Look for project indicators
    project_patterns = [
        r'(task management.*?application)',
        r'(web application.*?project)',
        r'(project.*?management.*?system)',
        r'(rest api.*?project)',
        r'(e-commerce.*?platform)',
        r'(portfolio.*?website)',
        r'(chat.*?application)',
        r'(dashboard.*?project)',
        r'(mobile.*?app)',
        r'(database.*?project)'
    ]
    
    # Look for technology stacks
    tech_patterns = [
        r'react\.?js', r'javascript', r'html', r'css', r'bootstrap',
        r'fastapi', r'python', r'supabase', r'github', r'git',
        r'node\.?js', r'express', r'mongodb', r'sql', r'postgresql'
    ]
    
    # Extract technologies mentioned in CV
    found_technologies = []
    for pattern in tech_patterns:
        matches = re.findall(pattern, cv_lower)
        found_technologies.extend(matches)
    
    # Clean up and deduplicate technologies
    technologies = list(set([tech.replace('.', '').title() for tech in found_technologies]))
    
    # Look for date patterns
    date_patterns = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[\s,]*(\d{4})'
    dates = re.findall(date_patterns, cv_lower, re.IGNORECASE)
    
    # Check if CV mentions projects or work experience
    if any(keyword in cv_lower for keyword in ['project', 'developed', 'built', 'created', 'implemented']):
        
        # Project 1: Task Management Application (if mentioned)
        if any(keyword in cv_lower for keyword in ['task management', 'web app', 'application']):
            projects.append({
                "title": "Task Management Web Application",
                "description": "Developed a comprehensive web application for task management with features for creating, updating, and managing tasks with deadlines and status tracking.",
                "technologies": [tech for tech in technologies if tech in ['React', 'Javascript', 'Html', 'Css', 'Bootstrap', 'Fastapi', 'Python']],
                "duration": "March 2025 - April 2025" if dates else "Recent Project",
                "highlights": [
                    "Built responsive UI with React.js and Bootstrap",
                    "Implemented REST APIs with FastAPI",
                    "Integrated database for data persistence",
                    "Added user authentication and authorization"
                ]
            })
        
        # Project 2: Full Stack Development (if backend/frontend mentioned)
        if any(keyword in cv_lower for keyword in ['full stack', 'rest api', 'backend', 'frontend']):
            projects.append({
                "title": "Full Stack Web Development Platform",
                "description": "Built a complete web development solution with front-end user interface and back-end API integration, featuring database management and user authentication.",
                "technologies": [tech for tech in technologies if tech in ['React', 'Javascript', 'Fastapi', 'Python', 'Supabase']],
                "duration": "2024 - 2025" if dates else "Ongoing",
                "highlights": [
                    "Developed responsive web applications",
                    "Created RESTful APIs for data management",
                    "Implemented database integration",
                    "Collaborated with team members on version control"
                ]
            })
        
        # Project 3: Database Integration (if database mentioned)
        if any(keyword in cv_lower for keyword in ['database', 'supabase', 'sql', 'data']):
            projects.append({
                "title": "Database Integration & Management System",
                "description": "Designed and implemented database solutions for web applications with focus on data storage, retrieval, and authentication systems.",
                "technologies": [tech for tech in technologies if tech in ['Supabase', 'Python', 'Fastapi', 'Javascript']],
                "duration": "2024" if dates else "Recent",
                "highlights": [
                    "Integrated Supabase for database management",
                    "Implemented data authentication systems",
                    "Optimized database queries for performance",
                    "Ensured data security and backup procedures"
                ]
            })
    
    # Remove duplicates and empty projects
    unique_projects = []
    seen_titles = set()
    for project in projects:
        if project['title'] not in seen_titles and project['technologies']:
            seen_titles.add(project['title'])
            unique_projects.append(project)
    
    return unique_projects[:3]  # Return max 3 projects to avoid duplication

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
        
        response = openai.ChatCompletion.create(
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
        
        response = openai.ChatCompletion.create(
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

def clean_duplicate_project_sections(cv_content: str) -> str:
    """Remove duplicate project sections like ADDITIONAL PROJECTS"""
    lines = cv_content.split('\n')
    cleaned_lines = []
    skip_section = False
    
    for line in lines:
        line_upper = line.upper().strip()
        
        # Check if this is an "ADDITIONAL" section header
        if (line_upper.startswith('ADDITIONAL') and 
            any(keyword in line_upper for keyword in ['PROJECT', 'SKILL', 'EXPERIENCE'])):
            skip_section = True
            continue
        
        # Check if we're starting a new non-additional section
        if (line_upper.isupper() and 
            any(keyword in line_upper for keyword in 
                ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS', 'CERTIFICATION']) and
            not line_upper.startswith('ADDITIONAL')):
            skip_section = False
        
        # Check for "Generated on" footer - stop skipping after it
        if 'Generated on' in line:
            skip_section = False
        
        if not skip_section:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def smart_section_integration(cv_content: str, section_type: str, new_content: List[str]) -> str:
    """Intelligently integrate new content into appropriate sections"""
    try:
        sections = parse_cv_sections(cv_content)
        cv_lines = cv_content.split('\n')
        
        # Find the target section
        if section_type in sections:
            # Append to existing section
            section_info = sections[section_type]
            end_line = section_info['end_line']
            
            # Insert new content before the next section starts
            for i, line in enumerate(reversed(new_content)):
                cv_lines.insert(end_line + 1, line)
        else:
            # Create new section at appropriate location
            section_headers = {
                'skills': 'SKILLS',
                'experience': 'WORK EXPERIENCE', 
                'education': 'EDUCATION',
                'projects': 'PROJECTS'
            }
            
            header = section_headers.get(section_type, section_type.upper())
            full_content = [f"\n{header}"] + new_content + [""]
            
            # Determine best insertion point based on standard CV order
            cv_order = ['skills', 'experience', 'education', 'projects']
            current_index = cv_order.index(section_type) if section_type in cv_order else len(cv_order)
            
            # Find insertion point based on existing sections
            insert_pos = len(cv_lines)
            for i in range(current_index + 1, len(cv_order)):
                next_section = cv_order[i]
                if next_section in sections:
                    insert_pos = sections[next_section]['start_line']
                    break
            
            # Insert new section
            for i, line in enumerate(reversed(full_content)):
                cv_lines.insert(insert_pos, line)
        
        return '\n'.join(cv_lines)
        
    except Exception as e:
        print(f"Error in smart section integration: {e}")
        return cv_content

def generate_cv_with_projects(cursor=None, conn=None) -> str:
    """Generate updated CV with all projects properly integrated"""
    try:
        # Use provided cursor or create new connection
        if cursor is None:
            with get_db_cursor() as (cursor, conn):
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
    
    # If no new projects to add, return original CV
    if not new_projects:
        return original_cv
    
    # Parse CV sections
    sections = parse_cv_sections(original_cv)
    cv_lines = original_cv.split('\n')
    
    # Extract existing projects from the CV text (only from projects section)
    existing_projects = extract_existing_projects_from_cv(original_cv, sections)
    
    # Merge existing projects with new projects (avoid duplicates)
    all_projects = existing_projects.copy()
    
    # Add new projects if they don't already exist
    existing_titles = {p.get('title', '').lower() for p in existing_projects}
    for new_project in new_projects:
        new_title = new_project.get('title', '').lower()
        if new_title not in existing_titles:
            all_projects.append(new_project)
    
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
    
    # Update the projects section intelligently
    if 'projects' in sections:
        # Replace the content of existing projects section
        start_line = sections['projects']['content_start']
        end_line = sections['projects']['end_line']
        
        # Remove old project content but keep the header
        del cv_lines[start_line:end_line + 1]
        
        # Insert updated projects content
        for i, line in enumerate(projects_content):
            cv_lines.insert(start_line + i, line)
    else:
        # Use smart section integration to create new projects section
        updated_cv = smart_section_integration(original_cv, 'projects', projects_content)
        cv_lines = updated_cv.split('\n')
    
    updated_cv = '\n'.join(cv_lines)
    
    # Final cleanup to remove any remaining duplicates
    updated_cv = clean_duplicate_project_sections(updated_cv)
    
    # Update in database
    cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
    
    return updated_cv

def extract_existing_projects_from_cv(cv_content: str, sections: dict) -> List[dict]:
    """Extract existing projects from CV text to preserve them"""
    existing_projects = []
    
    try:
        if 'projects' not in sections:
            return existing_projects
        
        cv_lines = cv_content.split('\n')
        start_line = sections['projects']['content_start']
        end_line = sections['projects']['end_line']
        
        current_project = None
        
        for i in range(start_line, min(end_line + 1, len(cv_lines))):
            line = cv_lines[i].strip()
            
            if not line:
                continue
            
            # Check if this is a project title (starts with number)
            title_match = re.match(r'^\d+\.\s*(.+)', line)
            if title_match:
                # Save previous project if exists
                if current_project:
                    existing_projects.append(current_project)
                
                # Start new project
                current_project = {
                    'title': title_match.group(1).strip(),
                    'description': '',
                    'duration': '',
                    'technologies': [],
                    'highlights': []
                }
            elif current_project:
                # Parse project details
                if line.lower().startswith('duration:'):
                    current_project['duration'] = line[9:].strip()
                elif line.lower().startswith('description:'):
                    current_project['description'] = line[12:].strip()
                elif line.lower().startswith('technologies:'):
                    tech_str = line[13:].strip()
                    current_project['technologies'] = [t.strip() for t in tech_str.split(',') if t.strip()]
                elif line.lower().startswith('key highlights:'):
                    continue  # Next lines will be highlights
                elif line.startswith('•') or line.startswith('-'):
                    # This is a highlight
                    highlight = line[1:].strip()
                    if highlight:
                        current_project['highlights'].append(highlight)
                elif not any(line.lower().startswith(prefix) for prefix in ['duration:', 'description:', 'technologies:']):
                    # If no specific prefix, add to description if not empty
                    if line and not current_project['description']:
                        current_project['description'] = line
        
        # Add last project
        if current_project:
            existing_projects.append(current_project)
        
    except Exception as e:
        print(f"Error extracting existing projects: {e}")
    
    return existing_projects

def parse_cv_sections(cv_content: str) -> dict:
    """Parse CV content to identify sections and their positions"""
    
    sections = {}
    cv_lines = cv_content.split('\n')
    
    # Common section headers patterns
    section_patterns = {
        'skills': [
            r'^\s*SKILLS?\s*$', r'^\s*TECHNICAL\s+SKILLS?\s*$', r'^\s*CORE\s+COMPETENCIES\s*$',
            r'^\s*TECHNOLOGIES\s*$', r'^\s*TECHNICAL\s+COMPETENCIES\s*$'
        ],
        'experience': [
            r'^\s*WORK\s+EXPERIENCE\s*$', r'^\s*EXPERIENCE\s*$', r'^\s*PROFESSIONAL\s+EXPERIENCE\s*$',
            r'^\s*EMPLOYMENT\s+HISTORY\s*$', r'^\s*CAREER\s+HISTORY\s*$'
        ],
        'education': [
            r'^\s*EDUCATION\s*$', r'^\s*EDUCATIONAL\s+BACKGROUND\s*$', r'^\s*ACADEMIC\s+BACKGROUND\s*$',
            r'^\s*QUALIFICATIONS\s*$', r'^\s*ACADEMIC\s+QUALIFICATIONS\s*$'
        ],
        'projects': [
            r'^\s*PROJECTS?\s*$', r'^\s*KEY\s+PROJECTS?\s*$', r'^\s*NOTABLE\s+PROJECTS?\s*$',
            r'^\s*PERSONAL\s+PROJECTS?\s*$', r'^\s*PORTFOLIO\s*$', r'^\s*SELECTED\s+PROJECTS?\s*$',
            r'^\s*MAJOR\s+PROJECTS?\s*$', r'^\s*PROJECT\s+EXPERIENCE\s*$', r'^\s*PROFESSIONAL\s+PROJECTS?\s*$'
        ]
    }
    
    for i, line in enumerate(cv_lines):
        line_upper = line.upper().strip()
        
        # Check for section headers
        for section_type, patterns in section_patterns.items():
            for pattern in patterns:
                if re.match(pattern, line_upper):
                    sections[section_type] = {
                        'start_line': i,
                        'header': line.strip(),
                        'content_start': i + 1
                    }
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
async def upload_cv(file: UploadFile = File(...)):
    try:
        cv_text = extract_text_from_file(file)
        
        with get_db_cursor() as (cursor, conn):
            # Generate a title from filename
            title = file.filename.replace('.pdf', '').replace('.docx', '').replace('.txt', '').replace('_', ' ').title()
            
            # Extract projects from uploaded CV and store them
            try:
                existing_projects = extract_projects_from_cv(cv_text)
                for project in existing_projects:
                    # Check if project already exists to avoid duplicates
                    cursor.execute("SELECT COUNT(*) FROM manual_projects WHERE project_data LIKE ?", 
                                 (f'%{project.get("title", "")}%',))
                    if cursor.fetchone()[0] == 0:
                        cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", 
                                     (json.dumps(project),))
            except Exception as e:
                print(f"Error extracting projects from uploaded CV: {e}")
            
            # Set all other CVs as inactive
            cursor.execute("UPDATE cvs SET is_active = FALSE")
            
            # Insert new CV as active
            cursor.execute('''INSERT INTO cvs (title, filename, original_content, current_content, is_active) 
                             VALUES (?, ?, ?, ?, TRUE)''', 
                          (title, file.filename, cv_text, cv_text))
        
        return JSONResponse(status_code=200, content={
            "message": "CV uploaded successfully! Projects automatically extracted and ready for enhancement.", 
            "filename": file.filename,
            "title": title
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/chat/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        with get_db_cursor() as (cursor, conn):
            cursor.execute("INSERT INTO chat_messages (message, message_type) VALUES (?, ?)", 
                          (request.message, "user"))
        
            classification = classify_message(request.message)
            category = classification.get("category", "OTHER")
            extracted_info = classification.get("extracted_info")
            
            response_text = ""
            
            if category == "CV_REQUEST":
                # Generate CV with projects using existing cursor
                updated_cv = generate_cv_with_projects(cursor, conn)
                response_text = "✅ Generated your enhanced CV with all projects included! Check the CV panel."
                
            elif category == "PROJECT_ADD":
                # Extract project from message and save
                project_data = extract_project_from_message(extracted_info)
                cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", 
                             (json.dumps(project_data),))
                response_text = f"🚀 Added project '{project_data['title']}' successfully! Say 'generate CV' to include it in your CV."
                
            elif category == "PROJECT_LIST":
                # List all projects
                cursor.execute("SELECT id, project_data FROM manual_projects ORDER BY created_at DESC")
                manual_projects = cursor.fetchall()
                
                if manual_projects:
                    response_text = "📂 Your Projects:\n\n"
                    for i, (project_id, project_json) in enumerate(manual_projects, 1):
                        try:
                            project = json.loads(project_json)
                            response_text += f"{i}. {project.get('title', 'Untitled')} (ID: {project_id})\n"
                            response_text += f"   Technologies: {', '.join(project.get('technologies', []))}\n\n"
                        except:
                            pass
                    response_text += "To modify a project, say 'update project [ID]' or 'delete project [ID]'"
                else:
                    response_text = "📭 No projects found. Tell me about a project you've worked on!"
                    
            elif category == "PROJECT_DELETE":
                # Extract project ID from message
                id_match = re.search(r'\b(\d+)\b', extracted_info)
                if id_match:
                    project_id = int(id_match.group(1))
                    cursor.execute("DELETE FROM manual_projects WHERE id = ?", (project_id,))
                    if cursor.rowcount > 0:
                        response_text = f"🗑️ Deleted project with ID {project_id} successfully!"
                    else:
                        response_text = f"❌ Project with ID {project_id} not found."
                else:
                    response_text = "Please specify the project ID to delete (e.g., 'delete project 1')"
                    
            elif category == "PROJECT_MODIFY":
                response_text = "🔧 To modify a project, please specify the project ID and what you want to change. For example: 'Update project 1 - change title to Mobile App'"
                
            elif category in ["SKILL_UPDATE", "EXPERIENCE_UPDATE", "EDUCATION_UPDATE"]:
                update_type = category.replace("_UPDATE", "").lower()
                cursor.execute("INSERT INTO cv_updates (update_type, content, original_message, processed) VALUES (?, ?, ?, ?)", 
                             (update_type, extracted_info, request.message, False))
                response_text = f"💡 Saved your {update_type}! Say 'generate CV' when ready to create updated CV."
                
            elif category == "CV_CLEANUP":
                response_text = "🧹 Cleaning up duplicate sections in your CV. This might take a moment..."
                # Clean up duplicate sections in the current CV content
                cleaned_cv = clean_duplicate_project_sections(generate_cv_with_projects(cursor, conn)) # Regenerate and clean
                cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (cleaned_cv,))
                response_text += "✅ CV cleaned up successfully! Your CV is now free of duplicate sections."
                
            else:
                response_text = """👋 I can help you with:
                
    📋 **CV Management:**
    • "Generate CV" - Create updated CV with projects
    • "Show CV" - Display current CV
    • "Clean CV" - Remove duplicate sections

    🚀 **Project Management:**
    • "I built a React app..." - Add new project
    • "Show my projects" - List all projects  
    • "Delete project 1" - Remove project
    • "Update project 1" - Modify project

    💼 **Profile Updates:**
    • "I learned Python" - Add skills
    • "I worked at..." - Add experience
    • "I got certified in..." - Add education

    Just tell me what you want to add or update! 😊"""
        
            cursor.execute("INSERT INTO chat_messages (message, message_type) VALUES (?, ?)", 
                          (response_text, "bot"))
            
            return ChatResponse(response=response_text, status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/cv/current/", response_model=CVResponse)
async def get_current_cv():
    try:
        with get_db_cursor() as (cursor, conn):
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
            
            cursor.execute("SELECT update_type, content FROM cv_updates WHERE processed = FALSE ORDER BY created_at")
            updates = cursor.fetchall()
            
            if updates:
                updated_cv = enhance_cv_with_openai(current_content, updates)
                cursor.execute("UPDATE cv_updates SET processed = TRUE")
                cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
            else:
                updated_cv = current_content
            
            # Ensure CV is regenerated with current projects only (removes deleted projects)
            updated_cv = generate_cv_with_projects(cursor, conn)
            
            # Format with AI for better presentation
            formatted_cv = format_cv_with_ai(updated_cv)
            
            cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (formatted_cv,))
            
            return CVResponse(content=formatted_cv, filename=filename, last_updated=updated_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# New CV Management Endpoints
@app.get("/cvs/")
async def list_all_cvs():
    """Get list of all CVs with metadata"""
    try:
        with get_db_cursor() as (cursor, conn):
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
        
        # Generate filename from title
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_title}_{timestamp}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Content-Length": str(len(pdf_content)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Content-Type": "application/pdf",
                "X-Content-Type-Options": "nosniff"
            }
        )
        
    except Exception as e:
        print(f"Error generating CV PDF: {str(e)}")
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
        with get_db_cursor() as (cursor, conn):
            # First check for manually created projects
            cursor.execute("SELECT project_data FROM manual_projects ORDER BY created_at DESC")
            manual_projects = cursor.fetchall()
            
            projects = []
            for project_row in manual_projects:
                try:
                    project_data = json.loads(project_row[0])
                    projects.append(project_data)
                except:
                    pass
            
            # Only return manual projects from database to ensure deleted projects are excluded
            # Note: We skip CV extraction to avoid showing deleted projects
            
            return {"projects": projects, "total_count": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/projects/")
async def create_project(project: ProjectRequest):
    try:
        with get_db_cursor() as (cursor, conn):
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
            
            return {"message": "Project created successfully", "project": project_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.put("/projects/{project_id}")
async def update_project(project_id: int, project: ProjectRequest):
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
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
        
        conn.commit()
        conn.close()
        
        return {"message": "Project updated successfully", "project": project_data}
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

@app.get("/projects/list")
async def list_projects_with_ids():
    try:
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
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
        
        conn.close()
        
        return {"projects": projects, "total_count": len(projects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/cv/cleanup")
async def cleanup_cv():
    """Clean up duplicate sections in the CV"""
    try:
        with get_db_cursor() as (cursor, conn):
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
        with get_db_cursor() as (cursor, conn):
            updated_cv = generate_cv_with_projects(cursor, conn)
            return {"message": "CV generated successfully", "cv_content": updated_cv}
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

        response = openai.ChatCompletion.create(
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
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Get project data
        cursor.execute("SELECT project_data FROM manual_projects WHERE id = ?", (project_id,))
        project_row = cursor.fetchone()
        
        if not project_row:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_data = json.loads(project_row[0])
        conn.close()
        
        # Generate blog post
        blog_content = generate_linkedin_blog(project_data)
        
        return {
            "message": "LinkedIn blog generated successfully",
            "blog_content": blog_content,
            "project_title": project_data.get('title', 'Project')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating blog: {str(e)}")

@app.post("/projects/blog")
async def generate_project_blog_by_title():
    """Generate a LinkedIn blog post for a project by title (for chatbot)"""
    try:
        from fastapi import Request
        
        request_body = await request.json() if hasattr(request, 'json') else {}
        project_title = request_body.get('project_title', '').lower()
        
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
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
        
        conn.close()
        
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
            cv_text += f"Technical Skills: {' | '.join(technical_skills)}\n"
        if professional_skills:
            cv_text += f"Professional Skills: {' | '.join(professional_skills)}\n"
    
    # Work Experience
    experience = cv_data.get('experience', [])
    if experience:
        cv_text += f"\n_____________________________ WORK EXPERIENCE _____________________________\n"
        for exp in experience:
            cv_text += f"{exp.get('job_title', '')} {exp.get('company', '')} | {exp.get('duration', '')}\n"
            if exp.get('description'):
                cv_text += f"{exp.get('description')}\n"
            if exp.get('achievements'):
                for achievement in exp.get('achievements', []):
                    cv_text += f"• {achievement}\n"
            cv_text += "\n"
    
    # Education
    education = cv_data.get('education', [])
    if education:
        cv_text += f"_____________________________ EDUCATION _____________________________\n"
        for edu in education:
            cv_text += f"{edu.get('degree', '')}"
            if edu.get('grade'):
                cv_text += f" {edu.get('grade')}"
            cv_text += f", from {edu.get('institution', '')}"
            if edu.get('year'):
                cv_text += f" ({edu.get('year')})"
            cv_text += "\n"
    
    # Projects
    projects = cv_data.get('projects', [])
    if projects:
        cv_text += f"\nPROJECTS\n"
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

Return only the formatted CV content, no additional commentary."""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        
        formatted_content = response.choices[0].message.content.strip()
        return formatted_content
        
    except Exception as e:
        print(f"AI formatting failed: {e}")
        return cv_content  # Return original if AI fails

def generate_cv_pdf(cv_content: str, projects: List[dict]) -> BytesIO:
    """Generate a modern, professional PDF CV with all projects"""
    buffer = BytesIO()
    
    try:
        # Create custom page template with margins
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        # Create custom styles
        styles = getSampleStyleSheet()
        
        # Custom header style
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#2C3E50'),
            fontName='Helvetica-Bold'
        )
        
        # Custom section header style
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            spaceBefore=15,
            textColor=HexColor('#34495E'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=HexColor('#3498DB'),
            borderPadding=5,
            backColor=HexColor('#ECF0F1')
        )
        
        # Custom content style
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=10,
            fontName='Helvetica'
        )
        
        # Custom project title style
        project_title_style = ParagraphStyle(
            'ProjectTitle',
            parent=styles['Normal'],
            fontSize=13,
            spaceAfter=4,
            spaceBefore=8,
            textColor=HexColor('#2980B9'),
            fontName='Helvetica-Bold'
        )
        
        # Custom tech style
        tech_style = ParagraphStyle(
            'TechStyle',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            textColor=HexColor('#7F8C8D'),
            fontName='Helvetica-Oblique'
        )
        
        story = []
        
        # Extract name from CV for header
        cv_lines = cv_content.strip().split('\n')
        name = "Professional CV"
        for line in cv_lines[:5]:  # Check first 5 lines for name
            if line.strip() and not any(keyword.lower() in line.lower() for keyword in 
                ['phone', 'email', 'address', 'cv', 'curriculum', 'vitae', 'resume']):
                name = line.strip()
                break
        
        # Add professional header
        story.append(Paragraph(name, header_style))
        story.append(Spacer(1, 10))
        
        # Parse CV content into sections
        current_section = None
        section_content = []
        sections = {}
        
        for line in cv_lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            is_section_header = (
                line.isupper() or 
                any(keyword in line.upper() for keyword in 
                    ['PERSONAL', 'PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 
                     'EDUCATION', 'PROJECTS', 'ACHIEVEMENTS', 'CERTIFICATIONS', 'CONTACT'])
            )
            
            if is_section_header:
                # Save previous section
                if current_section and section_content:
                    sections[current_section] = section_content
                
                # Start new section
                current_section = line
                section_content = []
            else:
                if current_section:
                    section_content.append(line)
        
        # Save last section
        if current_section and section_content:
            sections[current_section] = section_content
        
        # Add sections in logical order
        section_order = ['PERSONAL INFORMATION', 'CONTACT INFORMATION', 'CONTACT', 'PROFILE', 
                        'SUMMARY', 'PROFESSIONAL SUMMARY', 'SKILLS', 'TECHNICAL SKILLS', 
                        'EXPERIENCE', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 
                        'EDUCATION', 'CERTIFICATIONS', 'ACHIEVEMENTS', 'PROJECTS']
        
        # Add sections that exist in the CV
        added_sections = set()
        for section_name in section_order:
            for cv_section, content in sections.items():
                if (section_name.lower() in cv_section.lower() and 
                    cv_section not in added_sections and 
                    not cv_section.upper().startswith('ADDITIONAL')):  # Skip ADDITIONAL sections
                    story.append(Paragraph(cv_section, section_style))
                    
                    for item in content:
                        if item.strip():
                            # Clean up formatting
                            clean_item = item.replace('•', '').replace('-', '').strip()
                            if clean_item:
                                story.append(Paragraph(f"• {clean_item}", content_style))
                    
                    story.append(Spacer(1, 8))
                    added_sections.add(cv_section)
                    break
        
        # Add any remaining sections (but skip ADDITIONAL sections)
        for cv_section, content in sections.items():
            if (cv_section not in added_sections and 
                not cv_section.upper().startswith('ADDITIONAL')):  # Skip ADDITIONAL sections
                story.append(Paragraph(cv_section, section_style))
                
                for item in content:
                    if item.strip():
                        clean_item = item.replace('•', '').replace('-', '').strip()
                        if clean_item:
                            story.append(Paragraph(f"• {clean_item}", content_style))
                
                story.append(Spacer(1, 8))
        
        # Add projects section if we have manual projects
        if projects:
            # Note: Projects are already integrated into the CV content, but we can enhance the PDF display
            # Don't add "ADDITIONAL PROJECTS" - projects are already part of the main content
            pass
        
        # Add professional footer
        story.append(Spacer(1, 20))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=HexColor('#7F8C8D'),
            fontName='Helvetica-Oblique'
        )
        
        timestamp = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Generated on {timestamp} | CV Updater Platform", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        print("Modern PDF CV generated successfully")
        return buffer
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        # Fallback to basic PDF
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            story.append(Paragraph("CURRICULUM VITAE", styles['Title']))
            story.append(Spacer(1, 20))
            
            # Add CV content with basic formatting
            lines = cv_content.strip().split('\n')
            for line in lines:
                if line.strip():
                    if line.isupper():
                        story.append(Paragraph(f"<b>{line}</b>", styles['Heading2']))
                    else:
                        story.append(Paragraph(line, styles['Normal']))
            
            # Add projects
            if projects:
                story.append(Spacer(1, 15))
                story.append(Paragraph("<b>PROJECTS</b>", styles['Heading2']))
                for project in projects:
                    story.append(Paragraph(f"<b>{project.get('title', 'Project')}</b>", styles['Normal']))
                    if project.get('description'):
                        story.append(Paragraph(project['description'], styles['Normal']))
            
            doc.build(story)
            buffer.seek(0)
            print("Basic fallback PDF generated")
            return buffer
            
        except Exception as fallback_error:
            print(f"Fallback PDF generation failed: {fallback_error}")
            # Create minimal valid PDF
            buffer = BytesIO()
            buffer.write(b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000125 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n196\n%%EOF')
            buffer.seek(0)
            return buffer

@app.post("/cv/download")
async def download_cv():
    try:
        # Generate updated CV with all projects and pending updates
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Get current CV content
        cursor.execute("SELECT current_content FROM cvs LIMIT 1")
        cv_row = cursor.fetchone()
        
        if not cv_row:
            raise HTTPException(status_code=404, detail="No CV found. Please upload a CV first.")
        
        current_cv = cv_row[0]
        
        # Check for pending updates
        cursor.execute("SELECT update_type, content FROM cv_updates WHERE processed = FALSE ORDER BY created_at")
        updates = cursor.fetchall()
        
        if updates:
            # Apply pending updates
            updated_cv = enhance_cv_with_openai(current_cv, updates)
            # Mark updates as processed
            cursor.execute("UPDATE cv_updates SET processed = TRUE")
            # Update CV in database
            cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (updated_cv,))
        else:
            updated_cv = current_cv
        
        # Regenerate CV with current projects to ensure everything is up to date
        updated_cv = generate_cv_with_projects()
        
        # Format CV with AI for better structure
        formatted_cv = format_cv_with_ai(updated_cv)
        
        # Update the database with the clean CV
        cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (formatted_cv,))
        
        conn.commit()
        conn.close()
        
        # Generate PDF file - don't pass projects since they're already in CV content
        pdf_buffer = generate_cv_pdf(formatted_cv, [])  # Empty list prevents duplication
        pdf_content = pdf_buffer.getvalue()
        
        # Generate a proper filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Professional_CV_{timestamp}.pdf"
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Content-Length": str(len(pdf_content)),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "Content-Type": "application/pdf",
                "X-Content-Type-Options": "nosniff"
            }
        )
        
    except Exception as e:
        print(f"Error generating CV PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading CV: {str(e)}")

# Vercel handler - add this at the end of the file
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 