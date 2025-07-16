import axios from 'axios';

// OpenAI API configuration
const OPENAI_API_KEY = process.env.REACT_APP_OPENAI_API_KEY;
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

// Create axios instance with proper headers
const openaiApi = axios.create({
  baseURL: 'https://api.openai.com/v1',
  headers: {
    'Authorization': `Bearer ${OPENAI_API_KEY}`,
    'Content-Type': 'application/json',
  }
});

// Check if API key is available
const isApiKeyAvailable = () => {
  return OPENAI_API_KEY && OPENAI_API_KEY.startsWith('sk-');
};

// Generate CV enhancement using OpenAI
export const generateCVEnhancement = async (prompt, cvData = null) => {
  if (!isApiKeyAvailable()) {
    console.warn('OpenAI API key not available, using fallback response');
    return generateFallbackResponse(prompt);
  }

  try {
    const messages = [
      {
        role: "system",
        content: "You are a professional CV assistant. Provide helpful, accurate responses based on the user's CV content. Do not make up or hallucinate information that is not present in the CV."
      },
      {
        role: "user",
        content: prompt
      }
    ];

    const response = await openaiApi.post('/chat/completions', {
      model: "gpt-4o",
      messages: messages,
      temperature: 0.3,
      max_tokens: 500
    });

    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('OpenAI API error:', error);
    
    if (error.response?.status === 401) {
      console.error('OpenAI authentication failed. Please check your API key.');
      return "🔐 OpenAI authentication failed. Please check the API key configuration.";
    }
    
    return generateFallbackResponse(prompt);
  }
};

// Enhance CV content with new information
export const enhanceCV = async (currentCV, updates) => {
  if (!isApiKeyAvailable()) {
    console.warn('OpenAI API key not available, using simple text appending');
    return enhanceCVFallback(currentCV, updates);
  }

  try {
    const prompt = `
Please enhance this CV by incorporating the following updates naturally into the appropriate sections:

Current CV:
${currentCV}

Updates to add:
${updates.join('\n')}

Instructions:
1. Add the new information to the most appropriate section (Skills, Experience, Education, etc.)
2. Maintain the original CV structure and formatting
3. Don't duplicate existing information
4. Return the complete enhanced CV

Enhanced CV:`;

    const response = await openaiApi.post('/chat/completions', {
      model: "gpt-4o",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.2,
      max_tokens: 2000
    });

    return response.data.choices[0].message.content;
  } catch (error) {
    console.error('CV enhancement error:', error);
    return enhanceCVFallback(currentCV, updates);
  }
};

// Extract projects from CV content
export const extractProjectsFromCV = async (cvContent) => {
  if (!isApiKeyAvailable()) {
    console.warn('OpenAI API key not available, using pattern matching for project extraction');
    return extractProjectsFallback(cvContent);
  }

  try {
    const prompt = `
Extract project information from this CV content and return as JSON array:

${cvContent}

Extract projects with these fields:
- title: project name
- description: what the project does
- technologies: array of technologies used
- duration: timeframe if mentioned
- highlights: key achievements

Return JSON array format: [{"title": "", "description": "", "technologies": [], "duration": "", "highlights": []}]
Return empty array [] if no projects found.`;

    const response = await openaiApi.post('/chat/completions', {
      model: "gpt-4o",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.1,
      max_tokens: 1000
    });

    try {
      const result = JSON.parse(response.data.choices[0].message.content);
      return Array.isArray(result) ? result : [];
    } catch (parseError) {
      console.error('Failed to parse extracted projects:', parseError);
      return extractProjectsFallback(cvContent);
    }
  } catch (error) {
    console.error('Project extraction error:', error);
    return extractProjectsFallback(cvContent);
  }
};

// Fallback functions when OpenAI is not available
const generateFallbackResponse = (prompt) => {
  if (prompt.toLowerCase().includes('skill')) {
    return "I can see you're asking about skills. Could you provide more specific details about what skills you'd like to add or learn about?";
  } else if (prompt.toLowerCase().includes('experience')) {
    return "I'd be happy to help with work experience. Please provide details about your role, company, and key achievements.";
  } else if (prompt.toLowerCase().includes('education')) {
    return "I can help you with education information. Please share details about your degree, institution, and graduation year.";
  } else {
    return "I'm here to help you enhance your CV. Could you please provide more specific information about what you'd like to add or update?";
  }
};

const enhanceCVFallback = (currentCV, updates) => {
  // Simple fallback: append updates to the end of CV
  return currentCV + '\n\nAdditional Information:\n' + updates.join('\n');
};

const extractProjectsFallback = (cvContent) => {
  // Simple pattern matching for projects
  const projectKeywords = ['project', 'built', 'developed', 'created', 'designed', 'implemented'];
  const lines = cvContent.split('\n');
  const projects = [];
  
  for (const line of lines) {
    const lowerLine = line.toLowerCase();
    if (projectKeywords.some(keyword => lowerLine.includes(keyword))) {
      projects.push({
        title: line.trim(),
        description: 'Project extracted from CV',
        technologies: [],
        duration: '',
        highlights: []
      });
    }
  }
  
  return projects.slice(0, 3); // Limit to 3 projects
};

export default {
  generateCVEnhancement,
  enhanceCV,
  extractProjectsFromCV
}; 