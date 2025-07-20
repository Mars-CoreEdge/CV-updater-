import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ProjectChatbot from '../components/ProjectChatbot';
import CVUploadForProjects from '../components/CVUploadForProjects';


const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  padding: 20px;
  position: relative;
  overflow-x: hidden;
  
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(120, 200, 255, 0.2) 0%, transparent 50%);
    pointer-events: none;
  }
`;

const ContentWrapper = styled.div`
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.header`
  text-align: center;
  color: white;
  margin-bottom: 40px;
  animation: fadeInUp 0.8s ease-out;
`;

const BackButton = styled.button`
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 12px 20px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 1000;
  
  &:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: translateX(-5px);
  }
  
  .arrow {
    font-size: 1.2rem;
  }
`;

const Title = styled.h1`
  font-size: clamp(2.5rem, 5vw, 4rem);
  margin-bottom: 15px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 8px rgba(0,0,0,0.3);
  line-height: 1.2;
`;

const Subtitle = styled.p`
  font-size: clamp(1rem, 2.5vw, 1.3rem);
  opacity: 0.95;
  font-weight: 400;
  max-width: 600px;
  margin: 0 auto 30px auto;
  line-height: 1.6;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
`;

const StatsSection = styled.div`
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 40px;
  
  @media (max-width: 768px) {
    gap: 20px;
    flex-wrap: wrap;
  }
`;

const StatCard = styled.div`
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 20px 30px;
  color: white;
  text-align: center;
  transition: all 0.3s ease;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-5px);
  }
  
  .stat-number {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #ffffff, #f0f4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .stat-label {
    font-size: 0.9rem;
    opacity: 0.9;
    font-weight: 500;
  }
`;

const ProjectsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 30px;
  padding: 20px 0;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 25px;
  }
`;

const ProjectCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 25px;
  padding: 30px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.15),
    0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
    transition: height 0.3s ease;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.05) 0%, transparent 70%);
    transform: scale(0);
    transition: transform 0.6s ease;
    pointer-events: none;
  }
  
  &:hover {
    transform: translateY(-12px) scale(1.02);
    box-shadow: 
      0 30px 80px rgba(0, 0, 0, 0.2),
      0 12px 48px rgba(102, 126, 234, 0.3);
    border-color: rgba(102, 126, 234, 0.4);
  }
  
  &:hover::before {
    height: 8px;
  }
  
  &:hover::after {
    transform: scale(1);
  }
`;

const ProjectTitle = styled.h3`
  font-size: 1.4rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 15px 0;
  line-height: 1.3;
  background: linear-gradient(135deg, #2d3748, #4a5568);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const ProjectDescription = styled.p`
  color: #4a5568;
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 20px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const ProjectDuration = styled.div`
  color: #667eea;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  
  .icon {
    font-size: 1.1rem;
  }
`;

const TechnologiesContainer = styled.div`
  margin-bottom: 20px;
`;

const TechLabel = styled.div`
  font-size: 0.85rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const TechTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const TechTag = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 15px;
  white-space: nowrap;
  box-shadow: 0 3px 6px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
  }
`;

const HighlightsContainer = styled.div`
  margin-top: 18px;
`;

const HighlightsList = styled.ul`
  margin: 10px 0 0 0;
  padding: 0;
  list-style: none;
`;

const HighlightItem = styled.li`
  color: #4a5568;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 8px;
  padding-left: 20px;
  position: relative;
  
  &::before {
    content: '✨';
    position: absolute;
    left: 0;
    top: 0;
    font-size: 0.9rem;
  }
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 80px 20px;
  color: white;
  grid-column: 1 / -1;
  
  .empty-icon {
    font-size: 5rem;
    margin-bottom: 25px;
    opacity: 0.8;
    animation: float 3s ease-in-out infinite;
  }
  
  .empty-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 15px;
    background: linear-gradient(135deg, #ffffff, #f0f4ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .empty-subtitle {
    font-size: 1.1rem;
    opacity: 0.9;
    max-width: 500px;
    margin: 0 auto 30px auto;
    line-height: 1.5;
  }
  
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
  }
`;

const CreateProjectButton = styled.button`
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 15px 30px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
  position: relative;
  overflow: hidden;
  margin-top: 10px;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s ease;
  }
  
  &:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(40, 167, 69, 0.5);
    background: linear-gradient(135deg, #218838, #1ea384);
  }
  
  &:hover::before {
    left: 100%;
  }
  
  &:active {
    transform: translateY(-1px);
  }
  
  .button-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }
  
  .icon {
    font-size: 1.2rem;
  }
`;

const ActionButton = styled.button`
  background: ${props => props.variant === 'primary' ? 'linear-gradient(135deg, #667eea, #764ba2)' : 
                props.variant === 'success' ? 'linear-gradient(135deg, #28a745, #20c997)' :
                props.variant === 'warning' ? 'linear-gradient(135deg, #ffc107, #fd7e14)' :
                'linear-gradient(135deg, #6c757d, #495057)'};
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.3s ease;
  margin: 5px;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
  
  .button-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }
`;

const ProjectCheckbox = styled.input`
  margin-right: 10px;
  transform: scale(1.2);
  accent-color: #667eea;
`;

const ProjectActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 15px;
  flex-wrap: wrap;
`;

const EditButton = styled.button`
  background: linear-gradient(135deg, #17a2b8, #138496);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(23, 162, 184, 0.3);
  }
`;

const DeleteButton = styled.button`
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 10px rgba(220, 53, 69, 0.3);
  }
`;

const AssistantActions = styled.div`
  display: flex;
  justify-content: center;
  gap: 15px;
  margin: 30px 0;
  flex-wrap: wrap;
`;

const SectionTitle = styled.h2`
  color: white;
  font-size: 2rem;
  font-weight: 700;
  margin: 40px 0 20px 0;
  text-align: center;
  background: linear-gradient(135deg, #ffffff, #f0f4ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const LoadingSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px;
  grid-column: 1 / -1;
  color: white;
  
  .spinner {
    width: 60px;
    height: 60px;
    border: 5px solid rgba(255, 255, 255, 0.3);
    border-top: 5px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 25px;
  }
  
  .loading-text {
    font-size: 1.2rem;
    font-weight: 500;
    opacity: 0.9;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: rgba(255, 255, 255, 0.95);
  color: #721c24;
  padding: 30px;
  border-radius: 20px;
  margin: 20px;
  border-left: 6px solid #dc3545;
  text-align: center;
  grid-column: 1 / -1;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  
  .error-icon {
    font-size: 2.5rem;
    margin-bottom: 15px;
    display: block;
  }
  
  .error-title {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 10px;
  }
`;

const FloatingShape = styled.div`
  position: absolute;
  width: ${props => props.size || '100px'};
  height: ${props => props.size || '100px'};
  background: ${props => props.gradient || 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))'};
  border-radius: 50%;
  top: ${props => props.top || '10%'};
  left: ${props => props.left || '10%'};
  animation: float 6s ease-in-out infinite;
  pointer-events: none;
  
  @keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(180deg); }
  }
  
  &:nth-child(2) {
    animation-delay: -2s;
  }
  
  &:nth-child(3) {
    animation-delay: -4s;
  }
`;

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease-out;
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 25px;
  padding: 40px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideInUp 0.3s ease-out;
  position: relative;
  
  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
`;

const ModalTitle = styled.h2`
  color: #2d3748;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #a0aec0;
  padding: 5px;
  border-radius: 50%;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
    color: #667eea;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 25px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  color: #4a5568;
  font-weight: 600;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  min-height: 100px;
  resize: vertical;
  font-family: inherit;
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const TagInput = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  min-height: 45px;
  transition: all 0.3s ease;
  
  &:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Tag = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 5px;
  
  .remove {
    cursor: pointer;
    font-weight: bold;
    
    &:hover {
      color: #ffcccb;
    }
  }
`;

const TagInputField = styled.input`
  border: none;
  outline: none;
  flex: 1;
  min-width: 120px;
  padding: 4px;
  font-size: 0.9rem;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
`;

const ModalButton = styled.button`
  padding: 12px 24px;
  border-radius: 15px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  
  ${props => props.variant === 'primary' ? `
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
    }
  ` : `
    background: #f7fafc;
    color: #4a5568;
    border: 1px solid #e2e8f0;
    
    &:hover {
      background: #edf2f7;
    }
  `}
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [selectedProjects, setSelectedProjects] = useState([]);
  const [editingProject, setEditingProject] = useState(null);
  const [showCVUpload, setShowCVUpload] = useState(false);
  const [assistantActionLoading, setAssistantActionLoading] = useState('');
  const navigate = useNavigate();

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    duration: '',
    technologies: [],
    highlights: ['']
  });
  const [techInput, setTechInput] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  // Reload projects when component becomes visible (when navigating back to this page)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        console.log('Projects page became visible, reloading projects...');
        loadProjects();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  // Test backend connectivity first
  const testBackendConnection = async () => {
    try {
      const response = await axios.get('http://localhost:8081/test');
      console.log('Backend test response:', response.data);
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('Backend connection test failed:', error);
      return false;
    }
  };

  // Create a test project if no projects exist
  const createTestProject = async () => {
    try {
      const testProject = {
        title: "Sample Project",
        description: "This is a sample project to test the system.",
        duration: "Jan 2024 - Mar 2024",
        technologies: ["React", "Node.js", "MongoDB"],
        highlights: [
          "Built a responsive web application",
          "Implemented RESTful API endpoints",
          "Deployed to cloud platform"
        ]
      };
      
      const response = await axios.post('http://localhost:8081/projects/create', testProject);
      console.log('Test project created:', response.data);
      return response.data.project;
    } catch (error) {
      console.error('Error creating test project:', error);
      return null;
    }
  };

  const loadProjects = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('🔄 Loading projects from backend...');
      
      // Test backend connection first
      const backendHealthy = await testBackendConnection();
      if (!backendHealthy) {
        throw new Error('Backend is not responding properly');
      }
      
      // Try the primary endpoint first
      let response;
      try {
        console.log('📡 Trying /projects/list endpoint...');
        response = await axios.get('http://localhost:8081/projects/list');
        console.log('✅ Projects API response (list):', response.data);
        console.log('📊 Response structure:', Object.keys(response.data));
        console.log('📋 Projects array:', response.data.projects);
        console.log('🔢 Projects count:', response.data.projects?.length || 0);
      } catch (primaryError) {
        console.log('❌ Primary endpoint failed, trying fallback...');
        console.log('🔍 Primary error:', primaryError.message);
        // Fallback to the other projects endpoint
        response = await axios.get('http://localhost:8081/projects/');
        console.log('✅ Projects API response (fallback):', response.data);
      }
      
      if (response.data && response.data.projects) {
        console.log('🎯 Setting projects state with:', response.data.projects.length, 'projects');
        setProjects(response.data.projects);
        console.log('✅ Projects loaded successfully:', response.data.projects.length, 'projects');
        
        // If no projects exist, create a test project
        if (response.data.projects.length === 0) {
          console.log('⚠️ No projects found, creating test project...');
          const testProject = await createTestProject();
          if (testProject) {
            setProjects([testProject]);
            console.log('✅ Test project added to display');
          }
        }
      } else {
        console.log('❌ No projects found in response');
        console.log('🔍 Response data:', response.data);
        setProjects([]);
      }
    } catch (error) {
      console.error('❌ Error loading projects:', error);
      console.error('🔍 Error response:', error.response?.data);
      setError(error.response?.data?.detail || error.message || 'Failed to load projects');
      setProjects([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getTotalTechnologies = () => {
    const allTechs = projects.flatMap(project => project.technologies || []);
    return [...new Set(allTechs)].length;
  };

  const getAverageProjectDuration = () => {
    const durations = projects.filter(p => p.duration).length;
    return durations > 0 ? durations : 0;
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addTechnology = (e) => {
    if (e.key === 'Enter' && techInput.trim()) {
      e.preventDefault();
      if (!formData.technologies.includes(techInput.trim())) {
        setFormData(prev => ({
          ...prev,
          technologies: [...prev.technologies, techInput.trim()]
        }));
      }
      setTechInput('');
    }
  };

  const removeTechnology = (tech) => {
    setFormData(prev => ({
      ...prev,
      technologies: prev.technologies.filter(t => t !== tech)
    }));
  };

  const handleHighlightChange = (index, value) => {
    const newHighlights = [...formData.highlights];
    newHighlights[index] = value;
    setFormData(prev => ({
      ...prev,
      highlights: newHighlights
    }));
  };

  const addHighlight = () => {
    setFormData(prev => ({
      ...prev,
      highlights: [...prev.highlights, '']
    }));
  };

  const removeHighlight = (index) => {
    if (formData.highlights.length > 1) {
      setFormData(prev => ({
        ...prev,
        highlights: prev.highlights.filter((_, i) => i !== index)
      }));
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      duration: '',
      technologies: [],
      highlights: ['']
    });
    setTechInput('');
  };

  const handleSaveProject = async () => {
    if (!formData.title.trim()) return;
    
    setIsSaving(true);
    try {
      const projectData = {
        ...formData,
        highlights: formData.highlights.filter(h => h.trim())
      };
      
      const response = await axios.post('http://localhost:8081/projects/', projectData);
      
      // Reload projects from backend to get fresh data with IDs
      await loadProjects();
      setShowModal(false);
      resetForm();
    } catch (error) {
      console.error('Error saving project:', error);
      // For now, just add locally if backend fails
      const projectData = {
        ...formData,
        highlights: formData.highlights.filter(h => h.trim())
      };
      setProjects(prev => [...prev, projectData]);
      setShowModal(false);
      resetForm();
    } finally {
      setIsSaving(false);
    }
  };

  // Chatbot callback functions
  const handleProjectAdd = (projectData) => {
    setProjects(prev => [...prev, projectData]);
  };

  const handleProjectUpdate = (projectId, updatedData) => {
    setProjects(prev => prev.map((project, index) => 
      index === projectId ? { ...project, ...updatedData } : project
    ));
  };

  const handleProjectDelete = async (projectIndex) => {
    const projectToDelete = projects[projectIndex];
    
    if (projectToDelete && projectToDelete.id) {
      try {
        await axios.delete(`http://localhost:8081/projects/${projectToDelete.id}`);
        setProjects(prev => prev.filter((_, index) => index !== projectIndex));
      } catch (error) {
        console.error('Error deleting project:', error);
        // Still remove from UI even if backend fails
        setProjects(prev => prev.filter((_, index) => index !== projectIndex));
      }
    } else {
      // For projects without IDs (extracted from CV), just remove from UI
      setProjects(prev => prev.filter((_, index) => index !== projectIndex));
    }
  };

  const handleDownloadCV = async () => {
    try {
      const response = await axios.post('http://localhost:8081/cv/download', {}, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `cv_with_projects_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      alert('Error downloading CV. Please try again.');
    }
  };

  const handleDownloadCVWithSelectedProjects = async () => {
    if (selectedProjects.length === 0) {
      alert('Please select at least one project to include in your CV.');
      return;
    }

    try {
      setAssistantActionLoading('downloading');
      const response = await axios.post('http://localhost:8081/cv/download-with-selected-projects', {
        selected_project_ids: selectedProjects
      }, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `cv_selected_projects_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download error:', error);
      alert('Error downloading CV with selected projects. Please try again.');
    } finally {
      setAssistantActionLoading('');
    }
  };

  const handleCleanupCV = async () => {
    try {
      setAssistantActionLoading('cleaning');
      const response = await axios.post('http://localhost:8081/cv/cleanup');
      alert(response.data.message);
    } catch (error) {
      console.error('Cleanup error:', error);
      alert('Error cleaning up CV. Please try again.');
    } finally {
      setAssistantActionLoading('');
    }
  };

  const handleCreateLinkedInBlog = async () => {
    if (projects.length === 0) {
      alert('No projects available to create a blog post from.');
      return;
    }

    try {
      setAssistantActionLoading('creating-blog');
      const response = await axios.post('http://localhost:8081/projects/create-linkedin-blog');
      
      // Create a new window/tab with the blog content
      const blogWindow = window.open('', '_blank');
      blogWindow.document.write(`
        <html>
          <head>
            <title>LinkedIn Blog Post</title>
            <style>
              body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
              h1 { color: #0077b5; }
              .blog-content { white-space: pre-wrap; }
            </style>
          </head>
          <body>
            <h1>LinkedIn Blog Post</h1>
            <p><strong>Generated from ${response.data.projects_used} projects</strong></p>
            <div class="blog-content">${response.data.blog_content}</div>
          </body>
        </html>
      `);
      blogWindow.document.close();
    } catch (error) {
      console.error('Blog creation error:', error);
      alert('Error creating LinkedIn blog post. Please try again.');
    } finally {
      setAssistantActionLoading('');
    }
  };

  const handleProjectSelection = (projectId) => {
    setSelectedProjects(prev => {
      if (prev.includes(projectId)) {
        return prev.filter(id => id !== projectId);
      } else {
        return [...prev, projectId];
      }
    });
  };

  const handleEditProject = (project) => {
    setEditingProject(project);
    setFormData({
      title: project.title || '',
      description: project.description || '',
      duration: project.duration || '',
      technologies: project.technologies || [],
      highlights: project.highlights && project.highlights.length > 0 ? project.highlights : ['']
    });
    setShowModal(true);
  };

  const handleUpdateProject = async () => {
    if (!editingProject || !formData.title.trim()) return;
    
    setIsSaving(true);
    try {
      const projectData = {
        ...formData,
        highlights: formData.highlights.filter(h => h.trim())
      };
      
      await axios.put(`http://localhost:8081/projects/${editingProject.id}`, projectData);
      
      // Reload projects from backend
      await loadProjects();
      setShowModal(false);
      setEditingProject(null);
      resetForm();
    } catch (error) {
      console.error('Error updating project:', error);
      alert('Error updating project. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleProjectsExtracted = (extractedProjects) => {
    setProjects(extractedProjects);
    setShowCVUpload(false);
    setIsLoading(false);
  };

  return (
    <PageContainer>
      <FloatingShape 
        size="150px" 
        top="8%" 
        left="5%" 
        gradient="linear-gradient(135deg, rgba(240, 147, 251, 0.2), rgba(245, 87, 108, 0.2))"
      />
      <FloatingShape 
        size="100px" 
        top="75%" 
        left="85%" 
        gradient="linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(0, 242, 254, 0.2))"
      />
      <FloatingShape 
        size="120px" 
        top="45%" 
        left="90%" 
        gradient="linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2))"
      />
      
      <BackButton onClick={() => navigate('/')}>
        <span className="arrow">←</span>
        Back to CV
      </BackButton>
      
      <ContentWrapper>
        <Header>
          <Title>🚀 Projects Portfolio</Title>
          <Subtitle>
            Showcase your amazing projects and technical achievements
          </Subtitle>
          
          {!isLoading && !error && projects.length > 0 && (
            <StatsSection>
              <StatCard>
                <div className="stat-number">{projects.length}</div>
                <div className="stat-label">Total Projects</div>
              </StatCard>
              <StatCard>
                <div className="stat-number">{getTotalTechnologies()}</div>
                <div className="stat-label">Technologies</div>
              </StatCard>
              <StatCard>
                <div className="stat-number">{getAverageProjectDuration()}</div>
                <div className="stat-label">Active Projects</div>
              </StatCard>
              <CreateProjectButton onClick={() => setShowModal(true)}>
                <div className="button-content">
                  <span className="icon">➕</span>
                  Add New Project
                </div>
              </CreateProjectButton>
              <CreateProjectButton 
                onClick={() => setShowCVUpload(true)}
                style={{
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  marginLeft: '15px'
                }}
              >
                <div className="button-content">
                  <span className="icon">📄</span>
                  Extract from CV
                </div>
              </CreateProjectButton>
            </StatsSection>
          )}
        </Header>
        
        {/* CV Upload Section */}
        {showCVUpload && (
          <CVUploadForProjects onProjectsExtracted={handleProjectsExtracted} />
        )}
        

        
        {/* Assistant Actions */}
        {!isLoading && !error && projects.length > 0 && (
          <AssistantActions>
            <ActionButton 
              variant="primary" 
              onClick={handleDownloadCVWithSelectedProjects}
              disabled={selectedProjects.length === 0 || assistantActionLoading === 'downloading'}
            >
              <div className="button-content">
                {assistantActionLoading === 'downloading' ? '⏳' : '📄'}
                Download My CV (Selected Projects)
              </div>
            </ActionButton>
            
            <ActionButton 
              variant="warning" 
              onClick={handleCleanupCV}
              disabled={assistantActionLoading === 'cleaning'}
            >
              <div className="button-content">
                {assistantActionLoading === 'cleaning' ? '⏳' : '🧹'}
                Clean Up My CV
              </div>
            </ActionButton>
            
            <ActionButton 
              variant="success" 
              onClick={handleCreateLinkedInBlog}
              disabled={assistantActionLoading === 'creating-blog'}
            >
              <div className="button-content">
                {assistantActionLoading === 'creating-blog' ? '⏳' : '✍️'}
                Create LinkedIn Blog
              </div>
            </ActionButton>
          </AssistantActions>
        )}
        
        {/* My Projects Section */}
        {!isLoading && !error && projects.length > 0 && (
          <SectionTitle>My Projects</SectionTitle>
        )}
        
        <ProjectsGrid>
          {isLoading && (
            <LoadingSpinner>
              <div className="spinner"></div>
              <div className="loading-text">Extracting projects from your CV...</div>
            </LoadingSpinner>
          )}
          
          {error && (
            <ErrorMessage>
              <span className="error-icon">⚠️</span>
              <div className="error-title">Unable to Load Projects</div>
              <div>{error}</div>
            </ErrorMessage>
          )}
          
          {!isLoading && !error && projects.length === 0 && (
            <EmptyState>
              <div className="empty-icon">💼</div>
              <div className="empty-title">No Projects Found</div>
              <div className="empty-subtitle">
                Upload your CV to extract projects automatically, or create your first project manually.
              </div>
              <CreateProjectButton onClick={() => setShowModal(true)}>
                <div className="button-content">
                  <span className="icon">➕</span>
                  Create New Project
                </div>
              </CreateProjectButton>
              <CreateProjectButton 
                onClick={() => setShowCVUpload(true)}
                style={{
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  marginLeft: '15px'
                }}
              >
                <div className="button-content">
                  <span className="icon">📄</span>
                  Extract from CV
                </div>
              </CreateProjectButton>
            </EmptyState>
          )}
          
          {/* Debug Panel - Only show in development */}
          {process.env.NODE_ENV === 'development' && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              padding: '20px',
              borderRadius: '10px',
              margin: '20px 0',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}>
              <h4 style={{ color: 'white', margin: '0 0 10px 0' }}>🔧 Debug Info</h4>
              <div style={{ color: 'white', fontSize: '14px' }}>
                <div>Projects Count: {projects.length}</div>
                <div>Selected Projects: {selectedProjects.length}</div>
                <div>Error: {error || 'None'}</div>
              </div>
            </div>
          )}
          
          {projects.map((project, index) => (
            <ProjectCard key={index}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <ProjectTitle>{project.title || 'Untitled Project'}</ProjectTitle>
                <ProjectCheckbox
                  type="checkbox"
                  checked={selectedProjects.includes(project.id)}
                  onChange={() => handleProjectSelection(project.id)}
                  title="Select this project for CV inclusion"
                />
              </div>
              
              {project.duration && (
                <ProjectDuration>
                  <span className="icon">📅</span>
                  {project.duration}
                </ProjectDuration>
              )}
              
              <ProjectDescription>
                {project.description || 'No description available.'}
              </ProjectDescription>
              
              {project.technologies && project.technologies.length > 0 && (
                <TechnologiesContainer>
                  <TechLabel>Technologies Used</TechLabel>
                  <TechTags>
                    {project.technologies.map((tech, techIndex) => (
                      <TechTag key={techIndex}>{tech}</TechTag>
                    ))}
                  </TechTags>
                </TechnologiesContainer>
              )}
              
              {project.highlights && project.highlights.length > 0 && (
                <HighlightsContainer>
                  <TechLabel>Key Achievements</TechLabel>
                  <HighlightsList>
                    {project.highlights.slice(0, 4).map((highlight, highlightIndex) => (
                      <HighlightItem key={highlightIndex}>{highlight}</HighlightItem>
                    ))}
                  </HighlightsList>
                </HighlightsContainer>
              )}
              
              <ProjectActions>
                <EditButton onClick={() => handleEditProject(project)}>
                  ✏️ Edit
                </EditButton>
                <DeleteButton onClick={() => handleProjectDelete(index)}>
                  🗑️ Delete
                </DeleteButton>
              </ProjectActions>
            </ProjectCard>
          ))}
        </ProjectsGrid>
      </ContentWrapper>
      
      {/* Create Project Modal */}
      {showModal && (
        <ModalOverlay onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>{editingProject ? '✏️ Edit Project' : '✨ Create New Project'}</ModalTitle>
              <CloseButton onClick={() => {
                setShowModal(false);
                setEditingProject(null);
                resetForm();
              }}>×</CloseButton>
            </ModalHeader>
            
            <FormGroup>
              <Label>Project Title</Label>
              <Input
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Enter project title..."
                required
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Description</Label>
              <TextArea
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Describe your project..."
                rows={4}
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Duration / Timeline</Label>
              <Input
                type="text"
                value={formData.duration}
                onChange={(e) => handleInputChange('duration', e.target.value)}
                placeholder="e.g., Jan 2024 - Mar 2024"
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Technologies Used</Label>
              <TagInput>
                {formData.technologies.map((tech, index) => (
                  <Tag key={index}>
                    {tech}
                    <span className="remove" onClick={() => removeTechnology(tech)}>×</span>
                  </Tag>
                ))}
                <TagInputField
                  value={techInput}
                  onChange={(e) => setTechInput(e.target.value)}
                  onKeyDown={addTechnology}
                  placeholder="Type technology and press Enter..."
                />
              </TagInput>
            </FormGroup>
            
            <FormGroup>
              <Label>Key Highlights</Label>
              {formData.highlights.map((highlight, index) => (
                <div key={index} style={{display: 'flex', gap: '10px', marginBottom: '10px'}}>
                  <Input
                    value={highlight}
                    onChange={(e) => handleHighlightChange(index, e.target.value)}
                    placeholder={`Highlight ${index + 1}...`}
                    style={{flex: 1}}
                  />
                  {formData.highlights.length > 1 && (
                    <ModalButton onClick={() => removeHighlight(index)} style={{padding: '12px'}}>
                      ×
                    </ModalButton>
                  )}
                </div>
              ))}
              <ModalButton onClick={addHighlight} style={{marginTop: '10px'}}>
                ➕ Add Another Highlight
              </ModalButton>
            </FormGroup>
            
            <ButtonGroup>
              <ModalButton onClick={() => {
                setShowModal(false);
                setEditingProject(null);
                resetForm();
              }}>
                Cancel
              </ModalButton>
              <ModalButton 
                variant="primary" 
                onClick={editingProject ? handleUpdateProject : handleSaveProject}
                disabled={!formData.title.trim() || isSaving}
              >
                {isSaving ? 'Saving...' : (editingProject ? 'Update Project' : 'Save Project')}
              </ModalButton>
            </ButtonGroup>
          </ModalContent>
        </ModalOverlay>
      )}
      
      {/* Project Chatbot */}
      <ProjectChatbot
        projects={projects}
        onProjectAdd={handleProjectAdd}
        onProjectUpdate={handleProjectUpdate}
        onProjectDelete={handleProjectDelete}
        onProjectsReload={loadProjects}
      />
    </PageContainer>
  );
}

export default ProjectsPage; 