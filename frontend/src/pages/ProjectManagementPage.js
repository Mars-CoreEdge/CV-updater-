import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useTheme } from '../contexts/ThemeContext';
import ThemeToggle from '../components/ThemeToggle';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8081';

const PageContainer = styled.div`
  min-height: 100vh;
  background: ${props => props.theme.colors.background};
  padding: 20px;
  transition: background 0.3s ease;
`;

const ContentWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  text-align: center;
  color: ${props => props.theme.colors.textPrimary};
  margin-bottom: 30px;
  position: relative;
`;

const HeaderTop = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 15px;
  }
`;

const BackButton = styled.button`
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.textPrimary};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    background: ${props => props.theme.colors.surfaceHover};
    transform: translateY(-2px);
    box-shadow: 0 8px 25px ${props => props.theme.colors.shadow};
  }
`;

const Title = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
  background: ${props => props.theme.colors.gradient};
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  opacity: 0.9;
  color: ${props => props.theme.colors.textSecondary};
`;

const MainLayout = styled.div`
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
`;

const ActionBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 15px;
`;

const Button = styled.button`
  background: ${props => props.variant === 'primary' ? props.theme.colors.gradient : props.theme.colors.surface};
  color: ${props => props.variant === 'primary' ? props.theme.colors.textLight : props.theme.colors.textPrimary};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px ${props => props.theme.colors.shadow};
    background: ${props => props.variant === 'primary' ? props.theme.colors.gradientHover : props.theme.colors.surfaceHover};
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const ProjectsContainer = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 60px ${props => props.theme.colors.shadow};
  transition: all 0.3s ease;
`;

const ProjectsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
`;

const ProjectCard = styled.div`
  background: ${props => props.theme.colors.backgroundSecondary};
  border-radius: 15px;
  padding: 20px;
  border: 1px solid ${props => props.theme.colors.border};
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px ${props => props.theme.colors.shadow};
    background: ${props => props.theme.colors.surface};
  }
`;

const ProjectTitle = styled.h3`
  font-size: 1.2rem;
  color: ${props => props.theme.colors.textPrimary};
  margin: 0 0 10px 0;
`;

const ProjectDescription = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.9rem;
  margin: 0 0 15px 0;
  line-height: 1.5;
`;

const TechTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 15px;
`;

const TechTag = styled.span`
  background: ${props => props.theme.colors.gradient};
  color: ${props => props.theme.colors.textLight};
  font-size: 0.7rem;
  padding: 3px 8px;
  border-radius: 8px;
`;

const ProjectActions = styled.div`
  display: flex;
  gap: 10px;
`;

const ActionButton = styled.button`
  background: ${props => {
    if (props.variant === 'edit') return props.theme.colors.warning;
    if (props.variant === 'delete') return props.theme.colors.danger;
    return props.theme.colors.success;
  }};
  color: ${props => props.theme.colors.textLight};
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    opacity: 0.8;
    transform: scale(1.05);
  }
`;

// Chatbot Styles
const ChatContainer = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 20px 60px ${props => props.theme.colors.shadow};
  height: 600px;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
`;

const ChatHeader = styled.div`
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid ${props => props.theme.colors.border};
`;

const ChatTitle = styled.h3`
  color: ${props => props.theme.colors.textPrimary};
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 15px 0;
  display: flex;
  flex-direction: column;
  gap: 15px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.backgroundTertiary};
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.borderHover};
    border-radius: 3px;
  }
`;

const Message = styled.div`
  display: flex;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 10px;
`;

const MessageBubble = styled.div`
  background: ${props => props.isUser 
    ? props.theme.colors.gradient 
    : props.theme.colors.backgroundSecondary};
  color: ${props => props.isUser ? props.theme.colors.textLight : props.theme.colors.textPrimary};
  padding: 12px 16px;
  border-radius: ${props => props.isUser 
    ? '20px 20px 5px 20px' 
    : '20px 20px 20px 5px'};
  max-width: 80%;
  word-wrap: break-word;
  font-size: 0.9rem;
  line-height: 1.4;
  box-shadow: 0 2px 8px ${props => props.theme.colors.shadow};
  border: ${props => props.isUser ? 'none' : `1px solid ${props.theme.colors.border}`};
`;

const ChatInputContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid ${props => props.theme.colors.border};
`;

const ChatInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 25px;
  font-size: 0.9rem;
  outline: none;
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.textPrimary};
  
  &:focus {
    border-color: ${props => props.theme.colors.borderFocus};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.borderFocus}20;
  }
  
  &::placeholder {
    color: ${props => props.theme.colors.textMuted};
  }
`;

const SendButton = styled.button`
  background: ${props => props.theme.colors.gradient};
  color: ${props => props.theme.colors.textLight};
  border: none;
  border-radius: 50%;
  width: 45px;
  height: 45px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  transition: all 0.2s ease;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 15px ${props => props.theme.colors.shadow};
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const QuickActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
`;

const QuickActionButton = styled.button`
  background: ${props => props.theme.colors.primary}20;
  color: ${props => props.theme.colors.primary};
  border: 1px solid ${props => props.theme.colors.primary}40;
  border-radius: 15px;
  padding: 6px 12px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.theme.colors.primary}30;
    transform: scale(1.05);
  }
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: ${props => props.theme.colors.surface};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 20px;
  padding: 30px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ModalTitle = styled.h2`
  font-size: 1.5rem;
  color: ${props => props.theme.colors.textPrimary};
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: ${props => props.theme.colors.textTertiary};
  
  &:hover {
    color: ${props => props.theme.colors.textPrimary};
  }
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: ${props => props.theme.colors.textSecondary};
`;

const Input = styled.input`
  width: 100%;
  padding: 12px;
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  font-size: 0.9rem;
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.textPrimary};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.borderFocus};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.borderFocus}20;
  }
  
  &::placeholder {
    color: ${props => props.theme.colors.textMuted};
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  font-size: 0.9rem;
  min-height: 100px;
  resize: vertical;
  background: ${props => props.theme.colors.surface};
  color: ${props => props.theme.colors.textPrimary};
  
  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.borderFocus};
    box-shadow: 0 0 0 3px ${props => props.theme.colors.borderFocus}20;
  }
  
  &::placeholder {
    color: ${props => props.theme.colors.textMuted};
  }
`;

const ModalActions = styled.div`
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 25px;
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: ${props => props.theme.colors.textTertiary};
`;

const LoadingSpinner = styled.div`
  text-align: center;
  padding: 40px;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid ${props => props.theme.colors.border};
    border-top: 3px solid ${props => props.theme.colors.primary};
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 20px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  @keyframes pulse {
    0%, 80%, 100% { 
      opacity: 0.3;
      transform: scale(0.8);
    }
    40% { 
      opacity: 1;
      transform: scale(1);
    }
  }
`;

function ProjectManagementPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    technologies: '',
    duration: '',
    achievements: ''
  });
  
  // Chat states
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  const navigate = useNavigate();
  const { theme } = useTheme();

  useEffect(() => {
    loadProjects();
    // Add welcome message
    setMessages([
      {
        id: 1,
        text: "👋 Hi! I'm your Project Assistant. I can help you create, edit, and manage your projects through natural conversation. Try saying 'Create a new project' or 'Show me my projects'!",
        isUser: false,
        timestamp: new Date()
      }
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadProjects = async () => {
    try {
      setLoading(true);
      console.log('Loading projects from:', `${API_BASE_URL}/projects/`);
      
      const response = await axios.get(`${API_BASE_URL}/projects/`);
      console.log('Projects loaded:', response.data);
      
      setProjects(response.data.projects || []);
    } catch (error) {
      console.error('Error loading projects:', error);
      console.error('Full error details:', error.response?.data);
      
      if (error.response?.status === 404) {
        console.log('Projects endpoint not found, setting empty array');
        setProjects([]);
      } else if (error.code === 'ECONNREFUSED') {
        console.log('Cannot connect to backend, setting empty array');
        setProjects([]);
      } else {
        setProjects([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const addChatMessage = (text, isUser = false) => {
    const newMessage = {
      id: Date.now() + Math.random(),
      text,
      isUser,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const processChatMessage = async (message) => {
    setIsChatLoading(true);
    
    try {
      const lowerMessage = message.toLowerCase();
      
      // Check for project creation
      if (lowerMessage.includes('create') || lowerMessage.includes('add') || lowerMessage.includes('new project')) {
        await handleChatProjectCreation(message);
      }
      // Check for project listing
      else if (lowerMessage.includes('show') || lowerMessage.includes('list') || lowerMessage.includes('projects')) {
        handleChatProjectListing();
      }
      // Check for project deletion
      else if (lowerMessage.includes('delete') || lowerMessage.includes('remove')) {
        handleChatProjectDeletion(message);
      }
      // Check for project editing
      else if (lowerMessage.includes('edit') || lowerMessage.includes('update') || lowerMessage.includes('modify')) {
        handleChatProjectEditing(message);
      }
      // Check for adding projects to CV
      else if (lowerMessage.includes('add to cv') || lowerMessage.includes('cv')) {
        await handleChatAddToCV();
      }
      // General help
      else {
        addChatMessage("I can help you with:\n\n🔹 Create projects: 'Create a React website project'\n🔹 List projects: 'Show my projects'\n🔹 Edit projects: 'Edit project 1'\n🔹 Delete projects: 'Delete project 2'\n🔹 Add to CV: 'Add all projects to CV'\n\nWhat would you like to do?");
      }
    } catch (error) {
      console.error('Chat processing error:', error);
      addChatMessage("Sorry, I encountered an error processing your request. Please try again.");
    } finally {
      setIsChatLoading(false);
    }
  };

  const handleChatProjectCreation = async (message) => {
    try {
      console.log('Creating project from message:', message);
      addChatMessage("🔄 Creating your project...");
      
      // Use the new backend endpoint for better project extraction
      const response = await axios.post(`${API_BASE_URL}/projects/create-from-chat`, {
        message: message
      });
      
      console.log('Backend response:', response.data);
      
      if (response.data.success) {
        await loadProjects();
        addChatMessage(`🚀 Great! I've created the project "${response.data.project.title}" for you. You can see it in the projects list above.`);
        
        // Show project details
        const project = response.data.project;
        let details = `\n📋 Project Details:\n`;
        details += `• Title: ${project.title}\n`;
        if (project.technologies && project.technologies.length > 0) {
          details += `• Technologies: ${project.technologies.join(', ')}\n`;
        }
        if (project.highlights && project.highlights.length > 0) {
          details += `• Key Features: ${project.highlights.slice(0, 2).join(', ')}\n`;
        }
        
        addChatMessage(details);
      } else {
        console.log('Project creation failed:', response.data.message);
        addChatMessage(response.data.message || "I'd be happy to help you create a project! Could you provide more details? For example: 'Create a React e-commerce website project using React, Node.js, and MongoDB'");
      }
    } catch (error) {
      console.error('Error creating project:', error);
      console.error('Full error details:', error.response?.data);
      
      // More specific error messages
      if (error.response?.status === 404) {
        addChatMessage("❌ Backend server not found. Please make sure the backend is running on http://localhost:8081");
      } else if (error.response?.status >= 500) {
        addChatMessage("❌ Server error occurred. Check the backend console for details.");
      } else if (error.code === 'ECONNREFUSED') {
        addChatMessage("❌ Cannot connect to backend server. Please ensure it's running on http://localhost:8081");
      } else {
        addChatMessage("❌ Error creating project. Please try again or use the manual form. Check console for details.");
      }
    }
  };

  const handleChatProjectListing = () => {
    if (projects.length === 0) {
      addChatMessage("📭 You don't have any projects yet. Would you like to create one?");
    } else {
      let projectList = `📂 Here are your ${projects.length} projects:\n\n`;
      projects.forEach((project, index) => {
        projectList += `${index + 1}. **${project.title}**\n`;
        if (project.technologies && project.technologies.length > 0) {
          projectList += `   Tech: ${project.technologies.slice(0, 3).join(', ')}\n`;
        }
        projectList += `\n`;
      });
      addChatMessage(projectList);
    }
  };

  const handleChatProjectDeletion = async (message) => {
    const projectNumber = extractProjectNumber(message);
    if (projectNumber && projectNumber <= projects.length) {
      const project = projects[projectNumber - 1];
      try {
        await handleDelete(project.id);
        addChatMessage(`🗑️ Successfully deleted "${project.title}"`);
      } catch (error) {
        addChatMessage("❌ Error deleting project. Please try again.");
      }
    } else {
      addChatMessage("Please specify which project to delete (e.g., 'Delete project 1')");
    }
  };

  const handleChatProjectEditing = (message) => {
    const projectNumber = extractProjectNumber(message);
    if (projectNumber && projectNumber <= projects.length) {
      const project = projects[projectNumber - 1];
      addChatMessage(`✏️ To edit "${project.title}", please use the edit button in the project card above, or tell me specifically what you'd like to change about it.`);
    } else {
      addChatMessage("Please specify which project to edit (e.g., 'Edit project 1')");
    }
  };

  const handleChatAddToCV = async () => {
    try {
      addChatMessage("📄 Adding all projects to your CV...");
      
      const response = await axios.post(`${API_BASE_URL}/cv/add-projects`);
      
      if (response.data.success) {
        addChatMessage("✅ Successfully added all projects to your CV! You can view your updated CV in the main dashboard.");
      } else {
        addChatMessage("❌ Error adding projects to CV. Please try again.");
      }
    } catch (error) {
      console.error('Error adding projects to CV:', error);
      addChatMessage("❌ Error adding projects to CV. Please ensure you have an active CV uploaded.");
    }
  };

  const extractProjectNumber = (message) => {
    const match = message.match(/(\d+)/);
    return match ? parseInt(match[1]) : null;
  };

  const handleChatSend = () => {
    if (chatInput.trim()) {
      addChatMessage(chatInput, true);
      const userMessage = chatInput;
      setChatInput('');
      processChatMessage(userMessage);
    }
  };

  const handleChatKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleChatSend();
    }
  };

  const openModal = (project = null) => {
    if (project) {
      setEditingProject(project);
      setFormData({
        title: project.title || '',
        description: project.description || '',
        technologies: Array.isArray(project.technologies) ? project.technologies.join(', ') : '',
        duration: project.duration || '',
        achievements: Array.isArray(project.highlights) ? project.highlights.join('\n') : ''
      });
    } else {
      setEditingProject(null);
      setFormData({
        title: '',
        description: '',
        technologies: '',
        duration: '',
        achievements: ''
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingProject(null);
    setFormData({
      title: '',
      description: '',
      technologies: '',
      duration: '',
      achievements: ''
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const projectData = {
        title: formData.title,
        description: formData.description,
        technologies: formData.technologies.split(',').map(tech => tech.trim()).filter(tech => tech),
        duration: formData.duration,
        highlights: formData.achievements.split('\n').map(achievement => achievement.trim()).filter(achievement => achievement)
      };

      if (editingProject) {
        await axios.put(`${API_BASE_URL}/projects/${editingProject.id}`, projectData);
      } else {
        await axios.post(`${API_BASE_URL}/projects/create`, projectData);
      }

      await loadProjects();
      closeModal();
      addChatMessage(`✅ Successfully ${editingProject ? 'updated' : 'created'} project "${projectData.title}"`);
    } catch (error) {
      console.error('Error saving project:', error);
      addChatMessage('❌ Error saving project. Please try again.');
    }
  };

  const handleDelete = async (projectId) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      try {
        await axios.delete(`${API_BASE_URL}/projects/${projectId}`);
        await loadProjects();
        addChatMessage('🗑️ Project deleted successfully');
      } catch (error) {
        console.error('Error deleting project:', error);
        addChatMessage('❌ Error deleting project. Please try again.');
      }
    }
  };

  const addProjectsToCV = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/cv/add-projects`);
      if (response.data.success) {
        addChatMessage("✅ All projects successfully added to your CV!");
      } else {
        addChatMessage("❌ Error adding projects to CV. Please try again.");
      }
    } catch (error) {
      console.error('Error adding projects to CV:', error);
      addChatMessage("❌ Error adding projects to CV. Please ensure you have an active CV uploaded.");
    }
  };

  return (
    <PageContainer theme={theme}>
      <ContentWrapper>
        <Header theme={theme}>
          <HeaderTop>
            <BackButton theme={theme} onClick={() => navigate('/')}>
              ← Back to Dashboard
            </BackButton>
            <ThemeToggle />
          </HeaderTop>
          <Title theme={theme}>🚀 Project Management</Title>
          <Subtitle theme={theme}>
            Manage your projects with AI assistance and add them to your CV
          </Subtitle>
        </Header>

        <MainLayout>
          <LeftPanel>
            <ActionBar>
              <Button theme={theme} variant="primary" onClick={() => openModal()}>
                ➕ Add New Project
              </Button>
              <Button theme={theme} onClick={addProjectsToCV}>
                📄 Add All to CV
              </Button>
            </ActionBar>

            <ProjectsContainer theme={theme}>
              <h2 style={{ margin: '0 0 20px 0', color: theme.colors.textPrimary }}>Your Projects</h2>
              
              {loading ? (
                <LoadingSpinner theme={theme}>
                  <div className="spinner"></div>
                  Loading projects...
                </LoadingSpinner>
              ) : projects.length === 0 ? (
                <EmptyState theme={theme}>
                  <h3>No projects yet</h3>
                  <p>Create your first project using the button above or ask the AI assistant!</p>
                </EmptyState>
              ) : (
                <ProjectsGrid>
                  {projects.map((project, index) => (
                    <ProjectCard key={project.id || index} theme={theme}>
                      <ProjectTitle theme={theme}>{project.title}</ProjectTitle>
                      <ProjectDescription theme={theme}>{project.description}</ProjectDescription>
                      
                      {project.technologies && project.technologies.length > 0 && (
                        <TechTags>
                          {project.technologies.map((tech, techIndex) => (
                            <TechTag key={techIndex} theme={theme}>{tech}</TechTag>
                          ))}
                        </TechTags>
                      )}
                      
                      <ProjectActions>
                        <ActionButton 
                          theme={theme}
                          variant="edit" 
                          onClick={() => openModal(project)}
                        >
                          Edit
                        </ActionButton>
                        <ActionButton 
                          theme={theme}
                          variant="delete" 
                          onClick={() => handleDelete(project.id)}
                        >
                          Delete
                        </ActionButton>
                      </ProjectActions>
                    </ProjectCard>
                  ))}
                </ProjectsGrid>
              )}
            </ProjectsContainer>
          </LeftPanel>

          <RightPanel>
            <ChatContainer theme={theme}>
              <ChatHeader theme={theme}>
                <ChatTitle theme={theme}>
                  🤖 AI Project Assistant
                </ChatTitle>
              </ChatHeader>

              <QuickActions>
                <QuickActionButton theme={theme} onClick={() => processChatMessage("Create a new project")}>
                  Create Project
                </QuickActionButton>
                <QuickActionButton theme={theme} onClick={() => processChatMessage("Show my projects")}>
                  List Projects
                </QuickActionButton>
                <QuickActionButton theme={theme} onClick={() => processChatMessage("Add to CV")}>
                  Add to CV
                </QuickActionButton>
              </QuickActions>

              <MessagesContainer theme={theme}>
                {messages.map((message) => (
                  <Message key={message.id} isUser={message.isUser}>
                    <MessageBubble theme={theme} isUser={message.isUser}>
                      {message.text}
                    </MessageBubble>
                  </Message>
                ))}
                {isChatLoading && (
                  <Message isUser={false}>
                    <MessageBubble theme={theme} isUser={false}>
                      <div style={{display: 'flex', alignItems: 'center', gap: '10px'}}>
                        <div className="typing-indicator">
                          <span></span><span></span><span></span>
                        </div>
                        AI is thinking...
                      </div>
                    </MessageBubble>
                  </Message>
                )}
                <div ref={messagesEndRef} />
              </MessagesContainer>

              <ChatInputContainer theme={theme}>
                <ChatInput
                  theme={theme}
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={handleChatKeyPress}
                  placeholder="Ask me to create, edit, or manage your projects..."
                  disabled={isChatLoading}
                />
                <SendButton 
                  theme={theme}
                  onClick={handleChatSend}
                  disabled={isChatLoading || !chatInput.trim()}
                >
                  📤
                </SendButton>
              </ChatInputContainer>
            </ChatContainer>
          </RightPanel>
        </MainLayout>

        {showModal && (
          <Modal>
            <ModalContent theme={theme}>
              <ModalHeader>
                <ModalTitle theme={theme}>
                  {editingProject ? 'Edit Project' : 'Add New Project'}
                </ModalTitle>
                <CloseButton theme={theme} onClick={closeModal}>×</CloseButton>
              </ModalHeader>

              <form onSubmit={handleSubmit}>
                <FormGroup>
                  <Label theme={theme}>Project Title *</Label>
                  <Input
                    theme={theme}
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    placeholder="e.g., E-commerce Website"
                    required
                  />
                </FormGroup>

                <FormGroup>
                  <Label theme={theme}>Description</Label>
                  <Textarea
                    theme={theme}
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    placeholder="Brief description of your project..."
                  />
                </FormGroup>

                <FormGroup>
                  <Label theme={theme}>Technologies (comma-separated)</Label>
                  <Input
                    theme={theme}
                    type="text"
                    value={formData.technologies}
                    onChange={(e) => setFormData({...formData, technologies: e.target.value})}
                    placeholder="e.g., React, Node.js, MongoDB"
                  />
                </FormGroup>

                <FormGroup>
                  <Label theme={theme}>Duration</Label>
                  <Input
                    theme={theme}
                    type="text"
                    value={formData.duration}
                    onChange={(e) => setFormData({...formData, duration: e.target.value})}
                    placeholder="e.g., 3 months, Jan 2024 - Mar 2024"
                  />
                </FormGroup>

                <FormGroup>
                  <Label theme={theme}>Key Achievements (one per line)</Label>
                  <Textarea
                    theme={theme}
                    value={formData.achievements}
                    onChange={(e) => setFormData({...formData, achievements: e.target.value})}
                    placeholder="e.g., Implemented user authentication&#10;Built responsive design&#10;Deployed to AWS"
                  />
                </FormGroup>

                <ModalActions>
                  <Button theme={theme} type="button" onClick={closeModal}>Cancel</Button>
                  <Button theme={theme} type="submit" variant="primary">
                    {editingProject ? 'Update' : 'Create'} Project
                  </Button>
                </ModalActions>
              </form>
            </ModalContent>
          </Modal>
        )}
      </ContentWrapper>
    </PageContainer>
  );
}

export default ProjectManagementPage; 