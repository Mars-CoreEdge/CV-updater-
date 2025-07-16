-- =====================================================
-- STORAGE BUCKET AND POLICIES SETUP
-- =====================================================

-- Create storage bucket for CV files
INSERT INTO storage.buckets (id, name, public)
VALUES ('cvs', 'cvs', true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    public = EXCLUDED.public;

-- Storage policies for CV files
-- Users can upload their own files
CREATE POLICY "Users can upload own CV files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'cvs' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Users can view their own files
CREATE POLICY "Users can view own CV files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'cvs' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Users can update their own files
CREATE POLICY "Users can update own CV files" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'cvs' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Users can delete their own files
CREATE POLICY "Users can delete own CV files" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'cvs' AND 
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Verify bucket creation
SELECT * FROM storage.buckets WHERE id = 'cvs'; 