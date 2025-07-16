import { createClient } from '@supabase/supabase-js'

// Replace these with your actual Supabase project URL and anon key
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL || 'https://mqzmgrycagqyaqrxyrbl.supabase.co'
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1xem1ncnljYWdxeWFxcnh5cmJsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIxOTczOTksImV4cCI6MjA2Nzc3MzM5OX0.ENd4YMcum6l2lTqQ4U9BvHSFOWLdP84lwCpEfvOMjlI'

export const supabase = createClient(supabaseUrl, supabaseAnonKey) 