#!/usr/bin/env python3
"""
Enhanced Project Management Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
from contextlib import contextmanager

# Import the project extractor
from project_extractor import extract_and_format_projects

router = APIRouter()

class ProjectCreate(BaseModel):
    title: str
    description: str
    duration: str = ""
    technologies: List[str] = []
    highlights: List[str] = []
    role: str = ""

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None
    technologies: Optional[List[str]] = None
    highlights: Optional[List[str]] = None
    role: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    title: str
    description: str
    duration: str
    technologies: List[str]
    highlights: List[str]
    role: str
    created_at: str

@router.post("/projects/extract-from-cv")
async def extract_projects_from_cv():
    """Extract projects from the current CV and store them in the database."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Get current CV
            cursor.execute("SELECT current_content FROM cvs WHERE is_active = TRUE LIMIT 1")
            cv_row = cursor.fetchone()
            
            if not cv_row:
                raise HTTPException(status_code=404, detail="No active CV found")
            
            cv_content = cv_row[0]
            
            # Extract projects from CV
            projects = extract_and_format_projects(cv_content)
            
            # Clear existing projects
            cursor.execute("DELETE FROM manual_projects")
            
            # Store extracted projects
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
            
            return {
                "success": True,
                "message": f"Extracted {len(projects)} projects from CV",
                "projects": projects
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting projects: {str(e)}")

@router.get("/projects/all", response_model=List[ProjectResponse])
async def get_all_projects():
    """Get all projects from the database."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute("SELECT project_data FROM manual_projects ORDER BY created_at DESC")
            projects = cursor.fetchall()
            
            formatted_projects = []
            for (project_json,) in projects:
                try:
                    project_data = json.loads(project_json)
                    formatted_projects.append(ProjectResponse(**project_data))
                except:
                    continue
            
            return formatted_projects
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")

@router.post("/projects/create", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    """Create a new project manually."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            project_data = {
                'id': generate_project_id(project.title),
                'title': project.title,
                'description': project.description,
                'duration': project.duration,
                'technologies': project.technologies,
                'highlights': project.highlights,
                'role': project.role,
                'created_at': datetime.now().isoformat()
            }
            
            cursor.execute(
                "INSERT INTO manual_projects (project_data) VALUES (?)",
                (json.dumps(project_data),)
            )
            
            return ProjectResponse(**project_data)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project_update: ProjectUpdate):
    """Update an existing project."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Get existing project
            cursor.execute("SELECT project_data FROM manual_projects WHERE project_data LIKE ?", (f'%"id": "{project_id}"%',))
            project_row = cursor.fetchone()
            
            if not project_row:
                raise HTTPException(status_code=404, detail="Project not found")
            
            existing_data = json.loads(project_row[0])
            
            # Update fields
            update_data = project_update.dict(exclude_unset=True)
            existing_data.update(update_data)
            
            # Update in database
            cursor.execute(
                "UPDATE manual_projects SET project_data = ? WHERE project_data LIKE ?",
                (json.dumps(existing_data), f'%"id": "{project_id}"%')
            )
            
            return ProjectResponse(**existing_data)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")

@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project by ID."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute("DELETE FROM manual_projects WHERE project_data LIKE ?", (f'%"id": "{project_id}"%',))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return {"success": True, "message": "Project deleted successfully"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")

@router.delete("/projects/delete-by-title/{title}")
async def delete_project_by_title(title: str):
    """Delete a project by title."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            cursor.execute("DELETE FROM manual_projects WHERE project_data LIKE ?", (f'%"title": "{title}"%',))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Project not found")
            
            return {"success": True, "message": "Project deleted successfully"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")

@router.post("/projects/cleanup")
async def cleanup_projects():
    """Clean up duplicate or invalid projects."""
    try:
        with get_db_cursor_context() as (cursor, conn):
            # Get all projects
            cursor.execute("SELECT project_data FROM manual_projects")
            projects = cursor.fetchall()
            
            # Find duplicates and invalid entries
            seen_titles = set()
            valid_projects = []
            
            for (project_json,) in projects:
                try:
                    project_data = json.loads(project_json)
                    title = project_data.get('title', '').strip()
                    
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        valid_projects.append(project_json)
                except:
                    continue
            
            # Clear and reinsert valid projects
            cursor.execute("DELETE FROM manual_projects")
            
            for project_json in valid_projects:
                cursor.execute("INSERT INTO manual_projects (project_data) VALUES (?)", (project_json,))
            
            return {
                "success": True,
                "message": f"Cleaned up projects. Kept {len(valid_projects)} valid projects."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up projects: {str(e)}")

def generate_project_id(title: str) -> str:
    """Generate a unique ID for a project."""
    import re
    return re.sub(r'[^a-zA-Z0-9]', '_', title.lower()).strip('_')

# Database context manager (import from main_enhanced.py)
def get_db_cursor_context():
    """Database context manager."""
    # This should be imported from main_enhanced.py
    pass 