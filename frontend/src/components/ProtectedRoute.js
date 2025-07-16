import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import styled from 'styled-components'

const LoadingContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: 
    radial-gradient(ellipse at top left, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at top right, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at bottom, rgba(79, 172, 254, 0.1) 0%, transparent 50%),
    linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
`

const LoadingSpinner = styled.div`
  width: 60px;
  height: 60px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <LoadingContainer>
        <LoadingSpinner />
      </LoadingContainer>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default ProtectedRoute 