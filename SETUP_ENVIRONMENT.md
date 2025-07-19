# Environment Setup Guide

## Required Environment Variables

To run the CV Builder Platform, you need to set up the following environment variables:

### 1. OpenAI API Key
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 2. Supabase Configuration (Optional - uses SQLite by default)
```bash
export SUPABASE_URL="your-supabase-project-url"
export SUPABASE_ANON_KEY="your-supabase-anon-key"
export SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"
```

## Setup Instructions

### For Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="your-openai-api-key-here"
```

### For Windows (Command Prompt):
```cmd
set OPENAI_API_KEY=your-openai-api-key-here
```

### For Linux/Mac:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

## Getting API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and set it as an environment variable

### Supabase Keys (Optional)
1. Go to [Supabase](https://supabase.com/)
2. Create a new project
3. Go to Settings > API
4. Copy the URL and keys

## Security Notes
- Never commit API keys to version control
- Use environment variables instead of hardcoding
- Keep your API keys secure and don't share them

## Running the Application
After setting up environment variables:

```bash
# Start the backend
cd backend
python main_enhanced.py

# Start the frontend (in another terminal)
cd frontend
npm start
``` 