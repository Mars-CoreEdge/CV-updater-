# Projects Page Features

## Overview
The `/projects` page now provides comprehensive CV project management functionality with AI-powered extraction and intelligent project handling.

## 🚀 Key Features

### 1. CV Upload and Project Extraction
- **Upload CV**: Users can upload their CV in PDF, DOCX, or TXT format
- **AI-Powered Extraction**: Automatically extracts ONLY the Projects section from the CV
- **Smart Parsing**: Ignores other sections like Skills, Experience, Education, etc.
- **Dynamic Rendering**: Automatically creates project cards based on extracted content

### 2. Project Management
- **Add New Projects**: Manual project creation with detailed form
- **Edit Projects**: Modify existing project details
- **Delete Projects**: Remove unwanted projects
- **Project Selection**: Checkbox system to select which projects to include in final CV

### 3. Assistant Actions
- **📄 Download My CV**: Generate PDF with selected projects
- **🧹 Clean Up My CV**: Remove unwanted or low-quality content
- **✍️ Create LinkedIn Blog**: Generate blog post based on selected projects

## 🔧 Technical Implementation

### Backend Endpoints

#### CV Upload for Projects
```http
POST /upload-cv-for-projects/
```
- Extracts only projects from uploaded CV
- Uses enhanced project extractor
- Stores projects in database with proper formatting

#### Project Management
```http
GET /projects/list          # Get all projects
POST /projects/create       # Create new project
PUT /projects/{id}          # Update project
DELETE /projects/{id}       # Delete project
```

#### Assistant Actions
```http
POST /cv/download-with-selected-projects  # Download CV with selected projects
POST /cv/cleanup                          # Clean up CV content
POST /projects/create-linkedin-blog       # Generate LinkedIn blog
```

### Frontend Components

#### CVUploadForProjects
- Specialized upload component for project extraction
- Handles PDF, DOCX, and TXT files
- Shows extraction progress and results

#### Enhanced ProjectsPage
- Project cards with checkboxes for selection
- Edit and delete buttons for each project
- Assistant action buttons
- Modal for project creation/editing

## 📋 Project Data Structure

Each project contains:
```json
{
  "id": "unique_project_id",
  "title": "Project Name",
  "description": "Project description",
  "duration": "2023 - Present",
  "technologies": ["React", "Node.js", "MongoDB"],
  "highlights": [
    "Built responsive web application",
    "Implemented RESTful API endpoints"
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🎯 Project Extraction Logic

### Section Detection
The system looks for various project section headers:
- `PROJECTS`
- `PORTFOLIO`
- `PROJECT EXPERIENCE`
- `KEY PROJECTS`
- `SELECTED PROJECTS`

### Project Parsing
1. **Title Detection**: Identifies project titles based on capitalization and content
2. **Duration Extraction**: Finds date patterns like `[2023 - Present]`
3. **Technology Detection**: Extracts from "Technologies:" lines or keyword matching
4. **Highlights Parsing**: Converts bullet points into achievement lists

### Technology Recognition
Automatically detects common technologies:
- Frontend: React, Vue.js, Angular, JavaScript, TypeScript
- Backend: Node.js, Express, Django, Spring, Python
- Databases: PostgreSQL, MongoDB, MySQL, Redis
- Cloud: AWS, Docker, Kubernetes
- APIs: REST, GraphQL, Socket.io

## 🎨 User Interface Features

### Project Cards
- **Checkbox Selection**: Choose projects for CV inclusion
- **Edit/Delete Actions**: Quick project management
- **Technology Tags**: Visual display of tech stack
- **Achievement Lists**: Key highlights and accomplishments

### Assistant Actions Panel
- **Download CV**: Generate PDF with selected projects only
- **Clean Up CV**: AI-powered content optimization
- **LinkedIn Blog**: Professional blog post generation

### Modal Forms
- **Create Project**: Add new projects manually
- **Edit Project**: Modify existing project details
- **Technology Tags**: Dynamic tag input system
- **Highlights Management**: Add/remove achievement points

## 🔄 Workflow

### 1. CV Upload Workflow
```
Upload CV → Extract Projects → Display Cards → User Review
```

### 2. Project Management Workflow
```
Select Projects → Choose Actions → Generate Output
```

### 3. Assistant Actions Workflow
```
Select Projects → Choose Action → Process → Download/View Result
```

## 🛠️ Setup and Usage

### Prerequisites
- Backend server running on `http://localhost:8081`
- Frontend application running on `http://localhost:3000`
- Database initialized with required tables

### Usage Steps
1. Navigate to `/projects` page
2. Upload CV or create projects manually
3. Select projects for inclusion
4. Use assistant actions as needed
5. Download final CV with selected projects

## 🧪 Testing

### Project Extraction Test
```bash
cd backend
python test_project_extraction.py
```

### API Testing
```bash
# Test project extraction
curl -X POST http://localhost:8081/upload-cv-for-projects/ \
  -F "file=@sample_cv.pdf"

# Test project listing
curl http://localhost:8081/projects/list

# Test assistant actions
curl -X POST http://localhost:8081/projects/create-linkedin-blog
```

## 🔮 Future Enhancements

### Planned Features
- **Project Templates**: Pre-defined project templates
- **AI Enhancement**: AI-powered project descriptions
- **Export Options**: Multiple format exports (PDF, DOCX, JSON)
- **Collaboration**: Share projects with team members
- **Analytics**: Project performance metrics

### Technical Improvements
- **Caching**: Project data caching for better performance
- **Search**: Advanced project search and filtering
- **Bulk Operations**: Mass project selection and actions
- **Version Control**: Project version history

## 🐛 Troubleshooting

### Common Issues
1. **No Projects Extracted**: Check CV format and project section headers
2. **Upload Failures**: Verify file format and size limits
3. **API Errors**: Check backend server status and database connection

### Debug Information
- Check browser console for frontend errors
- Review backend logs for API issues
- Verify database table structure

## 📝 Notes

- The system only extracts the Projects section from CVs
- Other sections (Skills, Experience, Education) are ignored
- Projects are stored in the `manual_projects` table
- All assistant actions work with selected projects only
- The LinkedIn blog generator creates professional content based on project data 