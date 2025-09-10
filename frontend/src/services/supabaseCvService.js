import { supabase } from '../supabaseClient'
import { ensureStorageBucket } from './bucketSetup'

// Upload a CV file to the private 'cvs' bucket under `${userId}/${timestamp}_filename`
export async function uploadCvFileToStorage(file, userId) {
  const timestamp = Date.now()
  const sanitizedName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_')
  const storagePath = `${userId}/${timestamp}_${sanitizedName}`

  // Best-effort bucket check
  try { await ensureStorageBucket() } catch (_) {}

  const { data, error } = await supabase.storage
    .from('cvs')
    .upload(storagePath, file, {
      cacheControl: '3600',
      upsert: false,
      contentType: file.type || undefined
    })

  return { path: data?.path || storagePath, error }
}

// Insert a row into the `cvs` table using the provided schema
export async function insertCvRow({ filename, title, original_content, current_content, user_id, url }) {
  const { data, error } = await supabase
    .from('cvs')
    .insert([{ filename, title, original_content, current_content, user_id, url }])
    .select()
    .single()

  return { data, error }
}

// Fetch user CVs by filtering filename prefix `${userId}/`
export async function fetchUserCvs(userId) {
  const { data, error } = await supabase
    .from('cvs')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })

  return { data: data || [], error }
}

// Generate a signed URL for a file in the private bucket
export async function createSignedUrl(filePath, expiresInSeconds = 3600) {
  const { data, error } = await supabase.storage
    .from('cvs')
    .createSignedUrl(filePath, expiresInSeconds)

  return { url: data?.signedUrl || null, error }
}


