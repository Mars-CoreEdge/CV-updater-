import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 550px;
  position: relative;
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
  display: flex;
  gap: 8px;
  margin-bottom: 15px;
  flex-wrap: wrap;
`;

const QuickActionButton = styled.button`
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 120px;
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
    transition: left 0.5s ease;
  }
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
    border-color: rgba(102, 126, 234, 0.5);
    transform: translateY(-2px);
  }
  
  &:hover:not(:disabled)::before {
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
  }
`;

const GenerateCVButton = styled.button`
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
  margin-bottom: 15px;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
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
    transition: left 0.5s ease;
  }
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #218838, #1ea384);
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
  }
  
  &:hover:not(:disabled)::before {
    left: 100%;
  }
  
  &:active {
    transform: translateY(-1px);
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
  
  .icon {
    font-size: 1.1rem;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border-radius: 16px;
  margin-bottom: 20px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  position: relative;
  
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
  background: ${props => props.isUser ? 
    'var(--primary-gradient)' : 
    'linear-gradient(135deg, #ffffff, #f8f9fa)'};
  color: ${props => props.isUser ? 'white' : 'var(--text-primary)'};
  box-shadow: ${props => props.isUser ? 
    'var(--shadow-md)' : 
    '0 2px 12px rgba(0,0,0,0.08)'};
  word-wrap: break-word;
  border: ${props => props.isUser ? 'none' : '1px solid rgba(102, 126, 234, 0.1)'};
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
  border: 1px solid rgba(102, 126, 234, 0.1);
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

const PlaceholderMessage = styled.div`
  text-align: center;
  color: var(--text-secondary);
  font-style: italic;
  padding: 40px 30px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.03), rgba(118, 75, 162, 0.03));
  border-radius: 12px;
  border: 2px dashed rgba(102, 126, 234, 0.2);
  
  .placeholder-icon {
    font-size: 3rem;
    margin-bottom: 15px;
    display: block;
    opacity: 0.5;
  }
  
  .placeholder-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-primary);
  }
  
  .placeholder-subtitle {
    font-size: 0.9rem;
    margin-bottom: 15px;
    opacity: 0.8;
  }
  
  .placeholder-commands {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-align: left;
    max-width: 300px;
    margin: 0 auto;
    
    .command {
      margin: 5px 0;
      padding: 3px 0;
      border-left: 2px solid var(--primary-color);
      padding-left: 8px;
    }
  }
`;

const StatusIndicator = styled.div`
  position: absolute;
  bottom: -8px;
  right: 20px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 4px 12px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  border: 1px solid rgba(102, 126, 234, 0.1);
  animation: fadeInUp 0.3s ease-out;
  
  .status-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    background: ${props => props.isOnline ? '#2ecc71' : '#95a5a6'};
    border-radius: 50%;
    margin-right: 6px;
    animation: ${props => props.isOnline ? 'pulse 2s infinite' : 'none'};
  }
`;

function ChatInterface({ cvUploaded, onChatUpdate }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isGeneratingCV, setIsGeneratingCV] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const sendMessage = async (messageText = null) => {
    const textToSend = messageText || inputValue;
    if (!textToSend.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: textToSend,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      // Add a small delay for better UX
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const response = await axios.post('http://localhost:8000/chat/', {
        message: textToSend
      });

      setIsTyping(false);

      const botMessage = {
        id: Date.now() + 1,
        text: response.data.response,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
      onChatUpdate();
    } catch (error) {
      setIsTyping(false);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, I encountered an error. Please try again.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateCV = async () => {
    setIsGeneratingCV(true);
    try {
      const response = await axios.post('http://localhost:8000/cv/generate');
      
      const successMessage = {
        id: Date.now(),
        text: '✅ CV generated successfully with all your projects! Check the CV panel to see the updated version.',
        isUser: false,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, successMessage]);
      onChatUpdate();
    } catch (error) {
      const errorMessage = {
        id: Date.now(),
        text: '❌ Failed to generate CV. Please try again.',
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsGeneratingCV(false);
    }
  };

  const quickActions = [
    { text: '📂 Show projects', message: 'show my projects' },
    { text: '🚀 Add project', message: 'I built a new project' },
    { text: '💡 Add skill', message: 'I learned a new skill' },
    { text: '💼 Add experience', message: 'I worked on' }
  ];

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <ChatContainer>
      <Title>
        <span className="icon">💬</span>
        AI Project Manager
      </Title>
      
      {cvUploaded && (
        <>
          <GenerateCVButton 
            onClick={generateCV} 
            disabled={isGeneratingCV || isLoading}
          >
            <div className="button-content">
              <span className="icon">{isGeneratingCV ? '⏳' : '📄'}</span>
              {isGeneratingCV ? 'Generating CV...' : 'Generate Updated CV'}
            </div>
          </GenerateCVButton>
          
          <QuickActionsContainer>
            {quickActions.map((action, index) => (
              <QuickActionButton
                key={index}
                onClick={() => sendMessage(action.message)}
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
            <div className="placeholder-title">AI Project Manager Ready!</div>
            <div className="placeholder-subtitle">Try these commands:</div>
            <div className="placeholder-commands">
              <div className="command">🚀 "I built a React app using FastAPI"</div>
              <div className="command">📂 "Show my projects"</div>
              <div className="command">🗑️ "Delete project 1"</div>
              <div className="command">💡 "I learned Python and Docker"</div>
              <div className="command">📄 "Generate CV"</div>
            </div>
          </PlaceholderMessage>
        ) : (
          <>
            {messages.map(message => (
              <Message key={message.id} isUser={message.isUser}>
                <MessageWithAvatar isUser={message.isUser}>
                  <MessageAvatar isUser={message.isUser}>
                    {message.isUser ? '👤' : '🤖'}
                  </MessageAvatar>
                  <div>
                    <MessageBubble isUser={message.isUser}>
                      {message.text}
                    </MessageBubble>
                    <MessageTime isUser={message.isUser}>
                      {formatTime(message.timestamp)}
                    </MessageTime>
                  </div>
                </MessageWithAvatar>
              </Message>
            ))}
            
            {isTyping && (
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
            placeholder="Tell me about projects, skills, or say 'generate CV'..."
            disabled={!cvUploaded || isLoading}
          />
          <InputIcon>💭</InputIcon>
        </InputWrapper>
        <SendButton
          onClick={() => sendMessage()}
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