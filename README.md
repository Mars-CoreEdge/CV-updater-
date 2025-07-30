# CV Updater - AI-Powered CV Management System

A modern web application that allows users to upload, edit, and manage their CVs using AI-powered chat interface. The system supports automatic section detection, dynamic content updates, and PDF generation.

## Features

- **AI-Powered Chat Interface**: Update CV sections through natural language prompts
- **Automatic Section Detection**: Robust regex-based identification of CV sections (Education, Experience, Skills, etc.)
- **Dynamic Content Updates**: Add, modify, or append content to specific CV sections
- **PDF Generation**: Convert updated CV content back to properly formatted PDFs
- **Supabase Integration**: Modern PostgreSQL database with real-time updates
- **Responsive UI**: Clean, modern interface built with React

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database (via Supabase)
- **OpenAI API** - AI-powered chat and content processing
- **ReportLab** - PDF generation

### Frontend
- **React** - User interface
- **Supabase Client** - Database and authentication
- **Tailwind CSS** - Styling

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (required)
- Supabase account (optional, for advanced features)

### Automated Setup (Recommended)

**Windows (Batch):**
```bash
setup.bat
```

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Manual Setup:**

1. **Install Dependencies:**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Environment Configuration:**
   
   Copy the example environment files and configure them:
   ```bash
   # Backend
   cp backend/env.example backend/.env
   # Edit backend/.env with your OpenAI API key
   
   # Frontend
   cp frontend/env.example frontend/.env
   # Edit frontend/.env with your Supabase credentials (optional)
   ```

3. **Initialize Database:**
   ```bash
   cd backend
   python -c "from main_enhanced import init_db; init_db()"
   ```

### Running the Application

**Option 1: Use the provided startup scripts**
```bash
# Windows
start_all.bat

# PowerShell
.\start_all.ps1
```

**Option 2: Manual startup**
```bash
# Terminal 1 - Backend
cd backend
python main_enhanced.py

# Terminal 2 - Frontend
cd frontend
npm start
```

The application will be available at:
- **Backend API:** http://localhost:8000
- **Frontend:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs

## Usage

1. **Upload CV**: Upload your CV file (PDF, DOCX, or TXT)
2. **Chat Interface**: Use natural language to update your CV:
   - "Add MSc in AI at Oxford to my education"
   - "Update my skills with React and Node.js"
   - "Add a new project: E-commerce website"
3. **View Updates**: See real-time updates in the CV display panel
4. **Download**: Generate and download the updated PDF

## Project Structure

```
CV-updater/
├── backend/
│   ├── main_enhanced.py      # Main FastAPI application
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API services
│   │   └── contexts/         # React contexts
│   ├── package.json
│   └── public/
├── supabase-database-setup.sql
├── storage-policies.sql
└── README.md
```

## API Endpoints

- `POST /upload-cv/` - Upload and process CV file
- `POST /chat/` - AI chat interface for CV updates
- `GET /cv/current/` - Get current CV content
- `GET /cv/download/` - Download CV as PDF

## Troubleshooting

### Common Issues

**1. OpenAI API Key Issues**
- Ensure your API key is valid and has sufficient credits
- Check that the key is properly set in `backend/.env`
- Verify the key format starts with `sk-`

**2. Database Connection Issues**
- The application uses SQLite by default, no additional setup required
- If using Supabase, ensure your credentials are correct in the environment files

**3. Port Already in Use**
- Backend: Change `PORT=8000` in `backend/.env`
- Frontend: Change `PORT=3000` in `frontend/.env`

**4. Missing Dependencies**
- Run the setup script again: `setup.bat` or `.\setup.ps1`
- Or manually install: `pip install -r backend/requirements.txt` and `npm install` in frontend

**5. CORS Issues**
- Ensure the frontend URL is included in `CORS_ORIGINS` in `backend/.env`
- Default: `CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000`

### Getting Help

1. Check the API documentation at http://localhost:8000/docs
2. Review the console logs for error messages
3. Ensure all environment variables are properly set

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. 