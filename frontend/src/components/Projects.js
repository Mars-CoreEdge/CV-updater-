import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const ProjectsContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 2px solid rgba(102, 126, 234, 0.1);
`;

const Title = styled.h2`
  color: var(--text-primary);
  margin: 0;
  font-size: 1.6rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  
  .icon {
    font-size: 1.8rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

const ProjectsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  padding: 10px 0;
  max-height: 600px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 4px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const ProjectCard = styled.div`
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(248, 250, 252, 0.95));
  border-radius: 20px;
  padding: 25px;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.1),
    0 4px 16px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(102, 126, 234, 0.1);
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    transition: height 0.3s ease;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(102, 126, 234, 0.03) 0%, transparent 70%);
    transform: scale(0);
    transition: transform 0.5s ease;
    pointer-events: none;
  }
  
  &:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 
      0 20px 50px rgba(0, 0, 0, 0.15),
      0 8px 32px rgba(102, 126, 234, 0.2);
    border-color: rgba(102, 126, 234, 0.3);
  }
  
  &:hover::before {
    height: 6px;
  }
  
  &:hover::after {
    transform: scale(1);
  }
  
  &:active {
    transform: translateY(-4px) scale(1.01);
  }
`;

const ProjectTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0 0 12px 0;
  line-height: 1.3;
  background: linear-gradient(135deg, #2d3748, #4a5568);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
`;

const ProjectDescription = styled.p`
  color: #4a5568;
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0 0 18px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const ProjectDuration = styled.div`
  color: #667eea;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
  
  .icon {
    font-size: 1rem;
  }
`;

const TechnologiesContainer = styled.div`
  margin-bottom: 18px;
`;

const TechLabel = styled.div`
  font-size: 0.8rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const TechTags = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
`;

const TechTag = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 12px;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
  }
`;

const HighlightsContainer = styled.div`
  margin-top: 15px;
`;

const HighlightsList = styled.ul`
  margin: 8px 0 0 0;
  padding: 0;
  list-style: none;
`;

const HighlightItem = styled.li`
  color: #4a5568;
  font-size: 0.85rem;
  line-height: 1.5;
  margin-bottom: 6px;
  padding-left: 18px;
  position: relative;
  
  &::before {
    content: '✨';
    position: absolute;
    left: 0;
    top: 0;
    font-size: 0.8rem;
  }
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: #718096;
  grid-column: 1 / -1;
  
  .empty-icon {
    font-size: 4rem;
    margin-bottom: 20px;
    opacity: 0.6;
    animation: float 3s ease-in-out infinite;
  }
  
  .empty-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 12px;
    color: #4a5568;
  }
  
  .empty-subtitle {
    font-size: 1rem;
    opacity: 0.8;
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.5;
  }
  
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  grid-column: 1 / -1;
  
  .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(102, 126, 234, 0.2);
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
  }
  
  .loading-text {
    color: #4a5568;
    font-size: 1.1rem;
    font-weight: 500;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ProjectsStats = styled.div`
  display: flex;
  align-items: center;
  gap: 20px;
  color: #4a5568;
  font-size: 0.9rem;
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  font-weight: 500;
  
  .stat-icon {
    font-size: 1rem;
  }
`;

const ErrorMessage = styled.div`
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  padding: 25px;
  border-radius: 12px;
  margin: 20px 0;
  border-left: 4px solid #dc3545;
  text-align: center;
  grid-column: 1 / -1;
  
  .error-icon {
    font-size: 2rem;
    margin-bottom: 12px;
    display: block;
  }
  
  .error-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 8px;
  }
`;

function Projects({ cvUploaded }) {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (cvUploaded) {
      loadProjects();
    }
  }, [cvUploaded]);

  const loadProjects = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('http://localhost:8000/projects/');
      setProjects(response.data.projects || []);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to load projects');
      setProjects([]);
    } finally {
      setIsLoading(false);
    }
  };

  const getTotalTechnologies = () => {
    const allTechs = projects.flatMap(project => project.technologies || []);
    return [...new Set(allTechs)].length;
  };

  return (
    <ProjectsContainer>
      <Header>
        <Title>
          <span className="icon">🚀</span>
          Projects Portfolio
        </Title>
        {projects.length > 0 && (
          <ProjectsStats>
            <StatItem>
              <span className="stat-icon">📁</span>
              {projects.length} Projects
            </StatItem>
            <StatItem>
              <span className="stat-icon">⚡</span>
              {getTotalTechnologies()} Technologies
            </StatItem>
          </ProjectsStats>
        )}
      </Header>
      
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
        
        {!isLoading && !error && projects.length === 0 && cvUploaded && (
          <EmptyState>
            <div className="empty-icon">💼</div>
            <div className="empty-title">No Projects Found</div>
            <div className="empty-subtitle">
              Your CV doesn't seem to contain any project information. Try uploading a CV with project details or add project information through the chat.
            </div>
          </EmptyState>
        )}
        
        {!cvUploaded && (
          <EmptyState>
            <div className="empty-icon">📋</div>
            <div className="empty-title">Upload Your CV First</div>
            <div className="empty-subtitle">
              Please upload your CV to view your projects portfolio.
            </div>
          </EmptyState>
        )}
        
        {projects.map((project, index) => (
          <ProjectCard key={index}>
            <ProjectTitle>{project.title || 'Untitled Project'}</ProjectTitle>
            
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
                <TechLabel>Technologies</TechLabel>
                <TechTags>
                  {project.technologies.map((tech, techIndex) => (
                    <TechTag key={techIndex}>{tech}</TechTag>
                  ))}
                </TechTags>
              </TechnologiesContainer>
            )}
            
            {project.highlights && project.highlights.length > 0 && (
              <HighlightsContainer>
                <TechLabel>Key Highlights</TechLabel>
                <HighlightsList>
                  {project.highlights.slice(0, 3).map((highlight, highlightIndex) => (
                    <HighlightItem key={highlightIndex}>{highlight}</HighlightItem>
                  ))}
                </HighlightsList>
              </HighlightsContainer>
            )}
          </ProjectCard>
        ))}
      </ProjectsGrid>
    </ProjectsContainer>
  );
}

export default Projects; 