import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8081';

const UploadContainer = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 30px;
  margin: 20px 0;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  border: 2px dashed rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  
  &:hover {
    border-color: rgba(102, 126, 234, 0.6);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
  }
`;

const Title = styled.h3`
  color: #2d3748;
  margin-bottom: 15px;
  font-size: 1.3rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
  
  .icon {
    font-size: 1.5rem;
  }
`;

const Description = styled.p`
  color: #4a5568;
  font-size: 0.95rem;
  margin-bottom: 20px;
  line-height: 1.5;
`;

const DropZone = styled.div`
  border: 2px dashed ${props => props.isDragOver ? '#667eea' : '#cbd5e0'};
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: ${props => props.isDragOver ? 'rgba(102, 126, 234, 0.05)' : 'rgba(248, 250, 252, 0.8)'};
  
  &:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
  }
`;

const UploadIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 15px;
  color: #667eea;
`;

const UploadText = styled.p`
  color: #2d3748;
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 8px;
`;

const UploadSubtext = styled.p`
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 15px;
`;

const SupportedFormats = styled.div`
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
`;

const FormatBadge = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
`;

const HiddenInput = styled.input`
  display: none;
`;

const Button = styled.button`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-top: 15px;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
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
    gap: 8px;
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const SuccessMessage = styled.div`
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  color: #155724;
  padding: 15px;
  border-radius: 10px;
  margin-top: 15px;
  border-left: 4px solid #28a745;
  font-size: 0.9rem;
`;

const ErrorMessage = styled.div`
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  padding: 15px;
  border-radius: 10px;
  margin-top: 15px;
  border-left: 4px solid #dc3545;
  font-size: 0.9rem;
`;

const FileInfo = styled.div`
  margin-top: 15px;
  padding: 15px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(102, 126, 234, 0.2);
  
  .file-name {
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 5px;
  }
  
  .file-size {
    font-size: 0.85rem;
    color: #718096;
  }
`;

function CVUploadForProjects({ onProjectsExtracted }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleFileSelect = (file) => {
    if (file && (file.type === 'application/pdf' || 
                 file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
                 file.type === 'text/plain')) {
      setSelectedFile(file);
      setUploadStatus('');
      setError('');
    } else {
      setError('Please select a PDF, DOCX, or TXT file.');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    handleFileSelect(file);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadStatus('Extracting projects from CV...');
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(`${API_BASE_URL}/upload-cv-for-projects/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });

      console.log('CV upload response:', response.data);

      // Use the projects returned directly from the upload response
      const extractedProjects = response.data.extracted_projects || [];
      console.log('Extracted projects from response:', extractedProjects);

      setUploadStatus(`Successfully extracted ${extractedProjects.length} projects from your CV!`);
      
      // Notify parent component about the extracted projects
      if (onProjectsExtracted) {
        onProjectsExtracted(extractedProjects);
      }

      // Clear the file input
      setSelectedFile(null);
      setIsDragOver(false);
      
      setTimeout(() => {
        setUploadStatus('');
      }, 5000);

    } catch (error) {
      console.error('Upload error:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to extract projects from CV. Please try again.');
      setUploadStatus('');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <UploadContainer>
      <Title>
        <span className="icon">📄</span>
        Extract Projects from CV
      </Title>
      
      <Description>
        Upload your CV (PDF, DOCX, or TXT) to automatically extract and display your projects. 
        Only the Projects section will be extracted - other sections like Skills, Experience, and Education will be ignored.
      </Description>
      
      <DropZone
        isDragOver={isDragOver}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <UploadIcon>📤</UploadIcon>
        <UploadText>
          {isDragOver ? 'Drop your CV here' : 'Click or drag your CV here'}
        </UploadText>
        <UploadSubtext>
          We'll extract only the Projects section from your CV
        </UploadSubtext>
        <SupportedFormats>
          <FormatBadge>PDF</FormatBadge>
          <FormatBadge>DOCX</FormatBadge>
          <FormatBadge>TXT</FormatBadge>
        </SupportedFormats>
      </DropZone>

      <HiddenInput
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
      />

      {selectedFile && (
        <FileInfo>
          <div className="file-name">{selectedFile.name}</div>
          <div className="file-size">{formatFileSize(selectedFile.size)}</div>
          
          <Button 
            onClick={handleFileUpload} 
            disabled={isUploading}
          >
            <div className="button-content">
              {isUploading && <LoadingSpinner />}
              {isUploading ? 'Extracting Projects...' : 'Extract Projects from CV'}
            </div>
          </Button>
        </FileInfo>
      )}

      {uploadStatus && (
        <SuccessMessage>
          ✅ {uploadStatus}
        </SuccessMessage>
      )}

      {error && (
        <ErrorMessage>
          ❌ {error}
        </ErrorMessage>
      )}
    </UploadContainer>
  );
}

export default CVUploadForProjects; 