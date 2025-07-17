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
- Supabase account
- OpenAI API key

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Environment Configuration
1. Create `.env` file in backend directory:
```
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

2. Create `.env` file in frontend directory:
```
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Database Setup
1. Run the Supabase setup script:
```bash
psql -h your_supabase_host -U postgres -d postgres -f supabase-database-setup.sql
```

2. Apply storage policies:
```bash
psql -h your_supabase_host -U postgres -d postgres -f storage-policies.sql
```

### Running the Application
```bash
# Start backend
cd backend
python main_enhanced.py

# Start frontend (in new terminal)
cd frontend
npm start
```

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. 