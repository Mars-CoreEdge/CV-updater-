import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import axios from 'axios';
import jsPDF from 'jspdf';

const CVContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
  position: relative;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
  
  @media (max-width: 1200px) {
    height: calc(100vh - 130px);
  }
  
  @media (max-width: 768px) {
    height: calc(100vh - 110px);
  }
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-lg);
  border-bottom: 2px solid rgba(99, 102, 241, 0.08);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 60px;
    height: 2px;
    background: var(--primary-gradient);
    border-radius: var(--border-radius-full);
  }
`;

const Title = styled.h2`
  color: var(--text-primary);
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  letter-spacing: -0.02em;
  
  .icon {
    font-size: 2rem;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: iconFloat 3s ease-in-out infinite;
  }
  
  @keyframes iconFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-2px); }
  }
  
  @media (max-width: 768px) {
    font-size: 1.5rem;
    gap: var(--spacing-sm);
    
    .icon {
      font-size: 1.6rem;
    }
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
`;

const Button = styled.button`
  background: ${props => props.variant === 'secondary' ? 
    'var(--bg-card)' : 
    'var(--primary-gradient)'};
  color: ${props => props.variant === 'secondary' ? 'var(--text-primary)' : 'white'};
  border: ${props => props.variant === 'secondary' ? 
    '1px solid rgba(99, 102, 241, 0.15)' : 
    '1px solid transparent'};
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-xl);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: var(--transition-spring);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  backdrop-filter: var(--backdrop-blur-sm);
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: var(--transition-smooth);
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: ${props => props.variant === 'secondary' ? 
      'var(--primary-gradient)' : 
      'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))'};
    opacity: 0;
    transition: var(--transition-smooth);
    z-index: -1;
  }
  
  &:hover:not(:disabled) {
    transform: translateY(-3px) scale(1.02);
    box-shadow: var(--shadow-lg);
    border-color: ${props => props.variant === 'secondary' ? 
      'rgba(99, 102, 241, 0.3)' : 
      'rgba(255, 255, 255, 0.2)'};
  }
  
  &:hover:not(:disabled)::before {
    left: 100%;
  }
  
  &:hover:not(:disabled)::after {
    opacity: ${props => props.variant === 'secondary' ? '1' : '0.1'};
  }
  
  &:hover:not(:disabled) {
    color: ${props => props.variant === 'secondary' ? 'white' : 'white'};
  }
  
  &:active {
    transform: translateY(-1px) scale(1.01);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
  
  .button-content {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    position: relative;
    z-index: 1;
  }
  
  @media (max-width: 768px) {
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: 0.85rem;
  }
`;

const CVContent = styled.div`
  flex: 1;
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: 16px;
  padding: 25px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  overflow-y: auto;
  overflow-x: hidden;
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  font-family: 'Georgia', 'Times New Roman', serif;
  line-height: 1.6;
  color: var(--text-primary);
  min-height: 600px;
  max-height: calc(100vh - 200px);
  height: auto;
  width: 100%;
  max-width: 100%;
  position: relative;
  
  @media (max-width: 1200px) {
    max-height: calc(100vh - 180px);
    min-height: 500px;
    padding: 20px;
  }
  
  @media (max-width: 768px) {
    max-height: calc(100vh - 150px);
    min-height: 400px;
    padding: 15px;
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--primary-gradient);
    border-radius: 16px 16px 0 0;
  }
  
  /* Enhanced typography */
  font-size: 0.9rem;
  
  @media (max-width: 1200px) {
    font-size: 0.85rem;
  }
  
  @media (max-width: 768px) {
    font-size: 0.8rem;
  }
  
  /* Scrollbar styling */
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    border-radius: 4px;
  }
  
  /* CV Content styling */
  h1, h2, h3 {
    color: var(--text-primary);
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    font-weight: 600;
  }
  
  h1 {
    font-size: 1.8rem;
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 8px;
    margin-bottom: 1em;
  }
  
  h2 {
    font-size: 1.3rem;
    color: var(--primary-color);
  }
  
  h3 {
    font-size: 1.1rem;
  }
  
  p {
    margin-bottom: 0.8em;
  }
  
  ul, ol {
    margin-left: 1.5em;
    margin-bottom: 1em;
  }
  
  li {
    margin-bottom: 0.3em;
  }
  
  strong {
    color: var(--text-primary);
    font-weight: 600;
  }
  
  /* Print styles */
  @media print {
    background: white !important;
    color: black !important;
    box-shadow: none !important;
    border: none !important;
    border-radius: 0 !important;
    
    &::before {
      display: none !important;
    }
  }
`;

const PlaceholderMessage = styled.div`
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: 80px 40px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03), rgba(118, 75, 162, 0.03));
  border-radius: 12px;
  border: 2px dashed rgba(102, 126, 234, 0.2);
  font-family: 'Inter', sans-serif;
  
  .placeholder-icon {
    font-size: 4rem;
    margin-bottom: 20px;
    display: block;
    opacity: 0.6;
    animation: float 3s ease-in-out infinite;
  }
  
  .placeholder-title {
    font-size: 1.3rem;
    font-weight: 600;
    margin-bottom: 12px;
    color: var(--text-primary);
    font-style: normal;
  }
  
  .placeholder-subtitle {
    font-size: 1rem;
    margin-bottom: 8px;
    opacity: 0.8;
  }
  
  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
  }
`;

const MetaInfo = styled.div`
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  color: var(--text-primary);
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 0.9rem;
  border-left: 4px solid var(--primary-color);
  box-shadow: var(--shadow-sm);
  animation: slideInDown 0.3s ease-out;
  
  @keyframes slideInDown {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-top: 10px;
  }
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .meta-icon {
      font-size: 1.1rem;
    }
    
    .meta-label {
      font-weight: 600;
      color: var(--text-primary);
    }
    
    .meta-value {
      color: var(--text-secondary);
    }
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  
  .spinner {
    width: 50px;
    height: 50px;
    border: 4px solid rgba(102, 126, 234, 0.2);
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
  }
  
  .loading-text {
    color: var(--text-secondary);
    font-size: 1.1rem;
    font-weight: 500;
    text-align: center;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ErrorMessage = styled.div`
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  padding: 25px;
  border-radius: 12px;
  margin-bottom: 20px;
  border-left: 4px solid #dc3545;
  animation: shakeError 0.5s ease-out;
  box-shadow: var(--shadow-sm);
  
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
  
  .error-message {
    opacity: 0.9;
    line-height: 1.5;
  }
  
  @keyframes shakeError {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }
`;

const RefreshButton = styled(Button)`
  background: linear-gradient(135deg, #00f2fe, #4facfe);
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #00e5f2, #4a9ffe);
  }
`;

const CVStats = styled.div`
  position: absolute;
  top: -12px;
  right: 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  border: 1px solid rgba(102, 126, 234, 0.2);
  box-shadow: var(--shadow-sm);
  
  .stats-item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-right: 12px;
    
    &:last-child {
      margin-right: 0;
    }
  }
`;

function CVDisplay({ cvUploaded, refreshTrigger }) {
  const [cvData, setCvData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (cvUploaded) {
      loadCV();
    }
  }, [cvUploaded, refreshTrigger]);

  const loadCV = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('http://localhost:8000/cv/current/');
      setCvData(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to load CV');
      setCvData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadCV = () => {
    if (!cvData) return;

    try {
      const pdf = new jsPDF();
      
      // Set font
      pdf.setFont('times', 'normal');
      pdf.setFontSize(11);
      
      // Split text into lines that fit the page width
      const pageWidth = pdf.internal.pageSize.getWidth();
      const margin = 20;
      const maxWidth = pageWidth - (margin * 2);
      
      const lines = pdf.splitTextToSize(cvData.content, maxWidth);
      
      // Add text to PDF with page breaks
      let yPosition = margin;
      const lineHeight = 6;
      const pageHeight = pdf.internal.pageSize.getHeight();
      const maxYPosition = pageHeight - margin;
      
      for (let i = 0; i < lines.length; i++) {
        if (yPosition > maxYPosition) {
          pdf.addPage();
          yPosition = margin;
        }
        
        pdf.text(lines[i], margin, yPosition);
        yPosition += lineHeight;
      }
      
      // Download the PDF
      const filename = cvData.filename ? 
        `updated_${cvData.filename.replace(/\.[^/.]+$/, '')}.pdf` : 
        'updated_cv.pdf';
      
      pdf.save(filename);
    } catch (error) {
      console.error('Error generating PDF:', error);
      // Fallback to text download if PDF generation fails
      const blob = new Blob([cvData.content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `updated_${cvData.filename || 'cv.txt'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
  };

  const printCV = () => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
      <html>
        <head>
          <title>CV - ${cvData?.filename}</title>
          <style>
            body { 
              font-family: Georgia, 'Times New Roman', serif; 
              line-height: 1.6; 
              color: #333; 
              max-width: 800px; 
              margin: 0 auto; 
              padding: 20px;
            }
            h1, h2, h3 { color: #2c3e50; margin-top: 1.5em; margin-bottom: 0.5em; }
            h1 { font-size: 1.8rem; border-bottom: 2px solid #667eea; padding-bottom: 8px; }
            h2 { font-size: 1.3rem; color: #667eea; }
            h3 { font-size: 1.1rem; }
            p { margin-bottom: 0.8em; }
            ul, ol { margin-left: 1.5em; margin-bottom: 1em; }
            li { margin-bottom: 0.3em; }
            strong { font-weight: 600; }
          </style>
        </head>
        <body>
          <pre style="white-space: pre-wrap; font-family: inherit;">${cvData?.content}</pre>
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getWordCount = (text) => {
    if (!text) return 0;
    return text.trim().split(/\s+/).length;
  };

  return (
    <CVContainer>
      <Header>
        <Title>
          <span className="icon">📋</span>
          Your Enhanced CV
        </Title>
        
        {cvData && (
          <ActionButtons>
            <RefreshButton onClick={loadCV} disabled={isLoading}>
              <div className="button-content">
                🔄 Refresh
              </div>
            </RefreshButton>
            <Button variant="secondary" onClick={printCV}>
              <div className="button-content">
                🖨️ Print
              </div>
            </Button>
            <Button onClick={downloadCV}>
              <div className="button-content">
                📥 Download
              </div>
            </Button>
          </ActionButtons>
        )}
      </Header>

      {cvData && (
        <MetaInfo>
          <div className="meta-grid">
            <div className="meta-item">
              <span className="meta-icon">📄</span>
              <span className="meta-label">File:</span>
              <span className="meta-value">{cvData.filename}</span>
            </div>
            <div className="meta-item">
              <span className="meta-icon">🕒</span>
              <span className="meta-label">Updated:</span>
              <span className="meta-value">{formatDate(cvData.last_updated)}</span>
            </div>
            <div className="meta-item">
              <span className="meta-icon">📝</span>
              <span className="meta-label">Words:</span>
              <span className="meta-value">{getWordCount(cvData.content).toLocaleString()}</span>
            </div>
            <div className="meta-item">
              <span className="meta-icon">🤖</span>
              <span className="meta-label">AI Enhanced:</span>
              <span className="meta-value">Yes</span>
            </div>
          </div>
        </MetaInfo>
      )}

      {error && (
        <ErrorMessage>
          <span className="error-icon">⚠️</span>
          <div className="error-title">Error Loading CV</div>
          <div className="error-message">{error}</div>
        </ErrorMessage>
      )}

      <CVContent>
        {!cvUploaded ? (
          <PlaceholderMessage>
            <span className="placeholder-icon">📤</span>
            <div className="placeholder-title">Upload Required</div>
            <div className="placeholder-subtitle">Upload your CV to see it displayed here</div>
            Start by uploading your CV using the upload panel on the left.
          </PlaceholderMessage>
        ) : isLoading ? (
          <LoadingSpinner>
            <div className="spinner"></div>
            <div className="loading-text">
              Loading your enhanced CV...
              <br />
              <small>AI is processing your updates</small>
            </div>
          </LoadingSpinner>
        ) : error ? (
          <PlaceholderMessage>
            <span className="placeholder-icon">❌</span>
            <div className="placeholder-title">Failed to Load</div>
            <div className="placeholder-subtitle">Something went wrong</div>
            Please try refreshing or check your connection.
          </PlaceholderMessage>
        ) : cvData ? (
          <>
            <CVStats>
              <div className="stats-item">
                <span>📊</span>
                {getWordCount(cvData.content)} words
              </div>
              <div className="stats-item">
                <span>⭐</span>
                Enhanced
              </div>
            </CVStats>
            {cvData.content}
          </>
        ) : (
          <PlaceholderMessage>
            <span className="placeholder-icon">📄</span>
            <div className="placeholder-title">No Content</div>
            <div className="placeholder-subtitle">CV content not available</div>
            Try uploading your CV again or contact support if the issue persists.
          </PlaceholderMessage>
        )}
      </CVContent>
    </CVContainer>
  );
}

export default CVDisplay; 