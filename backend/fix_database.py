#!/usr/bin/env python3
"""
Fix database issue by ensuring cv_updater.db has the test projects
"""

import sqlite3
import json

def fix_database():
    """Fix the database by ensuring cv_updater.db has the test projects"""
    
    print("🔧 Fixing Database Issue")
    print("=" * 50)
    
    try:
        # Connect to cv_updater.db (the one the backend uses)
        print("1. Connecting to cv_updater.db...")
        conn = sqlite3.connect('cv_updater.db')
        cursor = conn.cursor()
        
        # Check if manual_projects table exists
        print("2. Checking if manual_projects table exists...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='manual_projects'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("📝 Creating manual_projects table...")
            cursor.execute('''CREATE TABLE manual_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            conn.commit()
            print("✅ Created manual_projects table")
        
        # Check current project count
        cursor.execute("SELECT COUNT(*) FROM manual_projects")
        project_count = cursor.fetchone()[0]
        print(f"📊 Current projects in cv_updater.db: {project_count}")
        
        if project_count == 0:
            print("📝 Adding test projects to cv_updater.db...")
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
            print(f"✅ Added {len(test_projects)} test projects to cv_updater.db")
            
            # Verify projects were added
            cursor.execute("SELECT COUNT(*) FROM manual_projects")
            new_count = cursor.fetchone()[0]
            print(f"📊 New project count: {new_count}")
            
        else:
            print(f"✅ cv_updater.db already has {project_count} projects")
        
        # Test the exact query that the endpoint uses
        print("3. Testing endpoint query...")
        cursor.execute("SELECT id, project_data FROM manual_projects ORDER BY created_at DESC")
        manual_projects = cursor.fetchall()
        
        print(f"✅ Query returned {len(manual_projects)} projects")
        
        projects = []
        for project_row in manual_projects:
            try:
                project_data = json.loads(project_row[1])
                project_data['id'] = project_row[0]
                projects.append(project_data)
                print(f"  Project: {project_data.get('title', 'N/A')} (ID: {project_row[0]})")
            except Exception as e:
                print(f"  ❌ Error parsing project: {e}")
        
        response = {"projects": projects, "total_count": len(projects)}
        print(f"📤 Endpoint response would be: {json.dumps(response, indent=2)}")
        
        conn.close()
        print("✅ Database fix completed successfully")
        
    except Exception as e:
        print(f"❌ Database fix failed: {e}")

if __name__ == "__main__":
    fix_database() 