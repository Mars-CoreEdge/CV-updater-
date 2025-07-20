#!/usr/bin/env python3
"""
Debug script for projects endpoint
"""

import sqlite3
import json

def debug_projects_endpoint():
    """Debug the projects endpoint and database"""
    
    print("🔍 Debugging Projects Endpoint")
    print("=" * 50)
    
    try:
        # Connect to database
        print("1. Connecting to database...")
        conn = sqlite3.connect('cv_database.db')
        cursor = conn.cursor()
        
        # Check if table exists
        print("2. Checking if manual_projects table exists...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manual_projects'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ manual_projects table exists")
            
            # Count projects
            cursor.execute("SELECT COUNT(*) FROM manual_projects")
            project_count = cursor.fetchone()[0]
            print(f"📊 Total projects in database: {project_count}")
            
            if project_count > 0:
                # Get all projects
                print("3. Fetching all projects...")
                cursor.execute("SELECT id, project_data FROM manual_projects ORDER BY created_at DESC")
                manual_projects = cursor.fetchall()
                
                print(f"✅ Retrieved {len(manual_projects)} projects from database")
                
                projects = []
                for i, project_row in enumerate(manual_projects):
                    try:
                        project_id = project_row[0]
                        project_data = json.loads(project_row[1])
                        project_data['id'] = project_id
                        projects.append(project_data)
                        print(f"  Project {i+1}: {project_data.get('title', 'N/A')} (ID: {project_id})")
                    except Exception as e:
                        print(f"  ❌ Error parsing project {i+1}: {e}")
                
                print(f"✅ Successfully parsed {len(projects)} projects")
                
                # Test the exact response format
                response = {"projects": projects, "total_count": len(projects)}
                print(f"📤 Response format: {json.dumps(response, indent=2)}")
                
            else:
                print("❌ No projects found in database")
                
        else:
            print("❌ manual_projects table does not exist")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    debug_projects_endpoint() 