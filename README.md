# CV Updater Chatbot

A modern web application that allows you to upload your CV and update it through conversational AI. Built with React.js, FastAPI, and SQLite.

## Features

- 📄 **CV Upload**: Support for PDF, DOCX, and TXT files
- 💬 **Conversational Updates**: Update your CV by chatting with the bot
- 🔄 **Real-time Updates**: See your CV update in real-time as you add new achievements
- 📋 **CV Display**: View your updated CV with a clean, professional layout
- ⬇️ **Download**: Download your updated CV as a text file
- 💾 **Persistent Storage**: All data is stored in SQLite database

## Tech Stack

- **Frontend**: React.js with styled-components
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **File Processing**: PyPDF2, docx2txt

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository** (if you haven't already)
   ```bash
   git clone <repository-url>
   cd CV-updater-
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the FastAPI backend**
   ```bash
   cd backend
   python main.py
   ```
   
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the React development server**
   ```bash
   npm start
   ```
   
   The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload Your CV**
   - Navigate to `http://localhost:3000`
   - Click the upload area or drag and drop your CV file
   - Supported formats: PDF, DOCX, TXT

2. **Chat to Update Your CV**
   - Once uploaded, start chatting with the bot
   - Tell it about your new skills, experience, or education
   - Examples:
     - "I have achieved the skill React.js"
     - "I worked as a Software Developer at XYZ Company from Jan 2023 to Dec 2023"
     - "I completed a certification in Data Science"

3. **View Updated CV**
   - Your CV will be displayed on the right side
   - Updates appear in real-time as you chat
   - Click "Download" to save your updated CV

## Example Conversations

```
User: I have achieved the skill React.js
Bot: Great! I've noted that you've gained the skill: React.js. This will be included in your updated CV.

User: I worked as a Frontend Developer at Tech Corp
Bot: Excellent! I've recorded your new experience: I worked as a Frontend Developer at Tech Corp. This will be added to your CV.

User: I completed a certification in AWS Cloud Computing
Bot: Wonderful! I've noted your educational achievement: I completed a certification in AWS Cloud Computing. This will be reflected in your CV.
```

## API Endpoints

- `POST /upload-cv/` - Upload CV file
- `POST /chat/` - Send chat message
- `GET /cv/current/` - Get updated CV
- `GET /chat/history/` - Get chat history

## Project Structure

```
CV-updater-/
├── backend/
│   ├── main.py          # FastAPI application
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   └── database.py      # Database configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.js
│   │   │   ├── ChatInterface.js
│   │   │   └── CVDisplay.js
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   └── package.json
├── requirements.txt     # Python dependencies
└── README.md
```

## Development

### Backend Development

The backend uses FastAPI with SQLAlchemy for database operations. Key components:

- **Models**: Define database schema for CVs, chat messages, and updates
- **Schemas**: Pydantic models for request/response validation
- **Main**: FastAPI application with all endpoints

### Frontend Development

The frontend is a React.js application with:

- **FileUpload**: Drag-and-drop CV upload component
- **ChatInterface**: Real-time chat with the bot
- **CVDisplay**: Display and download updated CV

### Adding New Features

1. **New CV Update Types**: Add new processing logic in `process_cv_update()` function
2. **Enhanced NLP**: Integrate with OpenAI or other NLP services for better message processing
3. **User Authentication**: Add user management for multi-user support
4. **Export Formats**: Add PDF/DOCX export functionality

## Troubleshooting

### Common Issues

1. **Backend not starting**: Check if all dependencies are installed
2. **File upload fails**: Ensure file is in supported format (PDF, DOCX, TXT)
3. **CORS errors**: Verify backend is running on port 8000
4. **Chat not working**: Check backend logs for errors

### Development Tips

- Use browser developer tools to debug frontend issues
- Check FastAPI docs at `http://localhost:8000/docs` for API testing
- Monitor backend console for error messages

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For bug reports and feature requests, please create an issue on GitHub. 