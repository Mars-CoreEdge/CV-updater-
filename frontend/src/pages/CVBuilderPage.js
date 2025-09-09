import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const PageContainer = styled.div`
  min-height: 100vh;
  background: radial-gradient(1200px 600px at -10% -10%, #eef2ff 0%, transparent 60%),
              radial-gradient(1000px 500px at 110% 10%, #fae8ff 0%, transparent 60%),
              linear-gradient(180deg, #f8fafc 0%, #eef2f7 60%, #e6eef5 100%);
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  position: relative;
  overflow-x: hidden;
  color: #0f172a;
`;

const TopNavBar = styled.nav`
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid #e2e8f0;
  padding: 0 24px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.06);
  backdrop-filter: saturate(140%) blur(6px);
`;

const NavLeft = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const BackButton = styled.button`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 10px 16px;
  color: #475569;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    background: #f1f5f9;
    border-color: #cbd5e0;
    color: #334155;
  }

  .arrow {
    font-size: 1rem;
  }
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  
  .icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.2rem;
    font-weight: 700;
  }
  
  .text {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1e293b;
  }
`;

const NavRight = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const SaveIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  color: #64748b;
  
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
  }
`;

const MainContainer = styled.div`
  display: flex;
  height: calc(100vh - 70px);
  background: transparent;
`;

const Sidebar = styled.div`
  width: 280px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  box-shadow: 8px 0 24px rgba(15, 23, 42, 0.04);
  
  @media (max-width: 1024px) {
    display: none;
  }
`;

const SidebarHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid #f1f5f9;
  
  h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 8px 0;
  }
  
  p {
    font-size: 0.85rem;
    color: #64748b;
    margin: 0;
    line-height: 1.4;
  }
`;

const StepsContainer = styled.div`
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
`;

const ProgressSection = styled.div`
  padding: 16px 24px 24px;
  border-bottom: 1px solid #f1f5f9;
  background: transparent;
`;

const ProgressLabel = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  span {
    font-size: 0.85rem;
    font-weight: 600;
    color: #475569;
  }
  
  .progress-text {
    font-size: 0.8rem;
    color: #64748b;
  }
`;

const ProgressBar = styled.div`
  background: #f1f5f9;
  border-radius: 10px;
  height: 8px;
  overflow: hidden;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    width: ${props => ((props.currentStep + 1) / props.totalSteps) * 100}%;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: inherit;
    transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  }
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ContentHeader = styled.div`
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  border-bottom: 1px solid #e2e8f0;
  padding: 24px 32px;
  box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
  
  h1 {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 8px 0;
    line-height: 1.2;
  }
  
  p {
    font-size: 1rem;
    color: #64748b;
    margin: 0;
    line-height: 1.5;
  }
`;

const ContentBody = styled.div`
  flex: 1;
  display: grid;
  grid-template-columns: 1.1fr 420px;
  gap: 20px;
  overflow: hidden;
  
  @media (max-width: 1400px) {
    grid-template-columns: 1fr 360px;
  }
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const FormSection = styled.div`
  background: #ffffff;
  overflow-y: auto;
  padding: 36px;
  border-right: 1px solid #eef2f7;
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f8fafc;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
  }
`;

const PreviewSection = styled.div`
  background: #f8fafc;
  border-left: 1px solid #e2e8f0;
  overflow-y: auto;
  padding: 32px 24px;
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: #f1f5f9;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 3px;
  }
`;

const StepItem = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  border-radius: 16px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: background 0.25s ease, border-color 0.25s ease, transform 0.15s ease, box-shadow 0.25s ease;
  color: ${props => props.active ? '#0f172a' : '#475569'};
  background: ${props => props.active ? 'rgba(255,255,255,0.98)' : 'rgba(255,255,255,0.8)'};
  border: 1px solid ${props => props.active ? '#e2e8f0' : '#eef2f7'};
  position: relative;
  overflow: hidden;
  box-shadow: ${props => props.active ? '0 8px 24px rgba(15, 23, 42, 0.08)' : '0 2px 8px rgba(15, 23, 42, 0.04)'};
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.08));
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  
  &:hover::before {
    opacity: ${props => props.active ? 0.05 : 1};
  }
  
  &:hover {
    background: ${props => props.active ? 'rgba(255,255,255,0.98)' : 'rgba(255,255,255,0.9)'};
    transform: translateX(3px);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12);
  }
  
  .step-number {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: ${props => 
      props.completed ? 'linear-gradient(135deg, #4CAF50, #45a049)' : 
      props.active ? 'linear-gradient(135deg, #667eea, #764ba2)' : 
      'rgba(255, 255, 255, 0.25)'};
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.95rem;
    position: relative;
    z-index: 2;
    box-shadow: ${props => 
      props.active || props.completed ? '0 4px 15px rgba(0, 0, 0, 0.2)' : 'none'};
    transition: all 0.3s ease;
  }
  
  .step-label {
    font-weight: 600;
    font-size: 0.95rem;
    position: relative;
    z-index: 2;
    letter-spacing: 0.01em;
  }
`;

const FormGroup = styled.div`
  margin-bottom: 24px;
  position: relative;
`;

const Label = styled.label`
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  letter-spacing: 0.01em;
  position: relative;
  
  &::after {
    content: ${props => props.required ? '"*"' : '""'};
    color: #ef4444;
    margin-left: 4px;
    font-weight: 700;
  }
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.925rem;
  font-weight: 400;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
  background: white;
  color: #1f2937;
  
  &::placeholder {
    color: #9ca3af;
    font-weight: 400;
  }
  
  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  &:hover:not(:focus) {
    border-color: #9ca3af;
  }
  
  &:disabled {
    background-color: #f9fafb;
    cursor: not-allowed;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.925rem;
  font-weight: 400;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
  background: white;
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
  line-height: 1.5;
  color: #1f2937;
  
  &::placeholder {
    color: #9ca3af;
    font-weight: 400;
  }
  
  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  &:hover:not(:focus) {
    border-color: #9ca3af;
  }
`;

const TagInput = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 16px 20px;
  border: 2px solid #e2e8f0;
  border-radius: 14px;
  background: white;
  min-height: 60px;
  align-items: center;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
  position: relative;
  z-index: 2;
  
  &:focus-within {
    border-color: #667eea;
    box-shadow: 
      0 0 0 4px rgba(102, 126, 234, 0.1),
      0 4px 12px rgba(0, 0, 0, 0.05);
    transform: translateY(-1px);
  }
  
  &:hover:not(:focus-within) {
    border-color: #cbd5e0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }
`;

const Tag = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 8px 14px;
  border-radius: 24px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
  
  .remove {
    cursor: pointer;
    font-weight: 700;
    padding: 4px 6px;
    border-radius: 50%;
    transition: background 0.15s ease, transform 0.15s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    font-size: 14px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.25);
      transform: scale(1.1);
    }
  }
`;

const TagInputField = styled.input`
  border: none;
  outline: none;
  flex: 1;
  min-width: 140px;
  padding: 10px 0;
  font-size: 1rem;
  font-weight: 500;
  color: #2d3748;
  
  &::placeholder {
    color: #a0aec0;
    font-weight: 400;
  }
`;

const Button = styled.button`
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 0.925rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease, opacity 0.2s ease;
  position: relative;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  letter-spacing: 0.01em;
  
  &:hover:not(:disabled) {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transform: translateY(-1px);
  }
  
  &:active:not(:disabled) {
    transform: translateY(0);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    
    &:hover {
      transform: none;
      background: linear-gradient(135deg, #3b82f6, #1d4ed8);
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 20px;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 1px solid #e2e8f0;
`;

const PreviewCV = styled.div`
  font-family: 'Inter', 'Segoe UI', sans-serif;
  line-height: 1.75;
  color: #1f2937;
  background: #ffffff;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 12px 30px rgba(16, 24, 40, 0.06);
  border: 1px solid #eef2f7;
  position: relative;

  /* Canva-style top accent */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 16px 16px 0 0;
  }
  
  /* Name heading */
  h1 {
    font-size: 2.2rem;
    color: #0f172a;
    margin: 8px 0 16px 0;
    font-weight: 800;
    letter-spacing: 0.02em;
    text-align: left;
  }
  
  /* Contact pill */
  .contact-info {
    text-align: left;
    margin-bottom: 26px;
    padding: 14px 16px;
    background: #f8fafc;
    border: 1px solid #e6edf5;
    border-radius: 12px;
    font-size: 0.96rem;
    color: #475569;
    font-weight: 500;
  }
  
  /* Section header chip */
  h2 {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: 0.95rem;
    font-weight: 800;
    color: #111827;
    margin: 18px 0 14px 0;
    padding: 10px 14px;
    border-radius: 999px;
    background: linear-gradient(180deg, rgba(99,102,241,0.12), rgba(139,92,246,0.08));
    border: 1px solid rgba(99,102,241,0.28);
    letter-spacing: 0.16em;
    text-transform: uppercase;
  }
  
  .section-content {
    margin-bottom: 20px;
  }
  
  /* Professional cards */
  .experience-item, .education-item, .project-item {
    margin-bottom: 18px;
    padding: 12px 14px;
    border-left: 4px solid #6366f1;
    background: #fbfdff;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
  }
  
  .item-title {
    font-weight: 700;
    color: #111827;
    font-size: 1rem;
    margin-bottom: 4px;
  }
  
  .item-subtitle {
    color: #64748b;
    font-style: italic;
    font-size: 0.9rem;
    margin-bottom: 8px;
  }
  
  /* Skills as chips */
  .skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
  }
  
  .skill-tag {
    background: linear-gradient(135deg, #f7fafc, #edf2f7);
    border: 1px solid #e2e8f0;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 0.85rem;
    color: #475569;
    font-weight: 600;
  }
`;

const AddButton = styled.button`
  background: #f8fafc;
  border: 2px dashed #cbd5e0;
  color: #64748b;
  padding: 16px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  &:hover {
    background: #3b82f6;
    color: white;
    border-color: #3b82f6;
    border-style: solid;
    transform: translateY(-1px);
  }
  
  &::before {
    content: '+';
    font-size: 1.1rem;
    font-weight: 700;
  }
`;

const RemoveButton = styled.button`
  background: linear-gradient(135deg, #e53e3e, #c53030);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: background 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 12px rgba(229, 62, 62, 0.3);
  
  &:hover {
    background: linear-gradient(135deg, #c53030, #9c2828);
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(229, 62, 62, 0.4);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const ItemCard = styled.div`
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
  position: relative;
  
  &:hover {
    border-color: #d1d5db;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  }
`;

const ItemHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
  
  h4 {
    color: #1a202c;
    font-size: 1.1rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.01em;
  }
`;

const StepNumber = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  margin-right: 12px;
  flex-shrink: 0;
  
  background: ${props => props.active 
    ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
    : props.completed 
      ? 'linear-gradient(135deg, #22c55e, #16a34a)'
      : '#e2e8f0'
  };
  
  color: ${props => (props.active || props.completed) ? 'white' : '#64748b'};
  
  transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
  
  &::after {
    content: '${props => props.completed ? '✓' : props.number}';
    font-size: ${props => props.completed ? '0.9rem' : '0.8rem'};
  }
`;

const StepContent = styled.div`
  flex: 1;
  
  .step-title {
    color: ${props => props.active ? '#0f172a' : '#475569'};
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 2px;
    transition: color 0.2s ease;
  }
  
  .step-description {
    color: ${props => props.active ? '#64748b' : '#94a3b8'};
    font-size: 0.75rem;
    line-height: 1.3;
    transition: color 0.2s ease;
  }
`;

const SectionTitle = styled.h2`
  font-size: 1.3rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: -0.01em;
  border-bottom: 1px solid #eef2f7;
  padding-bottom: 12px;
`;

function CVBuilderPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [isSaving, setIsSaving] = useState(false);

  const steps = [
    { 
      id: 0, 
      label: 'Personal Information', 
      icon: '👤',
      description: 'Basic contact details',
      fullDescription: 'Enter your basic contact information including name, email, phone, and address.'
    },
    { 
      id: 1, 
      label: 'Profile Summary', 
      icon: '📝',
      description: 'Professional overview',
      fullDescription: 'Write a compelling professional summary that highlights your key strengths and career objectives.'
    },
    { 
      id: 2, 
      label: 'Skills', 
      icon: '🛠️',
      description: 'Technical & soft skills',
      fullDescription: 'Add your technical skills and professional competencies to showcase your expertise.'
    },
    { 
      id: 3, 
      label: 'Work Experience', 
      icon: '💼',
      description: 'Professional history',
      fullDescription: 'Detail your work experience including job titles, companies, and key achievements.'
    },
    { 
      id: 4, 
      label: 'Education', 
      icon: '🎓',
      description: 'Academic background',
      fullDescription: 'Add your educational qualifications, degrees, and academic achievements.'
    },
    { 
      id: 5, 
      label: 'Projects', 
      icon: '🚀',
      description: 'Portfolio showcase',
      fullDescription: 'Showcase your key projects with descriptions, technologies used, and achievements.'
    },
    { 
      id: 6, 
      label: 'Review & Save', 
      icon: '✅',
      description: 'Final review',
      fullDescription: 'Review your complete CV and save it to start using our AI enhancement features.'
    }
  ];

  const [cvData, setCvData] = useState({
    personalInfo: {
      fullName: '',
      email: '',
      phone: '',
      address: '',
      linkedin: '',
      website: ''
    },
    profileSummary: '',
    skills: {
      technical: [],
      professional: []
    },
    experience: [],
    education: [],
    projects: []
  });

  const [tempInputs, setTempInputs] = useState({
    technicalSkill: '',
    professionalSkill: ''
  });

  const updateCvData = (section, data) => {
    setCvData(prev => ({
      ...prev,
      [section]: data
    }));
  };

  const addSkill = (type, skill) => {
    if (skill.trim()) {
      // Handle comma-separated skills
      const skills = skill.split(',').map(s => s.trim()).filter(s => s);
      
      setCvData(prev => ({
        ...prev,
        skills: {
          ...prev.skills,
          [type]: [...prev.skills[type], ...skills]
        }
      }));
      setTempInputs(prev => ({
        ...prev,
        [`${type}Skill`]: ''
      }));
    }
  };

  const removeSkill = (type, index) => {
    setCvData(prev => ({
      ...prev,
      skills: {
        ...prev.skills,
        [type]: prev.skills[type].filter((_, i) => i !== index)
      }
    }));
  };

  const addExperience = () => {
    setCvData(prev => ({
      ...prev,
      experience: [...prev.experience, {
        jobTitle: '',
        company: '',
        duration: '',
        description: '',
        achievements: []
      }]
    }));
  };

  const updateExperience = (index, field, value) => {
    setCvData(prev => ({
      ...prev,
      experience: prev.experience.map((exp, i) => 
        i === index ? { ...exp, [field]: value } : exp
      )
    }));
  };

  const removeExperience = (index) => {
    setCvData(prev => ({
      ...prev,
      experience: prev.experience.filter((_, i) => i !== index)
    }));
  };

  const addEducation = () => {
    setCvData(prev => ({
      ...prev,
      education: [...prev.education, {
        degree: '',
        institution: '',
        year: '',
        grade: ''
      }]
    }));
  };

  const updateEducation = (index, field, value) => {
    setCvData(prev => ({
      ...prev,
      education: prev.education.map((edu, i) => 
        i === index ? { ...edu, [field]: value } : edu
      )
    }));
  };

  const removeEducation = (index) => {
    setCvData(prev => ({
      ...prev,
      education: prev.education.filter((_, i) => i !== index)
    }));
  };

  const addProject = () => {
    setCvData(prev => ({
      ...prev,
      projects: [...prev.projects, {
        title: '',
        description: '',
        duration: '',
        technologies: [],
        highlights: []
      }]
    }));
  };

  const updateProject = (index, field, value) => {
    setCvData(prev => ({
      ...prev,
      projects: prev.projects.map((proj, i) => 
        i === index ? { ...proj, [field]: value } : proj
      )
    }));
  };

  const removeProject = (index) => {
    setCvData(prev => ({
      ...prev,
      projects: prev.projects.filter((_, i) => i !== index)
    }));
  };

  const handleStepChange = (stepIndex) => {
    setCurrentStep(stepIndex);
    if (stepIndex < currentStep) {
      setCompletedSteps(prev => new Set([...prev, currentStep]));
    }
  };

  const nextStep = () => {
    setCompletedSteps(prev => new Set([...prev, currentStep]));
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };



  const saveCV = async () => {
    setIsSaving(true);
    try {
      // Send structured data to the backend
      const response = await axios.post('http://localhost:8081/cv/create-from-builder', {
        personal_info: cvData.personalInfo,
        profile_summary: cvData.profileSummary,
        skills: cvData.skills,
        experience: cvData.experience,
        education: cvData.education,
        projects: cvData.projects
      });
      
      if (response.status === 200) {
        alert('CV created successfully! Redirecting to CV Management...');
        navigate('/cv-management');
      }
    } catch (error) {
      console.error('Error saving CV:', error);
      alert(`Error creating CV: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // Personal Info
        return (
          <div>
            <SectionTitle>👤 Personal Information</SectionTitle>
            <FormGroup>
              <Label>Full Name *</Label>
              <Input
                type="text"
                value={cvData.personalInfo.fullName}
                onChange={(e) => updateCvData('personalInfo', { ...cvData.personalInfo, fullName: e.target.value })}
                placeholder="John Doe"
                required
              />
            </FormGroup>
            <FormGroup>
              <Label>Email *</Label>
              <Input
                type="email"
                value={cvData.personalInfo.email}
                onChange={(e) => updateCvData('personalInfo', { ...cvData.personalInfo, email: e.target.value })}
                placeholder="john.doe@email.com"
                required
              />
            </FormGroup>
            <FormGroup>
              <Label>Phone *</Label>
              <Input
                type="tel"
                value={cvData.personalInfo.phone}
                onChange={(e) => updateCvData('personalInfo', { ...cvData.personalInfo, phone: e.target.value })}
                placeholder="+1-234-567-8900"
                required
              />
            </FormGroup>
            <FormGroup>
              <Label>Address</Label>
              <Input
                type="text"
                value={cvData.personalInfo.address}
                onChange={(e) => updateCvData('personalInfo', { ...cvData.personalInfo, address: e.target.value })}
                placeholder="City, State, Country"
              />
            </FormGroup>
            <FormGroup>
              <Label>LinkedIn Profile</Label>
              <Input
                type="url"
                value={cvData.personalInfo.linkedin}
                onChange={(e) => updateCvData('personalInfo', { ...cvData.personalInfo, linkedin: e.target.value })}
                placeholder="https://linkedin.com/in/johndoe"
              />
            </FormGroup>
            <FormGroup>
              <Label>Website/Portfolio</Label>
              <Input
                type="url"
                value={cvData.personalInfo.website}
                onChange={(e) => updateCvData('personalInfo', { ...cvData.personalInfo, website: e.target.value })}
                placeholder="https://johndoe.com"
              />
            </FormGroup>
          </div>
        );

      case 1: // Profile Summary
        return (
          <div>
            <SectionTitle>📝 Profile Summary</SectionTitle>
            <FormGroup>
              <Label>Professional Summary</Label>
              <TextArea
                value={cvData.profileSummary}
                onChange={(e) => updateCvData('profileSummary', e.target.value)}
                onKeyDown={(e) => {
                  // Allow Enter for new lines, Ctrl+Enter to submit
                  if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    // Could add auto-save or other functionality here
                  }
                }}
                placeholder="Write a compelling summary that highlights your key strengths, experience, and career objectives... (Press Enter for new line)"
                rows={6}
              />
            </FormGroup>
          </div>
        );

      case 2: // Skills
        return (
          <div>
            <SectionTitle>🛠️ Skills</SectionTitle>
            <FormGroup>
              <Label>Technical Skills</Label>
              <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: '8px' }}>
                💡 Press Enter to add each skill. Use commas for multiple skills at once.
              </div>
              <TagInput>
                {cvData.skills.technical.map((skill, index) => (
                  <Tag key={index}>
                    {skill}
                    <span className="remove" onClick={() => removeSkill('technical', index)}>×</span>
                  </Tag>
                ))}
                <TagInputField
                  value={tempInputs.technicalSkill}
                  onChange={(e) => setTempInputs(prev => ({ ...prev, technicalSkill: e.target.value }))}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addSkill('technical', tempInputs.technicalSkill);
                    }
                  }}
                  placeholder="Type a skill and press Enter to add..."
                />
              </TagInput>
            </FormGroup>
            <FormGroup>
              <Label>Professional Skills</Label>
              <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: '8px' }}>
                💡 Press Enter to add each skill. Use commas for multiple skills at once.
              </div>
              <TagInput>
                {cvData.skills.professional.map((skill, index) => (
                  <Tag key={index}>
                    {skill}
                    <span className="remove" onClick={() => removeSkill('professional', index)}>×</span>
                  </Tag>
                ))}
                <TagInputField
                  value={tempInputs.professionalSkill}
                  onChange={(e) => setTempInputs(prev => ({ ...prev, professionalSkill: e.target.value }))}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addSkill('professional', tempInputs.professionalSkill);
                    }
                  }}
                  placeholder="Type a skill and press Enter to add..."
                />
              </TagInput>
            </FormGroup>
          </div>
        );

      case 3: // Experience
        return (
          <div>
            <SectionTitle>💼 Work Experience</SectionTitle>
            {cvData.experience.map((exp, index) => (
              <ItemCard key={index}>
                <ItemHeader>
                  <h4 style={{ margin: 0, color: '#1f2937', fontSize: '1.1rem', fontWeight: '600' }}>Experience #{index + 1}</h4>
                  <RemoveButton onClick={() => removeExperience(index)}>Remove</RemoveButton>
                </ItemHeader>
                <FormGroup>
                  <Label>Job Title</Label>
                  <Input
                    value={exp.jobTitle}
                    onChange={(e) => updateExperience(index, 'jobTitle', e.target.value)}
                    placeholder="Software Developer"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Company</Label>
                  <Input
                    value={exp.company}
                    onChange={(e) => updateExperience(index, 'company', e.target.value)}
                    placeholder="Tech Company Inc."
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Duration</Label>
                  <Input
                    value={exp.duration}
                    onChange={(e) => updateExperience(index, 'duration', e.target.value)}
                    placeholder="Jan 2023 - Present"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Description</Label>
                                  <TextArea
                  value={exp.description}
                  onChange={(e) => updateExperience(index, 'description', e.target.value)}
                  onKeyDown={(e) => {
                    // Allow Enter for new lines, Ctrl+Enter to submit
                    if (e.key === 'Enter' && e.ctrlKey) {
                      e.preventDefault();
                      // Could add auto-save or other functionality here
                    }
                  }}
                  placeholder="Describe your role and responsibilities... (Press Enter for new line)"
                  rows={3}
                />
                </FormGroup>
              </ItemCard>
            ))}
            <AddButton onClick={addExperience}>+ Add Experience</AddButton>
          </div>
        );

      case 4: // Education
        return (
          <div>
            <SectionTitle>🎓 Education</SectionTitle>
            {cvData.education.map((edu, index) => (
              <ItemCard key={index}>
                <ItemHeader>
                  <h4 style={{ margin: 0, color: '#1f2937', fontSize: '1.1rem', fontWeight: '600' }}>Education #{index + 1}</h4>
                  <RemoveButton onClick={() => removeEducation(index)}>Remove</RemoveButton>
                </ItemHeader>
                <FormGroup>
                  <Label>Degree</Label>
                  <Input
                    value={edu.degree}
                    onChange={(e) => updateEducation(index, 'degree', e.target.value)}
                    placeholder="Bachelor of Computer Science"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Institution</Label>
                  <Input
                    value={edu.institution}
                    onChange={(e) => updateEducation(index, 'institution', e.target.value)}
                    placeholder="University of Technology"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Year</Label>
                  <Input
                    value={edu.year}
                    onChange={(e) => updateEducation(index, 'year', e.target.value)}
                    placeholder="2024"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Grade/GPA (Optional)</Label>
                  <Input
                    value={edu.grade}
                    onChange={(e) => updateEducation(index, 'grade', e.target.value)}
                    placeholder="3.8 GPA or First Class"
                  />
                </FormGroup>
              </ItemCard>
            ))}
            <AddButton onClick={addEducation}>+ Add Education</AddButton>
          </div>
        );

      case 5: // Projects
        return (
          <div>
            <SectionTitle>🚀 Projects</SectionTitle>
            {cvData.projects.map((project, index) => (
              <ItemCard key={index}>
                <ItemHeader>
                  <h4 style={{ margin: 0, color: '#1f2937', fontSize: '1.1rem', fontWeight: '600' }}>Project #{index + 1}</h4>
                  <RemoveButton onClick={() => removeProject(index)}>Remove</RemoveButton>
                </ItemHeader>
                <FormGroup>
                  <Label>Project Title</Label>
                  <Input
                    value={project.title}
                    onChange={(e) => updateProject(index, 'title', e.target.value)}
                    placeholder="E-commerce Website"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Description</Label>
                                  <TextArea
                  value={project.description}
                  onChange={(e) => updateProject(index, 'description', e.target.value)}
                  onKeyDown={(e) => {
                    // Allow Enter for new lines, Ctrl+Enter to submit
                    if (e.key === 'Enter' && e.ctrlKey) {
                      e.preventDefault();
                      // Could add auto-save or other functionality here
                    }
                  }}
                  placeholder="Describe what the project does and your role... (Press Enter for new line)"
                  rows={3}
                />
                </FormGroup>
                <FormGroup>
                  <Label>Duration</Label>
                  <Input
                    value={project.duration}
                    onChange={(e) => updateProject(index, 'duration', e.target.value)}
                    placeholder="3 months"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Technologies (comma-separated)</Label>
                  <Input
                    value={project.technologies?.join(', ') || ''}
                    onChange={(e) => updateProject(index, 'technologies', e.target.value.split(',').map(t => t.trim()).filter(t => t))}
                    placeholder="React, Node.js, MongoDB"
                  />
                </FormGroup>
                <FormGroup>
                  <Label>Key Highlights (comma-separated)</Label>
                  <Input
                    value={project.highlights?.join(', ') || ''}
                    onChange={(e) => updateProject(index, 'highlights', e.target.value.split(',').map(h => h.trim()).filter(h => h))}
                    placeholder="Increased sales by 30%, Improved user experience"
                  />
                </FormGroup>
              </ItemCard>
            ))}
            <AddButton onClick={addProject}>+ Add Project</AddButton>
          </div>
        );

      case 6: // Review & Save
        return (
          <div>
            <SectionTitle>✅ Review & Save</SectionTitle>
            <p style={{ marginBottom: '20px', color: '#7f8c8d' }}>
              Please review your CV below. You can go back to any section to make changes, or save your CV to start using the AI enhancement features.
            </p>
            <PreviewCV>
              <h1>{cvData.personalInfo.fullName || 'Your Name'}</h1>
              <div className="contact-info">
                {cvData.personalInfo.phone} | {cvData.personalInfo.email} | {cvData.personalInfo.address}
                {cvData.personalInfo.linkedin && <><br/>{cvData.personalInfo.linkedin}</>}
              </div>
              
              {cvData.profileSummary && (
                <>
                  <h2>Profile Summary</h2>
                  <div className="section-content">{cvData.profileSummary}</div>
                </>
              )}
              
              {(cvData.skills.technical.length > 0 || cvData.skills.professional.length > 0) && (
                <>
                  <h2>Skills</h2>
                  <div className="section-content">
                    {cvData.skills.technical.length > 0 && (
                      <>
                        <strong>Technical Skills:</strong>
                        <div className="skills-list">
                          {cvData.skills.technical.map((skill, index) => (
                            <span key={index} className="skill-tag">{skill}</span>
                          ))}
                        </div>
                      </>
                    )}
                    {cvData.skills.professional.length > 0 && (
                      <>
                        <strong>Professional Skills:</strong>
                        <div className="skills-list">
                          {cvData.skills.professional.map((skill, index) => (
                            <span key={index} className="skill-tag">{skill}</span>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                </>
              )}
              
              {cvData.experience.length > 0 && (
                <>
                  <h2>Work Experience</h2>
                  <div className="section-content">
                    {cvData.experience.map((exp, index) => (
                      <div key={index} className="experience-item">
                        <div className="item-title">{exp.jobTitle} - {exp.company}</div>
                        <div className="item-subtitle">{exp.duration}</div>
                        {exp.description && <div>{exp.description}</div>}
                      </div>
                    ))}
                  </div>
                </>
              )}
              
              {cvData.education.length > 0 && (
                <>
                  <h2>Education</h2>
                  <div className="section-content">
                    {cvData.education.map((edu, index) => (
                      <div key={index} className="education-item">
                        <div className="item-title">{edu.degree}</div>
                        <div className="item-subtitle">{edu.institution} ({edu.year})</div>
                        {edu.grade && <div>Grade: {edu.grade}</div>}
                      </div>
                    ))}
                  </div>
                </>
              )}
              
              {cvData.projects.length > 0 && (
                <>
                  <h2>Projects</h2>
                  <div className="section-content">
                    {cvData.projects.map((project, index) => (
                      <div key={index} className="project-item">
                        <div className="item-title">{index + 1}. {project.title}</div>
                        <div className="item-subtitle">Duration: {project.duration}</div>
                        {project.description && <div>{project.description}</div>}
                        {project.technologies && project.technologies.length > 0 && (
                          <div>Technologies: {project.technologies.join(', ')}</div>
                        )}
                        {project.highlights && project.highlights.length > 0 && (
                          <div>
                            <strong>Key Highlights:</strong>
                            <ul>
                              {project.highlights.map((highlight, hIndex) => (
                                <li key={hIndex}>{highlight}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </>
              )}
            </PreviewCV>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <PageContainer>
      <TopNavBar>
        <NavLeft>
          <BackButton onClick={() => navigate('/')}>
            <span className="arrow">←</span>
            Back to Dashboard
          </BackButton>
          <Logo>
            <div className="icon">C</div>
            <div className="text">CV Builder</div>
          </Logo>
        </NavLeft>
        <NavRight>
          <SaveIndicator>
            <div className="dot"></div>
            Auto-saving enabled
          </SaveIndicator>
        </NavRight>
      </TopNavBar>

      <MainContainer>
        <Sidebar>
          <SidebarHeader>
            <h3>Build Your CV</h3>
            <p>Complete each step to create your professional CV</p>
          </SidebarHeader>
          
          <ProgressSection>
            <ProgressLabel>
              <span>Progress</span>
              <span className="progress-text">{Math.round(((currentStep + 1) / steps.length) * 100)}%</span>
            </ProgressLabel>
            <ProgressBar currentStep={currentStep} totalSteps={steps.length} />
          </ProgressSection>

          <StepsContainer>
            {steps.map((step) => (
              <StepItem
                key={step.id}
                active={currentStep === step.id}
                completed={completedSteps.has(step.id)}
                onClick={() => handleStepChange(step.id)}
              >
                <StepNumber
                  active={currentStep === step.id}
                  completed={completedSteps.has(step.id)}
                  number={step.id + 1}
                />
                <StepContent active={currentStep === step.id}>
                  <div className="step-title">{step.icon} {step.label}</div>
                  <div className="step-description">{step.description}</div>
                </StepContent>
              </StepItem>
            ))}
          </StepsContainer>
        </Sidebar>

        <MainContent>
          <ContentHeader>
            <h1>{steps[currentStep]?.icon} {steps[currentStep]?.label}</h1>
            <p>{steps[currentStep]?.fullDescription}</p>
          </ContentHeader>

          <ContentBody>
            <FormSection>
              {renderStepContent()}
              
              <ButtonGroup>
                <Button 
                  onClick={prevStep} 
                  disabled={currentStep === 0}
                  style={{ background: '#6b7280', opacity: currentStep === 0 ? 0.5 : 1 }}
                >
                  Previous
                </Button>
                
                {currentStep === steps.length - 1 ? (
                  <Button 
                    onClick={saveCV} 
                    disabled={isSaving || !cvData.personalInfo.fullName}
                    style={{ background: '#10b981' }}
                  >
                    {isSaving ? 'Creating CV...' : '✅ Complete & Save CV'}
                  </Button>
                ) : (
                  <Button onClick={nextStep}>
                    Next Step →
                  </Button>
                )}
              </ButtonGroup>
            </FormSection>

            <PreviewSection>
              <div style={{ 
                position: 'sticky', 
                top: '24px',
                background: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                border: '1px solid #e2e8f0',
                maxHeight: 'calc(100vh - 120px)',
                overflowY: 'auto'
              }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between',
                  marginBottom: '20px',
                  paddingBottom: '16px',
                  borderBottom: '2px solid #f1f5f9'
                }}>
                  <h3 style={{ 
                    margin: 0, 
                    color: '#1e293b', 
                    fontSize: '1.2rem',
                    fontWeight: '700',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    👁️ Live Preview
                  </h3>
                  <div style={{
                    background: '#f0f9ff',
                    color: '#0369a1',
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '0.8rem',
                    fontWeight: '600'
                  }}>
                    Real-time
                  </div>
                </div>
                
                <PreviewCV>
                  <h1>{cvData.personalInfo.fullName || 'Your Name'}</h1>
                  <div className="contact-info">
                    {cvData.personalInfo.phone || '+1-234-567-8900'} | {cvData.personalInfo.email || 'your.email@example.com'}
                    {cvData.personalInfo.address && <> | {cvData.personalInfo.address}</>}
                    {!cvData.personalInfo.address && <> | Your City, Country</>}
                  </div>
                  
                  {cvData.profileSummary && (
                    <>
                      <h2>Profile Summary</h2>
                      <div className="section-content">{cvData.profileSummary.substring(0, 100)}...</div>
                    </>
                  )}
                  
                  {(cvData.skills.technical.length > 0 || cvData.skills.professional.length > 0) && (
                    <>
                      <h2>Skills</h2>
                      <div className="section-content">
                        <div className="skills-list">
                          {[...cvData.skills.technical, ...cvData.skills.professional].slice(0, 6).map((skill, index) => (
                            <span key={index} className="skill-tag">{skill}</span>
                          ))}
                          {[...cvData.skills.technical, ...cvData.skills.professional].length > 6 && <span className="skill-tag">...</span>}
                        </div>
                      </div>
                    </>
                  )}
                  
                  {cvData.experience.length > 0 && (
                    <>
                      <h2>Work Experience</h2>
                      <div className="section-content">
                        {cvData.experience.slice(0, 2).map((exp, index) => (
                          <div key={index} className="experience-item">
                            <div className="item-title">{exp.jobTitle || 'Job Title'}</div>
                            <div className="item-subtitle">{exp.company || 'Company'}</div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                  
                  {cvData.projects.length > 0 && (
                    <>
                      <h2>Projects</h2>
                      <div className="section-content">
                        {cvData.projects.slice(0, 2).map((project, index) => (
                          <div key={index} className="project-item">
                            <div className="item-title">{index + 1}. {project.title || 'Project Title'}</div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </PreviewCV>
              </div>
            </PreviewSection>
          </ContentBody>
        </MainContent>
      </MainContainer>
    </PageContainer>
  );
}

export default CVBuilderPage; 