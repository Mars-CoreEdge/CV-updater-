import React, { useState } from 'react';
import styled from 'styled-components';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import ThemeToggle from './components/ThemeToggle';
import FileUpload from './components/FileUpload';
import ChatInterface from './components/ChatInterface';
import CVDisplay from './components/CVDisplay';
import ProjectsPage from './pages/ProjectsPage';
import CVBuilderPage from './pages/CVBuilderPage';
import CVManagementPage from './pages/CVManagementPage';
import ProjectManagementPage from './pages/ProjectManagementPage';
import Login from './components/Login';
import Signup from './components/Signup';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import './App.css';

const TopNavigation = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: ${props => props.theme.colors.surface}E6;
  backdrop-filter: blur(20px);
  border-bottom: 1px solid ${props => props.theme.colors.border};
  padding: var(--spacing-md) var(--spacing-2xl);
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 999;
  box-shadow: 0 4px 20px ${props => props.theme.colors.shadow};
  transition: all 0.3s ease;
  height: 60px;
  
  @media (max-width: 768px) {
    padding: var(--spacing-sm) var(--spacing-lg);
    height: 55px;
  }
`;

const TopUserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  background: ${props => props.theme.colors.surfaceHover};
  backdrop-filter: blur(12px);
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-sm) var(--spacing-lg);
  color: ${props => props.theme.colors.textPrimary};
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 15px ${props => props.theme.colors.shadow};
  transition: all 0.3s ease;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #667eea, #764ba2, #4facfe);
    opacity: 0.9;
  }
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.12);
    border-color: rgba(102, 126, 234, 0.25);
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.12), rgba(118, 75, 162, 0.08));
  }
  
  .user-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 600;
    font-size: 1rem;
    box-shadow: 0 3px 10px rgba(102, 126, 234, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);
    transition: all 0.3s ease;
  }
  
  .user-avatar:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  }
  
  .user-details {
    display: flex;
    flex-direction: column;
    gap: 1px;
    
    @media (max-width: 768px) {
      display: none;
    }
  }
  
  .user-name {
    font-size: var(--font-size-sm);
    font-weight: 600;
    color: ${props => props.theme.colors.textPrimary};
    line-height: 1.3;
    letter-spacing: -0.01em;
  }
  
  .user-email {
    font-size: var(--font-size-xs);
    color: ${props => props.theme.colors.textSecondary};
    opacity: 0.8;
    line-height: 1.3;
    font-weight: 400;
  }
`;

const TopSignOutButton = styled.button`
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius-xl);
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 3px 12px rgba(239, 68, 68, 0.08);
  backdrop-filter: blur(12px);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s ease;
  }
  
  &:hover:not(:disabled) {
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 8px 20px rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.3);
    background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.08));
    color: #dc2626;
  }
  
  &:hover:not(:disabled)::before {
    left: 100%;
  }
  
  &:active {
    transform: translateY(-1px) scale(1.01);
  }
  
  .button-content {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    position: relative;
    z-index: 1;
  }
  
  .icon {
    font-size: 1rem;
    transition: transform 0.3s ease;
  }
  
  &:hover .icon {
    transform: scale(1.1) rotate(-5deg);
  }
  
  @media (max-width: 768px) {
    padding: var(--spacing-sm);
    
    .button-text {
      display: none;
    }
  }
`;

const AppContainer = styled.div`
  min-height: 100vh;
  background: ${props => props.theme.colors.background};
  padding: var(--spacing-xl);
  padding-top: 75px;
  padding-bottom: var(--spacing-md);
  position: relative;
  overflow-x: hidden;
  transition: background 0.3s ease;
  
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
    padding-top: 70px;
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
  background: ${props => props.theme.colors.gradient};
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: var(--line-height-tight);
  position: relative;
  text-shadow: 0 4px 8px ${props => props.theme.colors.shadow};
  
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
  color: ${props => props.theme.colors.textSecondary};
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
  background: ${props => props.theme.colors.surface};
  backdrop-filter: var(--backdrop-blur-lg);
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: var(--border-radius-2xl);
  padding: var(--spacing-lg) var(--spacing-xl);
  color: ${props => props.theme.colors.textPrimary};
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  transition: var(--transition-professional);
  box-shadow: 0 4px 20px ${props => props.theme.colors.shadow};
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
    background: ${props => props.theme.colors.surfaceHover};
    transform: translateY(-6px) scale(1.03);
    box-shadow: 0 8px 30px ${props => props.theme.colors.shadowHeavy};
    border-color: ${props => props.theme.colors.borderHover};
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
    background: ${props => props.theme.colors.gradient};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 2px 4px ${props => props.theme.colors.shadow});
  }
  
  @media (max-width: 768px) {
    padding: var(--spacing-md) var(--spacing-lg);
    font-size: var(--font-size-xs);
  }
`;

const MainContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-2xl);
  max-width: 1800px;
  width: 100%;
  margin: 0 auto;
  overflow: hidden;
  animation: fadeInScale 1.2s var(--transition-professional) 0.8s both;
  
  @media (max-width: 1200px) {
    gap: var(--spacing-xl);
    grid-template-columns: 1.2fr 0.8fr;
    max-width: 1400px;
  }
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
    max-width: 100%;
  }
`;

const LeftPanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  animation: slideInLeft 1s var(--transition-professional) 0.9s both;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
  
  @media (max-width: 768px) {
    gap: var(--spacing-lg);
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
  
  /* Removed hover effect from NavButton */
  /*
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
  */
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
  /* &:hover .icon {
    transform: scale(1.15) rotate(5deg);
  } */
  &.secondary {
    border-color: rgba(0, 200, 81, 0.1);
    &::before {
      background: var(--success-gradient);
    }
    /* &:hover {
      border-color: rgba(0, 200, 81, 0.2);
      box-shadow: var(--shadow-glow-success);
    } */
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
  top: 70px;
  right: var(--spacing-2xl);
  background: ${props => props.theme.colors.surface};
  backdrop-filter: var(--backdrop-blur-xl);
  border-radius: var(--border-radius-full);
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: ${props => props.theme.colors.textPrimary};
  border: 1px solid ${props => props.theme.colors.border};
  z-index: 998;
  animation: fadeInScale 1s var(--transition-professional) 1.5s both;
  box-shadow: 0 4px 20px ${props => props.theme.colors.shadow};
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
    top: 65px;
    right: var(--spacing-lg);
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-xs);
  }
`;

function CVUpdaterContent() {
  const [cvUploaded, setCvUploaded] = useState(false);
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const { theme } = useTheme();

  const handleFileUpload = (uploadSuccess) => {
    console.log('File upload completed:', uploadSuccess);
    if (uploadSuccess) {
      setCvUploaded(Date.now()); // Use timestamp to force refresh
    }
  };

  const handleChatUpdate = (isContentUpdate = false) => {
    // Normal chat update
  };

  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/login');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <>
      <TopNavigation theme={theme}>
        <TopUserInfo theme={theme}>
          <div className="user-avatar">
            {user?.user_metadata?.firstName ? 
              user.user_metadata.firstName.charAt(0).toUpperCase() : 
              user?.email?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="user-details">
            <div className="user-name">
              {user?.user_metadata?.fullName || 
               `${user?.user_metadata?.firstName || ''} ${user?.user_metadata?.lastName || ''}`.trim() || 
               'User'}
            </div>
            <div className="user-email">
              {user?.email || 'No email'}
            </div>
          </div>
        </TopUserInfo>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <ThemeToggle showLabel={false} size="compact" />
          
          <TopSignOutButton theme={theme} onClick={handleLogout}>
            <div className="button-content">
              <span className="icon">🚪</span>
              <span className="button-text">Sign Out</span>
            </div>
          </TopSignOutButton>
        </div>
      </TopNavigation>
      
      <AppContainer theme={theme}>
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
        
        <ConnectionIndicator theme={theme}>
          <span className="status-dot"></span>
          Connected
        </ConnectionIndicator>
        
        <ContentWrapper>
          <Header>
            <Title theme={theme}>✨ CV Updater Chatbot</Title>
            <Subtitle theme={theme}>
              Transform your career with AI-powered CV updates through intelligent conversation
            </Subtitle>
            <StatsBar>
              <StatItem theme={theme}>
                <span className="icon">🚀</span>
                AI Powered
              </StatItem>
              <StatItem theme={theme}>
                <span className="icon">💬</span>
                Real-time Chat
              </StatItem>
              <StatItem theme={theme}>
                <span className="icon">📋</span>
                Professional CVs
              </StatItem>
            </StatsBar>
          </Header>
          
          <MainContent>
            <LeftPanel>
              <ModernCard>
                <FileUpload onFileUploaded={handleFileUpload} />
              </ModernCard>
              
              <ModernCard>
                <ChatInterface 
                  cvUploaded={cvUploaded} 
                  onCVUpdate={handleChatUpdate}
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
                
                {/* <NavButton onClick={() => navigate('/project-management')}>
                  <div className="button-content">
                    <span className="icon">🚀</span>
                    Manage Projects
                  </div>
                </NavButton> */}
                
                {cvUploaded && (
                  <NavButton onClick={() => navigate('/projects')}>
                    <div className="button-content">
                      <span className="icon">🚀</span>
                      View Projects Portfolio
                    </div>
                  </NavButton>
                )}
              </NavigationPanel>
              
              <ModernCard style={{height: 'fit-content'}}>
                <CVDisplay 
                  cvUploaded={cvUploaded} 
                />
              </ModernCard>
            </RightPanel>
          </MainContent>
        </ContentWrapper>
      </AppContainer>
    </>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/" element={
              <ProtectedRoute>
                <CVUpdaterContent />
              </ProtectedRoute>
            } />
            <Route path="/projects" element={
              <ProtectedRoute>
                <ProjectsPage />
              </ProtectedRoute>
            } />
            <Route path="/cv-builder" element={
              <ProtectedRoute>
                <CVBuilderPage />
              </ProtectedRoute>
            } />
            <Route path="/cv-management" element={
              <ProtectedRoute>
                <CVManagementPage />
              </ProtectedRoute>
            } />
            <Route path="/project-management" element={
              <ProtectedRoute>
                <ProjectManagementPage />
              </ProtectedRoute>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App; 