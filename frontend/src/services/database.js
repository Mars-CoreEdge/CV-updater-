import { supabase } from '../supabaseClient'

// ===============================================
// USER PROFILE SERVICES
// ===============================================

export const userProfileService = {
  // Get user profile
  async getProfile(userId) {
    const { data, error } = await supabase
      .from('user_profiles')
      .select('*')
      .eq('user_id', userId)
      .single()
    
    return { data, error }
  },

  // Update user profile
  async updateProfile(userId, profileData) {
    const { data, error } = await supabase
      .from('user_profiles')
      .update(profileData)
      .eq('user_id', userId)
      .select()
      .single()
    
    return { data, error }
  },

  // Create user profile (usually done automatically via trigger)
  async createProfile(profileData) {
    const { data, error } = await supabase
      .from('user_profiles')
      .insert(profileData)
      .select()
      .single()
    
    return { data, error }
  }
}

// ===============================================
// CV SERVICES
// ===============================================

export const cvService = {
  // Get all user's CVs
  async getUserCVs(userId) {
    const { data, error } = await supabase
      .from('cvs')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
    
    return { data, error }
  },

  // Get current/active CV
  async getCurrentCV(userId) {
    try {
      const { data, error } = await supabase
        .from('cvs')
        .select('*')
        .eq('user_id', userId)
        .order('updated_at', { ascending: false })
        .limit(1);
      
      if (error) {
        console.error('Error fetching current CV:', error);
        return { data: null, error };
      }
      
      console.log('Current CV data:', data);
      return { data, error: null };
    } catch (error) {
      console.error('Error in getCurrentCV:', error);
      return { data: null, error };
    }
  },

  async createCV(cvData) {
    try {
      console.log('Creating CV with data:', cvData);
      
      const { data, error } = await supabase
        .from('cvs')
        .insert([{
          user_id: cvData.user_id,
          title: cvData.title,
          content: cvData.content,
          file_name: cvData.file_name,
          file_size: cvData.file_size,
          file_type: cvData.file_type,
          version_number: cvData.version_number || 1,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }])
        .select()
        .single();
      
      if (error) {
        console.error('Error creating CV:', error);
        return { data: null, error };
      }
      
      console.log('CV created successfully:', data);
      return { data, error: null };
    } catch (error) {
      console.error('Error in createCV:', error);
      return { data: null, error };
    }
  },

  async updateCV(cvId, cvData) {
    try {
      console.log('Updating CV:', cvId, 'with data:', cvData);
      
      const updateData = {
        updated_at: new Date().toISOString()
      };
      
      if (cvData.content) updateData.content = cvData.content;
      if (cvData.title) updateData.title = cvData.title;
      if (cvData.version_number) updateData.version_number = cvData.version_number;
      
      const { data, error } = await supabase
        .from('cvs')
        .update(updateData)
        .eq('id', cvId)
        .select()
        .single();
      
      if (error) {
        console.error('Error updating CV:', error);
        return { data: null, error };
      }
      
      console.log('CV updated successfully:', data);
      return { data, error: null };
    } catch (error) {
      console.error('Error in updateCV:', error);
      return { data: null, error };
    }
  },

  // Delete CV
  async deleteCV(cvId) {
    const { data, error } = await supabase
      .from('cvs')
      .delete()
      .eq('id', cvId)
    
    return { data, error }
  },

  // Set CV as current
  async setCurrentCV(userId, cvId) {
    // First, set all CVs as not current
    await supabase
      .from('cvs')
      .update({ is_current: false })
      .eq('user_id', userId)

    // Then set the selected CV as current
    const { data, error } = await supabase
      .from('cvs')
      .update({ is_current: true })
      .eq('id', cvId)
      .select()
      .single()
    
    return { data, error }
  }
}

// ===============================================
// CV VERSIONS SERVICES
// ===============================================

export const cvVersionService = {
  // Get CV versions
  async getCVVersions(cvId) {
    const { data, error } = await supabase
      .from('cv_versions')
      .select('*')
      .eq('cv_id', cvId)
      .order('version_number', { ascending: false })
    
    return { data, error }
  },

  // Get specific version
  async getVersion(cvId, versionNumber) {
    const { data, error } = await supabase
      .from('cv_versions')
      .select('*')
      .eq('cv_id', cvId)
      .eq('version_number', versionNumber)
      .single()
    
    return { data, error }
  }
}

// ===============================================
// PROJECT SERVICES
// ===============================================

export const projectService = {
  // Get user's projects
  async getUserProjects(userId) {
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('user_id', userId)
      .order('order_index', { ascending: true })
    
    return { data, error }
  },

  // Get CV-specific projects
  async getCVProjects(cvId) {
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('cv_id', cvId)
      .order('order_index', { ascending: true })
    
    return { data, error }
  },

  // Create project
  async createProject(projectData) {
    const { data, error } = await supabase
      .from('projects')
      .insert(projectData)
      .select()
      .single()
    
    return { data, error }
  },

  // Update project
  async updateProject(projectId, projectData) {
    const { data, error } = await supabase
      .from('projects')
      .update(projectData)
      .eq('id', projectId)
      .select()
      .single()
    
    return { data, error }
  },

  // Delete project
  async deleteProject(projectId) {
    const { data, error } = await supabase
      .from('projects')
      .delete()
      .eq('id', projectId)
    
    return { data, error }
  },

  // Get featured projects
  async getFeaturedProjects(userId) {
    const { data, error } = await supabase
      .from('projects')
      .select('*')
      .eq('user_id', userId)
      .eq('is_featured', true)
      .order('order_index', { ascending: true })
    
    return { data, error }
  }
}

// ===============================================
// CHAT MESSAGE SERVICES
// ===============================================

export const chatService = {
  // Get chat messages for session
  async getSessionMessages(sessionId) {
    const { data, error } = await supabase
      .from('chat_messages')
      .select('*')
      .eq('session_id', sessionId)
      .order('created_at', { ascending: true })
    
    return { data, error }
  },

  // Get CV-related messages
  async getCVMessages(cvId) {
    const { data, error } = await supabase
      .from('chat_messages')
      .select('*')
      .eq('cv_id', cvId)
      .order('created_at', { ascending: false })
    
    return { data, error }
  },

  // Save chat message
  async saveMessage(messageData) {
    const { data, error } = await supabase
      .from('chat_messages')
      .insert(messageData)
      .select()
      .single()
    
    return { data, error }
  },

  // Get user's chat sessions
  async getUserSessions(userId) {
    const { data, error } = await supabase
      .from('chat_messages')
      .select('session_id, created_at, cv_id')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
    
    // Group by session_id and get latest message per session
    const sessions = data?.reduce((acc, msg) => {
      if (!acc.find(s => s.session_id === msg.session_id)) {
        acc.push(msg)
      }
      return acc
    }, [])
    
    return { data: sessions, error }
  }
}

// ===============================================
// EXPERIENCE SERVICES
// ===============================================

export const experienceService = {
  // Get user experiences
  async getUserExperiences(userId) {
    const { data, error } = await supabase
      .from('experiences')
      .select('*')
      .eq('user_id', userId)
      .order('start_date', { ascending: false })
    
    return { data, error }
  },

  // Create experience
  async createExperience(experienceData) {
    const { data, error } = await supabase
      .from('experiences')
      .insert(experienceData)
      .select()
      .single()
    
    return { data, error }
  },

  // Update experience
  async updateExperience(experienceId, experienceData) {
    const { data, error } = await supabase
      .from('experiences')
      .update(experienceData)
      .eq('id', experienceId)
      .select()
      .single()
    
    return { data, error }
  },

  // Delete experience
  async deleteExperience(experienceId) {
    const { data, error } = await supabase
      .from('experiences')
      .delete()
      .eq('id', experienceId)
    
    return { data, error }
  }
}

// ===============================================
// EDUCATION SERVICES
// ===============================================

export const educationService = {
  // Get user education
  async getUserEducation(userId) {
    const { data, error } = await supabase
      .from('education')
      .select('*')
      .eq('user_id', userId)
      .order('start_date', { ascending: false })
    
    return { data, error }
  },

  // Create education entry
  async createEducation(educationData) {
    const { data, error } = await supabase
      .from('education')
      .insert(educationData)
      .select()
      .single()
    
    return { data, error }
  },

  // Update education
  async updateEducation(educationId, educationData) {
    const { data, error } = await supabase
      .from('education')
      .update(educationData)
      .eq('id', educationId)
      .select()
      .single()
    
    return { data, error }
  },

  // Delete education
  async deleteEducation(educationId) {
    const { data, error } = await supabase
      .from('education')
      .delete()
      .eq('id', educationId)
    
    return { data, error }
  }
}

// ===============================================
// SKILLS SERVICES
// ===============================================

export const skillsService = {
  // Get user skills
  async getUserSkills(userId) {
    const { data, error } = await supabase
      .from('skills')
      .select('*')
      .eq('user_id', userId)
      .order('order_index', { ascending: true })
    
    return { data, error }
  },

  // Get skills by category
  async getSkillsByCategory(userId, category) {
    const { data, error } = await supabase
      .from('skills')
      .select('*')
      .eq('user_id', userId)
      .eq('category', category)
      .order('order_index', { ascending: true })
    
    return { data, error }
  },

  // Create skill
  async createSkill(skillData) {
    const { data, error } = await supabase
      .from('skills')
      .insert(skillData)
      .select()
      .single()
    
    return { data, error }
  },

  // Update skill
  async updateSkill(skillId, skillData) {
    const { data, error } = await supabase
      .from('skills')
      .update(skillData)
      .eq('id', skillId)
      .select()
      .single()
    
    return { data, error }
  },

  // Delete skill
  async deleteSkill(skillId) {
    const { data, error } = await supabase
      .from('skills')
      .delete()
      .eq('id', skillId)
    
    return { data, error }
  },

  // Get featured skills
  async getFeaturedSkills(userId) {
    const { data, error } = await supabase
      .from('skills')
      .select('*')
      .eq('user_id', userId)
      .eq('is_featured', true)
      .order('proficiency_level', { ascending: false })
    
    return { data, error }
  }
}

// ===============================================
// FILE UPLOAD SERVICES
// ===============================================

export const fileService = {
  // Upload CV file
  async uploadCVFile(file, userId) {
    const fileExt = file.name.split('.').pop()
    const fileName = `${userId}/cv-${Date.now()}.${fileExt}`
    
    const { data, error } = await supabase.storage
      .from('cvs')
      .upload(fileName, file)
    
    if (error) return { data: null, error }
    
    // Get public URL
    const { data: { publicUrl } } = supabase.storage
      .from('cvs')
      .getPublicUrl(fileName)
    
    // Save file info to database
    const fileRecord = await supabase
      .from('file_uploads')
      .insert({
        user_id: userId,
        file_name: file.name,
        file_url: publicUrl,
        file_type: file.type,
        file_size: file.size,
        bucket_name: 'cvs',
        upload_path: fileName
      })
      .select()
      .single()
    
    return { 
      data: { 
        url: publicUrl, 
        path: fileName,
        record: fileRecord.data 
      }, 
      error: fileRecord.error 
    }
  },

  // Delete file
  async deleteFile(filePath) {
    const { data, error } = await supabase.storage
      .from('cvs')
      .remove([filePath])
    
    return { data, error }
  },

  // Get user files
  async getUserFiles(userId) {
    const { data, error } = await supabase
      .from('file_uploads')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
    
    return { data, error }
  }
}

// ===============================================
// COMPREHENSIVE DATA SERVICES
// ===============================================

export const comprehensiveService = {
  // Get complete user data
  async getCompleteUserData(userId) {
    const [profile, cvs, projects, experiences, education, skills] = await Promise.all([
      userProfileService.getProfile(userId),
      cvService.getUserCVs(userId),
      projectService.getUserProjects(userId),
      experienceService.getUserExperiences(userId),
      educationService.getUserEducation(userId),
      skillsService.getUserSkills(userId)
    ])
    
    return {
      profile: profile.data,
      cvs: cvs.data,
      projects: projects.data,
      experiences: experiences.data,
      education: education.data,
      skills: skills.data,
      errors: {
        profile: profile.error,
        cvs: cvs.error,
        projects: projects.error,
        experiences: experiences.error,
        education: education.error,
        skills: skills.error
      }
    }
  },

  // Get CV with all related data
  async getCVWithRelatedData(cvId, userId) {
    const [cv, versions, projects, messages] = await Promise.all([
      supabase.from('cvs').select('*').eq('id', cvId).single(),
      cvVersionService.getCVVersions(cvId),
      projectService.getCVProjects(cvId),
      chatService.getCVMessages(cvId)
    ])
    
    return {
      cv: cv.data,
      versions: versions.data,
      projects: projects.data,
      messages: messages.data,
      errors: {
        cv: cv.error,
        versions: versions.error,
        projects: projects.error,
        messages: messages.error
      }
    }
  }
}

// ===============================================
// REAL-TIME SUBSCRIPTIONS
// ===============================================

export const subscriptionService = {
  // Subscribe to CV changes
  subscribeToCVChanges(cvId, callback) {
    return supabase
      .channel(`cv-${cvId}`)
      .on('postgres_changes', 
        { event: '*', schema: 'public', table: 'cvs', filter: `id=eq.${cvId}` },
        callback
      )
      .subscribe()
  },

  // Subscribe to chat messages
  subscribeToChatMessages(sessionId, callback) {
    return supabase
      .channel(`chat-${sessionId}`)
      .on('postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'chat_messages', filter: `session_id=eq.${sessionId}` },
        callback
      )
      .subscribe()
  },

  // Subscribe to user profile changes
  subscribeToProfileChanges(userId, callback) {
    return supabase
      .channel(`profile-${userId}`)
      .on('postgres_changes',
        { event: '*', schema: 'public', table: 'user_profiles', filter: `user_id=eq.${userId}` },
        callback
      )
      .subscribe()
  }
}

// ===============================================
// UTILITY FUNCTIONS
// ===============================================

export const dbUtils = {
  // Generate session ID for chat
  generateSessionId() {
    return crypto.randomUUID()
  },

  // Format error message
  formatError(error) {
    if (!error) return null
    return error.message || 'An unexpected error occurred'
  },

  // Check if user owns resource
  async checkOwnership(table, resourceId, userId) {
    const { data, error } = await supabase
      .from(table)
      .select('user_id')
      .eq('id', resourceId)
      .single()
    
    if (error) return false
    return data.user_id === userId
  }
}

// Export all services as default
export default {
  userProfile: userProfileService,
  cv: cvService,
  cvVersion: cvVersionService,
  project: projectService,
  chat: chatService,
  experience: experienceService,
  education: educationService,
  skills: skillsService,
  file: fileService,
  comprehensive: comprehensiveService,
  subscription: subscriptionService,
  utils: dbUtils
} 