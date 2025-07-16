# 🗄️ CV Updater - Supabase Database Setup Guide

## Overview
This guide will help you set up the complete database schema for your CV Updater application using Supabase. The database supports all features including user profiles, CV management, project tracking, chat history, and file storage.

## 📊 Database Schema Overview

### Core Tables
1. **user_profiles** - Extended user information
2. **cvs** - Main CV documents and metadata
3. **cv_versions** - Version history tracking
4. **projects** - User projects and portfolio items
5. **chat_messages** - AI chat conversation history
6. **experiences** - Work experience entries
7. **education** - Educational background
8. **skills** - User skills and competencies
9. **file_uploads** - File upload tracking

## 🚀 Setup Instructions

### Step 1: Access Supabase SQL Editor
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor** in the sidebar
3. Click **"New Query"**

### Step 2: Run the Database Setup Script
1. Copy the entire content from `supabase-database-setup.sql`
2. Paste it into the SQL Editor
3. Click **"Run"** to execute the script

### Step 3: Set Up Storage Bucket
1. Go to **Storage** in your Supabase dashboard
2. Click **"Create Bucket"**
3. Name it `cvs`
4. Set it as **Public** (for easy file access)
5. Click **"Save"**

### Step 4: Configure Storage Policies
Run these additional SQL commands in the SQL Editor:

```sql
-- Create storage bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('cvs', 'cvs', true);

-- Storage policies for CV files
CREATE POLICY "Users can upload own CV files" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view own CV files" ON storage.objects
    FOR SELECT USING (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can update own CV files" ON storage.objects
    FOR UPDATE USING (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete own CV files" ON storage.objects
    FOR DELETE USING (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1]);
```

## 🔒 Security Features

### Row Level Security (RLS)
- All tables have RLS enabled
- Users can only access their own data
- Automatic user ID validation on all operations

### Data Validation
- Input length constraints
- Status field validation
- Email format validation
- Date consistency checks

## 🎯 Key Features

### ✅ User Management
- Automatic profile creation on signup
- Extended user metadata
- Social profile links
- Skill tracking

### ✅ CV Management
- Multiple CV support per user
- Version history tracking
- File upload integration
- Template system ready

### ✅ Project Portfolio
- Rich project metadata
- Technology stack tracking
- Achievement recording
- Project categorization

### ✅ AI Chat Integration
- Complete conversation history
- Session grouping
- Message threading
- Metadata storage

### ✅ Experience Tracking
- Work experience management
- Education history
- Skills assessment
- Timeline organization

## 📱 Integration with Your App

### Environment Variables
Add these to your `.env` file:

```env
REACT_APP_SUPABASE_URL=your-supabase-url
REACT_APP_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### Example API Calls

#### Create a new CV:
```javascript
const { data, error } = await supabase
  .from('cvs')
  .insert({
    title: 'My Professional CV',
    content: cvContent,
    status: 'active'
  });
```

#### Get user's CVs:
```javascript
const { data, error } = await supabase
  .from('cvs')
  .select('*')
  .eq('user_id', user.id)
  .order('created_at', { ascending: false });
```

#### Add a project:
```javascript
const { data, error } = await supabase
  .from('projects')
  .insert({
    title: 'My Awesome Project',
    description: 'Project description',
    technologies: ['React', 'Node.js', 'PostgreSQL'],
    project_url: 'https://myproject.com'
  });
```

#### Save chat message:
```javascript
const { data, error } = await supabase
  .from('chat_messages')
  .insert({
    session_id: sessionId,
    message_type: 'user',
    content: userMessage,
    cv_id: currentCvId
  });
```

## 🛠️ Database Maintenance

### Automatic Features
- `updated_at` timestamps auto-update
- User profiles auto-created on signup
- CV versions auto-generated on content changes
- Data integrity maintained with foreign keys

### Manual Operations
- Regular data cleanup (if needed)
- Performance monitoring via Supabase dashboard
- Backup management through Supabase

## 📊 Database Relationships

```
auth.users (Supabase Auth)
    ↓
user_profiles (1:1)
    ↓
cvs (1:many) ← cv_versions (many:1)
    ↓
projects (1:many)
    ↓
chat_messages (1:many)
experiences (1:many)
education (1:many)
skills (1:many)
file_uploads (1:many)
```

## 🔍 Useful Queries

### Get user's complete profile:
```sql
SELECT 
    up.*,
    COUNT(DISTINCT cv.id) as cv_count,
    COUNT(DISTINCT p.id) as project_count,
    COUNT(DISTINCT e.id) as experience_count
FROM user_profiles up
LEFT JOIN cvs cv ON up.user_id = cv.user_id
LEFT JOIN projects p ON up.user_id = p.user_id  
LEFT JOIN experiences e ON up.user_id = e.user_id
WHERE up.user_id = 'user-uuid'
GROUP BY up.id;
```

### Get CV with all related data:
```sql
SELECT 
    cv.*,
    json_agg(DISTINCT p.*) as projects,
    json_agg(DISTINCT e.*) as experiences,
    json_agg(DISTINCT s.*) as skills
FROM cvs cv
LEFT JOIN projects p ON cv.id = p.cv_id
LEFT JOIN experiences e ON cv.user_id = e.user_id
LEFT JOIN skills s ON cv.user_id = s.user_id
WHERE cv.id = 'cv-uuid'
GROUP BY cv.id;
```

## 🎉 Next Steps

1. **Test the Setup**: Create a test user and verify data flow
2. **Update Your App**: Integrate the database calls into your React components
3. **File Upload**: Set up file upload functionality for CV documents
4. **Real-time Features**: Consider enabling real-time subscriptions for live updates

## 🆘 Troubleshooting

### Common Issues:
- **RLS Errors**: Ensure user is authenticated before database operations
- **Foreign Key Errors**: Verify related records exist before creating references
- **Storage Access**: Check bucket policies if file upload fails

### Support Resources:
- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- Your application's error logs

---

**🎯 Your CV Updater database is now ready for production use!** 🚀 