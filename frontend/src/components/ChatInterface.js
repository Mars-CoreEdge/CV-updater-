import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 900px;
  position: relative;
  max-height: 900px;
  min-height: 900px;
  
  @media (max-width: 1200px) {
    height: 850px;
    max-height: 850px;
    min-height: 850px;
  }
  
  @media (max-width: 768px) {
    height: 800px;
    max-height: 800px;
    min-height: 800px;
  }
  
  @media (max-width: 480px) {
    height: 750px;
    max-height: 750px;
    min-height: 750px;
  }
`;

const Title = styled.h2`
  color: var(--text-primary);
  margin-bottom: 20px;
  font-size: 1.6rem;
  font-weight: 600;
  text-align: center;
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

const QuickActionsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 6px;
  margin-bottom: 10px;
  max-height: 350px;
  overflow-y: auto;
  
  @media (max-width: 768px) {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 4px;
    max-height: 100px;
  }
  
  @media (max-width: 480px) {
    max-height: 80px;
  }
`;

const RefreshCVButton = styled.button`
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  color: white;
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-xl);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-spring);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px) scale(1.02);
    box-shadow: var(--shadow-md);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .button-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-xs);
    position: relative;
    z-index: 1;
  }
`;

const QuickActionButton = styled.button`
  background: var(--bg-card);
  border: 1px solid rgba(139, 92, 246, 0.12);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: var(--border-radius-xl);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-spring);
  position: relative;
  overflow: hidden;
  backdrop-filter: var(--backdrop-blur-sm);
  box-shadow: var(--shadow-xs);
  white-space: nowrap;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: var(--primary-gradient);
    opacity: 0;
    transition: var(--transition-smooth);
    z-index: 0;
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: var(--transition-smooth);
    z-index: 1;
  }
  
  &:hover:not(:disabled) {
    border-color: rgba(139, 92, 246, 0.3);
    transform: translateY(-1px) scale(1.01);
    box-shadow: var(--shadow-md);
    color: white;
  }
  
  &:hover:not(:disabled)::before {
    opacity: 1;
  }
  
  &:hover:not(:disabled)::after {
    left: 100%;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .button-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    position: relative;
    z-index: 2;
  }
  
  @media (max-width: 768px) {
    font-size: 0.7rem;
    padding: 6px 8px;
  }
`;

const GenerateCVButton = styled.button`
  background: var(--success-gradient);
  color: white;
  border: 1px solid rgba(16, 185, 129, 0.2);
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-xl);
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: var(--transition-spring);
  width: 100%;
  margin-bottom: var(--spacing-sm);
  box-shadow: var(--shadow-glow-success);
  position: relative;
  overflow: hidden;
  backdrop-filter: var(--backdrop-blur-sm);
  letter-spacing: 0.01em;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
    opacity: 0;
    transition: var(--transition-smooth);
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: var(--transition-smooth);
  }
  
  &:hover:not(:disabled) {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 
      var(--shadow-glow-success),
      0 15px 35px rgba(16, 185, 129, 0.25);
    border-color: rgba(16, 185, 129, 0.4);
  }
  
  &:hover:not(:disabled)::before {
    opacity: 1;
  }
  
  &:hover:not(:disabled)::after {
    left: 100%;
  }
  
  &:active {
    transform: translateY(-1px) scale(1.01);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
    box-shadow: var(--shadow-sm);
  }
  
  .button-content {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
    position: relative;
    z-index: 1;
  }
  
  .icon {
    font-size: 1.2rem;
    animation: iconPulse 2s ease-in-out infinite;
  }
  
  @keyframes iconPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
  
  @media (max-width: 768px) {
    font-size: 0.9rem;
    padding: var(--spacing-sm) var(--spacing-md);
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border-radius: 16px;
  margin-bottom: 15px;
  border: 1px solid rgba(139, 92, 246, 0.1);
  position: relative;
  min-height: 500px;
  max-height: 700px;
  
  @media (max-width: 768px) {
    min-height: 450px;
    max-height: 600px;
  }
  
  @media (max-width: 480px) {
    min-height: 400px;
    max-height: 550px;
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--primary-gradient);
    border-radius: 16px 16px 0 0;
  }
  
  /* Scrollbar styling */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    border-radius: 3px;
  }
`;

const Message = styled.div`
  margin-bottom: 20px;
  display: flex;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  animation: messageSlideIn 0.3s ease-out;
  
  @keyframes messageSlideIn {
    from {
      opacity: 0;
      transform: translateY(15px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const MessageBubble = styled.div`
  max-width: 85%;
  padding: 16px 20px;
  border-radius: ${props => props.isUser ? '20px 20px 4px 20px' : '20px 20px 20px 4px'};
  background: ${props => {
    if (props.isUser) return 'var(--primary-gradient)';
    if (props.crudOperation) {
      switch(props.crudOperation) {
        case 'CREATE': return 'linear-gradient(135deg, #d4edda, #c3e6cb)';
        case 'READ': return 'linear-gradient(135deg, #d1ecf1, #bee5eb)';
        case 'UPDATE': return 'linear-gradient(135deg, #fff3cd, #ffeaa7)';
        case 'DELETE': return 'linear-gradient(135deg, #f8d7da, #f5c6cb)';
        default: return 'linear-gradient(135deg, #ffffff, #f8f9fa)';
      }
    }
    return 'linear-gradient(135deg, #ffffff, #f8f9fa)';
  }};
  color: ${props => props.isUser ? 'white' : 'var(--text-primary)'};
  box-shadow: ${props => props.isUser ? 
    'var(--shadow-md)' : 
    '0 2px 12px rgba(0,0,0,0.08)'};
  word-wrap: break-word;
  border: ${props => {
    if (props.isUser) return 'none';
    if (props.crudOperation) {
      switch(props.crudOperation) {
        case 'CREATE': return '1px solid #28a745';
        case 'READ': return '1px solid #17a2b8';
        case 'UPDATE': return '1px solid #ffc107';
        case 'DELETE': return '1px solid #dc3545';
        default: return '1px solid rgba(102, 126, 234, 0.1)';
      }
    }
    return '1px solid rgba(102, 126, 234, 0.1)';
  }};
  position: relative;
  font-weight: 400;
  line-height: 1.5;
  white-space: pre-wrap;
  
  &::before {
    content: '';
    position: absolute;
    width: 0;
    height: 0;
    border-style: solid;
    ${props => props.isUser ? `
      bottom: 0;
      right: -8px;
      border-left: 8px solid transparent;
      border-top: 8px solid var(--primary-color);
    ` : `
      bottom: 0;
      left: -8px;
      border-right: 8px solid transparent;
      border-top: 8px solid white;
    `}
  }
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: ${props => props.isUser ? 
      'var(--shadow-lg)' : 
      '0 4px 20px rgba(0,0,0,0.12)'};
  }
`;

const CrudOperationBadge = styled.div`
  position: absolute;
  top: -8px;
  right: -8px;
  background: ${props => {
    switch(props.operation) {
      case 'CREATE': return '#28a745';
      case 'READ': return '#17a2b8';
      case 'UPDATE': return '#ffc107';
      case 'DELETE': return '#dc3545';
      default: return '#6c757d';
    }
  }};
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
`;

const MessageTime = styled.div`
  font-size: 0.75rem;
  color: ${props => props.isUser ? 'rgba(255,255,255,0.8)' : 'var(--text-secondary)'};
  margin-top: 8px;
  font-weight: 400;
  text-align: ${props => props.isUser ? 'right' : 'left'};
`;

const MessageAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${props => props.isUser ? 
    'var(--primary-gradient)' : 
    'linear-gradient(135deg, #f093fb, #f5576c)'};
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: 600;
  margin: ${props => props.isUser ? '0 0 0 12px' : '0 12px 0 0'};
  box-shadow: var(--shadow-sm);
  flex-shrink: 0;
`;

const MessageWithAvatar = styled.div`
  display: flex;
  align-items: flex-end;
  flex-direction: ${props => props.isUser ? 'row-reverse' : 'row'};
  max-width: 100%;
`;

const TypingIndicator = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-out;
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
`;

const TypingBubble = styled.div`
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  border: 1px solid rgba(139, 92, 246, 0.1);
  border-radius: 20px 20px 20px 4px;
  padding: 16px 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  
  .typing-dots {
    display: flex;
    gap: 4px;
    
    .dot {
      width: 8px;
      height: 8px;
      background: var(--primary-color);
      border-radius: 50%;
      animation: typingBounce 1.4s infinite ease-in-out;
      
      &:nth-child(1) { animation-delay: -0.32s; }
      &:nth-child(2) { animation-delay: -0.16s; }
      &:nth-child(3) { animation-delay: 0s; }
    }
  }
  
  @keyframes typingBounce {
    0%, 80%, 100% { 
      transform: scale(0.8);
      opacity: 0.5;
    }
    40% { 
      transform: scale(1);
      opacity: 1;
    }
  }
`;

const InputContainer = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
  position: relative;
`;

const InputWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const Input = styled.input`
  width: 100%;
  padding: 16px 20px;
  padding-right: 50px;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: var(--transition-smooth);
  background: linear-gradient(135deg, #ffffff, #f8f9fa);
  color: var(--text-primary);
  
  &:focus {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    background: white;
  }
  
  &:disabled {
    background: #f8f9fa;
    cursor: not-allowed;
    opacity: 0.7;
  }
  
  &::placeholder {
    color: var(--text-secondary);
    font-style: italic;
  }
`;

const InputIcon = styled.div`
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 1.1rem;
  transition: var(--transition-fast);
  
  ${Input}:focus + & {
    color: var(--primary-color);
  }
`;

const SendButton = styled.button`
  background: var(--primary-gradient);
  color: white;
  border: none;
  padding: 16px 24px;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: var(--transition-smooth);
  min-width: 120px;
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
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  &:hover:not(:disabled)::before {
    left: 100%;
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    background: #d1d5db;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const StatusIndicator = styled.div`
  position: absolute;
  bottom: 8px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: ${props => props.isOnline ? '#10b981' : '#ef4444'};
    animation: ${props => props.isOnline ? 'pulse 2s infinite' : 'none'};
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
`;

const PlaceholderMessage = styled.div`
  text-align: center;
  color: var(--text-secondary);
  padding: 40px 20px;
  
  .placeholder-icon {
    font-size: 3rem;
    margin-bottom: 16px;
    display: block;
  }
  
  .placeholder-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-primary);
  }
  
  .placeholder-subtitle {
    font-size: 0.95rem;
    margin-bottom: 20px;
  }
  
  .placeholder-commands {
    text-align: left;
    max-width: 400px;
    margin: 0 auto;
    
    .command {
      background: linear-gradient(135deg, #f8f9fa, #ffffff);
      border: 1px solid rgba(139, 92, 246, 0.1);
      border-radius: 8px;
      padding: 10px 15px;
      margin: 8px 0;
      font-size: 0.85rem;
      color: var(--text-primary);
      font-family: 'Segoe UI', monospace;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
  }
`;

function ChatInterface({ cvUploaded, onCVUpdate }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdateCheck, setLastUpdateCheck] = useState(Date.now());
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  useEffect(() => {
    if (cvUploaded) {
      loadChatHistory();
    }
  }, [cvUploaded]);

  const loadChatHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/chat/history/`);
      const chatHistory = response.data || [];
      
      const formattedMessages = chatHistory.map(msg => ({
        id: msg.id,
        text: msg.message,
        sender: msg.type === 'user' ? 'user' : 'ai',
        timestamp: new Date(msg.timestamp)
      }));
      
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const detectCrudOperation = (userMessage, aiResponse) => {
    const msg = userMessage.toLowerCase();
    const response = aiResponse.toLowerCase();
    
    // CREATE operations
    if (msg.includes('i learned') || msg.includes('i worked') || msg.includes('i studied') || 
        msg.includes('i built') || msg.includes('add') || msg.includes('my email is') ||
        response.includes('successfully added') || response.includes('created')) {
      return 'CREATE';
    }
    
    // DELETE operations  
    if (msg.includes('remove') || msg.includes('delete') || msg.includes("don't have") ||
        response.includes('removed') || response.includes('deleted')) {
      return 'DELETE';
    }
    
    // UPDATE operations
    if (msg.includes('update') || msg.includes('change') || msg.includes('modify') ||
        response.includes('updated') || response.includes('modified')) {
      return 'UPDATE';
    }
    
    // READ operations
    if (msg.includes('show') || msg.includes('what') || msg.includes('my skills') ||
        msg.includes('my experience') || msg.includes('display') || msg.includes('list') ||
        response.includes('your skills') || response.includes('your experience')) {
      return 'READ';
    }
    
    return null;
  };

  const handleSendMessage = async (messageText = null) => {
    const userMessage = messageText || inputValue.trim();
    if (!userMessage || isLoading) return;

    if (!messageText) {
      setInputValue('');
    }
    setIsLoading(true);

    // Add user message to UI
    const userMsgObj = {
      id: Date.now(),
      text: userMessage,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsgObj]);

    try {
      // Send message to backend chat endpoint
      const response = await axios.post(`${API_BASE_URL}/chat/`, {
        message: userMessage
      });

      const aiResponse = response.data.response || 'Sorry, I encountered an error processing your request.';
      
      // Detect CRUD operation for visual feedback
      const crudOperation = detectCrudOperation(userMessage, aiResponse);

      // Add AI response to UI with CRUD operation indicator
      const aiMsgObj = {
        id: Date.now() + 1,
        text: aiResponse,
        sender: 'ai',
        timestamp: new Date(),
        crudOperation: crudOperation
      };
      setMessages(prev => [...prev, aiMsgObj]);

      // Trigger CV refresh if the response indicates CV updates (enhanced detection)
      const cvUpdateKeywords = [
        'updated', 'generated', 'enhanced', 'added', 'included', 'saved', 
        'recorded', 'noted', 'successfully', 'cv', 'section', 'skill', 
        'experience', 'education', 'project', 'automatically updated', 'removed', 'deleted'
      ];
      
      const shouldRefresh = cvUpdateKeywords.some(keyword => 
        aiResponse.toLowerCase().includes(keyword.toLowerCase())
      ) || userMessage.toLowerCase().includes('learn') || 
          userMessage.toLowerCase().includes('work') ||
          userMessage.toLowerCase().includes('skill') ||
          userMessage.toLowerCase().includes('experience') ||
          userMessage.toLowerCase().includes('degree') ||
          userMessage.toLowerCase().includes('certification') ||
          userMessage.toLowerCase().includes('remove') ||
          userMessage.toLowerCase().includes('delete') ||
          userMessage.toLowerCase().includes('update') ||
          crudOperation === 'CREATE' || crudOperation === 'UPDATE' || crudOperation === 'DELETE';
      
      if (shouldRefresh && onCVUpdate) {
        console.log(`🔄 Triggering CV refresh due to ${crudOperation || 'detected'} operation`);
        onCVUpdate(true);
        setLastUpdateCheck(Date.now());
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMsgObj = {
        id: Date.now() + 1,
        text: error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsgObj]);
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const quickActions = [
    { text: '📖 Show Skills', message: 'show my skills' },
    { text: '💼 Show Experience', message: 'show my experience' },
    { text: '🎓 Show Education', message: 'show my education' },
    { text: '🚀 Show Projects', message: 'show my projects' },
    { text: '✨ Add Skills', message: 'I learned Docker and Kubernetes' },
    { text: '💼 Add Experience', message: 'I worked as Senior Developer at TechCorp' },
    { text: '🎓 Add Education', message: 'I studied Computer Science at MIT' },
    { text: '🚀 Add Project', message: 'I built a React e-commerce app' },
    { text: '✏️ Add More Skills', message: 'I also know TypeScript and GraphQL' },
    { text: '🗑️ Remove Skill', message: 'remove JavaScript skill' },
    { text: '📋 Generate CV', message: 'generate cv' },
    { text: '❓ Help', message: 'help' }
  ];

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleManualCVRefresh = () => {
    console.log('🔄 Manual CV refresh triggered by user');
    if (onCVUpdate) {
      onCVUpdate(true);
      setLastUpdateCheck(Date.now());
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <ChatContainer>
      <Title>
        <span className="icon">💬</span>
        AI CV Assistant
      </Title>
      
      {cvUploaded && (
        <>
          <GenerateCVButton 
            onClick={() => handleSendMessage('generate cv')}
            disabled={isLoading}
          >
            <div className="button-content">
              <span className="icon">{isLoading ? '⏳' : '📄'}</span>
              {isLoading ? 'Generating CV...' : 'Generate Updated CV'}
            </div>
          </GenerateCVButton>
          
          <QuickActionsContainer>
            <RefreshCVButton
              onClick={handleManualCVRefresh}
              disabled={isLoading}
              title="Refresh CV display to show latest updates"
            >
              <div className="button-content">
                🔄 Refresh CV
              </div>
            </RefreshCVButton>
            {quickActions.map((action, index) => (
              <QuickActionButton
                key={index}
                onClick={() => handleSendMessage(action.message)}
                disabled={isLoading}
              >
                <div className="button-content">
                  {action.text}
                </div>
              </QuickActionButton>
            ))}
          </QuickActionsContainer>
        </>
      )}
      
      <MessagesContainer>
        {!cvUploaded ? (
          <PlaceholderMessage>
            <span className="placeholder-icon">📤</span>
            <div className="placeholder-title">Upload Required</div>
            <div className="placeholder-subtitle">Upload your CV first to start chatting!</div>
          </PlaceholderMessage>
        ) : messages.length === 0 ? (
          <PlaceholderMessage>
            <span className="placeholder-icon">🤖</span>
            <div className="placeholder-title">AI CV Assistant Ready!</div>
            <div className="placeholder-subtitle">I have full access to your CV and can help you with:</div>
            <div className="placeholder-commands">
              <div className="command">🚀 "I built a React app using FastAPI"</div>
              <div className="command">📂 "What experience do I have?"</div>
              <div className="command">🛠️ "What skills do I have?"</div>
              <div className="command">💡 "I learned Python and Docker"</div>
              <div className="command">📄 "Generate CV"</div>
              <div className="command">✏️ "Update my experience section"</div>
            </div>
          </PlaceholderMessage>
        ) : (
          <>
            {messages.map(message => (
              <Message key={message.id} isUser={message.sender === 'user'}>
                <MessageWithAvatar isUser={message.sender === 'user'}>
                  <MessageAvatar isUser={message.sender === 'user'}>
                    {message.sender === 'user' ? '👤' : '🤖'}
                  </MessageAvatar>
                  <div style={{position: 'relative'}}>
                    <MessageBubble 
                      isUser={message.sender === 'user'}
                      crudOperation={message.crudOperation}
                    >
                      {message.text}
                      {message.crudOperation && !message.isUser && (
                        <CrudOperationBadge operation={message.crudOperation}>
                          {message.crudOperation}
                        </CrudOperationBadge>
                      )}
                    </MessageBubble>
                    <MessageTime isUser={message.sender === 'user'}>
                      {formatTime(message.timestamp)}
                      {message.crudOperation && !message.isUser && (
                        <span style={{marginLeft: '8px', fontSize: '0.65rem', opacity: 0.7}}>
                          {message.crudOperation === 'CREATE' && '✨ Added'}
                          {message.crudOperation === 'READ' && '📖 Displayed'}
                          {message.crudOperation === 'UPDATE' && '✏️ Modified'}
                          {message.crudOperation === 'DELETE' && '🗑️ Removed'}
                        </span>
                      )}
                    </MessageTime>
                  </div>
                </MessageWithAvatar>
              </Message>
            ))}
            
            {isLoading && (
              <TypingIndicator>
                <MessageAvatar isUser={false}>🤖</MessageAvatar>
                <TypingBubble>
                  <div className="typing-dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                </TypingBubble>
              </TypingIndicator>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
        
        <StatusIndicator isOnline={cvUploaded && !isLoading}>
          <span className="status-dot"></span>
          {cvUploaded ? (isLoading ? 'Processing...' : 'Ready') : 'Offline'}
        </StatusIndicator>
      </MessagesContainer>
      
      <InputContainer>
        <InputWrapper>
          <Input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your CV, add new information, or say 'generate CV'..."
            disabled={!cvUploaded || isLoading}
          />
          <InputIcon>💭</InputIcon>
        </InputWrapper>
        <SendButton
          onClick={() => handleSendMessage()}
          disabled={!cvUploaded || !inputValue.trim() || isLoading}
        >
          <div className="button-content">
            {isLoading ? '⏳' : '🚀'}
            {isLoading ? 'Sending...' : 'Send'}
          </div>
        </SendButton>
      </InputContainer>
    </ChatContainer>
  );
}

export default ChatInterface; 