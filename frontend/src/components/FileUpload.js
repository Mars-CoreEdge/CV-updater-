import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import * as pdfjsLib from 'pdfjs-dist';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8081';

// Configure PDF.js worker - Use a reliable CDN version that's known to work
try {
  // Use a stable version that's definitely available on CDN
  pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;
  console.log('✅ PDF.js worker configured with stable version 3.11.174');
} catch (error) {
  console.warn('⚠️ PDF.js worker configuration failed:', error);
  // Try alternative CDN
  try {
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js`;
    console.log('✅ PDF.js worker configured with unpkg CDN');
  } catch (fallbackError) {
    console.warn('⚠️ All PDF.js worker configurations failed:', fallbackError);
  }
}

const UploadContainer = styled.div`
  text-align: center;
  position: relative;
  /* Remove all blurry effects */
  backdrop-filter: none !important;
  filter: none !important;
  &:hover {
    backdrop-filter: none !important;
    filter: none !important;
  }
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
  transition: none;
  position: relative;
  overflow: hidden;
  /* Remove hover and animation */
  &:hover {
    border-color: var(--primary-color);
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
    /* No transform or box-shadow */
  }
  &::before, &:hover::before {
    transition: none;
    left: -100%;
  }
  ${props => props.isDragOver && ''}
  backdrop-filter: none !important;
  filter: none !important;
  &:hover {
    backdrop-filter: none !important;
    filter: none !important;
  }
`;

const UploadIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 20px;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: none;
  /* Remove scale on hover */
  ${DropZone}:hover & {
    transform: none;
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
`;

const ErrorMessage = styled.div`
  background: linear-gradient(135deg, #f8d7da, #f5c6cb);
  color: #721c24;
  padding: 20px;
  border-radius: 12px;
  margin-top: 20px;
  border-left: 4px solid #dc3545;
  animation: shakeError 0.5s ease-out;
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

function FileUpload({ onFileUploaded }) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);
  const { user } = useAuth();
  
  // Check bucket access on component mount
  useEffect(() => {
    const checkBucketAccess = async () => {
      if (user) {
        // This part is no longer needed as we are using a backend API
        // const bucketExists = await ensureStorageBucket();
        // if (bucketExists) {
        //   await testBucketAccess();
        // }
      }
    };
    
    checkBucketAccess();
  }, [user]);

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
      setUploadStatus('');
      setError('');
      setUploadProgress(0);
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
    setUploadStatus('Processing file...');
    setError(null);

    try {
      // Step 1: Extract content from file (if possible)
      setUploadStatus('Reading file content...');
      const fileContent = await readFileContent(selectedFile);
      
      // Step 2: Upload CV to backend API
      setUploadStatus('Uploading CV to server...');
      
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Only add extracted_text if we have it (for text files)
      if (fileContent) {
        console.log('Extracted file content length:', fileContent.length);
        console.log('Content preview:', fileContent.substring(0, 500));
        formData.append('extracted_text', fileContent);
        
        // --- Education section regex extraction ---
        // This regex matches a wide variety of education section headers (robust, case-insensitive, underscores/dashes/spaces)
        const educationRegex = /^(?:[_\-\s]*)(EDUCATION|EDUCATIONAL\s+BACKGROUND|EDUCATION\s+&\s+QUALIFICATIONS|ACADEMIC\s+BACKGROUND|QUALIFICATIONS)[_\-\s]*$\n*([\s\S]*?)(?=^[_\-\s]*[A-Z][A-Z\s&]+[_\-\s]*$|$)/im;
        const educationMatch = fileContent.match(educationRegex);
        let educationSection = null;
        let educationIndices = null;
        if (educationMatch) {
          educationSection = educationMatch[0];
          educationIndices = {
            start: educationMatch.index,
            end: educationMatch.index + educationMatch[0].length
          };
          console.log('[DIAG] Education section found:', educationSection);
          console.log('[DIAG] Education section indices:', educationIndices);
        } else {
          console.log('[DIAG] No Education section found in extracted text.');
        }
        // --- End Education section regex extraction ---
      } else {
        console.log('No frontend extraction - backend will handle file processing');
      }

      const response = await axios.post(`${API_BASE_URL}/upload-cv/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      console.log('Upload response:', response.data);

      setUploadStatus('Upload completed successfully!');
      
      // Step 3: Trigger refresh and success callback
      if (onFileUploaded) {
        onFileUploaded(true);
      }
      // Dispatch a custom event to trigger CV refresh in other components
      window.dispatchEvent(new CustomEvent('cv-updated', { detail: { reason: 'upload' } }));
      
      // Clear the file input
      setSelectedFile(null);
      setIsDragOver(false);
      
      setTimeout(() => {
        setUploadStatus('');
      }, 3000);

    } catch (error) {
      console.error('Upload error:', error);
      setError(error.response?.data?.detail || error.message || 'Upload failed. Please try again.');
      setUploadStatus('');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const readFileContent = async (file) => {
    setUploadStatus('Reading file content...');
    try {
      let extractedText = '';
      if (file.type === 'application/pdf') {
        // Let the backend handle PDF extraction for best results
        return null;
      } else if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        setUploadStatus('Processing Word document...');
        // Return null to let backend handle DOCX processing
        return null;
      } else if (file.type === 'text/plain') {
        setUploadStatus('Reading text file...');
        extractedText = await file.text();
      } else {
        throw new Error('Unsupported file type');
      }
      return extractedText;
    } catch (error) {
      console.error('Error reading file content:', error);
      throw new Error(`Failed to read file: ${error.message}`);
    }
  };

  const extractTextFromPDF = async (file) => {
    try {
      console.log('Starting PDF text extraction...');
      const arrayBuffer = await file.arrayBuffer();
      // Load the PDF document
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      console.log(`PDF loaded successfully. Pages: ${pdf.numPages}`);
      let fullText = '';
      // Extract text from each page
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        console.log(`Processing page ${pageNum}/${pdf.numPages}`);
        setUploadStatus(`Extracting text from page ${pageNum}/${pdf.numPages}...`);
        try {
          const page = await pdf.getPage(pageNum);
          const textContent = await page.getTextContent();
          // Group items by their y position (line), and detect paragraph/section breaks
          let lines = [];
          let lastY = null;
          let currentLine = [];
          let lastLineY = null;
          let lastLineIndent = null;
          let lineYs = [];
          let lineIndents = [];
          textContent.items.forEach(item => {
            const thisY = Math.round(item.transform[5]);
            const thisX = Math.round(item.transform[4]);
            if (lastY === null) {
              lastY = thisY;
              lastLineIndent = thisX;
            }
            if (Math.abs(thisY - lastY) > 2) { // New line (tolerance for small y shifts)
              if (currentLine.length > 0) {
                lines.push({ text: currentLine.join(' '), y: lastY, x: lastLineIndent });
                lineYs.push(lastY);
                lineIndents.push(lastLineIndent);
              }
              currentLine = [item.str];
              lastY = thisY;
              lastLineIndent = thisX;
            } else {
              currentLine.push(item.str);
            }
          });
          if (currentLine.length > 0) {
            lines.push({ text: currentLine.join(' '), y: lastY, x: lastLineIndent });
            lineYs.push(lastY);
            lineIndents.push(lastLineIndent);
          }
          // Now, join lines, inserting an extra blank line if the vertical gap or indentation is large
          let pageText = '';
          for (let i = 0; i < lines.length; i++) {
            const lineText = lines[i].text.trim();
            if (!lineText) continue;
            pageText += lineText;
            // If next line exists, check vertical gap and indentation
            if (i < lines.length - 1) {
              const gap = Math.abs(lines[i+1].y - lines[i].y);
              const indentDiff = Math.abs(lines[i+1].x - lines[i].x);
              // Large vertical gap or big change in indentation = new paragraph/section
              if (gap > 15 || indentDiff > 30) {
                pageText += '\n\n';
              } else {
                pageText += '\n';
              }
            }
          }
          pageText = pageText.trim();
          if (pageText) {
            fullText += pageText + '\n\n';
          }
          console.log(`Page ${pageNum} text length:`, pageText.length);
        } catch (pageError) {
          console.warn(`Error processing page ${pageNum}:`, pageError);
          // Continue with other pages
        }
      }
      const finalText = fullText.trim();
      console.log('PDF extraction completed. Total text length:', finalText.length);
      if (!finalText || finalText.length < 10) {
        console.warn('PDF extraction resulted in minimal text');
        throw new Error('PDF appears to be empty or contains mostly images. Please try a text-based PDF or convert to TXT format. You can copy and paste your CV content into a .txt file.');
      }
      return finalText;
    } catch (error) {
      console.info('Frontend PDF extraction failed, but backend will handle extraction. This is normal for some files.');
      if (error.message.includes('Invalid PDF')) {
        throw new Error('Invalid PDF file. Please check the file and try again.');
      } else if (error.message.includes('password')) {
        throw new Error('PDF is password protected. Please remove the password and try again.');
      } else if (error.message.includes('API version') || error.message.includes('Worker version') || error.message.includes('Failed to fetch')) {
        throw new Error('PDF processing service temporarily unavailable. The backend will handle PDF processing instead. Please try uploading your PDF file.');
      } else if (error.message.includes('UnknownErrorException')) {
        throw new Error('PDF processing failed. The file might be corrupted or in an unsupported format. Please try converting to TXT format or let the backend process it.');
      } else {
        throw new Error(`PDF processing failed: ${error.message}. The backend will attempt to process your PDF file.`);
      }
    }
  };

  const handleDownloadSelectedCV = async (selectedProjectIds) => {
    try {
      const response = await axios.post(
        'http://localhost:8081/cv/download-with-selected-projects',
        selectedProjectIds, // should be an array of IDs
        { responseType: 'blob' }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Selected_Projects_CV.pdf');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Failed to download CV with selected projects.');
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
        <UploadIcon>📄</UploadIcon>
        <UploadText>
          {isDragOver ? 'Drop your file here' : 'Click or drag your CV here'}
        </UploadText>
        <UploadSubtext>
          Upload your CV to get started with AI enhancement
          <br />
          <small style={{ fontSize: '0.8rem', opacity: 0.7 }}>
            💡 Tip: If PDF upload fails, try converting to TXT format
          </small>
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
          <div className="file-icon">{getFileIcon(selectedFile)}</div>
          <strong>{selectedFile.name}</strong>
          <div className="file-details">
            <div><strong>Size:</strong> {formatFileSize(selectedFile.size)}</div>
            <div><strong>Type:</strong> {selectedFile.type.split('/').pop().toUpperCase()}</div>
          </div>
          
          <Button 
            onClick={handleFileUpload} 
            disabled={isUploading}
            style={{ marginTop: '15px' }}
          >
            <div className="button-content">
              {isUploading && <LoadingSpinner />}
              {isUploading ? 'Uploading...' : 'Upload CV'}
            </div>
          </Button>
          
          {uploadProgress > 0 && (
            <ProgressBar progress={uploadProgress}>
              <div className="progress-fill"></div>
            </ProgressBar>
          )}
        </FileInfo>
      )}

      {uploadStatus && (
        <SuccessMessage>
          <span className="success-icon">✅</span>
          <strong>{uploadStatus}</strong>
        </SuccessMessage>
      )}

      {error && (
        <ErrorMessage>
          <span className="error-icon">❌</span>
          <strong>Upload Error</strong>
          <div style={{ marginTop: '8px' }}>{error}</div>
        </ErrorMessage>
      )}
    </UploadContainer>
  );
}

export default FileUpload; 