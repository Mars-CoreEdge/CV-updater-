import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import ChatInterface from './components/ChatInterface';
import CVDisplay from './components/CVDisplay';
import ProjectsPage from './pages/ProjectsPage';
import CVBuilderPage from './pages/CVBuilderPage';
import CVManagementPage from './pages/CVManagementPage';
import './App.css';

const AppContainer = styled.div`
  min-height: 100vh;
  background: 
    radial-gradient(ellipse at top left, rgba(102, 126, 234, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse at top right, rgba(118, 75, 162, 0.12) 0%, transparent 50%),
    radial-gradient(ellipse at bottom, rgba(79, 172, 254, 0.08) 0%, transparent 50%),
    linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-primary) 50%, var(--bg-tertiary) 100%);
  background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%;
  background-attachment: fixed;
  padding: var(--spacing-2xl);
  padding-bottom: var(--spacing-lg);
  position: relative;
  overflow-x: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 15% 25%, rgba(102, 126, 234, 0.06) 0%, transparent 40%),
      radial-gradient(circle at 85% 75%, rgba(118, 75, 162, 0.04) 0%, transparent 40%),
      radial-gradient(circle at 50% 50%, rgba(79, 172, 254, 0.03) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.02) 50%, transparent 70%),
      linear-gradient(-45deg, transparent 30%, rgba(255, 255, 255, 0.01) 50%, transparent 70%);
    pointer-events: none;
    z-index: 1;
  }
  
  @media (max-width: 768px) {
    padding: var(--spacing-md);
  }
`;

const ContentWrapper = styled.div`
  position: relative;
  z-index: 2;
`;

const Header = styled.header`
  text-align: center;
  margin-bottom: var(--spacing-3xl);
  animation: fadeInDown 1s var(--transition-professional);
`;

const Title = styled.h1`
  font-family: 'Poppins', 'Inter', sans-serif;
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  margin-bottom: var(--spacing-xl);
  font-weight: var(--font-weight-extrabold);
  letter-spacing: -0.025em;
  background: var(--professional-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: var(--line-height-tight);
  position: relative;
  text-shadow: 0 4px 8px rgba(45, 55, 72, 0.1);
  
  &::before {
    content: '';
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 2px;
    background: var(--accent-gradient);
    border-radius: var(--border-radius-full);
    box-shadow: 0 0 20px rgba(79, 172, 254, 0.4);
  }
  
  &::after {
    content: '';
    position: absolute;
    bottom: -12px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 3px;
    background: var(--primary-gradient);
    border-radius: var(--border-radius-full);
    box-shadow: 0 0 15px rgba(102, 126, 234, 0.3);
    animation: glow 2s ease-in-out infinite;
  }
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
    margin-bottom: var(--spacing-lg);
    letter-spacing: -0.02em;
  }
`;

const Subtitle = styled.p`
  font-family: 'Inter', sans-serif;
  font-size: clamp(1.125rem, 2.5vw, 1.5rem);
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
  max-width: 800px;
  margin: 0 auto var(--spacing-2xl);
  line-height: var(--line-height-relaxed);
  letter-spacing: -0.015em;
  text-align: center;
  opacity: 0.9;
  animation: fadeInUp 1.2s var(--transition-professional) 0.3s both;
  
  @media (max-width: 768px) {
    font-size: 1.125rem;
    margin-bottom: var(--spacing-xl);
    max-width: 90%;
  }
`;

const StatsBar = styled.div`
  display: flex;
  justify-content: center;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-2xl);
  animation: fadeInScale 1s var(--transition-professional) 0.6s both;
  
  @media (max-width: 768px) {
    gap: var(--spacing-lg);
    flex-wrap: wrap;
    margin-bottom: var(--spacing-xl);
  }
`;

const StatItem = styled.div`
  background: var(--glass-gradient);
  backdrop-filter: var(--backdrop-blur-lg);
  border: 1px solid rgba(102, 126, 234, 0.08);
  border-radius: var(--border-radius-2xl);
  padding: var(--spacing-lg) var(--spacing-xl);
  color: var(--text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  transition: var(--transition-professional);
  box-shadow: var(--shadow-professional);
  position: relative;
  overflow: hidden;
  letter-spacing: -0.01em;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--accent-gradient);
    transform: scaleX(0);
    transition: var(--transition-professional);
    box-shadow: 0 0 10px rgba(79, 172, 254, 0.3);
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, 
      rgba(102, 126, 234, 0.02) 0%, 
      rgba(79, 172, 254, 0.01) 100%);
    opacity: 0;
    transition: var(--transition-professional);
    pointer-events: none;
  }
  
  &:hover {
    background: var(--bg-primary);
    transform: translateY(-6px) scale(1.03);
    box-shadow: var(--shadow-enterprise);
    border-color: rgba(102, 126, 234, 0.15);
  }
  
  &:hover::before {
    transform: scaleX(1);
  }
  
  &:hover::after {
    opacity: 1;
  }
  
  .icon {
    margin-right: var(--spacing-sm);
    font-size: 1.25rem;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.1));
  }
  
  @media (max-width: 768px) {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: var(--font-size-xs);
  }
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3xl);
  max-width: 1800px;
  width: 100%;
  margin: 0 auto;
  overflow: hidden;
  animation: fadeInScale 1.2s var(--transition-professional) 0.8s both;
  
  @media (max-width: 1200px) {
    gap: var(--spacing-2xl);
    grid-template-columns: 1.2fr 0.8fr;
    max-width: 1400px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: var(--spacing-xl);
    max-width: 100%;
  }
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
  animation: slideInLeft 1s var(--transition-professional) 0.9s both;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
  
  @media (max-width: 768px) {
    gap: var(--spacing-xl);
  }
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
  animation: slideInRight 1s var(--transition-professional) 1s both;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
`;

const NavButton = styled.button`
  background: var(--glass-gradient);
  color: var(--text-primary);
  border: 1px solid rgba(102, 126, 234, 0.1);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-radius: var(--border-radius-2xl);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-lg);
  transition: var(--transition-professional);
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-professional);
  width: 100%;
  backdrop-filter: var(--backdrop-blur-lg);
  letter-spacing: -0.01em;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--professional-gradient);
    opacity: 0;
    transition: var(--transition-professional);
    z-index: -1;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    right: 0;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: var(--transition-professional);
  }
  
  &:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: var(--shadow-enterprise);
    border-color: rgba(102, 126, 234, 0.2);
    color: white;
  }
  
  &:hover::before {
    opacity: 1;
  }
  
  &:hover::after {
    left: 100%;
  }
  
  &:active {
    transform: translateY(-2px) scale(1.02);
  }
  
  .button-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-md);
    position: relative;
    z-index: 1;
  }
  
  .icon {
    font-size: 1.3rem;
    transition: var(--transition-professional);
    filter: drop-shadow(0 2px 4px rgba(102, 126, 234, 0.1));
  }
  
  &:hover .icon {
    transform: scale(1.15) rotate(5deg);
  }
  
  &.secondary {
    border-color: rgba(0, 200, 81, 0.1);
    
    &::before {
      background: var(--success-gradient);
    }
    
    &:hover {
      border-color: rgba(0, 200, 81, 0.2);
      box-shadow: var(--shadow-glow-success);
    }
  }
  
  @media (max-width: 768px) {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: var(--font-size-xs);
    margin-bottom: var(--spacing-md);
  }
`;

const NavigationPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
`;

const ModernCard = styled.div`
  background: var(--glass-gradient);
  border-radius: var(--border-radius-3xl);
  padding: var(--spacing-2xl);
  box-shadow: var(--shadow-enterprise);
  backdrop-filter: var(--backdrop-blur-xl);
  border: 1px solid rgba(102, 126, 234, 0.06);
  position: relative;
  overflow: hidden;
  transition: var(--transition-professional);
  width: 100%;
  max-width: 100%;
  min-width: 0;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--professional-gradient);
    transition: var(--transition-professional);
    opacity: 0.8;
    box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at top left, rgba(102, 126, 234, 0.015) 0%, transparent 50%),
      radial-gradient(circle at bottom right, rgba(118, 75, 162, 0.015) 0%, transparent 50%);
    opacity: 0;
    transition: var(--transition-professional);
    pointer-events: none;
    z-index: 0;
  }
  
  > * {
    position: relative;
    z-index: 1;
  }
  
  &:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: var(--shadow-3xl);
    border-color: rgba(102, 126, 234, 0.12);
    background: var(--bg-primary);
  }
  
  &:hover::before {
    height: 3px;
    opacity: 1;
    box-shadow: 0 0 25px rgba(102, 126, 234, 0.4);
  }
  
  &:hover::after {
    opacity: 1;
  }
  
  @media (max-width: 768px) {
    padding: var(--spacing-xl);
    border-radius: var(--border-radius-2xl);
    
    &:hover {
      transform: translateY(-6px) scale(1.01);
    }
  }
`;

const FloatingShape = styled.div`
  position: absolute;
  width: ${props => props.size || '120px'};
  height: ${props => props.size || '120px'};
  background: ${props => props.gradient || 'linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(139, 92, 246, 0.06))'};
  border-radius: 50%;
  top: ${props => props.top || '10%'};
  left: ${props => props.left || '10%'};
  animation: float 8s ease-in-out infinite;
  pointer-events: none;
  filter: blur(1px);
  opacity: 0.7;
  
  @keyframes float {
    0%, 100% { 
      transform: translateY(0px) rotate(0deg) scale(1); 
    }
    33% { 
      transform: translateY(-15px) rotate(120deg) scale(1.05); 
    }
    66% { 
      transform: translateY(-10px) rotate(240deg) scale(0.95); 
    }
  }
  
  &:nth-child(2) {
    animation-delay: -2.5s;
    animation-duration: 10s;
  }
  
  &:nth-child(3) {
    animation-delay: -5s;
    animation-duration: 12s;
  }
`;

const ConnectionIndicator = styled.div`
  position: fixed;
  top: var(--spacing-2xl);
  right: var(--spacing-2xl);
  background: var(--glass-gradient);
  backdrop-filter: var(--backdrop-blur-xl);
  border-radius: var(--border-radius-full);
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  border: 1px solid rgba(102, 126, 234, 0.08);
  z-index: 1000;
  animation: fadeInScale 1s var(--transition-professional) 1.5s both;
  box-shadow: var(--shadow-enterprise);
  transition: var(--transition-professional);
  letter-spacing: -0.01em;
  
  &:hover {
    transform: scale(1.08);
    box-shadow: var(--shadow-3xl);
    border-color: rgba(102, 126, 234, 0.15);
  }
  
  .status-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    background: var(--success-gradient);
    border-radius: 50%;
    margin-right: var(--spacing-md);
    animation: gentlePulse 2.5s infinite;
    box-shadow: 0 0 8px rgba(0, 200, 81, 0.4);
  }
  
  @media (max-width: 768px) {
    top: var(--spacing-lg);
    right: var(--spacing-lg);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-xs);
  }
`;

function CVUpdaterContent() {
  const [cvUploaded, setCvUploaded] = useState(false);
  const [refreshCV, setRefreshCV] = useState(false);
  const navigate = useNavigate();

  const handleCVUpload = () => {
    setCvUploaded(true);
    setRefreshCV(!refreshCV);
  };

  const handleChatUpdate = (isContentUpdate = false) => {
    if (isContentUpdate) {
      // Force CV refresh when content is updated
      setRefreshCV(Date.now());
    } else {
      // Normal chat update
      setRefreshCV(!refreshCV);
    }
  };

  return (
    <AppContainer>
      <FloatingShape 
        size="180px" 
        top="8%" 
        left="5%" 
        gradient="linear-gradient(135deg, rgba(102, 126, 234, 0.06), rgba(118, 75, 162, 0.04))"
      />
      <FloatingShape 
        size="120px" 
        top="65%" 
        left="88%" 
        gradient="linear-gradient(135deg, rgba(79, 172, 254, 0.05), rgba(102, 126, 234, 0.03))"
      />
      <FloatingShape 
        size="150px" 
        top="35%" 
        left="92%" 
        gradient="linear-gradient(135deg, rgba(118, 75, 162, 0.04), rgba(79, 172, 254, 0.02))"
      />
      <FloatingShape 
        size="100px" 
        top="15%" 
        left="85%" 
        gradient="var(--accent-gradient)"
      />
      <FloatingShape 
        size="200px" 
        top="50%" 
        left="2%" 
        gradient="linear-gradient(135deg, rgba(0, 200, 81, 0.03), rgba(0, 150, 60, 0.02))"
      />
      
      <ConnectionIndicator>
        <span className="status-dot"></span>
        Connected
      </ConnectionIndicator>
      
      <ContentWrapper>
        <Header>
          <Title>✨ CV Updater Chatbot</Title>
          <Subtitle>
            Transform your career with AI-powered CV updates through intelligent conversation
          </Subtitle>
          <StatsBar>
            <StatItem>
              <span className="icon">🚀</span>
              AI Powered
            </StatItem>
            <StatItem>
              <span className="icon">💬</span>
              Real-time Chat
            </StatItem>
            <StatItem>
              <span className="icon">📋</span>
              Professional CVs
            </StatItem>
          </StatsBar>
        </Header>
        
        <MainContent>
          <LeftPanel>
            <ModernCard>
              <FileUpload onUploadSuccess={handleCVUpload} />
            </ModernCard>
            
            <ModernCard>
              <ChatInterface 
                cvUploaded={cvUploaded} 
                onChatUpdate={handleChatUpdate}
              />
            </ModernCard>
          </LeftPanel>
          
          <RightPanel>
            <NavigationPanel>
              <NavButton 
                className="secondary"
                onClick={() => navigate('/cv-builder')}
              >
                <div className="button-content">
                  <span className="icon">🎯</span>
                  Create New CV
                </div>
              </NavButton>
              
              <NavButton onClick={() => navigate('/cv-management')}>
                <div className="button-content">
                  <span className="icon">📋</span>
                  Manage My CVs
                </div>
              </NavButton>
              
              {cvUploaded && (
                <NavButton onClick={() => navigate('/projects')}>
                  <div className="button-content">
                    <span className="icon">🚀</span>
                    View Projects Portfolio
                  </div>
                </NavButton>
              )}
            </NavigationPanel>
            
            <ModernCard style={{height: 'fit-content', minHeight: '500px', maxHeight: '650px'}}>
              <CVDisplay 
                cvUploaded={cvUploaded} 
                refreshTrigger={refreshCV}
              />
            </ModernCard>
          </RightPanel>
        </MainContent>
      </ContentWrapper>
    </AppContainer>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<CVUpdaterContent />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/cv-builder" element={<CVBuilderPage />} />
        <Route path="/cv-management" element={<CVManagementPage />} />
      </Routes>
    </Router>
  );
}

export default App; 