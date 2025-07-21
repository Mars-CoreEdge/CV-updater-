import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import jsPDF from 'jspdf';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8081';

const CVContainer = styled.div`
  display: flex;
  flex-direction: column;
  position: relative;
  width: 100%;
  max-width: 100%;
  min-width: 0;
  height: 1040px;
  overflow-y: auto;
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
    /* Remove animation */
    animation: none;
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
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border-radius: 16px;
  padding: 30px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  font-family: 'Georgia', 'Times New Roman', serif;
  line-height: 1.8;
  color: var(--text-primary);
  width: 100%;
  max-width: 100%;
  position: relative;
  // min-height: 500px;
  
  @media (max-width: 1200px) {
    padding: 25px;
  }
  
  @media (max-width: 768px) {
    padding: 20px;
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--primary-gradient);
    border-radius: 16px 16px 0 0;
  }
  
  /* Enhanced typography for CV content */
  font-size: 1rem;
  
  @media (max-width: 1200px) {
    font-size: 0.95rem;
  }
  
  @media (max-width: 768px) {
    font-size: 0.9rem;
  }
  
  /* CV Section Headers */
  h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary);
    margin-top: 1.8em;
    margin-bottom: 0.8em;
    font-weight: 700;
    line-height: 1.3;
  }
  
  h1 {
    font-size: 2.2rem;
    padding-bottom: 12px;
    margin-bottom: 1.2em;
    text-align: center;
    color: #1a202c;
  }
  
  h2 {
    font-size: 1.4rem;
    color: var(--primary-color);
    padding-bottom: 6px;
    margin-top: 2em;
  }
  
  h3 {
    font-size: 1.2rem;
    color: #2d3748;
  }
  
  /* Paragraphs and text */
  p {
    margin-bottom: 1em;
    text-align: justify;
  }
  
  /* Lists */
  ul, ol {
    margin-left: 2em;
    margin-bottom: 1.2em;
  }
  
  li {
    margin-bottom: 0.5em;
    line-height: 1.6;
  }
  
  /* Strong text */
  strong, b {
    color: var(--text-primary);
    font-weight: 700;
  }
  
  /* Contact information styling */
  .contact-info {
    text-align: center;
    margin-bottom: 2em;
    padding: 1em;
    background: rgba(102, 126, 234, 0.05);
    border-radius: 8px;
    font-size: 1.1rem;
  }
  
  /* Section dividers */
  hr {
    display: none !important;
  }
  
  /* Improve spacing for better readability */
  & > * {
    margin-bottom: 0.8em;
  }
  
  /* Professional formatting for work experience and education */
  .experience-item, .education-item, .project-item {
    margin-bottom: 1.5em;
    padding: 1em;
    border-left: 4px solid var(--primary-color);
    background: rgba(102, 126, 234, 0.02);
    border-radius: 0 8px 8px 0;
  }
  
  /* Print styles for PDF generation */
  @media print {
    background: white !important;
    color: black !important;
    box-shadow: none !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 20px !important;
    
    &::before {
      display: none !important;
    }
    
    h1, h2, h3 {
      color: #000 !important;
      page-break-after: avoid;
    }
    
    p, li {
      orphans: 3;
      widows: 3;
    }
    
    .experience-item, .education-item, .project-item {
      page-break-inside: avoid;
      background: transparent !important;
      border-left: 2px solid #000 !important;
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
    /* Remove animation */
    animation: none;
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
  const [highlightEducation, setHighlightEducation] = useState(false);
  const [showPdfPreview, setShowPdfPreview] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const educationRef = useRef(null);

  useEffect(() => {
    if (cvUploaded) {
      loadCV();
    }
  }, [cvUploaded]);

  // Listen for cv-updated event to auto-refresh
  useEffect(() => {
    const handleCVUpdated = (e) => {
      console.log('[DIAG] CV update event received:', e.detail);
      loadCV();
      // After loading, highlight education section
      setTimeout(() => {
        setHighlightEducation(true);
        setTimeout(() => setHighlightEducation(false), 2500);
      }, 800);
    };
    window.addEventListener('cv-updated', handleCVUpdated);
    return () => window.removeEventListener('cv-updated', handleCVUpdated);
  }, []);

  useEffect(() => {
    if (highlightEducation && educationRef.current) {
      educationRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
      console.log('[DIAG] Scrolled to and highlighted education section.');
    }
  }, [highlightEducation]);

  // Load PDF preview when CV data changes
  useEffect(() => {
    if (cvData && cvData.content) {
      loadPdfPreview();
    }
  }, [cvData]);

  const loadPdfPreview = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/cv/pdf-preview`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
    } catch (error) {
      console.error('Error loading PDF preview:', error);
      setPdfUrl(null);
    }
  };

  const formatCVContent = (content) => {
    if (!content) return '';
    if (content.length < 100 || content.includes('[File:') || content.includes('PDF uploaded successfully')) {
      return content;
    }
    const lines = content.split('\n');
    let html = '';
    let inList = false;
    let nameRendered = false;
    let contactBlock = [];
    let lastWasSection = false;
    const sectionHeaderRegex = /^(PROFILE SUMMARY|SUMMARY|SKILLS|WORK EXPERIENCE|EXPERIENCE|EDUCATION|PROJECTS|PROFESSIONAL SKILLS|TECHNICAL SKILLS|CONTACT|OBJECTIVE|QUALIFICATIONS)$/i;
    const bulletRegex = /^([\u2022\u2023\u25E6\u2043\u2219\*-])\s?(.*)/;
    const contactRegex = /@|\+\d|linkedin|github|email|www\./i;
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();
      if (!line) {
        if (inList) {
          html += '</ul>';
          inList = false;
        }
        if (contactBlock.length > 0) {
          html += `<div style="text-align:center;margin:0 0 18px 0;font-size:1.05rem;color:#555;">${contactBlock.join('<br/>')}</div>`;
          contactBlock = [];
        }
        continue;
      }
      // Render name as big heading (only first non-empty line)
      if (!nameRendered) {
        html += `<div style="text-align:center;margin:18px 0 8px 0;"><h1 style="margin:0;font-size:2.1rem;font-weight:800;letter-spacing:0.01em;">${line}</h1></div>`;
        nameRendered = true;
        lastWasSection = false;
        continue;
      }
      // Collect contact info lines (immediately after name, up to 3 lines)
      if (nameRendered && contactBlock.length < 3 && contactRegex.test(line)) {
        contactBlock.push(line);
        continue;
      }
      if (contactBlock.length > 0) {
        html += `<div style="text-align:center;margin:0 0 24px 0;font-size:1.05rem;color:#555;">${contactBlock.join('<br/>')}</div>`;
        contactBlock = [];
      }
      // Section headers: match only if line is exactly a section name
      if (sectionHeaderRegex.test(line.replace(/[_\-\s]+/g, ' ').trim().toUpperCase())) {
        if (inList) {
          html += '</ul>';
          inList = false;
        }
        if (lastWasSection) {
          html += '<hr style="border:none;border-top:1.5px solid #e0e4ef;margin:32px 0 24px 0;">';
        }
        html += `<h2 style="text-align:left;text-transform:uppercase;margin:32px 0 12px 0;font-size:1.18rem;font-weight:700;letter-spacing:0.03em;border-bottom:2px solid #e0e4ef;padding-bottom:4px;">${line}</h2>`;
        lastWasSection = true;
        continue;
      }
      lastWasSection = false;
      // Bullet points
      const bulletMatch = line.match(bulletRegex);
      if (bulletMatch) {
        if (!inList) {
          html += '<ul style="margin-left:2em;margin-bottom:0.8em;padding-left:1.2em;">';
          inList = true;
        }
        html += `<li style="font-size:1rem;line-height:1.7;margin-bottom:0.3em;">${bulletMatch[2] || ''}</li>`;
        continue;
      } else if (inList) {
        html += '</ul>';
        inList = false;
      }
      // Job titles/companies: only bold if line is short and after a section header
      if (line.length < 60 && i > 0 && sectionHeaderRegex.test(lines[i-1].replace(/[_\-\s]+/g, ' ').trim().toUpperCase())) {
        html += `<div style="font-weight:600;font-size:1.07rem;margin-bottom:0.2em;">${line}</div>`;
        continue;
      }
      // Regular paragraph
      html += `<p style="margin:0 0 0.7em 0;font-size:1rem;line-height:1.7;font-weight:400;">${line}</p>`;
    }
    if (inList) html += '</ul>';
    if (contactBlock.length > 0) {
      html += `<div style="text-align:center;margin:0 0 24px 0;font-size:1.05rem;color:#555;">${contactBlock.join('<br/>')}</div>`;
    }
    return html;
  };

  const loadCV = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Loading CV from backend API...');
      
      // Get current CV from backend API
      const response = await axios.get(`${API_BASE_URL}/cv/current/`);
      const cvData = response.data;
      
      console.log('Loaded CV from backend:', cvData);
      
      if (cvData && cvData.content && cvData.content.trim().length > 0) {
        setCvData({
          content: cvData.content,
          filename: cvData.filename || 'CV Document',
          lastUpdated: cvData.last_updated
        });
        console.log('CV content loaded successfully, length:', cvData.content.length);
      } else {
        console.warn('CV found but no content');
        setError('CV found but content is empty');
      }
      
    } catch (error) {
      console.error('Error loading CV from backend:', error);
      if (error.response?.status === 404) {
        setError('No CV found. Please upload a CV to get started.');
      } else {
        setError(`Error loading CV: ${error.message}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const downloadCV = () => {
    if (!cvData) return;

    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      // Set up fonts and styling
      pdf.setFont('times', 'normal');
      
      // Page dimensions
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 20;
      const maxWidth = pageWidth - (margin * 2);
      
      let yPosition = margin;
      const lineHeight = 6;
      const maxYPosition = pageHeight - margin;
      
      // Helper function to add new page if needed
      const checkPageBreak = (requiredSpace = 15) => {
        if (yPosition + requiredSpace > maxYPosition) {
          pdf.addPage();
          yPosition = margin;
        }
      };
      
      // Helper function to add text with proper formatting
      const addFormattedText = (text, fontSize = 11, style = 'normal', align = 'left') => {
        pdf.setFontSize(fontSize);
        pdf.setFont('times', style);
        
        const lines = pdf.splitTextToSize(text, maxWidth);
        
        for (let i = 0; i < lines.length; i++) {
          checkPageBreak();
          
          if (align === 'center') {
            pdf.text(lines[i], pageWidth / 2, yPosition, { align: 'center' });
          } else {
            pdf.text(lines[i], margin, yPosition);
          }
          
          yPosition += lineHeight;
        }
      };
      
      // Helper function to add section header
      const addSectionHeader = (title) => {
        checkPageBreak(20);
        yPosition += 5; // Extra space before section
        
        // Add section line
        pdf.setDrawColor(102, 126, 234);
        pdf.setLineWidth(0.5);
        pdf.line(margin, yPosition - 2, pageWidth - margin, yPosition - 2);
        
        addFormattedText(title, 14, 'bold');
        yPosition += 3; // Space after header
      };
      
      // Parse CV content intelligently
      const content = cvData.content;
      const lines = content.split('\n');
      
      let isFirstLine = true;
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        if (!line) {
          yPosition += 3; // Small space for empty lines
          continue;
        }
        
        // Detect section headers (uppercase lines or lines with specific patterns)
        const isHeader = (
          line.toUpperCase() === line && 
          line.length > 3 && 
          line.length < 50 &&
          (line.includes('PROFILE') || line.includes('SUMMARY') || 
           line.includes('SKILLS') || line.includes('EXPERIENCE') || 
           line.includes('EDUCATION') || line.includes('PROJECTS') ||
           line.includes('WORK') || line.includes('PROFESSIONAL'))
        );
        
        // Detect name (usually first significant line)
        const isName = isFirstLine && line.length > 5 && line.length < 50 && !line.includes('@');
        
        // Detect contact info (contains email, phone, etc.)
        const isContactInfo = line.includes('@') || line.includes('+') || line.includes('linkedin') || line.includes('github');
        
        if (isName) {
          addFormattedText(line, 18, 'bold', 'center');
          yPosition += 5;
          isFirstLine = false;
        } else if (isContactInfo) {
          addFormattedText(line, 10, 'normal', 'center');
          yPosition += 3;
        } else if (isHeader) {
          addSectionHeader(line);
        } else {
          // Regular content
          let fontSize = 11;
          let style = 'normal';
          
          // Format based on content type
          if (line.startsWith('•') || line.startsWith('-') || line.startsWith('*')) {
            // Bullet points
            const bulletText = '• ' + line.substring(1).trim();
            addFormattedText(bulletText, fontSize, style);
          } else if (line.includes(':') && line.length < 100) {
            // Likely a label or job title
            addFormattedText(line, fontSize, 'bold');
          } else {
            // Regular text
            addFormattedText(line, fontSize, style);
          }
        }
      }
      
      // Add footer
      const pageCount = pdf.internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        pdf.setPage(i);
        pdf.setFontSize(8);
        pdf.setFont('times', 'italic');
        pdf.setTextColor(128, 128, 128);
        
        // Add page number
        pdf.text(`Page ${i} of ${pageCount}`, pageWidth - margin, pageHeight - 10, { align: 'right' });
        
        // Add generation date
        const date = new Date().toLocaleDateString();
        pdf.text(`Generated on ${date}`, margin, pageHeight - 10);
      }
      
      // Download the PDF
      const filename = cvData.filename ? `Enhanced_${cvData.filename.replace(/\.[^/.]+$/, '')}_${new Date().toISOString().split('T')[0]}.pdf` : `Enhanced_CV_${new Date().toISOString().split('T')[0]}.pdf`;
      
      pdf.save(filename);
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      
      // Fallback to text download if PDF generation fails
      const blob = new Blob([cvData.content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Enhanced_CV_${new Date().toISOString().split('T')[0]}.txt`;
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
            <Button 
              variant="secondary" 
              onClick={() => setShowPdfPreview(!showPdfPreview)}
            >
              <div className="button-content">
                {showPdfPreview ? '📄 Hide PDF' : '📄 Show PDF'}
              </div>
            </Button>
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
              <span className="meta-value">{formatDate(cvData.lastUpdated)}</span>
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
        {!cvData && !isLoading && !error ? (
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
        ) : cvData && cvData.content ? (
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
              <div className="stats-item">
                <span>🔄</span>
                {cvData.content && cvData.content.length > 100 ? 'Full Content' : 'Placeholder'}
              </div>
            </CVStats>
            <div
              ref={highlightEducation ? educationRef : null}
              style={highlightEducation ? { transition: 'background 0.5s', background: '#fffbe6', borderRadius: '6px', boxShadow: '0 0 0 2px #ffe066' } : {}}
              dangerouslySetInnerHTML={{ __html: formatCVContent(cvData.content) }}
            />
            {/* PDF Viewer: Show actual PDF visually if the file is a PDF */}
            {cvData && cvData.filename && cvData.filename.toLowerCase().endsWith('.pdf') && (
              <div style={{ marginTop: '20px', border: '1px solid #ddd', borderRadius: '8px', overflow: 'hidden' }}>
                <div style={{ padding: '10px', background: '#f8f9fa', borderBottom: '1px solid #ddd', fontWeight: 'bold' }}>
                  📄 PDF Preview
                </div>
                <iframe
                  src="http://localhost:8081/cv/pdf-preview"
                  style={{ width: '100%', height: '600px', border: 'none' }}
                  title="CV PDF Preview"
                />
              </div>
            )}
          </>
        ) : cvData && !cvData.content ? (
          <PlaceholderMessage>
            <span className="placeholder-icon">📄</span>
            <div className="placeholder-title">Content Processing</div>
            <div className="placeholder-subtitle">CV uploaded successfully, content is being processed</div>
            Your CV file "{cvData.filename}" was uploaded. If this message persists, please try refreshing or re-uploading your CV.
          </PlaceholderMessage>
        ) : (
          <PlaceholderMessage>
            <span className="placeholder-icon">📤</span>
            <div className="placeholder-title">No CV Available</div>
            <div className="placeholder-subtitle">Upload your CV to get started</div>
            Use the upload panel on the left to upload your CV file and start enhancing it with AI.
          </PlaceholderMessage>
        )}
      </CVContent>
    </CVContainer>
  );
}

export default CVDisplay; 