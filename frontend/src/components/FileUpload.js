import React, { useState, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const UploadContainer = styled.div`
  text-align: center;
  position: relative;
`;

const Title = styled.h2`
  color: var(--text-primary);
  margin-bottom: 25px;
  font-size: 1.6rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  
  .icon {
    font-size: 1.8rem;
    background: var(--primary-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
`;

const DropZone = styled.div`
  border: 3px dashed ${props => props.isDragOver ? 'var(--primary-color)' : '#e0e6ed'};
  border-radius: 16px;
  padding: 40px 20px;
  margin: 20px 0;
  background: ${props => props.isDragOver ? 
    'linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05))' : 
    'linear-gradient(135deg, #f8f9fa, #ffffff)'
  };
  cursor: pointer;
  transition: var(--transition-smooth);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
    transition: var(--transition-smooth);
  }
  
  &:hover {
    border-color: var(--primary-color);
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
  }
  
  &:hover::before {
    left: 100%;
  }
  
  ${props => props.isDragOver && `
    animation: bounceIn 0.3s ease-out;
    
    @keyframes bounceIn {
      0% { transform: scale(0.95); }
      50% { transform: scale(1.02); }
      100% { transform: scale(1); }
    }
  `}
`;

const UploadIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 20px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: var(--transition-smooth);
  
  ${DropZone}:hover & {
    transform: scale(1.1);
  }
`;

const UploadText = styled.p`
  color: var(--text-primary);
  font-size: 1.2rem;
  margin-bottom: 12px;
  font-weight: 500;
`;

const UploadSubtext = styled.p`
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 20px;
  opacity: 0.8;
`;

const SupportedFormats = styled.div`
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 15px;
  
  @media (max-width: 480px) {
    flex-direction: column;
    gap: 8px;
  }
`;

const FormatBadge = styled.span`
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  box-shadow: var(--shadow-sm);
`;

const FileInfo = styled.div`
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #e3f2fd, #f3e5f5);
  border-radius: 12px;
  color: var(--text-primary);
  border-left: 4px solid var(--primary-color);
  animation: slideInUp 0.3s ease-out;
  
  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .file-details {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 10px;
    font-size: 0.9rem;
    
    @media (max-width: 480px) {
      grid-template-columns: 1fr;
    }
  }
  
  .file-icon {
    font-size: 2rem;
    margin-bottom: 10px;
  }
`;

const HiddenInput = styled.input`
  display: none;
`;

const Button = styled.button`
  background: var(--primary-gradient);
  color: white;
  border: none;
  padding: 14px 30px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: var(--transition-smooth);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: var(--transition-smooth);
  }
  
  &:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
  }
  
  &:hover:not(:disabled)::before {
    left: 100%;
  }
  
  &:active {
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.7;
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

const SuccessMessage = styled.div`
  background: linear-gradient(135deg, #d4edda, #c3e6cb);
  color: #155724;
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
  border-left: 4px solid #28a745;
  animation: fadeInScale 0.5s ease-out;
  box-shadow: var(--shadow-sm);
  
  .success-icon {
    font-size: 1.5rem;
    margin-bottom: 8px;
    display: block;
  }
  
  @keyframes fadeInScale {
    from {
      opacity: 0;
      transform: scale(0.8);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
`;

const ErrorMessage = styled.div`
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
  border-left: 4px solid #dc3545;
  animation: shakeError 0.5s ease-out;
  box-shadow: var(--shadow-sm);
  
  .error-icon {
    font-size: 1.5rem;
    margin-bottom: 8px;
    display: block;
  }
  
  @keyframes shakeError {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-right: 10px;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 15px;
  
  .progress-fill {
    height: 100%;
    background: var(--primary-gradient);
    border-radius: 3px;
    transition: width 0.3s ease;
    width: ${props => props.progress || 0}%;
  }
`;

function FileUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const getFileIcon = (file) => {
    if (file.type === 'application/pdf') return '📄';
    if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') return '📝';
    if (file.type === 'text/plain') return '📃';
    return '📎';
  };

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
      setUploadStatus(null);
      setUploadProgress(0);
    } else {
      setUploadStatus({
        type: 'error',
        message: 'Please select a PDF, DOCX, or TXT file.'
      });
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

  const uploadFile = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadStatus(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://localhost:8000/upload-cv/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        },
      });

      setUploadStatus({
        type: 'success',
        message: 'CV uploaded successfully! You can now start chatting to update it.'
      });
      
      onUploadSuccess();
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: error.response?.data?.detail || 'Failed to upload CV. Please try again.'
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <UploadContainer>
      <Title>
        <span className="icon">📤</span>
        Upload Your CV
      </Title>
      
      <DropZone
        isDragOver={isDragOver}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={handleClick}
      >
        <UploadIcon>☁️</UploadIcon>
        <UploadText>
          Drag and drop your CV here
        </UploadText>
        <UploadSubtext>
          or click to browse your files
        </UploadSubtext>
        
        <SupportedFormats>
          <FormatBadge>PDF</FormatBadge>
          <FormatBadge>DOCX</FormatBadge>
          <FormatBadge>TXT</FormatBadge>
        </SupportedFormats>
      </DropZone>

      <HiddenInput
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,.docx,.txt"
      />

      {selectedFile && (
        <FileInfo>
          <div className="file-icon">{getFileIcon(selectedFile)}</div>
          <strong>Selected File:</strong> {selectedFile.name}
          <div className="file-details">
            <div><strong>Size:</strong> {formatFileSize(selectedFile.size)}</div>
            <div><strong>Type:</strong> {selectedFile.type.split('/')[1].toUpperCase()}</div>
          </div>
        </FileInfo>
      )}

      {selectedFile && uploadStatus?.type !== 'success' && (
        <>
          <Button
            onClick={uploadFile}
            disabled={isUploading}
            style={{marginTop: '20px'}}
          >
            <div className="button-content">
              {isUploading && <LoadingSpinner />}
              {isUploading ? 'Uploading...' : '🚀 Upload CV'}
            </div>
          </Button>
          
          {isUploading && (
            <ProgressBar progress={uploadProgress}>
              <div className="progress-fill"></div>
            </ProgressBar>
          )}
        </>
      )}

      {uploadStatus && (
        uploadStatus.type === 'success' ? (
          <SuccessMessage>
            <span className="success-icon">✅</span>
            <strong>Success!</strong><br />
            {uploadStatus.message}
          </SuccessMessage>
        ) : (
          <ErrorMessage>
            <span className="error-icon">❌</span>
            <strong>Error!</strong><br />
            {uploadStatus.message}
          </ErrorMessage>
        )
      )}
    </UploadContainer>
  );
}

export default FileUpload; 