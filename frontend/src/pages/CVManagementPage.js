import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
  padding: 20px;
  
  @keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
  }
`;

const ContentWrapper = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
  z-index: 1;
`;

const Header = styled.div`
  text-align: center;
  color: white;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 3rem;
  margin-bottom: 15px;
  font-weight: 700;
  background: linear-gradient(135deg, #ffffff 0%, #f0f4ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 4px 8px rgba(0,0,0,0.3);
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 30px;
`;

const ActionBar = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 15px;
  
  @media (max-width: 768px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

const ActionButton = styled.button`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
  }
  
  &.back {
    background: linear-gradient(135deg, #6c757d, #495057);
    box-shadow: 0 4px 15px rgba(108, 117, 125, 0.4);
  }
  
  &.back:hover {
    box-shadow: 0 8px 25px rgba(108, 117, 125, 0.5);
  }
`;

const StatsContainer = styled.div`
  display: flex;
  gap: 20px;
  color: white;
  
  @media (max-width: 768px) {
    justify-content: center;
  }
`;

const StatItem = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(255, 255, 255, 0.2);
`;

const CVGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
  margin-bottom: 40px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const CVCard = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 25px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: ${props => props.isActive ? 
      'linear-gradient(135deg, #667eea, #764ba2)' : 
      'linear-gradient(135deg, #6c757d, #495057)'};
  }
  
  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 30px 80px rgba(0,0,0,0.15);
  }
  
  ${props => props.isActive && `
    border: 2px solid rgba(102, 126, 234, 0.3);
    background: rgba(255, 255, 255, 1);
  `}
`;

const CVCardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
`;

const CVTitle = styled.h3`
  font-size: 1.3rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
  line-height: 1.3;
  flex: 1;
  margin-right: 10px;
`;

const ActiveBadge = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const CVMeta = styled.div`
  margin-bottom: 20px;
`;

const MetaItem = styled.div`
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 5px;
  
  strong {
    color: #495057;
  }
`;

const CVPreview = styled.div`
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  font-size: 0.8rem;
  color: #495057;
  line-height: 1.4;
  max-height: 120px;
  overflow: hidden;
  position: relative;
  margin-bottom: 20px;
  
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 30px;
    background: linear-gradient(transparent, #f8f9fa);
  }
`;

const CVActions = styled.div`
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
`;

const CVActionButton = styled.button`
  padding: 8px 16px;
  border-radius: 12px;
  border: none;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &.primary {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
  }
  
  &.secondary {
    background: #f8f9fa;
    color: #495057;
    border: 1px solid #dee2e6;
    
    &:hover {
      background: #e9ecef;
    }
  }
  
  &.success {
    background: #28a745;
    color: white;
    
    &:hover {
      background: #218838;
    }
  }
  
  &.danger {
    background: #dc3545;
    color: white;
    
    &:hover {
      background: #c82333;
    }
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  color: white;
`;

const EmptyIcon = styled.div`
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.7;
`;

const EmptyTitle = styled.h3`
  font-size: 1.5rem;
  margin-bottom: 10px;
  opacity: 0.9;
`;

const EmptyDescription = styled.p`
  font-size: 1rem;
  opacity: 0.7;
  margin-bottom: 30px;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: white;
  font-size: 1.1rem;
  
  &::before {
    content: '';
    width: 30px;
    height: 30px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-top: 3px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 10px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const EditModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 20px;
  padding: 30px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
`;

const ModalTitle = styled.h2`
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  padding: 5px;
  
  &:hover {
    color: #495057;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #495057;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #dee2e6;
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Textarea = styled.textarea`
  width: 100%;
  min-height: 300px;
  padding: 15px;
  border: 1px solid #dee2e6;
  border-radius: 10px;
  font-size: 0.9rem;
  font-family: 'Courier New', monospace;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const ModalActions = styled.div`
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px solid #e9ecef;
`;

function CVManagementPage() {
  const [cvs, setCvs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingCV, setEditingCV] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchCVs();
  }, []);

  const fetchCVs = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/cvs/`);
      const data = await response.json();
      setCvs(data.cvs || []);
    } catch (error) {
      console.error('Error fetching CVs:', error);
    } finally {
      setLoading(false);
    }
  };

  const activateCV = async (cvId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cvs/${cvId}/activate`, {
        method: 'POST'
      });
      
      if (response.ok) {
        fetchCVs(); // Refresh the list
      }
    } catch (error) {
      console.error('Error activating CV:', error);
    }
  };

  const deleteCV = async (cvId) => {
    if (!window.confirm('Are you sure you want to delete this CV? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/cvs/${cvId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchCVs(); // Refresh the list
      }
    } catch (error) {
      console.error('Error deleting CV:', error);
    }
  };

  const downloadCV = async (cvId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cvs/${cvId}/download`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `CV_${cvId}_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Error downloading CV:', error);
    }
  };

  const startEdit = async (cv) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cvs/${cv.id}`);
      const data = await response.json();
      
      setEditingCV(cv);
      setEditTitle(data.title);
      setEditContent(data.content);
    } catch (error) {
      console.error('Error fetching CV details:', error);
    }
  };

  const saveEdit = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/cvs/${editingCV.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          title: editTitle,
          content: editContent
        })
      });
      
      if (response.ok) {
        setEditingCV(null);
        fetchCVs(); // Refresh the list
      }
    } catch (error) {
      console.error('Error saving CV:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const truncateContent = (content, maxLength = 200) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  return (
    <PageContainer>
      <ContentWrapper>
        <Header>
          <Title>📋 CV Management</Title>
          <Subtitle>Manage, edit, and download your professional CVs</Subtitle>
        </Header>

        <ActionBar>
          <StatsContainer>
            <StatItem>
              <strong>{cvs.length}</strong> Total CVs
            </StatItem>
            <StatItem>
              <strong>{cvs.filter(cv => cv.is_active).length}</strong> Active
            </StatItem>
          </StatsContainer>
          
          <ActionButton 
            className="back"
            onClick={() => navigate('/')}
          >
            ← Back to Home
          </ActionButton>
        </ActionBar>

        {loading ? (
          <LoadingSpinner>Loading your CVs...</LoadingSpinner>
        ) : cvs.length === 0 ? (
          <EmptyState>
            <EmptyIcon>📄</EmptyIcon>
            <EmptyTitle>No CVs Found</EmptyTitle>
            <EmptyDescription>
              You haven't created any CVs yet. Upload a CV or use the CV Builder to get started.
            </EmptyDescription>
            <ActionButton onClick={() => navigate('/cv-builder')}>
              Create Your First CV
            </ActionButton>
          </EmptyState>
        ) : (
          <CVGrid>
            {cvs.map((cv) => (
              <CVCard key={cv.id} isActive={cv.is_active}>
                <CVCardHeader>
                  <CVTitle>{cv.title}</CVTitle>
                  {cv.is_active && <ActiveBadge>Active</ActiveBadge>}
                </CVCardHeader>

                <CVMeta>
                  <MetaItem>
                    <strong>Filename:</strong> {cv.filename}
                  </MetaItem>
                  <MetaItem>
                    <strong>Created:</strong> {formatDate(cv.created_at)}
                  </MetaItem>
                  <MetaItem>
                    <strong>Updated:</strong> {formatDate(cv.updated_at)}
                  </MetaItem>
                </CVMeta>

                <CVActions>
                  {!cv.is_active && (
                    <CVActionButton 
                      className="success"
                      onClick={() => activateCV(cv.id)}
                    >
                      Set Active
                    </CVActionButton>
                  )}
                  
                  <CVActionButton 
                    className="primary"
                    onClick={() => startEdit(cv)}
                  >
                    Edit
                  </CVActionButton>
                  
                  <CVActionButton 
                    className="secondary"
                    onClick={() => downloadCV(cv.id)}
                  >
                    Download
                  </CVActionButton>
                  
                  <CVActionButton 
                    className="danger"
                    onClick={() => deleteCV(cv.id)}
                  >
                    Delete
                  </CVActionButton>
                </CVActions>
              </CVCard>
            ))}
          </CVGrid>
        )}

        {editingCV && (
          <EditModal onClick={(e) => e.target === e.currentTarget && setEditingCV(null)}>
            <ModalContent>
              <ModalHeader>
                <ModalTitle>Edit CV: {editingCV.title}</ModalTitle>
                <CloseButton onClick={() => setEditingCV(null)}>×</CloseButton>
              </ModalHeader>

              <FormGroup>
                <Label>CV Title</Label>
                <Input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  placeholder="Enter CV title..."
                />
              </FormGroup>

              <FormGroup>
                <Label>CV Content</Label>
                <Textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  placeholder="Enter or paste your CV content here..."
                />
              </FormGroup>

              <ModalActions>
                <CVActionButton 
                  className="secondary"
                  onClick={() => setEditingCV(null)}
                >
                  Cancel
                </CVActionButton>
                <CVActionButton 
                  className="primary"
                  onClick={saveEdit}
                >
                  Save Changes
                </CVActionButton>
              </ModalActions>
            </ModalContent>
          </EditModal>
        )}
      </ContentWrapper>
    </PageContainer>
  );
}

export default CVManagementPage; 