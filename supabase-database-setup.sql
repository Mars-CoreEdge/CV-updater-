-- =====================================================
-- CV UPDATER APPLICATION - SUPABASE DATABASE SCHEMA
-- =====================================================

-- First, drop existing tables if they exist (careful in production!)
DROP TABLE IF EXISTS public.chat_messages CASCADE;
DROP TABLE IF EXISTS public.cv_versions CASCADE;
DROP TABLE IF EXISTS public.projects CASCADE;
DROP TABLE IF EXISTS public.cvs CASCADE;
DROP TABLE IF EXISTS public.user_profiles CASCADE;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- USER PROFILES TABLE
-- =====================================================
CREATE TABLE public.user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    email TEXT,
    avatar_url TEXT,
    phone TEXT,
    location TEXT,
    linkedin_url TEXT,
    github_url TEXT,
    portfolio_url TEXT,
    bio TEXT,
    skills TEXT[], -- Array of skills
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    CONSTRAINT unique_user_profile UNIQUE(user_id)
);

-- =====================================================
-- CVS TABLE (Main CV Documents)
-- =====================================================
CREATE TABLE public.cvs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'My CV',
    description TEXT,
    content TEXT, -- The actual CV content
    file_url TEXT, -- URL to uploaded CV file in Supabase Storage
    file_name TEXT,
    file_size INTEGER,
    file_type TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived')),
    is_template BOOLEAN DEFAULT FALSE,
    template_category TEXT,
    tags TEXT[], -- Array of tags for categorization
    metadata JSONB, -- Additional metadata
    version_number INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    CONSTRAINT cv_title_length CHECK (char_length(title) >= 1 AND char_length(title) <= 200)
);

-- =====================================================
-- CV VERSIONS TABLE (Track CV Changes)
-- =====================================================
CREATE TABLE public.cv_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cv_id UUID REFERENCES public.cvs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    changes_summary TEXT,
    file_url TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    CONSTRAINT unique_cv_version UNIQUE(cv_id, version_number)
);

-- =====================================================
-- PROJECTS TABLE
-- =====================================================
CREATE TABLE public.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    cv_id UUID REFERENCES public.cvs(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    technologies TEXT[], -- Array of technologies used
    project_url TEXT,
    github_url TEXT,
    demo_url TEXT,
    image_url TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'completed' CHECK (status IN ('planning', 'in_progress', 'completed', 'on_hold')),
    priority INTEGER DEFAULT 1 CHECK (priority >= 1 AND priority <= 5),
    category TEXT,
    role TEXT, -- User's role in the project
    achievements TEXT[], -- Array of achievements/accomplishments
    metrics JSONB, -- Performance metrics, stats, etc.
    order_index INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    CONSTRAINT project_title_length CHECK (char_length(title) >= 1 AND char_length(title) <= 200)
);

-- =====================================================
-- CHAT MESSAGES TABLE (AI Chat History)
-- =====================================================
CREATE TABLE public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    cv_id UUID REFERENCES public.cvs(id) ON DELETE SET NULL,
    session_id UUID, -- Group related messages
    message_type TEXT NOT NULL CHECK (message_type IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    metadata JSONB, -- Store additional data like tokens used, model info, etc.
    parent_message_id UUID REFERENCES public.chat_messages(id),
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    CONSTRAINT content_not_empty CHECK (char_length(content) > 0)
);

-- =====================================================
-- EXPERIENCES TABLE (Work Experience)
-- =====================================================
CREATE TABLE public.experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    cv_id UUID REFERENCES public.cvs(id) ON DELETE SET NULL,
    company_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    achievements TEXT[], -- Array of achievements
    technologies TEXT[], -- Technologies used in this role
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- EDUCATION TABLE
-- =====================================================
CREATE TABLE public.education (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    cv_id UUID REFERENCES public.cvs(id) ON DELETE SET NULL,
    institution_name TEXT NOT NULL,
    degree TEXT NOT NULL,
    field_of_study TEXT,
    location TEXT,
    start_date DATE,
    end_date DATE,
    grade TEXT,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- SKILLS TABLE
-- =====================================================
CREATE TABLE public.skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    cv_id UUID REFERENCES public.cvs(id) ON DELETE SET NULL,
    skill_name TEXT NOT NULL,
    category TEXT, -- e.g., 'programming', 'design', 'languages'
    proficiency_level INTEGER CHECK (proficiency_level >= 1 AND proficiency_level <= 5),
    years_experience INTEGER,
    is_featured BOOLEAN DEFAULT FALSE,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    
    CONSTRAINT unique_user_skill UNIQUE(user_id, skill_name)
);

-- =====================================================
-- FILE UPLOADS TABLE (Track all file uploads)
-- =====================================================
CREATE TABLE public.file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_url TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    bucket_name TEXT DEFAULT 'cvs',
    upload_path TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- User-based indexes
CREATE INDEX idx_user_profiles_user_id ON public.user_profiles(user_id);
CREATE INDEX idx_cvs_user_id ON public.cvs(user_id);
CREATE INDEX idx_projects_user_id ON public.projects(user_id);
CREATE INDEX idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX idx_experiences_user_id ON public.experiences(user_id);
CREATE INDEX idx_education_user_id ON public.education(user_id);
CREATE INDEX idx_skills_user_id ON public.skills(user_id);

-- CV-based indexes
CREATE INDEX idx_cv_versions_cv_id ON public.cv_versions(cv_id);
CREATE INDEX idx_projects_cv_id ON public.projects(cv_id);
CREATE INDEX idx_chat_messages_cv_id ON public.chat_messages(cv_id);

-- Session-based indexes
CREATE INDEX idx_chat_messages_session_id ON public.chat_messages(session_id);

-- Status and filtering indexes
CREATE INDEX idx_cvs_status ON public.cvs(status);
CREATE INDEX idx_projects_status ON public.projects(status);
CREATE INDEX idx_cvs_is_current ON public.cvs(is_current);

-- Date-based indexes
CREATE INDEX idx_cvs_created_at ON public.cvs(created_at);
CREATE INDEX idx_projects_created_at ON public.projects(created_at);
CREATE INDEX idx_chat_messages_created_at ON public.chat_messages(created_at);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cvs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cv_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.experiences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.education ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_uploads ENABLE ROW LEVEL SECURITY;

-- User Profiles Policies
CREATE POLICY "Users can view own profile" ON public.user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON public.user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON public.user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own profile" ON public.user_profiles
    FOR DELETE USING (auth.uid() = user_id);

-- CVs Policies
CREATE POLICY "Users can view own CVs" ON public.cvs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own CVs" ON public.cvs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own CVs" ON public.cvs
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own CVs" ON public.cvs
    FOR DELETE USING (auth.uid() = user_id);

-- CV Versions Policies
CREATE POLICY "Users can view own CV versions" ON public.cv_versions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own CV versions" ON public.cv_versions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Projects Policies
CREATE POLICY "Users can view own projects" ON public.projects
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own projects" ON public.projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own projects" ON public.projects
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own projects" ON public.projects
    FOR DELETE USING (auth.uid() = user_id);

-- Chat Messages Policies
CREATE POLICY "Users can view own chat messages" ON public.chat_messages
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat messages" ON public.chat_messages
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Experiences Policies
CREATE POLICY "Users can manage own experiences" ON public.experiences
    FOR ALL USING (auth.uid() = user_id);

-- Education Policies
CREATE POLICY "Users can manage own education" ON public.education
    FOR ALL USING (auth.uid() = user_id);

-- Skills Policies
CREATE POLICY "Users can manage own skills" ON public.skills
    FOR ALL USING (auth.uid() = user_id);

-- File Uploads Policies
CREATE POLICY "Users can manage own files" ON public.file_uploads
    FOR ALL USING (auth.uid() = user_id);

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON public.user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_cvs_updated_at
    BEFORE UPDATE ON public.cvs
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON public.projects
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_experiences_updated_at
    BEFORE UPDATE ON public.experiences
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_education_updated_at
    BEFORE UPDATE ON public.education
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER update_skills_updated_at
    BEFORE UPDATE ON public.skills
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Function to create user profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (user_id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', NEW.email)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user signup
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to create new CV version
CREATE OR REPLACE FUNCTION public.create_cv_version()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create version if content actually changed
    IF TG_OP = 'UPDATE' AND OLD.content IS DISTINCT FROM NEW.content THEN
        INSERT INTO public.cv_versions (
            cv_id,
            user_id,
            version_number,
            title,
            content,
            changes_summary,
            file_url,
            metadata
        ) VALUES (
            NEW.id,
            NEW.user_id,
            NEW.version_number,
            NEW.title,
            NEW.content,
            'Auto-generated version',
            NEW.file_url,
            NEW.metadata
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-create CV versions
CREATE TRIGGER create_cv_version_trigger
    AFTER UPDATE ON public.cvs
    FOR EACH ROW
    EXECUTE FUNCTION public.create_cv_version();

-- =====================================================
-- STORAGE SETUP (for file uploads)
-- =====================================================

-- Create storage bucket for CVs (run this in Supabase Dashboard)
-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('cvs', 'cvs', true);

-- Storage policies (run these in Supabase Dashboard)
-- CREATE POLICY "Users can upload own CV files" ON storage.objects
--     FOR INSERT WITH CHECK (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1]);

-- CREATE POLICY "Users can view own CV files" ON storage.objects
--     FOR SELECT USING (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1]);

-- CREATE POLICY "Users can update own CV files" ON storage.objects
--     FOR UPDATE USING (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1]);

-- CREATE POLICY "Users can delete own CV files" ON storage.objects
--     FOR DELETE USING (bucket_id = 'cvs' AND auth.uid()::text = (storage.foldername(name))[1]);

-- =====================================================
-- SAMPLE DATA (Optional - for testing)
-- =====================================================

-- You can insert sample data here for testing
-- This will be populated when users start using the application

-- =====================================================
-- USEFUL VIEWS
-- =====================================================

-- View for user's active CV with latest projects
CREATE OR REPLACE VIEW public.user_cv_summary AS
SELECT 
    up.user_id,
    up.full_name,
    up.email,
    cv.id as cv_id,
    cv.title as cv_title,
    cv.updated_at as cv_updated_at,
    COUNT(p.id) as project_count,
    COUNT(e.id) as experience_count,
    COUNT(ed.id) as education_count,
    COUNT(s.id) as skill_count
FROM public.user_profiles up
LEFT JOIN public.cvs cv ON up.user_id = cv.user_id AND cv.is_current = true
LEFT JOIN public.projects p ON cv.id = p.cv_id
LEFT JOIN public.experiences e ON up.user_id = e.user_id
LEFT JOIN public.education ed ON up.user_id = ed.user_id
LEFT JOIN public.skills s ON up.user_id = s.user_id
GROUP BY up.user_id, up.full_name, up.email, cv.id, cv.title, cv.updated_at;

-- =====================================================
-- COMPLETION MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '=====================================';
    RAISE NOTICE 'CV UPDATER DATABASE SETUP COMPLETE!';
    RAISE NOTICE '=====================================';
    RAISE NOTICE 'Tables created: user_profiles, cvs, cv_versions, projects, chat_messages, experiences, education, skills, file_uploads';
    RAISE NOTICE 'RLS policies enabled for data security';
    RAISE NOTICE 'Indexes created for performance';
    RAISE NOTICE 'Triggers set up for automation';
    RAISE NOTICE 'Ready for your CV Updater application!';
    RAISE NOTICE '=====================================';
END $$; 