import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const lightTheme = {
  name: 'light',
  colors: {
    primary: '#667eea',
    primaryDark: '#764ba2',
    secondary: '#10b981',
    accent: '#fbbf24',
    danger: '#ef4444',
    
    // Backgrounds
    background: '#ffffff',
    backgroundSecondary: '#f8f9fa',
    backgroundTertiary: '#f1f5f9',
    surface: '#ffffff',
    surfaceHover: '#f8f9fa',
    
    // Text
    textPrimary: '#2d3748',
    textSecondary: '#4a5568',
    textTertiary: '#718096',
    textMuted: '#a0aec0',
    textLight: '#ffffff',
    
    // Borders
    border: '#e2e8f0',
    borderHover: '#cbd5e0',
    borderFocus: '#667eea',
    
    // Shadows
    shadow: 'rgba(0, 0, 0, 0.1)',
    shadowHeavy: 'rgba(0, 0, 0, 0.2)',
    
    // Gradients
    gradient: 'linear-gradient(135deg, #667eea, #764ba2)',
    gradientHover: 'linear-gradient(135deg, #5a67d8, #6b46c1)',
    
    // Status colors
    success: '#10b981',
    warning: '#fbbf24',
    error: '#ef4444',
    info: '#3b82f6',
  }
};

export const darkTheme = {
  name: 'dark',
  colors: {
    primary: '#8b5cf6',
    primaryDark: '#7c3aed',
    secondary: '#34d399',
    accent: '#fbbf24',
    danger: '#f87171',
    
    // Backgrounds
    background: '#0f172a',
    backgroundSecondary: '#1e293b',
    backgroundTertiary: '#334155',
    surface: '#1e293b',
    surfaceHover: '#334155',
    
    // Text
    textPrimary: '#f1f5f9',
    textSecondary: '#cbd5e1',
    textTertiary: '#94a3b8',
    textMuted: '#64748b',
    textLight: '#ffffff',
    
    // Borders
    border: '#475569',
    borderHover: '#64748b',
    borderFocus: '#8b5cf6',
    
    // Shadows
    shadow: 'rgba(0, 0, 0, 0.3)',
    shadowHeavy: 'rgba(0, 0, 0, 0.5)',
    
    // Gradients
    gradient: 'linear-gradient(135deg, #8b5cf6, #7c3aed)',
    gradientHover: 'linear-gradient(135deg, #a78bfa, #8b5cf6)',
    
    // Status colors
    success: '#34d399',
    warning: '#fbbf24',
    error: '#f87171',
    info: '#60a5fa',
  }
};

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Load theme preference from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(prefersDark);
    }
  }, []);

  useEffect(() => {
    // Save theme preference to localStorage
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update document class for global styling
    document.documentElement.classList.toggle('dark-mode', isDarkMode);
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  const theme = isDarkMode ? darkTheme : lightTheme;

  const value = {
    theme,
    isDarkMode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}; 