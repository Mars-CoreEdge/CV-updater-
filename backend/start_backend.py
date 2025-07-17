#!/usr/bin/env python3
"""
Backend startup script with proper database initialization
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Start the backend server with proper initialization"""
    
    print("🚀 Starting CV Updater Backend...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main_enhanced.py"):
        print("❌ Error: main_enhanced.py not found!")
        print("   Please run this script from the backend directory.")
        return
    
    # Import and initialize the app
    try:
        from main_enhanced import app, init_db
        
        print("📊 Initializing database...")
        init_db()
        print("✅ Database initialized successfully!")
        
        print("🔧 Starting FastAPI server...")
        print("   Server will be available at: http://localhost:8000")
        print("   API docs will be available at: http://localhost:8000/docs")
        print("   Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the server
        uvicorn.run(
            "main_enhanced:app",
            host="0.0.0.0",
            port=8081,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("   Please check the error message above.")

if __name__ == "__main__":
    main() 