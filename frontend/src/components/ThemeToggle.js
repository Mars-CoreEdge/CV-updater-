import React from 'react';
import styled from 'styled-components';
import { useTheme } from '../contexts/ThemeContext';

const ToggleContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
`;

const ToggleLabel = styled.span`
  font-size: 0.9rem;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
  transition: color 0.3s ease;
`;

const ToggleSwitch = styled.button`
  position: relative;
  width: 60px;
  height: 30px;
  background: ${props => props.isDarkMode 
    ? props.theme.colors.gradient 
    : props.theme.colors.border};
  border: none;
  border-radius: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: inset 0 2px 4px ${props => props.theme.colors.shadow};
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 15px ${props => props.theme.colors.shadow};
  }
  
  &:focus {
    outline: none;
    box-shadow: 0 0 0 3px ${props => props.theme.colors.borderFocus}40;
  }
`;

const ToggleKnob = styled.div`
  position: absolute;
  top: 3px;
  left: ${props => props.isDarkMode ? '33px' : '3px'};
  width: 24px;
  height: 24px;
  background: ${props => props.theme.colors.surface};
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px ${props => props.theme.colors.shadow};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  
  &::after {
    content: '${props => props.isDarkMode ? '🌙' : '☀️'}';
    filter: ${props => props.isDarkMode ? 'none' : 'brightness(1.2)'};
  }
`;

const ThemeIcon = styled.span`
  font-size: 1.2rem;
  transition: all 0.3s ease;
  opacity: ${props => props.active ? 1 : 0.5};
`;

const ThemeToggle = ({ showLabel = true, size = 'normal' }) => {
  const { theme, isDarkMode, toggleTheme } = useTheme();

  const isCompact = size === 'compact';

  return (
    <ToggleContainer theme={theme}>
      {showLabel && !isCompact && (
        <ThemeIcon theme={theme} active={!isDarkMode}>
          ☀️
        </ThemeIcon>
      )}
      
      <ToggleSwitch 
        onClick={toggleTheme}
        isDarkMode={isDarkMode}
        theme={theme}
        title={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
        aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
      >
        <ToggleKnob isDarkMode={isDarkMode} theme={theme} />
      </ToggleSwitch>
      
      {showLabel && !isCompact && (
        <ThemeIcon theme={theme} active={isDarkMode}>
          🌙
        </ThemeIcon>
      )}
      
      {showLabel && (
        <ToggleLabel theme={theme}>
          {isDarkMode ? 'Dark' : 'Light'} Mode
        </ToggleLabel>
      )}
    </ToggleContainer>
  );
};

export default ThemeToggle; 