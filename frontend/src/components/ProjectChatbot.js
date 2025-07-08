import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const ChatbotContainer = styled.div`
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 400px;
  height: 600px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 25px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  transform: ${props => props.isOpen ? 'translateY(0)' : 'translateY(calc(100% - 70px))'};
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  
  @media (max-width: 768px) {
    width: calc(100vw - 40px);
    right: 20px;
    left: 20px;
    height: ${props => props.isOpen ? '80vh' : '70px'};
  }
`;

const ChatHeader = styled.div`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 20px;
  border-radius: 25px 25px 0 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  min-height: 70px;
  box-sizing: border-box;
`;

const HeaderInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  
  .bot-icon {
    font-size: 1.8rem;
    animation: pulse 2s infinite;
  }
  
  .header-text {
    .title {
      font-size: 1.1rem;
      font-weight: 700;
      margin: 0;
    }
    
    .subtitle {
      font-size: 0.85rem;
      opacity: 0.9;
      margin: 0;
    }
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.1);
  }
`;

const ChatMessages = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 15px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.05);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.3);
    border-radius: 3px;
  }
`;

const Message = styled.div`
  display: flex;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 12px;
`;

const MessageBubble = styled.div`
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 0.9rem;
  line-height: 1.4;
  
  ${props => props.isUser ? `
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border-bottom-right-radius: 6px;
    animation: slideInRight 0.3s ease-out;
  ` : `
    background: rgba(102, 126, 234, 0.1);
    color: #2d3748;
    border-bottom-left-radius: 6px;
    animation: slideInLeft 0.3s ease-out;
  `}
  
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
  
  @keyframes slideInLeft {
    from {
      opacity: 0;
      transform: translateX(-20px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
`;

const TypingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 18px;
  border-bottom-left-radius: 6px;
  max-width: 80px;
  
  .typing-dots {
    display: flex;
    gap: 4px;
    
    .dot {
      width: 6px;
      height: 6px;
      background: #667eea;
      border-radius: 50%;
      animation: typing 1.4s infinite;
      
      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
  }
  
  @keyframes typing {
    0%, 60%, 100% { transform: scale(1); opacity: 0.7; }
    30% { transform: scale(1.2); opacity: 1; }
  }
`;

const InputContainer = styled.div`
  padding: 20px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
  background: rgba(255, 255, 255, 0.9);
  border-radius: 0 0 25px 25px;
`;

const InputWrapper = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const Input = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 20px;
  font-size: 0.9rem;
  outline: none;
  transition: all 0.3s ease;
  
  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  &::placeholder {
    color: #a0aec0;
  }
`;

const SendButton = styled.button`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  min-width: 45px;
  min-height: 45px;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const SuggestedActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 15px;
`;

const ActionButton = styled.button`
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
  padding: 8px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateY(-2px);
  }
`;

const DownloadButton = styled.a`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  text-decoration: none;
  padding: 10px 16px;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-top: 10px;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
  }
`;

const BlogPostContainer = styled.div`
  background: rgba(0, 119, 181, 0.05);
  border: 1px solid rgba(0, 119, 181, 0.2);
  border-radius: 12px;
  padding: 16px;
  margin: 8px 0;
  position: relative;
  
  .blog-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-weight: 600;
    color: #0077b5;
    font-size: 0.9rem;
  }
  
  .blog-content {
    font-size: 0.85rem;
    line-height: 1.5;
    color: #2d3748;
    white-space: pre-line;
    margin-bottom: 12px;
  }
  
  .blog-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
`;

const CopyButton = styled.button`
  background: rgba(0, 119, 181, 0.1);
  color: #0077b5;
  border: 1px solid rgba(0, 119, 181, 0.3);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    background: rgba(0, 119, 181, 0.2);
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

function ProjectChatbot({ projects, onProjectUpdate, onProjectAdd, onProjectDelete, onProjectsReload }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "👋 Hi! I'm your Project Assistant. I can help you:\n\n• Add new projects\n• Delete existing projects\n• Edit project details\n• Generate and download your updated CV\n• Clean up duplicate CV sections\n• Create LinkedIn blog posts for your projects\n\nTry: 'Add a new project', 'Give me my updated CV', 'Clean up my CV', or 'Create a LinkedIn blog for [project name]'",
      isUser: false,
      timestamp: new Date(),
      isBlog: false
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const simulateTyping = (duration = 1000) => {
    setIsTyping(true);
    setTimeout(() => setIsTyping(false), duration);
  };

  const addMessage = (text, isUser = false, isBlog = false, blogData = null) => {
    const newMessage = {
      text,
      isUser,
      isBlog,
      blogData,
      id: Date.now() + Math.random()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      // Show temporary success message
      const tempMessage = {
        text: "✅ Blog post copied to clipboard!",
        isUser: false,
        id: Date.now() + Math.random(),
        isTemporary: true
      };
      setMessages(prev => [...prev, tempMessage]);
      
      // Remove temporary message after 2 seconds
      setTimeout(() => {
        setMessages(prev => prev.filter(msg => !msg.isTemporary));
      }, 2000);
    } catch (error) {
      console.error('Failed to copy text: ', error);
      addMessage("❌ Failed to copy to clipboard. Please select and copy the text manually.");
    }
  };

  const classifyMessage = (message) => {
    const msg = message.toLowerCase();
    
    if (msg.includes('cv') || msg.includes('download') || msg.includes('updated cv') || msg.includes('generate cv')) {
      return 'download_cv';
    }
    if (msg.includes('clean') || msg.includes('cleanup') || msg.includes('fix') || msg.includes('duplicate') || msg.includes('remove duplicate')) {
      return 'cleanup_cv';
    }
    if (msg.includes('blog') || msg.includes('linkedin')) {
      return 'generate_blog';
    }
    if (msg.includes('built') || msg.includes('created') || msg.includes('developed') || msg.includes('add') || msg.includes('new project')) {
      return 'add_project';
    }
    if (msg.includes('delete') || msg.includes('remove')) {
      return 'delete_project';
    }
    if (msg.includes('edit') || msg.includes('update') || msg.includes('modify')) {
      return 'edit_project';
    }
    if (msg.includes('list') || msg.includes('show') || msg.includes('projects')) {
      return 'list_projects';
    }
    return 'general';
  };

  const handleDownloadCV = async () => {
    try {
      const response = await axios.post('http://localhost:8000/cv/download', {}, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Professional_CV_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return "✅ Your updated CV has been downloaded to your local drive!";
    } catch (error) {
      console.error('Download error:', error);
      return "❌ Sorry, I couldn't download your CV. Please try again later.";
    }
  };

  const extractProjectName = (message) => {
    const msg = message.toLowerCase();
    
    // Look for patterns like "blog for [project name]", "blog about [project name]", etc.
    const patterns = [
      /blog (?:for|about|on) (.*?)(?:\s|$)/,
      /(?:create|write|generate) (?:a )?blog (?:for|about|on) (.*?)(?:\s|$)/,
      /linkedin (?:post|blog) (?:for|about|on) (.*?)(?:\s|$)/,
      /create linkedin blog for (.*?)(?:\s|$)/i,
      /linkedin blog for (.*?)(?:\s|$)/i,
      /(.*?) blog/,
      /(.*?) linkedin/
    ];
    
    for (const pattern of patterns) {
      const match = msg.match(pattern);
      if (match && match[1]) {
        return match[1].trim();
      }
    }
    
    // If "create linkedin blog" without "for", pick the first project
    if (msg.includes('create linkedin blog') || msg.includes('linkedin blog')) {
      if (projects && projects.length > 0) {
        return projects[0].title;
      }
    }
    
    // If no specific pattern found, check if any project names are mentioned
    for (const project of projects) {
      if (msg.includes(project.title.toLowerCase())) {
        return project.title;
      }
    }
    
    return null;
  };

  const extractProjectFromMessage = async (message) => {
    const msg = message.toLowerCase();
    
    try {
      // Try to extract project details using simple pattern matching
      let title = '';
      let technologies = [];
      let description = message;
      
      // Extract project title
      const titlePatterns = [
        /(?:built|created|developed|made|worked on) (?:a |an |the )?([^,\.]+?)(?:\s+using|\s+with|\s+in|$)/i,
        /project called ([^,\.]+)/i,
        /(?:built|created|developed|made) ([^,\.]+)/i
      ];
      
      for (const pattern of titlePatterns) {
        const match = message.match(pattern);
        if (match && match[1]) {
          title = match[1].trim();
          break;
        }
      }
      
      // Extract technologies
      const techPatterns = [
        /using ([^,\.]+)/gi,
        /with ([^,\.]+)/gi,
        /in ([^,\.]+)/gi
      ];
      
      const techSet = new Set();
      
      // First, extract from common patterns
      for (const pattern of techPatterns) {
        const matches = message.match(pattern);
        if (matches) {
          matches.forEach(match => {
            const tech = match.replace(/^(using|with|in)\s+/i, '').trim();
            if (tech.length > 0 && tech.length < 30) {
              // Split by 'and' to get individual technologies
              const techs = tech.split(/\s+and\s+/gi);
              techs.forEach(t => {
                if (t.trim().length > 0) {
                  techSet.add(t.trim());
                }
              });
            }
          });
        }
      }
      
      // Then, look for specific technology names
      const techNames = [
        'react', 'vue', 'angular', 'javascript', 'python', 'java', 'php', 'nodejs', 
        'express', 'django', 'flask', 'mongodb', 'mysql', 'postgresql', 'html', 
        'css', 'bootstrap', 'tailwind', 'typescript', 'golang', 'rust', 'c++', 
        'c#', 'swift', 'kotlin', 'flutter', 'dart', 'figma', 'docker', 'kubernetes', 
        'aws', 'azure', 'gcp', 'git', 'github', 'gitlab', 'jira', 'agile', 'scrum',
        'fastapi', 'next.js', 'nuxt.js', 'redux', 'vuex', 'sass', 'scss', 'webpack',
        'vite', 'firebase', 'supabase', 'graphql', 'rest', 'api', 'json', 'xml'
      ];
      
      const lowerMessage = message.toLowerCase();
      for (const tech of techNames) {
        if (lowerMessage.includes(tech)) {
          techSet.add(tech);
        }
      }
      
      technologies = Array.from(techSet);
      
      // If no title found, try to generate one from technologies
      if (!title && technologies.length > 0) {
        title = `${technologies[0]} Project`;
      }
      
      // Default title if nothing found
      if (!title) {
        title = 'New Project';
      }
      
      return {
        title: title,
        description: description.length > 20 ? description : 'A project I worked on',
        technologies: technologies,
        duration: 'Recently',
        highlights: []
      };
      
    } catch (error) {
      console.error('Error extracting project:', error);
      return null;
    }
  };

  const handleGenerateBlog = async (projectName) => {
    try {
      const response = await axios.post('http://localhost:8000/blog/generate', {
        project_title: projectName
      });
      
      if (response.data.success) {
        return {
          success: true,
          blog: response.data.blog_content,
          projectTitle: response.data.project_title
        };
      } else {
        return {
          success: false,
          message: response.data.blog_content
        };
      }
    } catch (error) {
      console.error('Blog generation error:', error);
      return {
        success: false,
        message: "❌ Sorry, I couldn't generate the blog post. Please try again later."
      };
    }
  };

  const processMessage = async (message) => {
    const category = classifyMessage(message);
    
    switch (category) {
      case 'download_cv':
        simulateTyping(1500);
        setTimeout(async () => {
          const result = await handleDownloadCV();
          addMessage(result);
        }, 1500);
        break;
        
      case 'cleanup_cv':
        simulateTyping(1500);
        setTimeout(async () => {
          const result = await axios.post('http://localhost:8000/cv/cleanup');
          if (result.data.success) {
            addMessage("✅ Your CV has been cleaned up and updated!");
          } else {
            addMessage("❌ Sorry, I couldn't clean up your CV. Please try again later.");
          }
        }, 1500);
        break;
        
      case 'generate_blog':
        let projectName = extractProjectName(message);
        
        // If no specific project name found but user wants to create blog, use first available project
        if (!projectName && projects && projects.length > 0) {
          projectName = projects[0].title;
        }
        
        if (!projectName) {
          simulateTyping();
          setTimeout(() => {
            if (projects.length === 0) {
              addMessage("📭 You don't have any projects yet. Please add a project first before generating a blog post.");
            } else {
              const projectList = projects.map((p, i) => `${i + 1}. ${p.title}`).join('\n');
              addMessage(`📝 Please specify which project you'd like to create a LinkedIn blog about:\n\n${projectList}\n\nJust say "blog for [project name]" or "create LinkedIn post for [project name]"`);
            }
          }, 1000);
        } else {
          simulateTyping(2000);
          setTimeout(async () => {
            const result = await handleGenerateBlog(projectName);
            if (result.success) {
              addMessage(
                `📝 LinkedIn Blog Post for "${result.projectTitle}"`, 
                false, 
                true, 
                {
                  blog: result.blog,
                  projectTitle: result.projectTitle
                }
              );
            } else {
              addMessage(result.message);
            }
          }, 2000);
        }
        break;
        
      case 'add_project':
        simulateTyping();
        setTimeout(async () => {
          // Check if user provided project details in their message
          const msg = message.toLowerCase();
          
          if (msg.includes('built') || msg.includes('created') || msg.includes('developed') || msg.includes('made') || msg.includes('worked on')) {
            try {
              // Extract project details from message
              const projectData = await extractProjectFromMessage(message);
              
              if (projectData) {
                const response = await axios.post('http://localhost:8000/projects/', projectData);
                
                if (response.data && response.data.message === "Project created successfully") {
                  // Reload projects to get fresh data with IDs
                  if (onProjectsReload) {
                    await onProjectsReload();
                  }
                  const createdProject = response.data.project || projectData;
                  addMessage(`🎉 Awesome! I've added "${createdProject.title}" to your projects!\n\n📝 **Technologies**: ${createdProject.technologies.join(', ')}\n📅 **Duration**: ${createdProject.duration || 'Not specified'}\n\nYour project is now part of your portfolio!`);
                } else {
                  addMessage("❌ Sorry, I couldn't add that project. Please try again with more details.");
                }
              } else {
                addMessage("🤔 I need more details to create your project. Please provide:\n\n1. Project title\n2. Technologies used\n3. Brief description\n\nTry: 'I built a Weather App using React and OpenWeatherMap API'");
              }
            } catch (error) {
              console.error('Error adding project:', error);
              addMessage("❌ Sorry, there was an error adding your project. Please try again or use the 'Add New Project' button.");
            }
          } else {
            addMessage("🚀 I'd love to help you add a new project! Please tell me about what you built:\n\n**Examples:**\n• 'I built a Weather App using React and OpenWeatherMap API'\n• 'I created an e-commerce site with Node.js and MongoDB'\n• 'I developed a mobile app using React Native'\n\nOr use the 'Add New Project' button above for a guided form.");
          }
        }, 1000);
        break;
        
      case 'delete_project':
        simulateTyping();
        setTimeout(async () => {
          if (projects.length === 0) {
            addMessage("📭 You don't have any projects to delete yet.");
          } else {
            // Try to extract project name or number from message
            const msg = message.toLowerCase();
            let projectToDelete = null;
            
            // Check for project number
            const numberMatch = msg.match(/delete project (\d+)|remove project (\d+)|(\d+)/);
            if (numberMatch) {
              const projectIndex = parseInt(numberMatch[1] || numberMatch[2] || numberMatch[3]) - 1;
              if (projectIndex >= 0 && projectIndex < projects.length) {
                projectToDelete = projectIndex;
              }
            }
            
            // Check for project name
            if (!projectToDelete && projectToDelete !== 0) {
              for (let i = 0; i < projects.length; i++) {
                if (msg.includes(projects[i].title.toLowerCase())) {
                  projectToDelete = i;
                  break;
                }
              }
            }
            
            if (projectToDelete !== null) {
              // Delete the project
              const deletedProject = projects[projectToDelete];
              
              // Check if project has an ID (can be deleted from backend)
              if (deletedProject.id) {
                try {
                  await axios.delete(`http://localhost:8000/projects/${deletedProject.id}`);
                  // Reload projects after successful deletion
                  if (onProjectsReload) {
                    await onProjectsReload();
                  }
                  addMessage(`🗑️ Successfully deleted "${deletedProject.title}" project!`);
                } catch (error) {
                  console.error('Error deleting project:', error);
                  addMessage(`❌ Sorry, I couldn't delete "${deletedProject.title}". Please try again.`);
                }
              } else {
                addMessage(`❌ Sorry, I can't delete "${deletedProject.title}" because it was extracted from your CV. Only manually created projects can be deleted.`);
              }
            } else {
              const projectList = projects.map((p, i) => `${i + 1}. ${p.title}${p.id ? '' : ' (from CV)'}`).join('\n');
              addMessage(`🗑️ Which project would you like to delete? Here are your current projects:\n\n${projectList}\n\nJust say "delete project 1" or "delete [project name]"\n\nNote: Only manually created projects can be deleted.`);
            }
          }
        }, 1000);
        break;
        
      case 'list_projects':
        simulateTyping();
        setTimeout(() => {
          if (projects.length === 0) {
            addMessage("📭 You don't have any projects yet. Would you like to add one?");
          } else {
            const projectList = projects.map((p, i) => 
              `${i + 1}. **${p.title}**\n   Duration: ${p.duration || 'Not specified'}\n   Technologies: ${p.technologies?.join(', ') || 'None specified'}`
            ).join('\n\n');
            addMessage(`📂 Here are your current projects:\n\n${projectList}`);
          }
        }, 1000);
        break;
        
      default:
        simulateTyping();
        setTimeout(() => {
          addMessage("🤔 I can help you with:\n\n• **Adding projects**: 'Add a new project'\n• **Deleting projects**: 'Delete project [name]'\n• **Listing projects**: 'Show my projects'\n• **Downloading CV**: 'Give me my updated CV'\n• **Cleaning CV**: 'Clean up my CV'\n• **Creating blogs**: 'Create LinkedIn blog for [project name]'\n\nWhat would you like to do?");
        }, 1000);
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isSending) return;
    
    setIsSending(true);
    const userMessage = inputValue.trim();
    setInputValue('');
    
    // Add user message
    addMessage(userMessage, true);
    
    // Process the message
    await processMessage(userMessage);
    
    setIsSending(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedActions = [
    "Add new project",
    "Show my projects", 
    "Download my CV",
    "Clean up my CV",
    "Create LinkedIn blog",
    "Delete a project"
  ];

  return (
    <ChatbotContainer isOpen={isOpen}>
      <ChatHeader onClick={() => setIsOpen(!isOpen)}>
        <HeaderInfo>
          <div className="bot-icon">🤖</div>
          <div className="header-text">
            <div className="title">Project Assistant</div>
            <div className="subtitle">
              {isOpen ? 'Managing your projects' : 'Click to chat'}
            </div>
          </div>
        </HeaderInfo>
        <ToggleButton>
          {isOpen ? '▼' : '▲'}
        </ToggleButton>
      </ChatHeader>
      
      {isOpen && (
        <>
          <ChatMessages>
            {messages.map((message) => (
              <Message key={message.id} isUser={message.isUser}>
                <MessageBubble isUser={message.isUser}>
                  {message.isBlog ? (
                    <BlogPostContainer>
                      <div className="blog-header">
                        <span>🔗</span>
                        <span>{message.text}</span>
                      </div>
                      <div className="blog-content">
                        {message.blogData.blog}
                      </div>
                      <div className="blog-actions">
                        <CopyButton onClick={() => copyToClipboard(message.blogData.blog)}>
                          📋 Copy to Clipboard
                        </CopyButton>
                        <span style={{fontSize: '0.8rem', color: '#666'}}>
                          Ready for LinkedIn!
                        </span>
                      </div>
                    </BlogPostContainer>
                  ) : (
                    message.text.split('\n').map((line, i) => (
                      <div key={i}>
                        {line.includes('**') ? (
                          <span dangerouslySetInnerHTML={{
                            __html: line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          }} />
                        ) : line}
                      </div>
                    ))
                  )}
                </MessageBubble>
              </Message>
            ))}
            
            {isTyping && (
              <Message isUser={false}>
                <TypingIndicator>
                  <div className="typing-dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                </TypingIndicator>
              </Message>
            )}
            
            <div ref={messagesEndRef} />
          </ChatMessages>
          
          <InputContainer>
            <SuggestedActions>
              {suggestedActions.map((action, index) => (
                <ActionButton 
                  key={index} 
                  onClick={() => {
                    setInputValue(action);
                    setTimeout(handleSend, 100);
                  }}
                >
                  {action}
                </ActionButton>
              ))}
            </SuggestedActions>
            
            <InputWrapper>
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about projects or CV..."
                disabled={isSending}
              />
              <SendButton 
                onClick={handleSend} 
                disabled={!inputValue.trim() || isSending}
              >
                {isSending ? '⏳' : '➤'}
              </SendButton>
            </InputWrapper>
          </InputContainer>
        </>
      )}
    </ChatbotContainer>
  );
}

export default ProjectChatbot; 