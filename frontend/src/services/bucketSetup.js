import { supabase } from '../supabaseClient';

export const ensureStorageBucket = async () => {
  try {
    // Check if bucket exists
    const { data: buckets, error: listError } = await supabase.storage.listBuckets();
    
    if (listError) {
      console.error('Error listing buckets:', listError);
      return false;
    }
    
    const cvsBucket = buckets.find(bucket => bucket.id === 'cvs');
    
    if (!cvsBucket) {
      console.log('CVs bucket not found. Please create it manually in Supabase dashboard.');
      return false;
    }
    
    console.log('CVs bucket found:', cvsBucket);
    return true;
  } catch (error) {
    console.error('Error checking storage bucket:', error);
    return false;
  }
};

// Test file upload to ensure bucket is accessible
export const testBucketAccess = async () => {
  try {
    // Try to list files in the bucket
    const { data, error } = await supabase.storage
      .from('cvs')
      .list('', { limit: 1 });
    
    if (error) {
      console.error('Error accessing bucket:', error);
      return false;
    }
    
    console.log('Bucket access test successful');
    return true;
  } catch (error) {
    console.error('Error testing bucket access:', error);
    return false;
  }
}; 