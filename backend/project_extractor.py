#!/usr/bin/env python3
"""
Enhanced Project Extraction Module
Extracts projects from CV with detailed information
"""

import re
import json
from typing import List, Dict, Optional
from datetime import datetime

def extract_projects_from_cv(cv_content: str) -> List[Dict]:
    """
    Extract all projects from CV content with detailed information.
    Returns list of project dictionaries with title, tech stack, description, role, duration.
    """
    projects = []
    
    # Find the PROJECTS section
    projects_section = find_projects_section(cv_content)
    if not projects_section:
        return projects
    
    # Extract individual projects
    project_blocks = split_project_blocks(projects_section)
    
    for block in project_blocks:
        project = parse_project_block(block)
        if project:
            projects.append(project)
    
    return projects

def find_projects_section(cv_content: str) -> Optional[str]:
    """Find the PROJECTS section in CV content."""
    # Use the more reliable line-by-line approach
    lines = cv_content.split('\n')
    in_projects_section = False
    projects_content = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if we're entering the PROJECTS section
        if re.match(r'^PROJECTS?$', line_stripped, re.IGNORECASE):
            in_projects_section = True
            continue
        
        # If we're in the projects section, collect content
        elif in_projects_section:
            # Stop when we hit another major section
            if re.match(r'^(ACHIEVEMENTS|LANGUAGES|INTERESTS|CERTIFICATIONS|EDUCATION|WORK EXPERIENCE)$', line_stripped, re.IGNORECASE):
                break
            projects_content.append(line)
    
    if projects_content:
        result = '\n'.join(projects_content).strip()
        print(f"Found projects section: {len(result)} characters")
        return result
    
    # Fallback to regex patterns if line-by-line approach fails
    project_patterns = [
        r'PROJECTS?\s*\n(.*?)(?=\nACHIEVEMENTS|$)',
        r'PROJECTS?\s*\n(.*?)(?=\nLANGUAGES|$)',
        r'PROJECTS?\s*\n(.*?)(?=\nINTERESTS|$)',
        r'PROJECTS?\s*\n(.*?)(?=\n[A-Z][A-Z\s&]+[A-Z]|$)',
    ]
    
    for pattern in project_patterns:
        match = re.search(pattern, cv_content, re.IGNORECASE | re.DOTALL)
        if match:
            section_content = match.group(1).strip()
            print(f"Found projects section with regex: {len(section_content)} characters")
            return section_content
    
    return None

def split_project_blocks(projects_section: str) -> List[str]:
    """Split projects section into individual project blocks."""
    lines = projects_section.split('\n')
    blocks = []
    current_block = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a new project title
        if is_project_title(line):
            if current_block:
                blocks.append('\n'.join(current_block))
            current_block = [line]
        else:
            current_block.append(line)
    
    # Add the last block
    if current_block:
        blocks.append('\n'.join(current_block))
    
    # If we only got one block, try to split it more aggressively
    if len(blocks) == 1 and len(projects_section) > 200:
        print("Only one block found, trying aggressive splitting...")
        # Look for patterns like "Project Name\n[ Year ]" to split
        lines = projects_section.split('\n')
        new_blocks = []
        current_block = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if this looks like a project title followed by a date
            if is_project_title(line) and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # If next line contains a date pattern, it's likely a new project
                if re.search(r'\[\s*\d{4}\s*[-–]\s*(?:Present|\d{4})\s*\]', next_line):
                    if current_block:
                        new_blocks.append('\n'.join(current_block))
                    current_block = [line]
                    continue
            
            current_block.append(line)
        
        if current_block:
            new_blocks.append('\n'.join(current_block))
        
        if len(new_blocks) > 1:
            blocks = new_blocks
            print(f"Split into {len(blocks)} blocks using aggressive method")
    
    print(f"Split projects section into {len(blocks)} blocks")
    for i, block in enumerate(blocks):
        print(f"Block {i+1}: {block[:100]}...")
    
    return blocks

def is_project_title(line: str) -> bool:
    """Check if a line represents a project title."""
    # Project titles typically:
    # - Start with capital letters
    # - Don't end with ':'
    # - Are not too long (usually 2-6 words)
    # - Don't contain typical bullet point indicators
    
    if not line or line.startswith('-') or line.startswith('•'):
        return False
    
    if line.endswith(':'):
        return False
    
    # Check if it looks like a project title
    words = line.split()
    if len(words) < 1 or len(words) > 10:  # More flexible word count
        return False
    
    # Check if it starts with capital letters
    if not line[0].isupper():
        return False
    
    # Check for common project title patterns
    project_indicators = ['app', 'platform', 'system', 'dashboard', 'website', 'tool', 'application', 'portal', 'management']
    line_lower = line.lower()
    
    # If it contains project indicators, it's likely a title
    if any(indicator in line_lower for indicator in project_indicators):
        return True
    
    # If it's followed by a date pattern, it's likely a title
    if re.search(r'\[\s*\d{4}\s*[-–]\s*(?:Present|\d{4})\s*\]', line):
        return True
    
    # If it's a short line (likely a title) and not a bullet point
    if len(line.strip()) < 50 and not line.strip().startswith(('-', '•', '[')):
        return True
    
    return False

def parse_project_block(block: str) -> Optional[Dict]:
    """Parse a single project block into structured data."""
    lines = [line.strip() for line in block.split('\n') if line.strip()]
    if not lines:
        return None
    
    project = {
        'title': '',
        'duration': '',
        'description': '',
        'technologies': [],
        'role': '',
        'highlights': []
    }
    
    # First line is usually the title
    project['title'] = lines[0]
    
    # Look for duration in the block
    duration = extract_duration(block)
    if duration:
        project['duration'] = duration
    
    # Extract technologies
    technologies = extract_technologies(block)
    if technologies:
        project['technologies'] = technologies
    
    # Extract description and highlights
    description, highlights = extract_description_and_highlights(block)
    if description:
        project['description'] = description
    if highlights:
        project['highlights'] = highlights
    
    # Extract role/responsibilities
    role = extract_role(block)
    if role:
        project['role'] = role
    
    return project

def extract_duration(text: str) -> str:
    """Extract project duration from text."""
    # Look for date patterns like [2023 - Present] or [2022]
    duration_patterns = [
        r'\[\s*(\d{4})\s*[-–]\s*(?:Present|\d{4})\s*\]',
        r'\[\s*(\d{4})\s*\]',
        r'\((\d{4})\s*[-–]\s*(?:Present|\d{4})\)',
        r'(\d{4})\s*[-–]\s*(?:Present|\d{4})'
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).strip('[]()')
    
    return ''

def extract_technologies(text: str) -> List[str]:
    """Extract technologies from project text."""
    technologies = []
    
    # Look for "Technologies:" line
    tech_patterns = [
        r'Technologies?:\s*(.+)',
        r'Tech\s+Stack:\s*(.+)',
        r'Built\s+with:\s*(.+)',
        r'Using:\s*(.+)'
    ]
    
    for pattern in tech_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            tech_text = match.group(1)
            # Split by commas, semicolons, or 'and'
            tech_list = re.split(r'[,;]\s*|\s+and\s+', tech_text)
            technologies.extend([tech.strip() for tech in tech_list if tech.strip()])
            break
    
    # If no explicit technologies line, look for common tech keywords
    if not technologies:
        tech_keywords = [
            'React', 'Node.js', 'Python', 'JavaScript', 'TypeScript', 'Vue.js', 'Angular',
            'Express', 'Django', 'Spring', 'PostgreSQL', 'MongoDB', 'MySQL', 'Redis',
            'AWS', 'Docker', 'Kubernetes', 'Git', 'REST', 'GraphQL', 'Socket.io',
            'PWA', 'Local Storage', 'OpenWeather API', 'Slack API', 'Google Calendar API'
        ]
        
        text_lower = text.lower()
        for tech in tech_keywords:
            if tech.lower() in text_lower:
                technologies.append(tech)
    
    return list(set(technologies))  # Remove duplicates

def extract_description_and_highlights(text: str) -> tuple[str, List[str]]:
    """Extract project description and highlights."""
    description = ''
    highlights = []
    
    lines = text.split('\n')
    
    # Look for bullet points (highlights)
    for line in lines:
        line = line.strip()
        if line.startswith('-') or line.startswith('•'):
            highlight = line.lstrip('-•').strip()
            if highlight:
                highlights.append(highlight)
    
    # If we have highlights, use the first one as description
    if highlights:
        description = highlights[0]
        highlights = highlights[1:]  # Rest are highlights
    
    # If no highlights, try to extract description from non-bullet lines
    if not description:
        non_bullet_lines = [line.strip() for line in lines 
                           if line.strip() and not line.strip().startswith(('-', '•', '['))]
        if non_bullet_lines:
            description = non_bullet_lines[0]
    
    return description, highlights

def extract_role(text: str) -> str:
    """Extract role/responsibilities from project text."""
    role_keywords = ['led', 'developed', 'built', 'created', 'implemented', 'designed', 'architected']
    
    for line in text.split('\n'):
        line_lower = line.lower()
        for keyword in role_keywords:
            if keyword in line_lower:
                # Extract the sentence containing the role
                sentences = re.split(r'[.!?]', line)
                for sentence in sentences:
                    if keyword in sentence.lower():
                        return sentence.strip()
    
    return ''

def format_project_for_display(project: Dict) -> Dict:
    """Format project data for frontend display."""
    return {
        'id': project.get('id', generate_project_id(project['title'])),
        'title': project['title'],
        'description': project['description'],
        'duration': project['duration'],
        'technologies': project['technologies'],
        'highlights': project['highlights'],
        'role': project['role'],
        'created_at': project.get('created_at', datetime.now().isoformat())
    }

def generate_project_id(title: str) -> str:
    """Generate a unique ID for a project based on its title."""
    return re.sub(r'[^a-zA-Z0-9]', '_', title.lower()).strip('_')

def extract_and_format_projects(cv_content: str) -> List[Dict]:
    """Main function to extract and format projects from CV."""
    raw_projects = extract_projects_from_cv(cv_content)
    formatted_projects = []
    
    for project in raw_projects:
        formatted_project = format_project_for_display(project)
        formatted_projects.append(formatted_project)
    
    return formatted_projects

# Example usage and testing
if __name__ == "__main__":
    # Test with sample CV content
    sample_cv = """
    PROJECTS
    E-Commerce Platform
    [ 2023 - Present ]
    - Built full-stack e-commerce solution with React, Node.js, and PostgreSQL
    - Implemented user authentication, payment processing, and inventory management
    - Deployed on AWS with Docker containers and CI/CD pipeline
    - Technologies: React, Node.js, PostgreSQL, AWS, Docker

    Task Management App
    [ 2022 ]
    - Developed collaborative task management application with real-time updates
    - Features include user roles, file sharing, and progress tracking
    - Integrated with Google Calendar and Slack APIs
    - Technologies: Vue.js, Express, MongoDB, Socket.io
    """
    
    projects = extract_and_format_projects(sample_cv)
    print(json.dumps(projects, indent=2)) 