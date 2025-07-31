from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
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
import io
from contextlib import contextmanager
from typing import List, Optional, Dict
from datetime import datetime
from contextlib import asynccontextmanager

# Import database connection
try:
    from db import get_db_cursor
    USE_SUPABASE = False  # Temporarily using SQLite
    print("✅ Using SQLite database (temporary)")
except ImportError:
    print("❌ ERROR: db.py not found. Please ensure the database configuration file exists.")
    raise ImportError("Database configuration file (db.py) is required")

# Comprehensive Section Detection Patterns - Exhaustive CV Section Headings
SECTION_PATTERNS = {
    # Personal & Contact Information
    "contact": [
        r"^CONTACT\s+INFORMATION$", r"^CONTACT\s+DETAILS$", r"^PERSONAL\s+INFORMATION$", r"^PROFILE$", r"^BIO$", r"^SUMMARY$",
        r"^PERSONAL\s+SUMMARY$", r"^ABOUT\s+ME$", r"^PERSONAL\s+PROFILE$", r"^CANDIDATE\s+PROFILE$", r"^CAREER\s+OVERVIEW$",
        r"^EXECUTIVE\s+SUMMARY$", r"^CAREER\s+PROFILE$", r"^SNAPSHOT$", r"^RESUME\s+SUMMARY$", r"^STATEMENT\s+OF\s+PURPOSE$",
        r"^[_\-=\s]*CONTACT\s+INFORMATION[_\-=\s]*$", r"^[_\-=\s]*CONTACT\s+DETAILS[_\-=\s]*$", r"^[_\-=\s]*PERSONAL\s+INFORMATION[_\-=\s]*$",
        r"^[_\-=\s]*PROFILE[_\-=\s]*$", r"^[_\-=\s]*BIO[_\-=\s]*$", r"^[_\-=\s]*SUMMARY[_\-=\s]*$", r"^[_\-=\s]*PERSONAL\s+SUMMARY[_\-=\s]*$",
        r"^[_\-=\s]*ABOUT\s+ME[_\-=\s]*$", r"^[_\-=\s]*PERSONAL\s+PROFILE[_\-=\s]*$", r"^[_\-=\s]*CANDIDATE\s+PROFILE[_\-=\s]*$",
        r"^[_\-=\s]*CAREER\s+OVERVIEW[_\-=\s]*$", r"^[_\-=\s]*EXECUTIVE\s+SUMMARY[_\-=\s]*$", r"^[_\-=\s]*CAREER\s+PROFILE[_\-=\s]*$",
        r"^[_\-=\s]*SNAPSHOT[_\-=\s]*$", r"^[_\-=\s]*RESUME\s+SUMMARY[_\-=\s]*$", r"^[_\-=\s]*STATEMENT\s+OF\s+PURPOSE[_\-=\s]*$"
    ],
    
    # Objective / Goal
    "objective": [
        r"^OBJECTIVE$", r"^CAREER\s+OBJECTIVE$", r"^PROFESSIONAL\s+OBJECTIVE$", r"^EMPLOYMENT\s+OBJECTIVE$",
        r"^CAREER\s+GOAL$", r"^PERSONAL\s+OBJECTIVE$",
        r"^[_\-=\s]*OBJECTIVE[_\-=\s]*$", r"^[_\-=\s]*CAREER\s+OBJECTIVE[_\-=\s]*$", r"^[_\-=\s]*PROFESSIONAL\s+OBJECTIVE[_\-=\s]*$",
        r"^[_\-=\s]*EMPLOYMENT\s+OBJECTIVE[_\-=\s]*$", r"^[_\-=\s]*CAREER\s+GOAL[_\-=\s]*$", r"^[_\-=\s]*PERSONAL\s+OBJECTIVE[_\-=\s]*$"
    ],
    
    # Professional Experience
    "experience": [
        r"^WORK\s+EXPERIENCE$", r"^PROFESSIONAL\s+EXPERIENCE$", r"^EXPERIENCE$", r"^EMPLOYMENT\s+HISTORY$",
        r"^JOB\s+HISTORY$", r"^CAREER\s+HISTORY$", r"^CAREER\s+EXPERIENCE$", r"^WORK\s+HISTORY$", r"^RELEVANT\s+EXPERIENCE$",
        r"^FREELANCE\s+EXPERIENCE$", r"^INDUSTRY\s+EXPERIENCE$", r"^INTERNSHIPS$", r"^INTERNSHIP\s+EXPERIENCE$",
        r"^PRACTICAL\s+EXPERIENCE$", r"^PROJECT\s+EXPERIENCE$", r"^CONSULTING\s+EXPERIENCE$", r"^FIELD\s+WORK$",
        r"^[_\-=\s]*WORK\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*PROFESSIONAL\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*EXPERIENCE[_\-=\s]*$",
        r"^[_\-=\s]*EMPLOYMENT\s+HISTORY[_\-=\s]*$", r"^[_\-=\s]*JOB\s+HISTORY[_\-=\s]*$", r"^[_\-=\s]*CAREER\s+HISTORY[_\-=\s]*$",
        r"^[_\-=\s]*CAREER\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*WORK\s+HISTORY[_\-=\s]*$", r"^[_\-=\s]*RELEVANT\s+EXPERIENCE[_\-=\s]*$",
        r"^[_\-=\s]*FREELANCE\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*INDUSTRY\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*INTERNSHIPS[_\-=\s]*$",
        r"^[_\-=\s]*INTERNSHIP\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*PRACTICAL\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*PROJECT\s+EXPERIENCE[_\-=\s]*$",
        r"^[_\-=\s]*CONSULTING\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*FIELD\s+WORK[_\-=\s]*$"
    ],
    
    # Education & Academics
    "education": [
        r"^EDUCATION$", r"^ACADEMIC\s+BACKGROUND$", r"^EDUCATIONAL\s+BACKGROUND$", r"^ACADEMIC\s+QUALIFICATIONS$",
        r"^ACADEMIC\s+HISTORY$", r"^EDUCATION\s+&\s+TRAINING$", r"^DEGREES$", r"^QUALIFICATIONS$", r"^SCHOOLING$",
        r"^ACADEMIC\s+PROFILE$", r"^CERTIFICATIONS\s+AND\s+EDUCATION$", r"^EDUCATIONAL\s+EXPERIENCE$",
        r"^[_\-=\s]*EDUCATION[_\-=\s]*$", r"^[_\-=\s]*ACADEMIC\s+BACKGROUND[_\-=\s]*$", r"^[_\-=\s]*EDUCATIONAL\s+BACKGROUND[_\-=\s]*$",
        r"^[_\-=\s]*ACADEMIC\s+QUALIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*ACADEMIC\s+HISTORY[_\-=\s]*$", r"^[_\-=\s]*EDUCATION\s+&\s+TRAINING[_\-=\s]*$",
        r"^[_\-=\s]*DEGREES[_\-=\s]*$", r"^[_\-=\s]*QUALIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*SCHOOLING[_\-=\s]*$",
        r"^[_\-=\s]*ACADEMIC\s+PROFILE[_\-=\s]*$", r"^[_\-=\s]*CERTIFICATIONS\s+AND\s+EDUCATION[_\-=\s]*$", r"^[_\-=\s]*EDUCATIONAL\s+EXPERIENCE[_\-=\s]*$"
    ],
    
    # Skills
    "skills": [
        r"^SKILLS$", r"^TECHNICAL\s+SKILLS$", r"^HARD\s+SKILLS$", r"^SOFT\s+SKILLS$", r"^CORE\s+SKILLS$", r"^KEY\s+SKILLS$",
        r"^TRANSFERABLE\s+SKILLS$", r"^FUNCTIONAL\s+SKILLS$", r"^COMPETENCIES$", r"^AREAS\s+OF\s+EXPERTISE$",
        r"^AREAS\s+OF\s+KNOWLEDGE$", r"^SKILL\s+HIGHLIGHTS$", r"^SKILLS\s+SUMMARY$", r"^LANGUAGE\s+SKILLS$", r"^IT\s+SKILLS$",
        r"^[_\-=\s]*SKILLS[_\-=\s]*$", r"^[_\-=\s]*TECHNICAL\s+SKILLS[_\-=\s]*$", r"^[_\-=\s]*HARD\s+SKILLS[_\-=\s]*$",
        r"^[_\-=\s]*SOFT\s+SKILLS[_\-=\s]*$", r"^[_\-=\s]*CORE\s+SKILLS[_\-=\s]*$", r"^[_\-=\s]*KEY\s+SKILLS[_\-=\s]*$",
        r"^[_\-=\s]*TRANSFERABLE\s+SKILLS[_\-=\s]*$", r"^[_\-=\s]*FUNCTIONAL\s+SKILLS[_\-=\s]*$", r"^[_\-=\s]*COMPETENCIES[_\-=\s]*$",
        r"^[_\-=\s]*AREAS\s+OF\s+EXPERTISE[_\-=\s]*$", r"^[_\-=\s]*AREAS\s+OF\s+KNOWLEDGE[_\-=\s]*$", r"^[_\-=\s]*SKILL\s+HIGHLIGHTS[_\-=\s]*$",
        r"^[_\-=\s]*SKILLS\s+SUMMARY[_\-=\s]*$", r"^[_\-=\s]*LANGUAGE\s+SKILLS[_\-=\s]*$", r"^[_\-=\s]*IT\s+SKILLS[_\-=\s]*$"
    ],
    
    # Certifications & Training
    "certifications": [
        r"^CERTIFICATIONS$", r"^LICENSES$", r"^COURSES$", r"^ONLINE\s+COURSES$", r"^CERTIFICATIONS\s+&\s+LICENSES$",
        r"^CREDENTIALS$", r"^PROFESSIONAL\s+CERTIFICATIONS$", r"^TECHNICAL\s+CERTIFICATIONS$", r"^SPECIALIZED\s+TRAINING$",
        r"^TRAINING\s+&\s+DEVELOPMENT$", r"^COMPLETED\s+COURSES$",
        r"^[_\-=\s]*CERTIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*LICENSES[_\-=\s]*$", r"^[_\-=\s]*COURSES[_\-=\s]*$",
        r"^[_\-=\s]*ONLINE\s+COURSES[_\-=\s]*$", r"^[_\-=\s]*CERTIFICATIONS\s+&\s+LICENSES[_\-=\s]*$", r"^[_\-=\s]*CREDENTIALS[_\-=\s]*$",
        r"^[_\-=\s]*PROFESSIONAL\s+CERTIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*TECHNICAL\s+CERTIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*SPECIALIZED\s+TRAINING[_\-=\s]*$",
        r"^[_\-=\s]*TRAINING\s+&\s+DEVELOPMENT[_\-=\s]*$", r"^[_\-=\s]*COMPLETED\s+COURSES[_\-=\s]*$"
    ],
    
    # Projects
    "projects": [
        r"^PROJECTS$", r"^KEY\s+PROJECTS$", r"^PROJECT\s+PORTFOLIO$", r"^MAJOR\s+PROJECTS$", r"^TECHNICAL\s+PROJECTS$",
        r"^CLIENT\s+PROJECTS$", r"^NOTABLE\s+PROJECTS$", r"^FREELANCE\s+PROJECTS$", r"^PROJECT\s+HIGHLIGHTS$",
        r"^RESEARCH\s+PROJECTS$", r"^CAPSTONE\s+PROJECT$",
        r"^[_\-=\s]*PROJECTS[_\-=\s]*$", r"^[_\-=\s]*KEY\s+PROJECTS[_\-=\s]*$", r"^[_\-=\s]*PROJECT\s+PORTFOLIO[_\-=\s]*$",
        r"^[_\-=\s]*MAJOR\s+PROJECTS[_\-=\s]*$", r"^[_\-=\s]*TECHNICAL\s+PROJECTS[_\-=\s]*$", r"^[_\-=\s]*CLIENT\s+PROJECTS[_\-=\s]*$",
        r"^[_\-=\s]*NOTABLE\s+PROJECTS[_\-=\s]*$", r"^[_\-=\s]*FREELANCE\s+PROJECTS[_\-=\s]*$", r"^[_\-=\s]*PROJECT\s+HIGHLIGHTS[_\-=\s]*$",
        r"^[_\-=\s]*RESEARCH\s+PROJECTS[_\-=\s]*$", r"^[_\-=\s]*CAPSTONE\s+PROJECT[_\-=\s]*$"
    ],
    
    # Research & Academic Work
    "research": [
        r"^RESEARCH$", r"^RESEARCH\s+EXPERIENCE$", r"^PUBLICATIONS$", r"^PAPERS$", r"^ACADEMIC\s+WORK$", r"^RESEARCH\s+PAPERS$",
        r"^THESES$", r"^DISSERTATIONS$", r"^CONFERENCE\s+PRESENTATIONS$", r"^PRESENTATIONS$", r"^ACADEMIC\s+CONTRIBUTIONS$",
        r"^RESEARCH\s+HIGHLIGHTS$", r"^SCHOLARLY\s+WORK$",
        r"^[_\-=\s]*RESEARCH[_\-=\s]*$", r"^[_\-=\s]*RESEARCH\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*PUBLICATIONS[_\-=\s]*$",
        r"^[_\-=\s]*PAPERS[_\-=\s]*$", r"^[_\-=\s]*ACADEMIC\s+WORK[_\-=\s]*$", r"^[_\-=\s]*RESEARCH\s+PAPERS[_\-=\s]*$",
        r"^[_\-=\s]*THESES[_\-=\s]*$", r"^[_\-=\s]*DISSERTATIONS[_\-=\s]*$", r"^[_\-=\s]*CONFERENCE\s+PRESENTATIONS[_\-=\s]*$",
        r"^[_\-=\s]*PRESENTATIONS[_\-=\s]*$", r"^[_\-=\s]*ACADEMIC\s+CONTRIBUTIONS[_\-=\s]*$", r"^[_\-=\s]*RESEARCH\s+HIGHLIGHTS[_\-=\s]*$",
        r"^[_\-=\s]*SCHOLARLY\s+WORK[_\-=\s]*$"
    ],
    
    # Awards & Achievements
    "achievements": [
        r"^AWARDS$", r"^HONORS$", r"^HONORS\s+&\s+AWARDS$", r"^ACHIEVEMENTS$", r"^NOTABLE\s+ACHIEVEMENTS$",
        r"^CAREER\s+ACHIEVEMENTS$", r"^DISTINCTIONS$", r"^RECOGNITIONS$", r"^SCHOLARSHIPS$", r"^FELLOWSHIPS$",
        r"^ACADEMIC\s+AWARDS$",
        r"^[_\-=\s]*AWARDS[_\-=\s]*$", r"^[_\-=\s]*HONORS[_\-=\s]*$", r"^[_\-=\s]*HONORS\s+&\s+AWARDS[_\-=\s]*$",
        r"^[_\-=\s]*ACHIEVEMENTS[_\-=\s]*$", r"^[_\-=\s]*NOTABLE\s+ACHIEVEMENTS[_\-=\s]*$", r"^[_\-=\s]*CAREER\s+ACHIEVEMENTS[_\-=\s]*$",
        r"^[_\-=\s]*DISTINCTIONS[_\-=\s]*$", r"^[_\-=\s]*RECOGNITIONS[_\-=\s]*$", r"^[_\-=\s]*SCHOLARSHIPS[_\-=\s]*$",
        r"^[_\-=\s]*FELLOWSHIPS[_\-=\s]*$", r"^[_\-=\s]*ACADEMIC\s+AWARDS[_\-=\s]*$"
    ],
    
    # Leadership & Activities
    "leadership": [
        r"^LEADERSHIP\s+EXPERIENCE$", r"^LEADERSHIP\s+ROLES$", r"^ACTIVITIES$", r"^STUDENT\s+ACTIVITIES$",
        r"^CAMPUS\s+INVOLVEMENT$", r"^PROFESSIONAL\s+ACTIVITIES$", r"^ORGANIZATIONAL\s+INVOLVEMENT$",
        r"^LEADERSHIP\s+&\s+INVOLVEMENT$",
        r"^[_\-=\s]*LEADERSHIP\s+EXPERIENCE[_\-=\s]*$", r"^[_\-=\s]*LEADERSHIP\s+ROLES[_\-=\s]*$", r"^[_\-=\s]*ACTIVITIES[_\-=\s]*$",
        r"^[_\-=\s]*STUDENT\s+ACTIVITIES[_\-=\s]*$", r"^[_\-=\s]*CAMPUS\s+INVOLVEMENT[_\-=\s]*$", r"^[_\-=\s]*PROFESSIONAL\s+ACTIVITIES[_\-=\s]*$",
        r"^[_\-=\s]*ORGANIZATIONAL\s+INVOLVEMENT[_\-=\s]*$", r"^[_\-=\s]*LEADERSHIP\s+&\s+INVOLVEMENT[_\-=\s]*$"
    ],
    
    # Volunteer / Community Involvement
    "volunteer": [
        r"^VOLUNTEER\s+WORK$", r"^VOLUNTEERING$", r"^COMMUNITY\s+SERVICE$", r"^CIVIC\s+ENGAGEMENT$",
        r"^SOCIAL\s+INVOLVEMENT$", r"^COMMUNITY\s+INVOLVEMENT$", r"^CHARITABLE\s+WORK$", r"^PRO\s+BONO\s+WORK$",
        r"^[_\-=\s]*VOLUNTEER\s+WORK[_\-=\s]*$", r"^[_\-=\s]*VOLUNTEERING[_\-=\s]*$", r"^[_\-=\s]*COMMUNITY\s+SERVICE[_\-=\s]*$",
        r"^[_\-=\s]*CIVIC\s+ENGAGEMENT[_\-=\s]*$", r"^[_\-=\s]*SOCIAL\s+INVOLVEMENT[_\-=\s]*$", r"^[_\-=\s]*COMMUNITY\s+INVOLVEMENT[_\-=\s]*$",
        r"^[_\-=\s]*CHARITABLE\s+WORK[_\-=\s]*$", r"^[_\-=\s]*PRO\s+BONO\s+WORK[_\-=\s]*$"
    ],
    
    # Languages
    "languages": [
        r"^LANGUAGES$", r"^LANGUAGE\s+PROFICIENCY$", r"^SPOKEN\s+LANGUAGES$", r"^FOREIGN\s+LANGUAGES$",
        r"^[_\-=\s]*LANGUAGES[_\-=\s]*$", r"^[_\-=\s]*LANGUAGE\s+PROFICIENCY[_\-=\s]*$", r"^[_\-=\s]*SPOKEN\s+LANGUAGES[_\-=\s]*$",
        r"^[_\-=\s]*FOREIGN\s+LANGUAGES[_\-=\s]*$"
    ],
    
    # Tools & Technologies
    "technologies": [
        r"^TOOLS$", r"^TECHNOLOGIES$", r"^SOFTWARE$", r"^PROGRAMMING\s+LANGUAGES$", r"^FRAMEWORKS$", r"^PLATFORMS$",
        r"^IT\s+PROFICIENCY$", r"^SOFTWARE\s+PROFICIENCY$", r"^SYSTEMS$", r"^ENVIRONMENTS$",
        r"^[_\-=\s]*TOOLS[_\-=\s]*$", r"^[_\-=\s]*TECHNOLOGIES[_\-=\s]*$", r"^[_\-=\s]*SOFTWARE[_\-=\s]*$",
        r"^[_\-=\s]*PROGRAMMING\s+LANGUAGES[_\-=\s]*$", r"^[_\-=\s]*FRAMEWORKS[_\-=\s]*$", r"^[_\-=\s]*PLATFORMS[_\-=\s]*$",
        r"^[_\-=\s]*IT\s+PROFICIENCY[_\-=\s]*$", r"^[_\-=\s]*SOFTWARE\s+PROFICIENCY[_\-=\s]*$", r"^[_\-=\s]*SYSTEMS[_\-=\s]*$",
        r"^[_\-=\s]*ENVIRONMENTS[_\-=\s]*$"
    ],
    
    # Hobbies & Personal Interests
    "interests": [
        r"^HOBBIES$", r"^INTERESTS$", r"^PERSONAL\s+INTERESTS$", r"^ACTIVITIES\s+&\s+INTERESTS$", r"^OUTSIDE\s+INTERESTS$",
        r"^EXTRACURRICULAR\s+ACTIVITIES$", r"^LEISURE\s+INTERESTS$",
        r"^[_\-=\s]*HOBBIES[_\-=\s]*$", r"^[_\-=\s]*INTERESTS[_\-=\s]*$", r"^[_\-=\s]*PERSONAL\s+INTERESTS[_\-=\s]*$",
        r"^[_\-=\s]*ACTIVITIES\s+&\s+INTERESTS[_\-=\s]*$", r"^[_\-=\s]*OUTSIDE\s+INTERESTS[_\-=\s]*$",
        r"^[_\-=\s]*EXTRACURRICULAR\s+ACTIVITIES[_\-=\s]*$", r"^[_\-=\s]*LEISURE\s+INTERESTS[_\-=\s]*$"
    ],
    
    # References & Availability
    "references": [
        r"^REFERENCES$", r"^REFERENCES\s+AVAILABLE\s+UPON\s+REQUEST$", r"^REFEREES$", r"^CONTACTABLE\s+REFERENCES$",
        r"^PROFESSIONAL\s+REFERENCES$", r"^AVAILABILITY$", r"^NOTICE\s+PERIOD$", r"^JOINING\s+DATE$",
        r"^[_\-=\s]*REFERENCES[_\-=\s]*$", r"^[_\-=\s]*REFERENCES\s+AVAILABLE\s+UPON\s+REQUEST[_\-=\s]*$",
        r"^[_\-=\s]*REFEREES[_\-=\s]*$", r"^[_\-=\s]*CONTACTABLE\s+REFERENCES[_\-=\s]*$", r"^[_\-=\s]*PROFESSIONAL\s+REFERENCES[_\-=\s]*$",
        r"^[_\-=\s]*AVAILABILITY[_\-=\s]*$", r"^[_\-=\s]*NOTICE\s+PERIOD[_\-=\s]*$", r"^[_\-=\s]*JOINING\s+DATE[_\-=\s]*$"
    ],
    
    # Additional / Miscellaneous
    "additional": [
        r"^ADDITIONAL\s+INFORMATION$", r"^MISCELLANEOUS$", r"^ADDENDUM$", r"^ANNEXURES$", r"^SUPPLEMENTARY\s+DETAILS$",
        r"^ACCOMPLISHMENTS$", r"^CAREER\s+HIGHLIGHTS$", r"^SUMMARY\s+OF\s+QUALIFICATIONS$", r"^WORK\s+AUTHORIZATION$",
        r"^CITIZENSHIP$", r"^MILITARY\s+SERVICE$", r"^SECURITY\s+CLEARANCE$", r"^PUBLICATIONS\s+&\s+PRESENTATIONS$",
        r"^PROFESSIONAL\s+MEMBERSHIPS$", r"^AFFILIATIONS$", r"^MEMBERSHIPS$", r"^PORTFOLIOS$", r"^GITHUB$", r"^LINKEDIN$",
        r"^SOCIAL\s+LINKS$", r"^ONLINE\s+PRESENCE$",
        r"^[_\-=\s]*ADDITIONAL\s+INFORMATION[_\-=\s]*$", r"^[_\-=\s]*MISCELLANEOUS[_\-=\s]*$", r"^[_\-=\s]*ADDENDUM[_\-=\s]*$",
        r"^[_\-=\s]*ANNEXURES[_\-=\s]*$", r"^[_\-=\s]*SUPPLEMENTARY\s+DETAILS[_\-=\s]*$", r"^[_\-=\s]*ACCOMPLISHMENTS[_\-=\s]*$",
        r"^[_\-=\s]*CAREER\s+HIGHLIGHTS[_\-=\s]*$", r"^[_\-=\s]*SUMMARY\s+OF\s+QUALIFICATIONS[_\-=\s]*$", r"^[_\-=\s]*WORK\s+AUTHORIZATION[_\-=\s]*$",
        r"^[_\-=\s]*CITIZENSHIP[_\-=\s]*$", r"^[_\-=\s]*MILITARY\s+SERVICE[_\-=\s]*$", r"^[_\-=\s]*SECURITY\s+CLEARANCE[_\-=\s]*$",
        r"^[_\-=\s]*PUBLICATIONS\s+&\s+PRESENTATIONS[_\-=\s]*$", r"^[_\-=\s]*PROFESSIONAL\s+MEMBERSHIPS[_\-=\s]*$",
        r"^[_\-=\s]*AFFILIATIONS[_\-=\s]*$", r"^[_\-=\s]*MEMBERSHIPS[_\-=\s]*$", r"^[_\-=\s]*PORTFOLIOS[_\-=\s]*$",
        r"^[_\-=\s]*GITHUB[_\-=\s]*$", r"^[_\-=\s]*LINKEDIN[_\-=\s]*$", r"^[_\-=\s]*SOCIAL\s+LINKS[_\-=\s]*$", r"^[_\-=\s]*ONLINE\s+PRESENCE[_\-=\s]*$"
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
        # Special handling for contact info
        if section_name.lower() == 'contact':
            # Check if contact info already exists in the CV content
            cv_content_lower = cv_content.lower()
            contact_indicators = ['@', 'phone:', 'email:', 'linkedin.com', 'github.com', 'gmail.com', 'outlook.com', 'yahoo.com']
            if any(indicator in cv_content_lower for indicator in contact_indicators):
                print(f"📝 Contact info already exists in CV content, skipping creation")
                return cv_content
            
            # For contact info, insert after the first few lines (name and any existing contact info)
            insert_position = 0
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                line_stripped = line.strip()
                # If we find a section header or if we've passed the name/contact area
                if (line_stripped and 
                    (line_stripped.isupper() and len(line_stripped) > 3) or
                    any(keyword in line_stripped.upper() for keyword in ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'OBJECTIVE'])):
                    insert_position = i
                    break
            # If we didn't find a section header, insert after first few lines
            if insert_position == 0:
                insert_position = min(5, len(lines))
        else:
            # For other sections, find a good position to insert (after profile/summary, before experience)
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

    # Always use a Unicode font for non-ASCII characters
    use_custom_font = False
    try:
        pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        pdf.add_font('DejaVu', 'B', 'DejaVuSansCondensed-Bold.ttf', uni=True)
        use_custom_font = True
    except Exception as e:
        print(f"Warning: Could not load DejaVu font: {e}. Falling back to Arial.")
        use_custom_font = False
        # ASCII fallback: replace common non-ASCII characters with ASCII equivalents
        replacements = {
            '\u2022': '-',  # bullet
            '\u2023': '-',  # triangular bullet
            '\u25E6': '-',  # white bullet
            '\u2043': '-',  # hyphen bullet
            '\u2219': '-',  # bullet operator
            '\u2013': '-',  # en dash
            '\u2014': '-',  # em dash
            '\uf0b7': '-',  # another bullet
        }
        for uni, ascii_char in replacements.items():
            cv_content = cv_content.replace(uni, ascii_char)
        # Also replace any other non-ASCII chars with '?'
        cv_content = cv_content.encode('ascii', errors='replace').decode('ascii')

    # Parse CV content
    lines = cv_content.split('\n')

    # Extract name and title (first few lines)
    name = ""
    title = ""
    contact_info = []

    for i, line in enumerate(lines[:10]):
        line = line.strip()
        if line and not re.match(r'^[_\-\=\s]*[A-Z][A-Z\s&]+[_\-\=\s]*$', line):
            if not name:
                name = line
            elif not title and len(line) < 50:
                title = line
            elif '@' in line or re.match(r'^[\+]?\d', line) or 'www.' in line:
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

    pdf.ln(1)

    # Improved section/heading detection and decoration
    section_keywords = ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS', 'ABOUT', 'CERTIFICATIONS', 'ACHIEVEMENTS', 'CONTACT']
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Detect section headers: all uppercase and longer than 3 chars, or contains section keyword
        is_header = (
            (line.isupper() and len(line) > 3) or
            any(kw in line.upper() for kw in section_keywords)
        )
        if is_header:
            pdf.ln(1)  # Extra space before section
            if use_custom_font:
                pdf.set_font('DejaVu', 'B', 14)
            else:
                pdf.set_font('Arial', 'B', 14)
            pdf.set_fill_color(230, 236, 245)
            pdf.cell(0, 10, line.title(), ln=True, fill=True)
            pdf.ln(1)
        else:
            # Bullet points
            if line.startswith('-') or line.startswith('*'):
                pdf.set_x(20)
                if use_custom_font:
                    pdf.set_font('DejaVu', '', 10)
                else:
                    pdf.set_font('Arial', '', 10)
                pdf.cell(0, 8, line, ln=True)
            else:
                if use_custom_font:
                    pdf.set_font('DejaVu', '', 10)
                else:
                    pdf.set_font('Arial', '', 10)
                pdf.multi_cell(0, 8, line)

    # Return PDF as bytes
    pdf_bytes = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1') if not use_custom_font else pdf.output(dest='S').encode('utf-8', errors='replace')
    pdf_bytes.write(pdf_output)
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
    pdf.ln(1)
    
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
    
    pdf.ln(1)

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

class ProjectSelectionRequest(BaseModel):
    selected_project_ids: List[int]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    init_db()
    yield
    # (Optional) Shutdown code here

app = FastAPI(lifespan=lifespan)

# Load environment variables
load_dotenv()

# Get CORS origins from environment or use default
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
print(f"🔧 CORS_ORIGINS from env: {cors_origins}")

# Temporary fix: Hardcode production CORS origins until Render environment variables are set
if cors_origins and cors_origins != "http://localhost:3000,http://127.0.0.1:3000":
    allowed_origins = [origin.strip() for origin in cors_origins.split(",")]
else:
    # Production CORS origins - this will work immediately
    allowed_origins = [
        "https://cv-updater-dwj2.vercel.app",
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ]

print(f"🔧 Allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting CV Updater backend...")
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise e

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
        
        # Add some test projects if none exist
        try:
            cursor, conn = get_db_cursor()
            cursor.execute("SELECT COUNT(*) FROM manual_projects")
            project_count = cursor.fetchone()[0]
            
            if project_count == 0:
                print("📝 Adding test projects to database...")
                test_projects = [
                    {
                        "title": "E-Commerce Platform",
                        "description": "Built full-stack e-commerce solution with React, Node.js, and PostgreSQL",
                        "duration": "2023 - Present",
                        "technologies": ["React", "Node.js", "PostgreSQL", "AWS", "Docker"],
                        "highlights": [
                            "Implemented user authentication, payment processing, and inventory management",
                            "Deployed on AWS with Docker containers and CI/CD pipeline",
                            "Technologies: React, Node.js, PostgreSQL, AWS, Docker"
                        ],
                        "role": "Full Stack Developer"
                    },
                    {
                        "title": "Task Management App",
                        "description": "Developed collaborative task management application with real-time updates",
                        "duration": "2022",
                        "technologies": ["Vue.js", "Express", "MongoDB", "Socket.io"],
                        "highlights": [
                            "Features include user roles, file sharing, and progress tracking",
                            "Integrated with Google Calendar and Slack APIs",
                            "Technologies: Vue.js, Express, MongoDB, Socket.io"
                        ],
                        "role": "Full Stack Developer"
                    },
                    {
                        "title": "Weather Dashboard",
                        "description": "Created weather application with location-based forecasts",
                        "duration": "2021",
                        "technologies": ["React", "OpenWeather API", "PWA", "Local Storage"],
                        "highlights": [
                            "Implemented responsive design and offline functionality",
                            "Integrated multiple weather APIs for comprehensive data",
                            "Technologies: React, OpenWeather API, PWA, Local Storage"
                        ],
                        "role": "Frontend Developer"
                    }
                ]
                
                for project in test_projects:
                    cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", 
                                  (json.dumps(project),))
                
                conn.commit()
                print(f"✅ Added {len(test_projects)} test projects to database")
            else:
                print(f"📊 Database already contains {project_count} projects")
                
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Warning: Could not add test projects: {e}")
        
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
                    extracted_text = content.decode('utf-8')
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
    
    # Remove other problematic Unicode characters that can't be encoded in utf-8
    # cleaned_text = ''.join(char for char in cleaned_text if ord(char) < 256 or char in '•')
    
    # Normalize Unicode characters
    cleaned_text = unicodedata.normalize('NFKC', cleaned_text)
    
    # Clean up extra whitespace but preserve line breaks
    # Replace multiple spaces with single space, but keep newlines
    cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text)
    # Clean up multiple newlines
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    # Remove trailing spaces from lines
    cleaned_text = re.sub(r' +$', '', cleaned_text, flags=re.MULTILINE)
    
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
CONTACT_ADD: adding contact info ("my email is", "phone number", "linkedin", "address", "my name is", "i am", "age", "github", "twitter", "facebook", "instagram", "youtube", "portfolio", "website", "gmail", "outlook", "yahoo", "contact me", "reach me", "call me", "text me", "whatsapp", "telegram", "discord", "slack", "skype", "zoom", "meet", "teams")
OBJECTIVE_ADD: adding career objective ("my objective", "career goal", "aim to", "professional objective")
CERTIFICATION_ADD: adding certifications ("certified", "license", "credential", "training")
RESEARCH_ADD: adding research ("research paper", "publication", "study", "thesis")
ACHIEVEMENT_ADD: adding achievements ("award", "recognition", "honor", "accomplishment")
LEADERSHIP_ADD: adding leadership ("led team", "managed", "supervised", "directed")
VOLUNTEER_ADD: adding volunteer work ("volunteered", "community service", "charity")
LANGUAGE_ADD: adding languages ("speak", "fluent in", "language", "bilingual")
TECHNOLOGY_ADD: adding technologies ("tool", "software", "platform", "system")
INTEREST_ADD: adding interests ("hobby", "interest", "enjoy", "passion")
REFERENCE_ADD: adding references ("reference", "recommendation", "endorsement")
ADDITIONAL_ADD: adding additional info ("additional", "miscellaneous", "other")

=== READ OPERATIONS ===
CV_SHOW: show full CV ("show cv", "display cv", "my cv", "current cv")
SKILL_SHOW: show skills ("what skills", "my skills", "list skills", "show skills")
EXPERIENCE_SHOW: show experience ("what experience", "my jobs", "work history", "employment")
EDUCATION_SHOW: show education ("my education", "degrees", "qualifications", "academic")
PROJECT_SHOW: show projects ("my projects", "what projects", "list projects", "portfolio")
CONTACT_SHOW: show contact info ("my contact", "contact details", "how to reach")
OBJECTIVE_SHOW: show objective ("my objective", "career goal", "show objective")
CERTIFICATION_SHOW: show certifications ("my certifications", "show certifications", "list certifications")
RESEARCH_SHOW: show research ("my research", "show research", "list research")
ACHIEVEMENT_SHOW: show achievements ("my achievements", "show achievements", "list achievements")
LEADERSHIP_SHOW: show leadership ("my leadership", "show leadership", "list leadership")
VOLUNTEER_SHOW: show volunteer work ("my volunteer", "show volunteer", "list volunteer")
LANGUAGE_SHOW: show languages ("my languages", "show languages", "list languages")
TECHNOLOGY_SHOW: show technologies ("my technologies", "show technologies", "list technologies")
INTEREST_SHOW: show interests ("my interests", "show interests", "list interests")
REFERENCE_SHOW: show references ("my references", "show references", "list references")
ADDITIONAL_SHOW: show additional info ("my additional", "show additional", "list additional")

=== UPDATE OPERATIONS ===
SKILL_UPDATE: modify existing skills ("update skill", "change skill", "modify skill")
EXPERIENCE_UPDATE: modify work experience ("update job", "change experience", "modify work")
EDUCATION_UPDATE: modify education ("update degree", "change education", "modify qualification")
PROJECT_UPDATE: modify project ("update project", "change project", "modify project")
CONTACT_UPDATE: modify contact info ("update contact", "change email", "new phone")
OBJECTIVE_UPDATE: modify objective ("update objective", "change objective", "modify objective")
CERTIFICATION_UPDATE: modify certifications ("update certification", "change certification", "modify certification")
RESEARCH_UPDATE: modify research ("update research", "change research", "modify research")
ACHIEVEMENT_UPDATE: modify achievements ("update achievement", "change achievement", "modify achievement")
LEADERSHIP_UPDATE: modify leadership ("update leadership", "change leadership", "modify leadership")
VOLUNTEER_UPDATE: modify volunteer work ("update volunteer", "change volunteer", "modify volunteer")
LANGUAGE_UPDATE: modify languages ("update language", "change language", "modify language")
TECHNOLOGY_UPDATE: modify technologies ("update technology", "change technology", "modify technology")
INTEREST_UPDATE: modify interests ("update interest", "change interest", "modify interest")
REFERENCE_UPDATE: modify references ("update reference", "change reference", "modify reference")
ADDITIONAL_UPDATE: modify additional info ("update additional", "change additional", "modify additional")

=== DELETE OPERATIONS ===
SKILL_DELETE: remove skills ("remove skill", "delete skill", "don't have skill")
EXPERIENCE_DELETE: remove experience ("remove job", "delete experience", "wasn't employed")
EDUCATION_DELETE: remove education ("remove degree", "delete education", "didn't study")
PROJECT_DELETE: remove project ("remove project", "delete project", "didn't build")
CONTACT_DELETE: remove contact info ("remove contact", "delete email", "no phone")
OBJECTIVE_DELETE: remove objective ("remove objective", "delete objective", "no objective")
CERTIFICATION_DELETE: remove certifications ("remove certification", "delete certification", "no certification")
RESEARCH_DELETE: remove research ("remove research", "delete research", "no research")
ACHIEVEMENT_DELETE: remove achievements ("remove achievement", "delete achievement", "no achievement")
LEADERSHIP_DELETE: remove leadership ("remove leadership", "delete leadership", "no leadership")
VOLUNTEER_DELETE: remove volunteer work ("remove volunteer", "delete volunteer", "no volunteer")
LANGUAGE_DELETE: remove languages ("remove language", "delete language", "no language")
TECHNOLOGY_DELETE: remove technologies ("remove technology", "delete technology", "no technology")
INTEREST_DELETE: remove interests ("remove interest", "delete interest", "no interest")
REFERENCE_DELETE: remove references ("remove reference", "delete reference", "no reference")
ADDITIONAL_DELETE: remove additional info ("remove additional", "delete additional", "no additional")

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
    print(f"[DEBUG] classify_message_fallback: message='{message}' (lower='{msg}')")

    # SPECIFIC ADD OPERATIONS - Check these FIRST before any other patterns
    print(f"[DEBUG] UPDATED CODE VERSION - Checking OBJECTIVE_ADD: add/insert/put/append in msg? {any(kw in msg for kw in ['add', 'include', 'insert', 'put', 'append'])}, objective/goal in msg? {any(kw in msg for kw in ['objective', 'goal', 'career objective', 'professional objective'])}")
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("objective" in msg or "goal" in msg or "career objective" in msg or "professional objective" in msg):
        print("[DEBUG] classify_message_fallback: Detected OBJECTIVE_ADD")
        return {"category": "OBJECTIVE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("volunteer" in msg or "community service" in msg or "charity" in msg or "pro bono" in msg):
        print("[DEBUG] classify_message_fallback: Detected VOLUNTEER_ADD")
        return {"category": "VOLUNTEER_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("language" in msg or "speak" in msg or "fluent in" in msg or "proficient in" in msg):
        print("[DEBUG] classify_message_fallback: Detected LANGUAGE_ADD")
        return {"category": "LANGUAGE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("reference" in msg or "referee" in msg or "recommendation" in msg or "endorsement" in msg):
        print("[DEBUG] classify_message_fallback: Detected REFERENCE_ADD")
        return {"category": "REFERENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("additional" in msg or "miscellaneous" in msg or "other" in msg or "extra" in msg):
        print("[DEBUG] classify_message_fallback: Detected ADDITIONAL_ADD")
        return {"category": "ADDITIONAL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("hobby" in msg or "interest" in msg or "passion" in msg or "enjoy" in msg or "like to" in msg):
        print("[DEBUG] classify_message_fallback: Detected INTEREST_ADD")
        return {"category": "INTEREST_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("certification" in msg or "certified" in msg or "license" in msg or "credential" in msg or "training" in msg):
        print("[DEBUG] classify_message_fallback: Detected CERTIFICATION_ADD")
        return {"category": "CERTIFICATION_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("research" in msg or "publication" in msg or "paper" in msg or "thesis" in msg or "dissertation" in msg or "study" in msg):
        print("[DEBUG] classify_message_fallback: Detected RESEARCH_ADD")
        return {"category": "RESEARCH_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("award" in msg or "honor" in msg or "achievement" in msg or "recognition" in msg or "scholarship" in msg):
        print("[DEBUG] classify_message_fallback: Detected ACHIEVEMENT_ADD")
        return {"category": "ACHIEVEMENT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("leadership" in msg or "led" in msg or "managed" in msg or "supervised" in msg or "directed" in msg):
        print("[DEBUG] classify_message_fallback: Detected LEADERSHIP_ADD")
        return {"category": "LEADERSHIP_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("tool" in msg or "technology" in msg or "technologies" in msg or "software" in msg or "platform" in msg or "system" in msg):
        print("[DEBUG] classify_message_fallback: Detected TECHNOLOGY_ADD")
        return {"category": "TECHNOLOGY_ADD", "extracted_info": message.strip(), "operation": "CREATE"}

    # UTILITY OPERATIONS - Check these AFTER specific ADD patterns
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
    elif any(phrase in msg for phrase in ["help", "what can you do", "commands", "how to use"]) and not any(phrase in msg for phrase in ["add", "include", "insert", "put", "append", "objective", "volunteer", "language", "reference", "additional"]):
        print("[DEBUG] classify_message_fallback: Detected CV_HELP")
        return {"category": "CV_HELP", "extracted_info": message.strip(), "operation": "READ"}

    # PROJECT MANAGEMENT COMMANDS
    if any(phrase in msg for phrase in ["extract projects", "extract from cv", "get projects from cv", "parse projects"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_EXTRACT")
        return {"category": "PROJECT_EXTRACT", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["show my projects", "list my projects", "display projects", "my projects"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_SHOW")
        return {"category": "PROJECT_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["delete project", "remove project", "delete a project"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_DELETE")
        return {"category": "PROJECT_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["download cv", "download my cv", "get cv download"]):
        print("[DEBUG] classify_message_fallback: Detected CV_DOWNLOAD")
        return {"category": "CV_DOWNLOAD", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["clean up cv", "clean cv", "fix cv", "organize cv"]):
        print("[DEBUG] classify_message_fallback: Detected CV_CLEANUP")
        return {"category": "CV_CLEANUP", "extracted_info": message.strip(), "operation": "UPDATE"}
    elif any(phrase in msg for phrase in ["create linkedin blog", "generate blog", "write blog", "linkedin post"]):
        print("[DEBUG] classify_message_fallback: Detected LINKEDIN_BLOG")
        return {"category": "LINKEDIN_BLOG", "extracted_info": message.strip(), "operation": "CREATE"}
    
    # IMPLICIT ADD OPERATIONS - For messages without explicit "add" words
    # These are treated as CREATE operations when specific section keywords are detected
    if ("objective" in msg or "goal" in msg or "career objective" in msg or "professional objective" in msg or "aim" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected OBJECTIVE_ADD (implicit)")
        return {"category": "OBJECTIVE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("certification" in msg or "certified" in msg or "license" in msg or "credential" in msg or "training" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected CERTIFICATION_ADD (implicit)")
        return {"category": "CERTIFICATION_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("research" in msg or "publication" in msg or "paper" in msg or "thesis" in msg or "dissertation" in msg or "study" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected RESEARCH_ADD (implicit)")
        return {"category": "RESEARCH_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("award" in msg or "honor" in msg or "achievement" in msg or "recognition" in msg or "scholarship" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected ACHIEVEMENT_ADD (implicit)")
        return {"category": "ACHIEVEMENT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("leadership" in msg or "led" in msg or "managed" in msg or "supervised" in msg or "directed" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected LEADERSHIP_ADD (implicit)")
        return {"category": "LEADERSHIP_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("volunteer" in msg or "community service" in msg or "charity" in msg or "pro bono" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected VOLUNTEER_ADD (implicit)")
        return {"category": "VOLUNTEER_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("language" in msg or "speak" in msg or "fluent in" in msg or "proficient in" in msg or any(lang in msg for lang in ["chinese", "english", "spanish", "french", "german", "italian", "portuguese", "russian", "japanese", "korean", "arabic", "hindi", "urdu"])) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected LANGUAGE_ADD (implicit)")
        return {"category": "LANGUAGE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("tool" in msg or "software" in msg or "platform" in msg or "system" in msg or "git" in msg or "proficient with" in msg or "skilled in" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected TECHNOLOGY_ADD (implicit)")
        return {"category": "TECHNOLOGY_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("hobby" in msg or "interest" in msg or "passion" in msg or "enjoy" in msg or "like to" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected INTEREST_ADD (implicit)")
        return {"category": "INTEREST_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("reference" in msg or "referee" in msg or "recommendation" in msg or "endorsement" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected REFERENCE_ADD (implicit)")
        return {"category": "REFERENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if ("additional" in msg or "miscellaneous" in msg or "other" in msg or "extra" in msg) and not any(kw in msg for kw in ["show", "display", "list", "what", "update", "change", "modify", "delete", "remove"]):
        print("[DEBUG] classify_message_fallback: Detected ADDITIONAL_ADD (implicit)")
        return {"category": "ADDITIONAL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    
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
    
    # UPDATE OPERATIONS - Check UPDATE before ADD to avoid conflicts
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("objective" in msg or "goal" in msg or "career objective" in msg or "professional objective" in msg):
        print("[DEBUG] classify_message_fallback: Detected OBJECTIVE_UPDATE")
        return {"category": "OBJECTIVE_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("certification" in msg or "license" in msg or "certificate" in msg or "credential" in msg or "training" in msg):
        print("[DEBUG] classify_message_fallback: Detected CERTIFICATION_UPDATE")
        return {"category": "CERTIFICATION_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("research" in msg or "publication" in msg or "paper" in msg or "thesis" in msg or "dissertation" in msg):
        print("[DEBUG] classify_message_fallback: Detected RESEARCH_UPDATE")
        return {"category": "RESEARCH_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("award" in msg or "honor" in msg or "achievement" in msg or "recognition" in msg or "scholarship" in msg):
        print("[DEBUG] classify_message_fallback: Detected ACHIEVEMENT_UPDATE")
        return {"category": "ACHIEVEMENT_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("leadership" in msg or "led" in msg or "managed" in msg or "supervised" in msg or "directed" in msg):
        print("[DEBUG] classify_message_fallback: Detected LEADERSHIP_UPDATE")
        return {"category": "LEADERSHIP_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("volunteer" in msg or "community service" in msg or "charity" in msg or "pro bono" in msg):
        print("[DEBUG] classify_message_fallback: Detected VOLUNTEER_UPDATE")
        return {"category": "VOLUNTEER_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("language" in msg or "speak" in msg or "fluent in" in msg or "proficient in" in msg):
        print("[DEBUG] classify_message_fallback: Detected LANGUAGE_UPDATE")
        return {"category": "LANGUAGE_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("tool" in msg or "technology" in msg or "technologies" in msg or "software" in msg or "framework" in msg or "platform" in msg):
        print("[DEBUG] classify_message_fallback: Detected TECHNOLOGY_UPDATE")
        return {"category": "TECHNOLOGY_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("hobby" in msg or "interest" in msg or "passion" in msg or "enjoy" in msg or "like to" in msg):
        print("[DEBUG] classify_message_fallback: Detected INTEREST_UPDATE")
        return {"category": "INTEREST_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("reference" in msg or "referee" in msg or "recommendation" in msg or "endorsement" in msg):
        print("[DEBUG] classify_message_fallback: Detected REFERENCE_UPDATE")
        return {"category": "REFERENCE_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    if any(kw in msg for kw in ["update", "change", "modify"]) and ("additional" in msg or "miscellaneous" in msg or "other" in msg or "extra" in msg):
        print("[DEBUG] classify_message_fallback: Detected ADDITIONAL_UPDATE")
        return {"category": "ADDITIONAL_UPDATE", "extracted_info": message.strip(), "operation": "UPDATE"}
    
    # ADD OPERATIONS - More specific patterns to avoid catching UPDATE messages
    # Note: Specific ADD patterns moved to the top to be checked before education patterns
    
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
    
    # ADDITIONAL READ OPERATIONS
    elif any(phrase in msg for phrase in ["my objective", "career goal", "professional objective"]):
        print("[DEBUG] classify_message_fallback: Detected OBJECTIVE_SHOW")
        return {"category": "OBJECTIVE_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my certifications", "licenses", "credentials", "training"]):
        print("[DEBUG] classify_message_fallback: Detected CERTIFICATION_SHOW")
        return {"category": "CERTIFICATION_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my research", "publications", "papers", "academic work"]):
        print("[DEBUG] classify_message_fallback: Detected RESEARCH_SHOW")
        return {"category": "RESEARCH_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my awards", "honors", "achievements", "recognition"]):
        print("[DEBUG] classify_message_fallback: Detected ACHIEVEMENT_SHOW")
        return {"category": "ACHIEVEMENT_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my leadership", "leadership roles", "management experience"]):
        print("[DEBUG] classify_message_fallback: Detected LEADERSHIP_SHOW")
        return {"category": "LEADERSHIP_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my volunteer", "community service", "charitable work"]):
        print("[DEBUG] classify_message_fallback: Detected VOLUNTEER_SHOW")
        return {"category": "VOLUNTEER_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my languages", "language skills", "spoken languages"]):
        print("[DEBUG] classify_message_fallback: Detected LANGUAGE_SHOW")
        return {"category": "LANGUAGE_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my tools", "technologies", "software", "frameworks"]):
        print("[DEBUG] classify_message_fallback: Detected TECHNOLOGY_SHOW")
        return {"category": "TECHNOLOGY_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my hobbies", "interests", "personal interests"]):
        print("[DEBUG] classify_message_fallback: Detected INTEREST_SHOW")
        return {"category": "INTEREST_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["my references", "referees", "recommendations"]):
        print("[DEBUG] classify_message_fallback: Detected REFERENCE_SHOW")
        return {"category": "REFERENCE_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    elif any(phrase in msg for phrase in ["additional info", "miscellaneous", "other information"]):
        print("[DEBUG] classify_message_fallback: Detected ADDITIONAL_SHOW")
        return {"category": "ADDITIONAL_SHOW", "extracted_info": message.strip(), "operation": "READ"}
    
    # UPDATE OPERATIONS - Check UPDATE before DELETE to avoid conflicts
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
    

    
    # DELETE OPERATIONS - Moved after UPDATE to avoid conflicts
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
    
    # ADDITIONAL DELETE OPERATIONS
    elif any(phrase in msg for phrase in ["remove objective", "delete goal", "no objective"]):
        print("[DEBUG] classify_message_fallback: Detected OBJECTIVE_DELETE")
        return {"category": "OBJECTIVE_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove certification", "delete license", "no credential"]):
        print("[DEBUG] classify_message_fallback: Detected CERTIFICATION_DELETE")
        return {"category": "CERTIFICATION_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove research", "delete publication", "no paper"]):
        print("[DEBUG] classify_message_fallback: Detected RESEARCH_DELETE")
        return {"category": "RESEARCH_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove award", "delete achievement", "no honor"]):
        print("[DEBUG] classify_message_fallback: Detected ACHIEVEMENT_DELETE")
        return {"category": "ACHIEVEMENT_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove leadership", "delete management", "no role"]):
        print("[DEBUG] classify_message_fallback: Detected LEADERSHIP_DELETE")
        return {"category": "LEADERSHIP_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove volunteer", "delete service", "no charity"]):
        print("[DEBUG] classify_message_fallback: Detected VOLUNTEER_DELETE")
        return {"category": "VOLUNTEER_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove language", "delete language skill", "no language"]):
        print("[DEBUG] classify_message_fallback: Detected LANGUAGE_DELETE")
        return {"category": "LANGUAGE_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove tool", "delete technology", "no software"]):
        print("[DEBUG] classify_message_fallback: Detected TECHNOLOGY_DELETE")
        return {"category": "TECHNOLOGY_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove hobby", "delete interest", "no passion"]):
        print("[DEBUG] classify_message_fallback: Detected INTEREST_DELETE")
        return {"category": "INTEREST_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove reference", "delete referee", "no recommendation"]):
        print("[DEBUG] classify_message_fallback: Detected REFERENCE_DELETE")
        return {"category": "REFERENCE_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    elif any(phrase in msg for phrase in ["remove additional", "delete miscellaneous", "no other"]):
        print("[DEBUG] classify_message_fallback: Detected ADDITIONAL_DELETE")
        return {"category": "ADDITIONAL_DELETE", "extracted_info": message.strip(), "operation": "DELETE"}
    
    # SPECIFIC ADD OPERATIONS - Check these BEFORE legacy patterns
    print(f"[DEBUG] Checking OBJECTIVE_ADD: add/insert/put/append in msg? {any(kw in msg for kw in ['add', 'include', 'insert', 'put', 'append'])}, objective/goal in msg? {any(kw in msg for kw in ['objective', 'goal', 'career objective', 'professional objective'])}")
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("objective" in msg or "goal" in msg or "career objective" in msg or "professional objective" in msg):
        print("[DEBUG] classify_message_fallback: Detected OBJECTIVE_ADD")
        return {"category": "OBJECTIVE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("volunteer" in msg or "community service" in msg or "charity" in msg or "pro bono" in msg):
        print("[DEBUG] classify_message_fallback: Detected VOLUNTEER_ADD")
        return {"category": "VOLUNTEER_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("language" in msg or "speak" in msg or "fluent in" in msg or "proficient in" in msg):
        print("[DEBUG] classify_message_fallback: Detected LANGUAGE_ADD")
        return {"category": "LANGUAGE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("reference" in msg or "referee" in msg or "recommendation" in msg or "endorsement" in msg):
        print("[DEBUG] classify_message_fallback: Detected REFERENCE_ADD")
        return {"category": "REFERENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    if any(kw in msg for kw in ["add", "include", "insert", "put", "append"]) and ("additional" in msg or "miscellaneous" in msg or "other" in msg or "extra" in msg):
        print("[DEBUG] classify_message_fallback: Detected ADDITIONAL_ADD")
        return {"category": "ADDITIONAL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    
    # CREATE OPERATIONS - Enhanced with all section types
    elif any(phrase in msg for phrase in ["i learned", "i know", "add skill", "skilled in", "proficient in", "expert in"]):
        print("[DEBUG] classify_message_fallback: Detected SKILL_ADD")
        return {"category": "SKILL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["i worked", "i was employed", "job at", "worked as", "position at", "role as"]):
        print("[DEBUG] classify_message_fallback: Detected EXPERIENCE_ADD")
        return {"category": "EXPERIENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["i studied", "graduated from", "degree in", "certification in", "completed course", "attended"]):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_ADD")
        return {"category": "EDUCATION_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["i built", "i created", "i developed", "project called", "designed", "implemented"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_ADD")
        return {"category": "PROJECT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["my email is", "phone number", "linkedin", "address", "my name is", "i am", "age", "github", "twitter", "facebook", "instagram", "youtube", "portfolio", "website", "gmail", "outlook", "yahoo", "contact me", "reach me", "call me", "text me", "whatsapp", "telegram", "discord", "slack", "skype", "zoom", "meet", "teams"]):
        print("[DEBUG] classify_message_fallback: Detected CONTACT_ADD")
        return {"category": "CONTACT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    

    
    # LEGACY SUPPORT (backward compatibility) - Removed conflicting patterns
    elif any(phrase in msg for phrase in ["skill", "learned", "achieved"]) and not any(phrase in msg for phrase in ["objective", "certification", "research", "achievement", "leadership", "volunteer", "language", "technology", "interest", "reference", "additional"]):
        print("[DEBUG] classify_message_fallback: Detected SKILL_ADD")
        return {"category": "SKILL_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["worked", "job", "experience"]) and not any(phrase in msg for phrase in ["objective", "certification", "research", "achievement", "leadership", "volunteer", "language", "technology", "interest", "reference", "additional"]):
        print("[DEBUG] classify_message_fallback: Detected EXPERIENCE_ADD")
        return {"category": "EXPERIENCE_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["degree", "education"]) and not any(phrase in msg for phrase in ["objective", "certification", "research", "achievement", "leadership", "volunteer", "language", "technology", "interest", "reference", "additional"]):
        print("[DEBUG] classify_message_fallback: Detected EDUCATION_ADD")
        return {"category": "EDUCATION_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    elif any(phrase in msg for phrase in ["project", "built", "developed", "created", "app", "website", "system"]) and not any(phrase in msg for phrase in ["objective", "certification", "research", "achievement", "leadership", "volunteer", "language", "technology", "interest", "reference", "additional"]):
        print("[DEBUG] classify_message_fallback: Detected PROJECT_ADD")
        return {"category": "PROJECT_ADD", "extracted_info": message.strip(), "operation": "CREATE"}
    

    
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

# ===== SECTION EXTRACTION FUNCTIONS =====

def extract_objective_from_message(message: str) -> str:
    """Extract and format objective from chat message"""
    try:
        prompt = f"""Extract career objective information from this message and format it properly:
        
        Message: {message}
        
        Format the objective as a clear, professional career goal statement.
        
        Examples:
        - "To become a senior software engineer and lead development teams"
        - "To leverage my technical skills in a challenging software development role"
        - "To contribute to innovative projects as a full-stack developer"
        
        Extract and format only the objective, no bullet points or extra text."""
        
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
        return extract_objective_fallback(message)

def extract_objective_fallback(message: str) -> str:
    """Fallback method to extract and format objective"""
    msg_lower = message.lower()
    
    # Remove common prefixes
    prefixes_to_remove = [
        "my career objective is", "my objective is", "my goal is", "i aim to", "i want to",
        "career objective:", "objective:", "goal:", "aim:", "target:"
    ]
    
    content = message.strip()
    for prefix in prefixes_to_remove:
        if content.lower().startswith(prefix):
            content = content[len(prefix):].strip()
            break
    
    # If content is too short, return original
    if len(content) < 10:
        return message.strip()
    
    return content

def extract_certification_from_message(message: str) -> str:
    """Extract and format certification from chat message"""
    try:
        prompt = f"""Extract certification information from this message and format it properly:
        
        Message: {message}
        
        Format the certification as: "[Certification Name] - [Issuing Organization] [Year/Status]"
        
        Examples:
        - "AWS Certified Solutions Architect - Amazon Web Services 2023"
        - "Microsoft Azure Developer - Microsoft 2022"
        - "Google Cloud Professional - Google Cloud Platform 2024"
        
        Extract and format only the certification, no bullet points or extra text."""
        
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
        return extract_certification_fallback(message)

def extract_certification_fallback(message: str) -> str:
    """Fallback method to extract and format certification"""
    msg_lower = message.lower()
    
    # Extract certification name
    cert_patterns = [
        r'aws\s+certified\s+([^,\.]+)',
        r'microsoft\s+([^,\.]+)\s+certification',
        r'google\s+cloud\s+([^,\.]+)',
        r'([^,\.]+)\s+certification',
        r'certified\s+([^,\.]+)',
        r'([^,\.]+)\s+certified'
    ]
    
    cert_name = ""
    for pattern in cert_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            cert_name = match.group(1).strip().title()
            break
    
    # Extract organization
    org_patterns = [
        r'from\s+([^,\.]+)',
        r'by\s+([^,\.]+)',
        r'([^,\.]+)\s+certification',
        r'aws|amazon|microsoft|google|cisco|oracle'
    ]
    
    organization = "Professional Organization"
    for pattern in org_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            org = match.group(1).strip().title()
            if org.lower() in ['aws', 'amazon']:
                organization = "Amazon Web Services"
            elif org.lower() == 'microsoft':
                organization = "Microsoft"
            elif org.lower() == 'google':
                organization = "Google Cloud Platform"
            else:
                organization = org
            break
    
    # Extract year
    year_match = re.search(r'(\d{4})', message)
    year = year_match.group(1) if year_match else "2024"
    
    if not cert_name:
        return message.strip()
    
    return f"{cert_name} - {organization} {year}"

def extract_research_from_message(message: str) -> str:
    """Extract and format research from chat message"""
    try:
        prompt = f"""Extract research information from this message and format it properly:
        
        Message: {message}
        
        Format the research as: "[Research Title/Type] - [Institution/Journal] [Year]"
        
        Examples:
        - "Machine Learning Ethics - Stanford University 2023"
        - "Blockchain Technology Study - MIT 2022"
        - "AI Research Paper - IEEE Conference 2024"
        
        Extract and format only the research, no bullet points or extra text."""
        
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
        return extract_research_fallback(message)

def extract_research_fallback(message: str) -> str:
    """Fallback method to extract and format research"""
    msg_lower = message.lower()
    
    # Extract research type/title
    research_patterns = [
        r'research\s+(?:on|about|paper\s+on)\s+([^,\.]+)',
        r'study\s+(?:on|about)\s+([^,\.]+)',
        r'paper\s+(?:on|about)\s+([^,\.]+)',
        r'([^,\.]+)\s+research',
        r'([^,\.]+)\s+study'
    ]
    
    research_topic = ""
    for pattern in research_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            research_topic = match.group(1).strip().title()
            break
    
    # Extract institution/journal
    inst_patterns = [
        r'at\s+([^,\.]+)',
        r'from\s+([^,\.]+)',
        r'([^,\.]+)\s+university',
        r'([^,\.]+)\s+journal',
        r'([^,\.]+)\s+conference'
    ]
    
    institution = "Academic Institution"
    for pattern in inst_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            institution = match.group(1).strip().title()
            break
    
    # Extract year
    year_match = re.search(r'(\d{4})', message)
    year = year_match.group(1) if year_match else "2024"
    
    if not research_topic:
        return message.strip()
    
    return f"{research_topic} Research - {institution} {year}"

def extract_achievement_from_message(message: str) -> str:
    """Extract and format achievement from chat message"""
    try:
        prompt = f"""Extract achievement information from this message and format it properly:
        
        Message: {message}
        
        Format the achievement as: "[Achievement Name] - [Organization/Event] [Year]"
        
        Examples:
        - "Best Developer Award - Tech Conference 2023"
        - "Hackathon Winner - University Competition 2022"
        - "Outstanding Performance - Company Recognition 2024"
        
        Extract and format only the achievement, no bullet points or extra text."""
        
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
        return extract_achievement_fallback(message)

def extract_achievement_fallback(message: str) -> str:
    """Fallback method to extract and format achievement"""
    msg_lower = message.lower()
    
    # Extract achievement type
    achievement_patterns = [
        r'received\s+([^,\.]+)',
        r'won\s+([^,\.]+)',
        r'earned\s+([^,\.]+)',
        r'([^,\.]+)\s+award',
        r'([^,\.]+)\s+recognition',
        r'([^,\.]+)\s+honor'
    ]
    
    achievement = ""
    for pattern in achievement_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            achievement = match.group(1).strip().title()
            break
    
    # Extract organization/event
    org_patterns = [
        r'from\s+([^,\.]+)',
        r'at\s+([^,\.]+)',
        r'([^,\.]+)\s+conference',
        r'([^,\.]+)\s+competition',
        r'([^,\.]+)\s+university'
    ]
    
    organization = "Organization"
    for pattern in org_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            organization = match.group(1).strip().title()
            break
    
    # Extract year
    year_match = re.search(r'(\d{4})', message)
    year = year_match.group(1) if year_match else "2024"
    
    if not achievement:
        return message.strip()
    
    return f"{achievement} - {organization} {year}"

def extract_leadership_from_message(message: str) -> str:
    """Extract and format leadership from chat message"""
    try:
        prompt = f"""Extract leadership information from this message and format it properly:
        
        Message: {message}
        
        Format the leadership as: "[Role/Responsibility] - [Organization/Team] [Duration]"
        
        Examples:
        - "Team Lead - Software Development Team 2022-2023"
        - "Project Manager - Agile Development Team 6 months"
        - "Technical Lead - Engineering Department 2023-2024"
        
        Extract and format only the leadership, no bullet points or extra text."""
        
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
        return extract_leadership_fallback(message)

def extract_leadership_fallback(message: str) -> str:
    """Fallback method to extract and format leadership"""
    msg_lower = message.lower()
    
    # Extract role
    role_patterns = [
        r'led\s+([^,\.]+)',
        r'managed\s+([^,\.]+)',
        r'supervised\s+([^,\.]+)',
        r'team\s+lead\s+([^,\.]+)',
        r'([^,\.]+)\s+lead',
        r'([^,\.]+)\s+manager'
    ]
    
    role = ""
    for pattern in role_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            role = match.group(1).strip().title()
            break
    
    # Extract team/organization
    team_patterns = [
        r'team\s+of\s+([^,\.]+)',
        r'([^,\.]+)\s+team',
        r'([^,\.]+)\s+department',
        r'([^,\.]+)\s+group'
    ]
    
    team = "Team"
    for pattern in team_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            team = match.group(1).strip().title()
            break
    
    # Extract duration
    duration_patterns = [
        r'for\s+([^,\.]+)',
        r'([^,\.]+)\s+months',
        r'([^,\.]+)\s+years',
        r'(\d{4}-\d{4})'
    ]
    
    duration = "2023-2024"
    for pattern in duration_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            duration = match.group(1).strip()
            break
    
    if not role:
        return message.strip()
    
    return f"{role} - {team} {duration}"

def extract_volunteer_from_message(message: str) -> str:
    """Extract and format volunteer work from chat message"""
    try:
        prompt = f"""Extract volunteer work information from this message and format it properly:
        
        Message: {message}
        
        Format the volunteer work as: "[Role/Activity] - [Organization] [Duration]"
        
        Examples:
        - "Coding Instructor - Local Bootcamp 2023-2024"
        - "Community Service - Charity Organization 6 months"
        - "Mentor - Youth Program 2022-2023"
        
        Extract and format only the volunteer work, no bullet points or extra text."""
        
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
        return extract_volunteer_fallback(message)

def extract_volunteer_fallback(message: str) -> str:
    """Fallback method to extract and format volunteer work"""
    msg_lower = message.lower()
    
    # Extract activity
    activity_patterns = [
        r'volunteered\s+([^,\.]+)',
        r'community\s+service\s+([^,\.]+)',
        r'mentored\s+([^,\.]+)',
        r'([^,\.]+)\s+volunteer',
        r'([^,\.]+)\s+mentor'
    ]
    
    activity = ""
    for pattern in activity_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            activity = match.group(1).strip().title()
            break
    
    # Extract organization
    org_patterns = [
        r'at\s+([^,\.]+)',
        r'for\s+([^,\.]+)',
        r'([^,\.]+)\s+organization',
        r'([^,\.]+)\s+program',
        r'([^,\.]+)\s+bootcamp'
    ]
    
    organization = "Community Organization"
    for pattern in org_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            organization = match.group(1).strip().title()
            break
    
    # Extract duration
    duration_patterns = [
        r'for\s+([^,\.]+)',
        r'([^,\.]+)\s+months',
        r'([^,\.]+)\s+years',
        r'(\d{4}-\d{4})'
    ]
    
    duration = "2023-2024"
    for pattern in duration_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            duration = match.group(1).strip()
            break
    
    if not activity:
        return message.strip()
    
    return f"{activity} - {organization} {duration}"

def extract_language_from_message(message: str) -> str:
    """Extract and format language skills from chat message"""
    try:
        prompt = f"""Extract language skills information from this message and format it properly:
        
        Message: {message}
        
        Format the language skills as: "[Language] - [Proficiency Level]"
        
        Examples:
        - "English - Native"
        - "Spanish - Fluent"
        - "French - Conversational"
        - "German - Intermediate"
        
        Extract and format only the language skills, no bullet points or extra text."""
        
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
        return extract_language_fallback(message)

def extract_language_fallback(message: str) -> str:
    """Fallback method to extract and format language skills"""
    msg_lower = message.lower()
    
    # Extract languages
    language_patterns = [
        r'speak\s+([^,\.]+)',
        r'fluent\s+in\s+([^,\.]+)',
        r'proficient\s+in\s+([^,\.]+)',
        r'([^,\.]+)\s+language',
        r'([^,\.]+)\s+speaker'
    ]
    
    languages = []
    for pattern in language_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            lang = match.group(1).strip().title()
            if lang not in languages:
                languages.append(lang)
    
    # Extract proficiency
    proficiency_patterns = [
        r'native\s+speaker',
        r'fluent',
        r'proficient',
        r'conversational',
        r'intermediate',
        r'basic'
    ]
    
    proficiency = "Proficient"
    for pattern in proficiency_patterns:
        if re.search(pattern, msg_lower):
            proficiency = pattern.title()
            break
    
    if not languages:
        return message.strip()
    
    if len(languages) == 1:
        return f"{languages[0]} - {proficiency}"
    else:
        return f"{', '.join(languages)} - {proficiency}"

def extract_technology_from_message(message: str) -> str:
    """Extract and format technology/tools from chat message"""
    try:
        prompt = f"""Extract technology/tools information from this message and format it properly:
        
        Message: {message}
        
        Format the technology as: "[Technology Category] - [Tools/Platforms]"
        
        Examples:
        - "Development Tools - Git, Docker, Jenkins"
        - "Project Management - Jira, Confluence, Slack"
        - "Cloud Platforms - AWS, Azure, GCP"
        
        Extract and format only the technology, no bullet points or extra text."""
        
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
        return extract_technology_fallback(message)

def extract_technology_fallback(message: str) -> str:
    """Fallback method to extract and format technology/tools"""
    msg_lower = message.lower()
    
    # Extract tools/technologies
    tool_patterns = [
        r'proficient\s+with\s+([^,\.]+)',
        r'skilled\s+in\s+([^,\.]+)',
        r'([^,\.]+)\s+tools',
        r'([^,\.]+)\s+software',
        r'([^,\.]+)\s+platform'
    ]
    
    tools = []
    for pattern in tool_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            tool = match.group(1).strip().title()
            if tool not in tools:
                tools.append(tool)
    
    # Extract category
    category_patterns = [
        r'development\s+tools',
        r'project\s+management',
        r'cloud\s+platforms',
        r'version\s+control',
        r'collaboration\s+tools'
    ]
    
    category = "Technology Tools"
    for pattern in category_patterns:
        if re.search(pattern, msg_lower):
            category = pattern.title()
            break
    
    if not tools:
        return message.strip()
    
    return f"{category} - {', '.join(tools)}"

def extract_interest_from_message(message: str) -> str:
    """Extract and format interests/hobbies from chat message"""
    try:
        prompt = f"""Extract interests/hobbies information from this message and format it properly:
        
        Message: {message}
        
        Format the interests as: "[Interest Category] - [Activities/Hobbies]"
        
        Examples:
        - "Technical Interests - Coding, Reading Tech Blogs"
        - "Outdoor Activities - Hiking, Photography"
        - "Creative Hobbies - Playing Guitar, Painting"
        
        Extract and format only the interests, no bullet points or extra text."""
        
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
        return extract_interest_fallback(message)

def extract_interest_fallback(message: str) -> str:
    """Fallback method to extract and format interests/hobbies"""
    msg_lower = message.lower()
    
    # Extract hobbies/interests
    hobby_patterns = [
        r'hobbies?\s*:\s*([^,\.]+)',
        r'enjoy\s+([^,\.]+)',
        r'like\s+([^,\.]+)',
        r'passionate\s+about\s+([^,\.]+)',
        r'love\s+([^,\.]+)'
    ]
    
    hobbies = []
    for pattern in hobby_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            hobby = match.group(1).strip().title()
            if hobby not in hobbies:
                hobbies.append(hobby)
    
    # Extract category
    category_patterns = [
        r'technical\s+interests',
        r'outdoor\s+activities',
        r'creative\s+hobbies',
        r'sports',
        r'music'
    ]
    
    category = "Personal Interests"
    for pattern in category_patterns:
        if re.search(pattern, msg_lower):
            category = pattern.title()
            break
    
    if not hobbies:
        return message.strip()
    
    return f"{category} - {', '.join(hobbies)}"

def extract_reference_from_message(message: str) -> str:
    """Extract and format references from chat message"""
    try:
        prompt = f"""Extract reference information from this message and format it properly:
        
        Message: {message}
        
        Format the references as: "[Reference Type] - [Availability/Details]"
        
        Examples:
        - "Professional References - Available upon request"
        - "Academic References - From University Professors"
        - "Industry References - From Previous Employers"
        
        Extract and format only the references, no bullet points or extra text."""
        
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
        return extract_reference_fallback(message)

def extract_reference_fallback(message: str) -> str:
    """Fallback method to extract and format references"""
    msg_lower = message.lower()
    
    # Extract reference type
    ref_patterns = [
        r'professional\s+references',
        r'academic\s+references',
        r'industry\s+references',
        r'work\s+references',
        r'personal\s+references'
    ]
    
    ref_type = "Professional References"
    for pattern in ref_patterns:
        if re.search(pattern, msg_lower):
            ref_type = pattern.title()
            break
    
    # Extract availability
    availability_patterns = [
        r'available\s+upon\s+request',
        r'upon\s+request',
        r'provided\s+upon\s+request',
        r'can\s+provide'
    ]
    
    availability = "Available upon request"
    for pattern in availability_patterns:
        if re.search(pattern, msg_lower):
            availability = "Available upon request"
            break
    
    return f"{ref_type} - {availability}"

def extract_additional_from_message(message: str) -> str:
    """Extract and format additional information from chat message"""
    try:
        prompt = f"""Extract additional information from this message and format it properly:
        
        Message: {message}
        
        Format the additional information as: "[Category] - [Details]"
        
        Examples:
        - "Work Authorization - US Citizen"
        - "Open Source - Active Contributor"
        - "Professional Memberships - IEEE Member"
        
        Extract and format only the additional information, no bullet points or extra text."""
        
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
        return extract_additional_fallback(message)

def extract_additional_fallback(message: str) -> str:
    """Fallback method to extract and format additional information"""
    msg_lower = message.lower()
    
    # Extract category
    category_patterns = [
        r'work\s+authorization',
        r'open\s+source',
        r'professional\s+memberships',
        r'volunteer\s+work',
        r'certifications',
        r'publications'
    ]
    
    category = "Additional Information"
    for pattern in category_patterns:
        if re.search(pattern, msg_lower):
            category = pattern.title()
            break
    
    # Extract details
    details_patterns = [
        r'([^,\.]+)\s+authorization',
        r'([^,\.]+)\s+contributor',
        r'([^,\.]+)\s+member',
        r'([^,\.]+)\s+citizen'
    ]
    
    details = "Details available"
    for pattern in details_patterns:
        match = re.search(pattern, msg_lower)
        if match:
            details = match.group(1).strip().title()
            break
    
    return f"{category} - {details}"

# ===== SECTION DETECTION FUNCTIONS =====

def get_objective_section(cv_content: str) -> str:
    """
    Extract the objective/career goal section from CV content.
    Uses smart regex patterns to detect various objective section headers.
    """
    section_info = find_section_in_cv(cv_content, "objective")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_certifications_section(cv_content: str) -> str:
    """
    Extract the certifications section from CV content.
    Uses smart regex patterns to detect various certification section headers.
    """
    section_info = find_section_in_cv(cv_content, "certifications")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_research_section(cv_content: str) -> str:
    """
    Extract the research section from CV content.
    Uses smart regex patterns to detect various research section headers.
    """
    section_info = find_section_in_cv(cv_content, "research")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_achievements_section(cv_content: str) -> str:
    """
    Extract the achievements section from CV content.
    Uses smart regex patterns to detect various achievement section headers.
    """
    section_info = find_section_in_cv(cv_content, "achievements")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_leadership_section(cv_content: str) -> str:
    """
    Extract the leadership section from CV content.
    Uses smart regex patterns to detect various leadership section headers.
    """
    section_info = find_section_in_cv(cv_content, "leadership")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_volunteer_section(cv_content: str) -> str:
    """
    Extract the volunteer section from CV content.
    Uses smart regex patterns to detect various volunteer section headers.
    """
    section_info = find_section_in_cv(cv_content, "volunteer")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_languages_section(cv_content: str) -> str:
    """
    Extract the languages section from CV content.
    Uses smart regex patterns to detect various language section headers.
    """
    section_info = find_section_in_cv(cv_content, "languages")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_technologies_section(cv_content: str) -> str:
    """
    Extract the technologies section from CV content.
    Uses smart regex patterns to detect various technology section headers.
    """
    section_info = find_section_in_cv(cv_content, "technologies")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_interests_section(cv_content: str) -> str:
    """
    Extract the interests section from CV content.
    Uses smart regex patterns to detect various interest section headers.
    """
    section_info = find_section_in_cv(cv_content, "interests")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

def get_additional_section(cv_content: str) -> str:
    """
    Extract the additional information section from CV content.
    Uses smart regex patterns to detect various additional section headers.
    """
    section_info = find_section_in_cv(cv_content, "additional")
    if section_info and section_info.get('found'):
        # Remove the header line and return only the content
        content_lines = section_info['content'].split('\n')
        if len(content_lines) > 1:
            return '\n'.join(content_lines[1:]).strip()
        return section_info['content'].strip()
    return ""

# ===== NEW CRUD HELPER FUNCTIONS =====

def extract_intelligent_content(message: str) -> tuple[str, str]:
    """
    Intelligently extract main content and auto-detect section from a message.
    Returns (extracted_content, detected_section)
    """
    message_lower = message.lower().strip()
    
    # Auto-detect section based on keywords and patterns
    section_keywords = {
        "skills": ["skill", "programming", "language", "framework", "expertise", "know", "learned", "mastered"],
        "experience": ["experience", "work", "job", "employment", "position", "role", "responsibility", "led", "managed", "developed", "built", "created", "implemented"],
        "education": ["education", "degree", "university", "college", "school", "graduated", "studied", "certification", "course", "diploma", "masters", "bachelors", "phd"],
        "projects": ["project", "built", "created", "developed", "application", "website", "app", "system", "platform"],
        "contact": ["contact", "phone", "email", "linkedin", "address", "location", "portfolio", "website"],
        "objective": ["objective", "goal", "career objective", "professional objective", "aim", "target"],
        "certifications": ["certification", "certified", "license", "credential", "training", "certificate"],
        "research": ["research", "publication", "paper", "thesis", "dissertation", "study", "academic"],
        "achievements": ["achievement", "award", "recognition", "honor", "accomplishment", "success", "milestone", "scholarship"],
        "leadership": ["leadership", "led", "managed", "supervised", "directed", "team lead", "manager"],
        "volunteer": ["volunteer", "community service", "charity", "pro bono", "community work"],
        "languages": ["language", "speak", "fluent", "conversational", "native", "bilingual", "proficient in"],
        "technologies": ["tool", "software", "platform", "system", "technology", "technologies", "git", "docker", "jenkins", "jira", "confluence", "slack", "proficient with", "skilled in"],
        "interests": ["interest", "hobby", "passion", "enjoy", "like", "love", "favorite"],
        "references": ["reference", "referee", "recommendation", "endorsement"],
        "additional": ["additional", "miscellaneous", "other", "extra"]
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
                'contact': ['email', 'phone', 'linkedin', 'address', 'contact'],
                'objective': ['objective', 'goal', 'career objective', 'professional objective'],
                'certifications': ['certification', 'certified', 'license', 'credential', 'training'],
                'research': ['research', 'publication', 'paper', 'thesis', 'dissertation', 'study'],
                'achievements': ['achievement', 'award', 'honor', 'recognition', 'scholarship'],
                'leadership': ['leadership', 'led', 'managed', 'supervised', 'directed'],
                'volunteer': ['volunteer', 'community', 'charity', 'service', 'pro bono'],
                'languages': ['language', 'speak', 'fluent', 'proficient', 'bilingual'],
                'technologies': ['tool', 'software', 'platform', 'system', 'technology'],
                'interests': ['interest', 'hobby', 'passion', 'enjoy', 'like'],
                'references': ['reference', 'referee', 'recommendation', 'endorsement'],
                'additional': ['additional', 'miscellaneous', 'other', 'extra']
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
    # Remove common prefixes for all contact types
    contact_prefixes = [
        'my email is', 'phone number', 'my phone', 'contact', 'address',
        'my name is', 'i am', 'age', 'github', 'twitter', 'facebook', 'instagram',
        'youtube', 'portfolio', 'website', 'gmail', 'outlook', 'yahoo',
        'contact me', 'reach me', 'call me', 'text me', 'whatsapp', 'telegram',
        'discord', 'slack', 'skype', 'zoom', 'meet', 'teams'
    ]
    
    clean_message = message.lower()
    for prefix in contact_prefixes:
        clean_message = re.sub(rf'^{prefix}\s*', '', clean_message)
    
    return clean_message.strip()

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
        
        # Special handling for contact info - also check if contact info exists in the content
        if section_type == 'contact' and not target_section:
            # Check if contact info already exists in the CV content
            cv_content_lower = cv_content.lower()
            contact_indicators = ['@', 'phone:', 'email:', 'linkedin.com', 'github.com', 'gmail.com', 'outlook.com', 'yahoo.com']
            if any(indicator in cv_content_lower for indicator in contact_indicators):
                print(f"📝 Contact info already exists in CV content, skipping creation")
                return cv_content
        
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
                'contact': 'CONTACT INFORMATION',
                'objective': 'CAREER OBJECTIVE',
                'certifications': 'CERTIFICATIONS',
                'research': 'RESEARCH',
                'achievements': 'ACHIEVEMENTS',
                'leadership': 'LEADERSHIP',
                'volunteer': 'VOLUNTEER WORK',
                'languages': 'LANGUAGES',
                'technologies': 'TECHNOLOGIES',
                'interests': 'INTERESTS',
                'references': 'REFERENCES',
                'additional': 'ADDITIONAL INFORMATION'
            }
            
            header = section_headers.get(section_type, section_type.upper())
            full_content = [f"\n{header}"] + new_content + [""]
            
            # Determine best insertion point based on standard CV order
            # Contact info should be near the top, after name but before other sections
            if section_type == 'contact':
                # For contact info, insert after the first few lines (name and any existing contact info)
                insert_pos = 0
                for i, line in enumerate(cv_lines[:10]):  # Check first 10 lines
                    line_stripped = line.strip()
                    # If we find a section header or if we've passed the name/contact area
                    if (line_stripped and 
                        (line_stripped.isupper() and len(line_stripped) > 3) or
                        any(keyword in line_stripped.upper() for keyword in ['EDUCATION', 'EXPERIENCE', 'SKILLS', 'OBJECTIVE'])):
                        insert_pos = i
                        break
                    # If we find existing contact info, don't add more
                    if any(contact_indicator in line_stripped.lower() for contact_indicator in ['@', 'phone:', 'email:', 'linkedin.com', 'github.com']):
                        # Contact info already exists, don't create new section
                        print(f"📝 Contact info already exists, skipping creation")
                        return cv_content
                # If we didn't find a section header, insert after first few lines
                if insert_pos == 0:
                    insert_pos = min(5, len(cv_lines))
            else:
                # For other sections, use standard CV order
                cv_order = ['objective', 'skills', 'experience', 'education', 'projects', 'certifications', 'research', 'achievements', 'leadership', 'volunteer', 'languages', 'technologies', 'interests', 'references', 'additional']
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
    
    # Reorganize CV content to ensure proper section placement
    original_cv = reorganize_cv_content(original_cv)
    
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
    
    # Parse CV sections first
    sections = parse_cv_sections(original_cv)
    cv_lines = original_cv.split('\n')
    
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
        ],
        'contact': [
            r'[_\-\s]*CONTACT[_\-\s]*',
            r'[_\-\s]*CONTACT\s+INFORMATION[_\-\s]*',
            r'[_\-\s]*CONTACT\s+DETAILS[_\-\s]*',
            r'[_\-\s]*PERSONAL\s+INFORMATION[_\-\s]*',
            r'[_\-\s]*CONTACT\s+INFO[_\-\s]*'
        ],
        'objective': [
            r'[_\-\s]*OBJECTIVE[_\-\s]*',
            r'[_\-\s]*CAREER\s+OBJECTIVE[_\-\s]*',
            r'[_\-\s]*PROFESSIONAL\s+OBJECTIVE[_\-\s]*',
            r'[_\-\s]*GOAL[_\-\s]*',
            r'[_\-\s]*CAREER\s+GOAL[_\-\s]*'
        ],
        'certifications': [
            r'[_\-\s]*CERTIFICATIONS[_\-\s]*',
            r'[_\-\s]*CERTIFICATES[_\-\s]*',
            r'[_\-\s]*PROFESSIONAL\s+CERTIFICATIONS[_\-\s]*',
            r'[_\-\s]*LICENSES[_\-\s]*',
            r'[_\-\s]*CREDENTIALS[_\-\s]*',
            r'[_\-\s]*TRAINING[_\-\s]*'
        ],
        'research': [
            r'[_\-\s]*RESEARCH[_\-\s]*',
            r'[_\-\s]*PUBLICATIONS[_\-\s]*',
            r'[_\-\s]*RESEARCH\s+PAPERS[_\-\s]*',
            r'[_\-\s]*ACADEMIC\s+PUBLICATIONS[_\-\s]*',
            r'[_\-\s]*THESIS[_\-\s]*',
            r'[_\-\s]*DISSERTATION[_\-\s]*',
            r'[_\-\s]*STUDIES[_\-\s]*'
        ],
        'achievements': [
            r'[_\-\s]*ACHIEVEMENTS[_\-\s]*',
            r'[_\-\s]*AWARDS[_\-\s]*',
            r'[_\-\s]*HONORS[_\-\s]*',
            r'[_\-\s]*RECOGNITIONS[_\-\s]*',
            r'[_\-\s]*SCHOLARSHIPS[_\-\s]*',
            r'[_\-\s]*ACCOMPLISHMENTS[_\-\s]*'
        ],
        'leadership': [
            r'[_\-\s]*LEADERSHIP[_\-\s]*',
            r'[_\-\s]*MANAGEMENT[_\-\s]*',
            r'[_\-\s]*TEAM\s+LEADERSHIP[_\-\s]*',
            r'[_\-\s]*SUPERVISION[_\-\s]*',
            r'[_\-\s]*DIRECTION[_\-\s]*'
        ],
        'volunteer': [
            r'[_\-\s]*VOLUNTEER[_\-\s]*',
            r'[_\-\s]*VOLUNTEER\s+WORK[_\-\s]*',
            r'[_\-\s]*COMMUNITY\s+SERVICE[_\-\s]*',
            r'[_\-\s]*CHARITY\s+WORK[_\-\s]*',
            r'[_\-\s]*PRO\s+BONO[_\-\s]*'
        ],
        'languages': [
            r'[_\-\s]*LANGUAGES[_\-\s]*',
            r'[_\-\s]*LANGUAGE\s+SKILLS[_\-\s]*',
            r'[_\-\s]*SPOKEN\s+LANGUAGES[_\-\s]*',
            r'[_\-\s]*LINGUISTIC\s+SKILLS[_\-\s]*'
        ],
        'technologies': [
            r'[_\-\s]*TECHNOLOGIES[_\-\s]*',
            r'[_\-\s]*TOOLS[_\-\s]*',
            r'[_\-\s]*SOFTWARE[_\-\s]*',
            r'[_\-\s]*PLATFORMS[_\-\s]*',
            r'[_\-\s]*SYSTEMS[_\-\s]*'
        ],
        'interests': [
            r'[_\-\s]*INTERESTS[_\-\s]*',
            r'[_\-\s]*HOBBIES[_\-\s]*',
            r'[_\-\s]*PERSONAL\s+INTERESTS[_\-\s]*',
            r'[_\-\s]*PASSIONS[_\-\s]*'
        ],
        'references': [
            r'[_\-\s]*REFERENCES[_\-\s]*',
            r'[_\-\s]*REFEREES[_\-\s]*',
            r'[_\-\s]*RECOMMENDATIONS[_\-\s]*',
            r'[_\-\s]*ENDORSEMENTS[_\-\s]*'
        ],
        'additional': [
            r'[_\-\s]*ADDITIONAL[_\-\s]*',
            r'[_\-\s]*MISCELLANEOUS[_\-\s]*',
            r'[_\-\s]*OTHER[_\-\s]*',
            r'[_\-\s]*EXTRA[_\-\s]*'
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
        ],
        'contact': [
            r'^\s*CONTACT\s*$', r'^\s*CONTACT\s+INFORMATION\s*$', r'^\s*CONTACT\s+DETAILS\s*$',
            r'^\s*PERSONAL\s+INFORMATION\s*$', r'^\s*CONTACT\s+INFO\s*$',
            r'^\s*_+\s*CONTACT\s*_+\s*$', r'^\s*_+\s*CONTACT\s+INFORMATION\s*_+\s*$'
        ],
        'objective': [
            r'^\s*OBJECTIVE\s*$', r'^\s*CAREER\s+OBJECTIVE\s*$', r'^\s*PROFESSIONAL\s+OBJECTIVE\s*$',
            r'^\s*GOAL\s*$', r'^\s*CAREER\s+GOAL\s*$',
            r'^\s*_+\s*OBJECTIVE\s*_+\s*$', r'^\s*_+\s*CAREER\s+OBJECTIVE\s*_+\s*$'
        ],
        'certifications': [
            r'^\s*CERTIFICATIONS\s*$', r'^\s*CERTIFICATES\s*$', r'^\s*PROFESSIONAL\s+CERTIFICATIONS\s*$',
            r'^\s*LICENSES\s*$', r'^\s*CREDENTIALS\s*$', r'^\s*TRAINING\s*$',
            r'^\s*_+\s*CERTIFICATIONS\s*_+\s*$'
        ],
        'research': [
            r'^\s*RESEARCH\s*$', r'^\s*PUBLICATIONS\s*$', r'^\s*RESEARCH\s+PAPERS\s*$',
            r'^\s*ACADEMIC\s+PUBLICATIONS\s*$', r'^\s*THESIS\s*$', r'^\s*DISSERTATION\s*$',
            r'^\s*STUDIES\s*$', r'^\s*_+\s*RESEARCH\s*_+\s*$'
        ],
        'achievements': [
            r'^\s*ACHIEVEMENTS\s*$', r'^\s*AWARDS\s*$', r'^\s*HONORS\s*$',
            r'^\s*RECOGNITIONS\s*$', r'^\s*SCHOLARSHIPS\s*$', r'^\s*ACCOMPLISHMENTS\s*$',
            r'^\s*_+\s*ACHIEVEMENTS\s*_+\s*$'
        ],
        'leadership': [
            r'^\s*LEADERSHIP\s*$', r'^\s*MANAGEMENT\s*$', r'^\s*TEAM\s+LEADERSHIP\s*$',
            r'^\s*SUPERVISION\s*$', r'^\s*DIRECTION\s*$',
            r'^\s*_+\s*LEADERSHIP\s*_+\s*$'
        ],
        'volunteer': [
            r'^\s*VOLUNTEER\s*$', r'^\s*VOLUNTEER\s+WORK\s*$', r'^\s*COMMUNITY\s+SERVICE\s*$',
            r'^\s*CHARITY\s+WORK\s*$', r'^\s*PRO\s+BONO\s*$',
            r'^\s*_+\s*VOLUNTEER\s*_+\s*$'
        ],
        'languages': [
            r'^\s*LANGUAGES\s*$', r'^\s*LANGUAGE\s+SKILLS\s*$', r'^\s*SPOKEN\s+LANGUAGES\s*$',
            r'^\s*LINGUISTIC\s+SKILLS\s*$',
            r'^\s*_+\s*LANGUAGES\s*_+\s*$'
        ],
        'technologies': [
            r'^\s*TECHNOLOGIES\s*$', r'^\s*TOOLS\s*$', r'^\s*SOFTWARE\s*$',
            r'^\s*PLATFORMS\s*$', r'^\s*SYSTEMS\s*$',
            r'^\s*_+\s*TECHNOLOGIES\s*_+\s*$'
        ],
        'interests': [
            r'^\s*INTERESTS\s*$', r'^\s*HOBBIES\s*$', r'^\s*PERSONAL\s+INTERESTS\s*$',
            r'^\s*PASSIONS\s*$',
            r'^\s*_+\s*INTERESTS\s*_+\s*$'
        ],
        'references': [
            r'^\s*REFERENCES\s*$', r'^\s*REFEREES\s*$', r'^\s*RECOMMENDATIONS\s*$',
            r'^\s*ENDORSEMENTS\s*$',
            r'^\s*_+\s*REFERENCES\s*_+\s*$'
        ],
        'additional': [
            r'^\s*ADDITIONAL\s*$', r'^\s*MISCELLANEOUS\s*$', r'^\s*OTHER\s*$',
            r'^\s*EXTRA\s*$',
            r'^\s*_+\s*ADDITIONAL\s*_+\s*$'
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
    return {"message": "CV Updater API is running", "status": "healthy"}

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify backend and database connectivity"""
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Test database connection
            cursor.execute("SELECT COUNT(*) FROM manual_projects")
            project_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cvs")
            cv_count = cursor.fetchone()[0]
            
            return {
                "status": "healthy",
                "database": "connected",
                "projects_count": project_count,
                "cvs_count": cv_count,
                "timestamp": datetime.now().isoformat(),
                "cors_origins": os.getenv("CORS_ORIGINS", "not_set"),
                "allowed_origins": allowed_origins
            }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/test-download")
async def test_download_endpoint(request: ProjectSelectionRequest):
    """Test endpoint to debug download issues"""
    return {
        "message": "Test endpoint working",
        "received_ids": request.selected_project_ids,
        "ids_type": str(type(request.selected_project_ids)),
        "ids_length": len(request.selected_project_ids) if request.selected_project_ids else 0
        }

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

@app.post("/upload-cv-for-projects/")
async def upload_cv_for_projects(
    file: UploadFile = File(...),
    extracted_text: str = Form(None)
):
    """Upload CV specifically for project extraction - only extracts projects section"""
    try:
        print(f"🔄 Starting project extraction from CV: {file.filename}")
        
        # Use extracted_text if provided, else extract from file
        if extracted_text:
            cv_text = extracted_text
        else:
            # For project extraction, we need to extract text without cleaning
            # to preserve the formatting that the project extractor needs
            content = file.file.read()
            print(f"📄 Processing file: {file.filename} ({len(content)} bytes)")
            
            if not content:
                raise HTTPException(status_code=400, detail="File is empty or corrupted")
            
            if file.filename.lower().endswith('.pdf'):
                cv_text = extract_text_from_pdf(content)
            elif file.filename.lower().endswith('.docx'):
                cv_text = docx2txt.process(BytesIO(content))
            elif file.filename.lower().endswith('.txt'):
                # Handle different encodings for text files
                try:
                    cv_text = content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        cv_text = content.decode('utf-8')
                    except UnicodeDecodeError:
                        cv_text = content.decode('utf-8', errors='ignore')
            else:
                raise HTTPException(status_code=400, detail="Unsupported file format. Please use PDF, DOCX, or TXT files.")
            
            # For project extraction, we don't clean the text to preserve formatting
            cv_text = cv_text.strip()
        
        if not cv_text or len(cv_text.strip()) < 50:
            raise HTTPException(
                status_code=400, 
                detail="The uploaded file doesn't contain enough readable text. Please ensure your CV has substantial content."
            )
        
        print(f"📄 CV content preview: {cv_text[:200]}...")
        
        with get_db_cursor_context() as (cursor, conn):
            # Generate a title from filename
            title = file.filename.replace('.pdf', '').replace('.docx', '').replace('.txt', '').replace('_', ' ').title()
            
            # Clear all existing projects when new CV is uploaded for project extraction
            cursor.execute("DELETE FROM manual_projects")
            print("🗑️ Cleared existing projects for new CV upload")
            
            # Extract ONLY projects from CV using the enhanced project extractor
            try:
                from project_extractor import extract_and_format_projects
                print(f"📄 CV content length: {len(cv_text)}")
                print(f"📄 CV content preview: {cv_text[:500]}...")
                
                extracted_projects = extract_and_format_projects(cv_text)
                print(f"🔍 Extracted {len(extracted_projects)} projects from CV using enhanced extractor.")
                
                # Debug: Check if projects were extracted
                if len(extracted_projects) == 0:
                    print("⚠️ No projects extracted! Checking CV content...")
                    if 'PROJECTS' in cv_text.upper():
                        print("✅ 'PROJECTS' keyword found in CV")
                    else:
                        print("❌ 'PROJECTS' keyword NOT found in CV")
                else:
                    print(f"✅ Successfully extracted {len(extracted_projects)} projects")
                    
            except Exception as e:
                print(f"❌ Error in project extraction: {e}")
                import traceback
                traceback.print_exc()
                extracted_projects = []
            
            # Debug: Print extracted projects
            for i, project in enumerate(extracted_projects):
                print(f"  Project {i+1}: {project.get('title', 'N/A')}")
                print(f"    Description: {project.get('description', 'N/A')}")
                print(f"    Technologies: {project.get('technologies', [])}")
            
            # Insert extracted projects into database
            for project in extracted_projects:
                cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", (json.dumps(project),))
            print(f"✅ Inserted {len(extracted_projects)} projects into manual_projects table.")
            
            # Verify projects were inserted
            cursor.execute("SELECT COUNT(*) FROM manual_projects")
            inserted_count = cursor.fetchone()[0]
            print(f"📊 Verified {inserted_count} projects in database")
        
        return JSONResponse(status_code=200, content={
            "message": f"✅ Successfully extracted {len(extracted_projects)} projects from your CV!", 
            "filename": file.filename,
            "title": title,
            "projects_extracted": len(extracted_projects),
            "extracted_projects": extracted_projects,  # Return the actual projects
            "status": "projects_extracted"
        })
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        print(f"❌ Project extraction error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Project extraction failed: {str(e)}")

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
            elif category in ["SKILL_ADD", "EXPERIENCE_ADD", "EDUCATION_ADD", "PROJECT_ADD", "PROFILE_ADD", "CONTACT_ADD", 
                             "OBJECTIVE_ADD", "CERTIFICATION_ADD", "RESEARCH_ADD", "ACHIEVEMENT_ADD", "LEADERSHIP_ADD", 
                             "VOLUNTEER_ADD", "LANGUAGE_ADD", "TECHNOLOGY_ADD", "INTEREST_ADD", "REFERENCE_ADD", "ADDITIONAL_ADD"]:
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
                        "CONTACT_ADD": "contact",
                        "OBJECTIVE_ADD": "objective",
                        "CERTIFICATION_ADD": "certifications",
                        "RESEARCH_ADD": "research",
                        "ACHIEVEMENT_ADD": "achievements",
                        "LEADERSHIP_ADD": "leadership",
                        "VOLUNTEER_ADD": "volunteer",
                        "LANGUAGE_ADD": "languages",
                        "TECHNOLOGY_ADD": "technologies",
                        "INTEREST_ADD": "interests",
                        "REFERENCE_ADD": "references",
                        "ADDITIONAL_ADD": "additional"
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
            elif category in ["CV_SHOW", "SKILL_SHOW", "EXPERIENCE_SHOW", "EDUCATION_SHOW", "PROJECT_SHOW", "CONTACT_SHOW",
                             "OBJECTIVE_SHOW", "CERTIFICATION_SHOW", "RESEARCH_SHOW", "ACHIEVEMENT_SHOW", "LEADERSHIP_SHOW",
                             "VOLUNTEER_SHOW", "LANGUAGE_SHOW", "TECHNOLOGY_SHOW", "INTEREST_SHOW", "REFERENCE_SHOW", "ADDITIONAL_SHOW"]:
                if cv_content:
                    section_map = {
                        "CV_SHOW": "cv",
                        "SKILL_SHOW": "skills",
                        "EXPERIENCE_SHOW": "experience",
                        "EDUCATION_SHOW": "education",
                        "PROJECT_SHOW": "projects",
                        "CONTACT_SHOW": "contact",
                        "OBJECTIVE_SHOW": "objective",
                        "CERTIFICATION_SHOW": "certifications",
                        "RESEARCH_SHOW": "research",
                        "ACHIEVEMENT_SHOW": "achievements",
                        "LEADERSHIP_SHOW": "leadership",
                        "VOLUNTEER_SHOW": "volunteer",
                        "LANGUAGE_SHOW": "languages",
                        "TECHNOLOGY_SHOW": "technologies",
                        "INTEREST_SHOW": "interests",
                        "REFERENCE_SHOW": "references",
                        "ADDITIONAL_SHOW": "additional"
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
            elif category in ["SKILL_UPDATE", "EXPERIENCE_UPDATE", "EDUCATION_UPDATE", "PROJECT_UPDATE", "PROFILE_UPDATE", "CONTACT_UPDATE",
                             "OBJECTIVE_UPDATE", "CERTIFICATION_UPDATE", "RESEARCH_UPDATE", "ACHIEVEMENT_UPDATE", "LEADERSHIP_UPDATE",
                             "VOLUNTEER_UPDATE", "LANGUAGE_UPDATE", "TECHNOLOGY_UPDATE", "INTEREST_UPDATE", "REFERENCE_UPDATE", "ADDITIONAL_UPDATE"]:
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
                        "CONTACT_UPDATE": "contact",
                        "OBJECTIVE_UPDATE": "objective",
                        "CERTIFICATION_UPDATE": "certifications",
                        "RESEARCH_UPDATE": "research",
                        "ACHIEVEMENT_UPDATE": "achievements",
                        "LEADERSHIP_UPDATE": "leadership",
                        "VOLUNTEER_UPDATE": "volunteer",
                        "LANGUAGE_UPDATE": "languages",
                        "TECHNOLOGY_UPDATE": "technologies",
                        "INTEREST_UPDATE": "interests",
                        "REFERENCE_UPDATE": "references",
                        "ADDITIONAL_UPDATE": "additional"
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
            elif category in ["SKILL_DELETE", "EXPERIENCE_DELETE", "EDUCATION_DELETE", "PROJECT_DELETE", "CONTACT_DELETE",
                             "OBJECTIVE_DELETE", "CERTIFICATION_DELETE", "RESEARCH_DELETE", "ACHIEVEMENT_DELETE", "LEADERSHIP_DELETE",
                             "VOLUNTEER_DELETE", "LANGUAGE_DELETE", "TECHNOLOGY_DELETE", "INTEREST_DELETE", "REFERENCE_DELETE", "ADDITIONAL_DELETE"]:
                if cv_content:
                    section_map = {
                        "SKILL_DELETE": "skills",
                        "EXPERIENCE_DELETE": "experience",
                        "EDUCATION_DELETE": "education",
                        "PROJECT_DELETE": "projects", 
                        "CONTACT_DELETE": "contact",
                        "OBJECTIVE_DELETE": "objective",
                        "CERTIFICATION_DELETE": "certifications",
                        "RESEARCH_DELETE": "research",
                        "ACHIEVEMENT_DELETE": "achievements",
                        "LEADERSHIP_DELETE": "leadership",
                        "VOLUNTEER_DELETE": "volunteer",
                        "LANGUAGE_DELETE": "languages",
                        "TECHNOLOGY_DELETE": "technologies",
                        "INTEREST_DELETE": "interests",
                        "REFERENCE_DELETE": "references",
                        "ADDITIONAL_DELETE": "additional"
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
            
            # ===== PROJECT MANAGEMENT COMMANDS =====
            elif category == "PROJECT_EXTRACT":
                try:
                    # Extract projects from CV
                    from project_extractor import extract_and_format_projects
                    projects = extract_and_format_projects(cv_content)
                    
                    # Clear existing projects and store new ones
                    cursor.execute("DELETE FROM manual_projects")
                    
                    for project in projects:
                        project_data = {
                            'id': project['id'],
                            'title': project['title'],
                            'description': project['description'],
                            'duration': project['duration'],
                            'technologies': project['technologies'],
                            'highlights': project['highlights'],
                            'role': project['role'],
                            'created_at': datetime.now().isoformat()
                        }
                        
                        cursor.execute(
                            "INSERT INTO manual_projects (project_data) VALUES (?)",
                            (json.dumps(project_data),)
                        )
                    
                    response_text = f"✅ Extracted {len(projects)} projects from your CV!\n\n"
                    for i, project in enumerate(projects, 1):
                        response_text += f"{i}. **{project['title']}** ({project['duration']})\n"
                        response_text += f"   {project['description']}\n"
                        response_text += f"   Tech: {', '.join(project['technologies'])}\n\n"
                    
                    cv_updated = True
                    
                except Exception as e:
                    response_text = f"❌ Error extracting projects: {str(e)}"
            
            elif category == "PROJECT_SHOW":
                try:
                    cursor.execute("SELECT project_data FROM manual_projects ORDER BY created_at DESC")
                    projects = cursor.fetchall()
                    
                    if not projects:
                        response_text = "📋 No projects found. Use 'Extract projects from CV' to get started!"
                    else:
                        response_text = f"📋 **Your Projects ({len(projects)} total):**\n\n"
                        for i, (project_json,) in enumerate(projects, 1):
                            try:
                                project = json.loads(project_json)
                                response_text += f"{i}. **{project['title']}** ({project['duration']})\n"
                                response_text += f"   {project['description']}\n"
                                if project['technologies']:
                                    response_text += f"   Tech: {', '.join(project['technologies'])}\n"
                                if project['highlights']:
                                    response_text += f"   Highlights: {len(project['highlights'])} items\n"
                                response_text += "\n"
                            except:
                                continue
                
                except Exception as e:
                    response_text = f"❌ Error showing projects: {str(e)}"
            
            elif category == "PROJECT_DELETE":
                try:
                    # Extract project title or index from message
                    project_identifier = extracted_info.strip()
                    
                    cursor.execute("SELECT project_data FROM manual_projects ORDER BY created_at DESC")
                    projects = cursor.fetchall()
                    
                    if not projects:
                        response_text = "❌ No projects found to delete."
                    else:
                        deleted = False
                        
                        # Try to delete by index
                        try:
                            index = int(project_identifier) - 1
                            if 0 <= index < len(projects):
                                project_json = projects[index][0]
                                project = json.loads(project_json)
                                project_id = project.get('id', '')
                                
                                cursor.execute("DELETE FROM manual_projects WHERE project_data LIKE ?", (f'%"id": "{project_id}"%',))
                                response_text = f"✅ Deleted project: {project['title']}"
                                deleted = True
                        except ValueError:
                            pass
                        
                        # Try to delete by title
                        if not deleted:
                            cursor.execute("DELETE FROM manual_projects WHERE project_data LIKE ?", (f'%"title": "{project_identifier}"%',))
                            if cursor.rowcount > 0:
                                response_text = f"✅ Deleted project: {project_identifier}"
                                deleted = True
                            else:
                                response_text = f"❌ Project '{project_identifier}' not found."
                
                except Exception as e:
                    response_text = f"❌ Error deleting project: {str(e)}"
            
            elif category == "CV_DOWNLOAD":
                response_text = "📄 Your CV download is ready! Check the download section or use the download button."
            
            elif category == "CV_CLEANUP":
                try:
                    # Clean up CV content
                    cleaned_cv = clean_cv_content(cv_content)
                    
                    if cleaned_cv != cv_content:
                        cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (cleaned_cv,))
                        cv_updated = True
                        response_text = "🧹 CV cleaned up successfully! Removed duplicates and formatting issues."
                    else:
                        response_text = "✅ CV is already clean! No changes needed."
                
                except Exception as e:
                    response_text = f"❌ Error cleaning up CV: {str(e)}"
            
            elif category == "LINKEDIN_BLOG":
                try:
                    # Get all projects
                    cursor.execute("SELECT project_data FROM manual_projects ORDER BY created_at DESC")
                    projects = cursor.fetchall()
                    
                    if not projects:
                        response_text = "❌ No projects found. Please extract projects from your CV first."
                    else:
                        # Generate LinkedIn blog post
                        blog_content = generate_linkedin_blog_from_projects(projects)
                        
                        response_text = f"""📝 **LinkedIn Blog Post Generated Successfully!**

**Blog Content:**
{blog_content}

**💡 Tips for posting:**
• Copy the content above
• Paste it into LinkedIn
• Add relevant hashtags (#softwareengineering #webdevelopment #projects)
• Tag relevant technologies/companies
• Engage with comments

**🎯 Ready to share your projects with the world!**"""
                
                except Exception as e:
                    response_text = f"❌ Error generating LinkedIn blog: {str(e)}"
            
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
                formatted_lines.append(clean_header)  # Remove emoji and underlines
            else:
                # Clean up bullet points and formatting
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    formatted_lines.append(f"• {line[1:].strip()}")  # Keep bullet points clean
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
            
            # Update CV content after adding project
            updated_cv = generate_cv_with_projects(cursor, conn)
            cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
            
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
            
            # Update CV content after adding project
            updated_cv = generate_cv_with_projects(cursor, conn)
            cursor.execute("UPDATE cvs SET current_content = ?, updated_at = CURRENT_TIMESTAMP WHERE is_active = TRUE", (updated_cv,))
            
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
        # Clean Zero Width Space characters
        cv_content = cv_content.replace('\u200B', '')
        lines = cv_content.split('\n')
        
        # Helper function to check if a line is a potential section header
        def is_potential_header_reorganize(line: str) -> bool:
            """Check if a line is a potential section header"""
            line_upper = line.upper().strip()
            section_keywords = [
                'EDUCATION', 'EXPERIENCE', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS',
                'PROFILE', 'SUMMARY', 'OBJECTIVE', 'ACHIEVEMENTS', 'LEADERSHIP',
                'VOLUNTEER', 'LANGUAGES', 'TECHNOLOGIES', 'INTERESTS', 'REFERENCES',
                'ADDITIONAL', 'ACTIVITIES', 'AWARDS', 'PUBLICATIONS', 'RESEARCH'
            ]
            return any(keyword in line_upper for keyword in section_keywords)
        
        # Extract name and contact info from the very beginning
        name_and_contact = []
        remaining_lines = []
        found_first_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # If we haven't found the first section header yet, collect as name/contact
            if not found_first_section and line_stripped:
                if is_potential_header_reorganize(line_stripped):
                    found_first_section = True
                    remaining_lines.append(line_stripped)
                else:
                    name_and_contact.append(line_stripped)
            else:
                remaining_lines.append(line_stripped)
        
        # Parse sections from remaining content
        sections = parse_cv_sections('\n'.join(remaining_lines))
        
        # Rebuild CV with proper structure
        rebuilt_cv = []
        
        # Always start with name and contact info
        if name_and_contact:
            rebuilt_cv.extend(name_and_contact)
            rebuilt_cv.append('')
        
        # Add sections in order
        section_order = ['profile_summary', 'skills', 'experience', 'education', 'projects', 'certifications']
        
        for section_name in section_order:
            if section_name in sections:
                section_info = sections[section_name]
                start_line = section_info['start_line']
                end_line = section_info['end_line']
                
                # Add section header
                rebuilt_cv.append(section_info['header'])
                
                # Add section content
                for j in range(start_line + 1, end_line + 1):
                    if j < len(remaining_lines) and remaining_lines[j].strip():
                        rebuilt_cv.append(remaining_lines[j])
                
                rebuilt_cv.append('')
        
        # Add any remaining sections not in the standard order
        for section_name, section_info in sections.items():
            if section_name not in section_order:
                start_line = section_info['start_line']
                end_line = section_info['end_line']
                
                # Add section header
                rebuilt_cv.append(section_info['header'])
                
                # Add section content
                for j in range(start_line + 1, end_line + 1):
                    if j < len(remaining_lines) and remaining_lines[j].strip():
                        rebuilt_cv.append(remaining_lines[j])
                
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
    """Generate a modern, professional PDF using ReportLab"""
    buffer = BytesIO()
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
        from reportlab.lib.colors import HexColor, black, white
        from reportlab.lib.units import inch
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        # Get base styles
        styles = getSampleStyleSheet()
        
        # Define custom styles
        accent_color = HexColor('#667eea')
        
        header_style = ParagraphStyle(
            'Header', parent=styles['Heading1'], fontSize=24, spaceAfter=8, alignment=TA_CENTER, textColor=accent_color
        )
        
        contact_style = ParagraphStyle(
            'Contact', parent=styles['Normal'], fontSize=10, spaceAfter=8, alignment=TA_CENTER, textColor=black
        )
        
        section_style = ParagraphStyle(
            'Section', parent=styles['Heading2'], fontSize=16, spaceAfter=6, spaceBefore=8, textColor=accent_color
        )
        
        job_title_style = ParagraphStyle(
            'JobTitle', parent=styles['Heading3'], fontSize=14, spaceAfter=6, textColor=black
        )
        
        date_style = ParagraphStyle(
            'Date', parent=styles['Normal'], fontSize=10, spaceAfter=8, textColor=accent_color
        )
        
        body_style = ParagraphStyle(
            'Body', parent=styles['Normal'], fontSize=11, spaceAfter=4, alignment=TA_JUSTIFY
        )
        
        skill_style = ParagraphStyle(
            'Skill', parent=styles['Normal'], fontSize=10, spaceAfter=3, textColor=accent_color
        )
        
        bullet_style = ParagraphStyle(
            'Bullet', parent=styles['Normal'], fontSize=10, spaceAfter=2, leftIndent=20
        )
        
        # Build PDF content
        story = []
        
        # Parse CV content
        lines = cv_content.split('\n')
        name = "PROFESSIONAL CV"
        contact_info = []
        sections = []
        current_section = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if line.startswith('📋') or '─' in line or line.startswith('='):
                continue
            if i == 0 and not any(keyword in line.upper() for keyword in ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS']):
                name = line.upper()
            elif '@' in line or 'http' in line or any(char.isdigit() for char in line):
                contact_info.append(line)
            elif (line.isupper() and len(line) > 3) or any(keyword in line.upper() for keyword in ['PROFILE', 'SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION', 'PROJECTS', 'ABOUT']):
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
        
        # Add header
        story.append(Paragraph(name, header_style))
        if contact_info:
            contact_text = " | ".join(contact_info)
            story.append(Paragraph(contact_text, contact_style))
        story.append(Spacer(1, 12))
        
        # Add divider
        divider_style = ParagraphStyle(
            'Divider', parent=styles['Normal'], fontSize=2, spaceAfter=8, spaceBefore=8, alignment=TA_CENTER, textColor=accent_color
        )
        story.append(Paragraph("_" * 60, divider_style))
        
        # Process sections
        inserted_projects = False
        for section in sections:
            if not section:
                continue
            section_title = section[0]
            section_content = section[1:] if len(section) > 1 else []
            
            if 'PROJECTS' in section_title.upper():
                if projects and len(projects) > 0:
                    # Replace this section with the selected projects
                    story.append(Paragraph('Projects', section_style))
                    underline_style = ParagraphStyle(
                        'Underline', parent=styles['Normal'], fontSize=1, spaceAfter=15, spaceBefore=0, alignment=TA_LEFT, textColor=accent_color
                    )
                    story.append(Paragraph("_" * 50, underline_style))
                    
                    for i, project in enumerate(projects, 1):
                        title = project.get('title', f'Project {i}')
                        duration = project.get('duration', '')
                        description = project.get('description', '')
                        technologies = project.get('technologies', [])
                        highlights = project.get('highlights', [])
                        
                        story.append(Paragraph(f"{i}. {title}", job_title_style))
                        if duration:
                            story.append(Paragraph(f"Duration: {duration}", date_style))
                        if description:
                            story.append(Paragraph(f"{description}", body_style))
                        if technologies:
                            tech_str = ', '.join(technologies) if isinstance(technologies, list) else str(technologies)
                            story.append(Paragraph(f"Technologies: {tech_str}", skill_style))
                        if highlights:
                            story.append(Paragraph("Key Highlights:", body_style))
                            if isinstance(highlights, list):
                                for highlight in highlights:
                                    story.append(Paragraph(f"• {highlight}", bullet_style))
                            else:
                                story.append(Paragraph(f"• {highlights}", bullet_style))
                        story.append(Spacer(1, 8))
                    story.append(Spacer(1, 15))
                    inserted_projects = True
                # If projects are provided, skip the original section_content
                continue
            else:
                # Add other sections
                section_text = section_title.replace('_', ' ').title()
                story.append(Paragraph(section_text, section_style))
                underline_style = ParagraphStyle(
                    'Underline', parent=styles['Normal'], fontSize=1, spaceAfter=15, spaceBefore=0, alignment=TA_LEFT, textColor=accent_color
                )
                story.append(Paragraph("_" * 50, underline_style))
                
                for line in section_content:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                        clean_line = line[1:].strip()
                        if clean_line:
                            story.append(Paragraph(f"• {clean_line}", bullet_style))
                    elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.'):
                        story.append(Paragraph(line, bullet_style))
                    elif ':' in line and len(line.split(':')) == 2:
                        key, value = line.split(':', 1)
                        if key.strip() and value.strip():
                            story.append(Paragraph(f"<b>{key.strip()}:</b> {value.strip()}", body_style))
                        else:
                            story.append(Paragraph(line, body_style))
                    else:
                        if line and not line.startswith('Generated on'):
                            story.append(Paragraph(line, body_style))
                story.append(Spacer(1, 15))
        # If there was no projects section but projects are provided, add it at the end
        if projects and len(projects) > 0 and not inserted_projects:
            story.append(Paragraph('Projects', section_style))
            underline_style = ParagraphStyle(
                'Underline', parent=styles['Normal'], fontSize=1, spaceAfter=15, spaceBefore=0, alignment=TA_LEFT, textColor=accent_color
            )
            story.append(Paragraph("_" * 50, underline_style))
            for i, project in enumerate(projects, 1):
                title = project.get('title', f'Project {i}')
                duration = project.get('duration', '')
                description = project.get('description', '')
                technologies = project.get('technologies', [])
                highlights = project.get('highlights', [])
                story.append(Paragraph(f"{i}. {title}", job_title_style))
                if duration:
                    story.append(Paragraph(f"Duration: {duration}", date_style))
                if description:
                    story.append(Paragraph(f"{description}", body_style))
                if technologies:
                    tech_str = ', '.join(technologies) if isinstance(technologies, list) else str(technologies)
                    story.append(Paragraph(f"Technologies: {tech_str}", skill_style))
                if highlights:
                    story.append(Paragraph("Key Highlights:", body_style))
                    if isinstance(highlights, list):
                        for highlight in highlights:
                            story.append(Paragraph(f"• {highlight}", bullet_style))
                    else:
                        story.append(Paragraph(f"• {highlights}", bullet_style))
                story.append(Spacer(1, 8))
            story.append(Spacer(1, 15))
        
        # Add footer
        story.append(Spacer(1, 40))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=accent_color,
        )
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y')}", footer_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        # Fallback to simple text PDF
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

@app.post("/cv/download-with-selected-projects")
async def download_cv_with_selected_projects(request: ProjectSelectionRequest):
    print(f"🔍 Received request: {request}")
    print(f"🔍 Selected project IDs: {request.selected_project_ids}")
    
    # Simple validation - just check if we have any IDs
    selected_project_ids = request.selected_project_ids or []
    print(f"🔍 Processed project IDs: {selected_project_ids}")
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Always update CV before download
            updated_cv = generate_cv_with_projects(cursor, conn)
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                raise HTTPException(status_code=404, detail="No active CV found")
            
            cv_content = cv_row[0]
            
            # Get only selected projects
            selected_projects = []
            if selected_project_ids:
                placeholders = ','.join(['?' for _ in selected_project_ids])
                cursor.execute(f"SELECT project_data FROM manual_projects WHERE id IN ({placeholders}) ORDER BY created_at DESC", selected_project_ids)
                project_rows = cursor.fetchall()
                for row in project_rows:
                    try:
                        project_data = json.loads(row[0])
                        selected_projects.append(project_data)
                    except Exception as e:
                        print(f"Error parsing project data: {e}")
                        continue
            
            print(f"Selected {len(selected_projects)} projects for CV download")
            
            # Generate PDF with selected projects
            pdf_buffer = generate_cv_pdf(cv_content, selected_projects)
            
            return StreamingResponse(
                io.BytesIO(pdf_buffer.getvalue()),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=cv_selected_projects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Download error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@app.post("/projects/create-linkedin-blog")
async def create_linkedin_blog_from_projects():
    """Create LinkedIn blog post based on selected projects"""
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Get all projects
            cursor.execute("SELECT project_data FROM manual_projects ORDER BY created_at DESC")
            project_rows = cursor.fetchall()
            projects = []
            for row in project_rows:
                try:
                    project_data = json.loads(row[0])
                    projects.append(project_data)
                except:
                    pass
            
            if not projects:
                raise HTTPException(status_code=404, detail="No projects found to create blog from")
            
            # Generate LinkedIn blog post
            blog_content = generate_linkedin_blog_from_projects(projects)
            
            return JSONResponse(status_code=200, content={
                "message": "✅ LinkedIn blog post generated successfully!",
                "blog_content": blog_content,
                "projects_used": len(projects),
                "word_count": len(blog_content.split())
            })
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ LinkedIn blog creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Blog creation failed: {str(e)}")

@app.get("/cv/pdf-preview")
async def get_cv_pdf_preview():
    """Get CV as PDF for preview (not download)."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Always update CV before preview
            updated_cv = generate_cv_with_projects(cursor, conn)
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

def generate_linkedin_blog_from_projects(projects) -> str:
    """Generate a LinkedIn blog post from project data."""
    if not projects:
        return "No projects available to generate blog post."
    
    blog_content = """🚀 Excited to share some of my recent projects and the technologies I've been working with!

"""
    
    # Add projects
    for i, (project_json,) in enumerate(projects[:3], 1):  # Limit to 3 projects
        try:
            project = json.loads(project_json)
            
            blog_content += f"**{i}. {project['title']}**\n"
            if project['duration']:
                blog_content += f"📅 {project['duration']}\n"
            blog_content += f"💡 {project['description']}\n"
            
            if project['technologies']:
                tech_tags = ' '.join([f"#{tech.replace(' ', '').replace('.', '').replace('-', '')}" for tech in project['technologies'][:5]])
                blog_content += f"🛠️ {tech_tags}\n"
            
            if project['highlights']:
                blog_content += f"✨ Key features: {', '.join(project['highlights'][:3])}\n"
            
            blog_content += "\n"
            
        except:
            continue
    
    blog_content += """🔧 **Technologies I've been working with:**
"""
    
    # Collect all technologies
    all_technologies = set()
    for (project_json,) in projects:
        try:
            project = json.loads(project_json)
            all_technologies.update(project.get('technologies', []))
        except:
            continue
    
    # Add technology section
    if all_technologies:
        tech_list = list(all_technologies)[:10]  # Limit to 10 technologies
        blog_content += f"{', '.join(tech_list)}\n\n"
    
    blog_content += """💭 **What I learned:**
• Building scalable applications requires careful architecture planning
• User experience is just as important as technical implementation
• Continuous learning and staying updated with new technologies is crucial
• Collaboration and code reviews improve code quality significantly

#softwareengineering #webdevelopment #projects #coding #technology #innovation

What projects have you been working on lately? I'd love to hear about your experiences! 👇"""
    
    return blog_content

def clean_cv_content(cv_content: str) -> str:
    """Clean up CV content by removing duplicates and formatting issues."""
    lines = cv_content.split('\n')
    cleaned_lines = []
    seen_lines = set()
    
    for line in lines:
        line = line.strip()
        if line and line not in seen_lines:
            cleaned_lines.append(line)
            seen_lines.add(line)
        elif not line and cleaned_lines and cleaned_lines[-1]:  # Add empty line only if previous line wasn't empty
            cleaned_lines.append('')
    
    return '\n'.join(cleaned_lines).strip()

# Vercel handler - add this at the end of the file
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081) 