import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import ChatInterface from './components/ChatInterface';
import CVDisplay from './components/CVDisplay';
import ProjectsPage from './pages/ProjectsPage';
import CVBuilderPage from './pages/CVBuilderPage';
import './App.css';

const AppContainer = styled.div`
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
`;

const Header = styled.header`
  text-align: center;
  color: white;
  margin-bottom: 40px;
  animation: fadeInUp 0.8s ease-out;
`;

const Title = styled.h1`
  font-size: clamp(2rem, 5vw, 3.5rem);
  margin-bottom: 15px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 8px rgba(0,0,0,0.3);
  line-height: 1.2;
  
  @media (max-width: 768px) {
    font-size: 2.5rem;
  }
`;

const Subtitle = styled.p`
  font-size: clamp(1rem, 2.5vw, 1.3rem);
  opacity: 0.95;
  font-weight: 400;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
  text-shadow: 0 2px 4px rgba(0,0,0,0.2);
`;

const StatsBar = styled.div`
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 20px;
  
  @media (max-width: 768px) {
    gap: 20px;
    flex-wrap: wrap;
  }
`;

const StatItem = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 12px 20px;
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
  transition: var(--transition-smooth);
  
  &:hover {
    background: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
  }
  
  .icon {
    margin-right: 8px;
    font-size: 1.1rem;
  }
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  max-width: 1600px;
  margin: 0 auto;
  
  @media (max-width: 1200px) {
    gap: 25px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 25px;
  animation: slideInLeft 0.8s ease-out 0.2s both;
`;

const RightPanel = styled.div`
  display: flex;
  flex-direction: column;
  animation: slideInRight 0.8s ease-out 0.4s both;
`;

const NavButton = styled.button`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  margin-bottom: 15px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  width: 100%;
  
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
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    background: linear-gradient(135deg, #5a67d8, #6b46c1);
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
  
  &.secondary {
    background: linear-gradient(135deg, #2ecc71, #27ae60);
    box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
    
    &:hover {
      background: linear-gradient(135deg, #27ae60, #229954);
      box-shadow: 0 8px 25px rgba(46, 204, 113, 0.5);
    }
  }
`;

const NavigationPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
`;

const ModernCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  box-shadow: 
    0 20px 60px rgba(0,0,0,0.1),
    0 8px 32px rgba(0,0,0,0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
  transition: var(--transition-smooth);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--primary-gradient);
    transition: var(--transition-smooth);
  }
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: 
      0 30px 80px rgba(0,0,0,0.15),
      0 12px 48px rgba(0,0,0,0.1);
  }
  
  &:hover::before {
    height: 5px;
  }
  
  @media (max-width: 768px) {
    padding: 25px;
    border-radius: 16px;
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

const ConnectionIndicator = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 25px;
  padding: 8px 16px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-primary);
  border: 1px solid rgba(255, 255, 255, 0.3);
  z-index: 1000;
  animation: fadeInScale 0.5s ease-out;
  
  .status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #2ecc71;
    border-radius: 50%;
    margin-right: 8px;
    animation: pulse 2s infinite;
  }
  
  @media (max-width: 768px) {
    top: 10px;
    right: 10px;
    padding: 6px 12px;
    font-size: 0.75rem;
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

  const handleChatUpdate = () => {
    setRefreshCV(!refreshCV);
  };

  return (
    <AppContainer>
      <FloatingShape 
        size="120px" 
        top="5%" 
        left="5%" 
        gradient="linear-gradient(135deg, rgba(240, 147, 251, 0.15), rgba(245, 87, 108, 0.15))"
      />
      <FloatingShape 
        size="80px" 
        top="70%" 
        left="85%" 
        gradient="linear-gradient(135deg, rgba(79, 172, 254, 0.15), rgba(0, 242, 254, 0.15))"
      />
      <FloatingShape 
        size="100px" 
        top="40%" 
        left="90%" 
        gradient="linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15))"
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
              
              {cvUploaded && (
                <NavButton onClick={() => navigate('/projects')}>
                  <div className="button-content">
                    <span className="icon">🚀</span>
                    View Projects Portfolio
                  </div>
                </NavButton>
              )}
            </NavigationPanel>
            
            <ModernCard style={{height: 'fit-content', minHeight: '600px'}}>
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
      </Routes>
    </Router>
  );
}

export default App; 