import React from 'react'
import styled from 'styled-components'

const AuthContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: 
    radial-gradient(ellipse at top left, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at top right, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at bottom, rgba(79, 172, 254, 0.1) 0%, transparent 50%),
    linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%;
  background-attachment: fixed;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
      radial-gradient(circle at 15% 25%, rgba(102, 126, 234, 0.08) 0%, transparent 40%),
      radial-gradient(circle at 85% 75%, rgba(118, 75, 162, 0.06) 0%, transparent 40%),
      radial-gradient(circle at 50% 50%, rgba(79, 172, 254, 0.05) 0%, transparent 60%);
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
    padding: 1rem;
  }
`

const AuthCard = styled.div`
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 3rem;
  width: 100%;
  max-width: 480px;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.05),
    inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 2;
  animation: fadeInScale 0.8s ease-out;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, 
      rgba(102, 126, 234, 0.8) 0%, 
      rgba(79, 172, 254, 0.8) 50%, 
      rgba(118, 75, 162, 0.8) 100%);
    border-radius: 24px 24px 0 0;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
  }
  
  @keyframes fadeInScale {
    from {
      opacity: 0;
      transform: scale(0.95) translateY(10px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }
  
  @media (max-width: 768px) {
    padding: 2rem;
    max-width: 100%;
    margin: 0 1rem;
  }
`

const AuthHeader = styled.div`
  text-align: center;
  margin-bottom: 2.5rem;
`

const AuthTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.025em;
`

const AuthSubtitle = styled.p`
  color: #94a3b8;
  font-size: 1.1rem;
  font-weight: 400;
  margin: 0;
  letter-spacing: -0.01em;
`

const AuthContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`

const FloatingOrb = styled.div`
  position: absolute;
  width: ${props => props.size || '200px'};
  height: ${props => props.size || '200px'};
  background: ${props => props.gradient || 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(79, 172, 254, 0.1))'};
  border-radius: 50%;
  top: ${props => props.top || '10%'};
  left: ${props => props.left || '10%'};
  animation: float 8s ease-in-out infinite;
  pointer-events: none;
  filter: blur(2px);
  opacity: 0.6;
  z-index: 0;
  
  @keyframes float {
    0%, 100% { 
      transform: translateY(0px) rotate(0deg) scale(1); 
    }
    33% { 
      transform: translateY(-20px) rotate(120deg) scale(1.1); 
    }
    66% { 
      transform: translateY(-15px) rotate(240deg) scale(0.9); 
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
`

const AuthLayout = ({ title, subtitle, children }) => {
  return (
    <AuthContainer>
      <FloatingOrb 
        size="150px" 
        top="15%" 
        left="10%" 
        gradient="linear-gradient(135deg, rgba(102, 126, 234, 0.08), rgba(79, 172, 254, 0.08))"
      />
      <FloatingOrb 
        size="120px" 
        top="70%" 
        left="80%" 
        gradient="linear-gradient(135deg, rgba(118, 75, 162, 0.08), rgba(244, 114, 182, 0.08))"
      />
      <FloatingOrb 
        size="180px" 
        top="40%" 
        left="75%" 
        gradient="linear-gradient(135deg, rgba(79, 172, 254, 0.06), rgba(102, 126, 234, 0.06))"
      />
      
      <AuthCard>
        <AuthHeader>
          <AuthTitle>{title}</AuthTitle>
          <AuthSubtitle>{subtitle}</AuthSubtitle>
        </AuthHeader>
        <AuthContent>
          {children}
        </AuthContent>
      </AuthCard>
    </AuthContainer>
  )
}

export default AuthLayout 