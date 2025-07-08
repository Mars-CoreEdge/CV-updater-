import React, { useState } from 'react';
import styled from 'styled-components';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const PageContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow-x: hidden;
`;

const FloatingShape = styled.div`
  position: absolute;
  width: ${props => props.size || '100px'};
  height: ${props => props.size || '100px'};
  background: ${props => props.gradient || 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))'};
  border-radius: 50%;
  top: ${props => props.top || '20%'};
  left: ${props => props.left || '20%'};
  animation: float 6s ease-in-out infinite;
  z-index: 1;

  @keyframes float {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(180deg); }
  }
`;

const BackButton = styled.button`
  position: absolute;
  top: 30px;
  left: 30px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  padding: 12px 20px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
  }

  .arrow {
    font-size: 1.2rem;
  }
`;

const ContentWrapper = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
  padding-top: 80px;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 40px;
`;

const Title = styled.h1`
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(135deg, #ffffff, #f0f0f0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 10px;
  text-shadow: 0 4px 8px rgba(0,0,0,0.1);
`;

const Subtitle = styled.p`
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
  margin-bottom: 20px;
`;

const BuilderContainer = styled.div`
  display: grid;
  grid-template-columns: 300px 1fr 400px;
  gap: 30px;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    gap: 20px;
  }
`;

const StepsPanel = styled.div`
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 25px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  height: fit-content;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const StepItem = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 12px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: ${props => props.active ? '#667eea' : 'rgba(255, 255, 255, 0.8)'};
  background: ${props => props.active ? 'rgba(255, 255, 255, 0.9)' : 'transparent'};
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
  
  .step-number {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: ${props => props.completed ? '#4CAF50' : props.active ? '#667eea' : 'rgba(255, 255, 255, 0.3)'};
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 0.9rem;
  }
  
  .step-label {
    font-weight: 500;
  }
`;

const FormPanel = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const PreviewPanel = styled.div`
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 30px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  height: fit-content;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
`;

const SectionTitle = styled.h2`
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  font-size: 0.95rem;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 8px;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;
  resize: vertical;
  min-height: 100px;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const TagInput = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 12px;
  border: 2px solid #e1e8ed;
  border-radius: 12px;
  background: white;
  min-height: 50px;
  align-items: center;
  
  &:focus-within {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const Tag = styled.span`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  
  .remove {
    cursor: pointer;
    font-weight: bold;
    padding: 2px 4px;
    border-radius: 50%;
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
    }
  }
`;

const TagInputField = styled.input`
  border: none;
  outline: none;
  flex: 1;
  min-width: 120px;
  padding: 8px;
  font-size: 0.95rem;
`;

const Button = styled.button`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 15px;
  justify-content: space-between;
  margin-top: 30px;
`;

const PreviewCV = styled.div`
  font-family: 'Georgia', serif;
  line-height: 1.6;
  color: #2c3e50;
  
  h1 {
    font-size: 1.8rem;
    color: #2c3e50;
    margin-bottom: 5px;
    font-weight: 700;
  }
  
  .contact-info {
    color: #7f8c8d;
    margin-bottom: 20px;
    font-size: 0.9rem;
  }
  
  h2 {
    font-size: 1.2rem;
    color: #34495e;
    border-bottom: 2px solid #3498db;
    padding-bottom: 5px;
    margin: 20px 0 10px 0;
  }
  
  .section-content {
    margin-bottom: 15px;
  }
  
  .experience-item, .education-item, .project-item {
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 3px solid #ecf0f1;
  }
  
  .item-title {
    font-weight: 600;
    color: #2c3e50;
  }
  
  .item-subtitle {
    color: #7f8c8d;
    font-style: italic;
  }
  
  .skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .skill-tag {
    background: #ecf0f1;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.85rem;
    color: #2c3e50;
  }
`;

const AddButton = styled.button`
  background: transparent;
  border: 2px dashed #3498db;
  color: #3498db;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    background: #3498db;
    color: white;
  }
`;

const RemoveButton = styled.button`
  background: #e74c3c;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 0.8rem;
  
  &:hover {
    background: #c0392b;
  }
`;

function CVBuilderPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState(new Set());
  const [isSaving, setIsSaving] = useState(false);

  const steps = [
    { id: 0, label: 'Personal Info', icon: '👤' },
    { id: 1, label: 'Profile Summary', icon: '📝' },
    { id: 2, label: 'Skills', icon: '🛠️' },
    { id: 3, label: 'Experience', icon: '💼' },
    { id: 4, label: 'Education', icon: '🎓' },
    { id: 5, label: 'Projects', icon: '🚀' },
    { id: 6, label: 'Review & Save', icon: '✅' }
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
      setCvData(prev => ({
        ...prev,
        skills: {
          ...prev.skills,
          [type]: [...prev.skills[type], skill.trim()]
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
      const response = await axios.post('http://localhost:8000/cv/create-from-builder', {
        personal_info: cvData.personalInfo,
        profile_summary: cvData.profileSummary,
        skills: cvData.skills,
        experience: cvData.experience,
        education: cvData.education,
        projects: cvData.projects
      });
      
      if (response.status === 200) {
        alert('CV created successfully! You can now enhance it with AI features.');
        navigate('/');
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
                placeholder="Write a compelling summary that highlights your key strengths, experience, and career objectives..."
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
                  placeholder="Type a skill and press Enter..."
                />
              </TagInput>
            </FormGroup>
            <FormGroup>
              <Label>Professional Skills</Label>
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
                  placeholder="Type a skill and press Enter..."
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
              <div key={index} style={{ marginBottom: '30px', padding: '20px', border: '1px solid #e1e8ed', borderRadius: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h4>Experience #{index + 1}</h4>
                  <RemoveButton onClick={() => removeExperience(index)}>Remove</RemoveButton>
                </div>
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
                    placeholder="Describe your role and responsibilities..."
                    rows={3}
                  />
                </FormGroup>
              </div>
            ))}
            <AddButton onClick={addExperience}>+ Add Experience</AddButton>
          </div>
        );

      case 4: // Education
        return (
          <div>
            <SectionTitle>🎓 Education</SectionTitle>
            {cvData.education.map((edu, index) => (
              <div key={index} style={{ marginBottom: '30px', padding: '20px', border: '1px solid #e1e8ed', borderRadius: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h4>Education #{index + 1}</h4>
                  <RemoveButton onClick={() => removeEducation(index)}>Remove</RemoveButton>
                </div>
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
              </div>
            ))}
            <AddButton onClick={addEducation}>+ Add Education</AddButton>
          </div>
        );

      case 5: // Projects
        return (
          <div>
            <SectionTitle>🚀 Projects</SectionTitle>
            {cvData.projects.map((project, index) => (
              <div key={index} style={{ marginBottom: '30px', padding: '20px', border: '1px solid #e1e8ed', borderRadius: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <h4>Project #{index + 1}</h4>
                  <RemoveButton onClick={() => removeProject(index)}>Remove</RemoveButton>
                </div>
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
                    placeholder="Describe what the project does and your role..."
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
              </div>
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
      <FloatingShape 
        size="120px" 
        top="10%" 
        left="8%" 
        gradient="linear-gradient(135deg, rgba(240, 147, 251, 0.2), rgba(245, 87, 108, 0.2))"
      />
      <FloatingShape 
        size="80px" 
        top="70%" 
        left="85%" 
        gradient="linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(0, 242, 254, 0.2))"
      />
      <FloatingShape 
        size="100px" 
        top="45%" 
        left="90%" 
        gradient="linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2))"
      />
      
      <BackButton onClick={() => navigate('/')}>
        <span className="arrow">←</span>
        Back to Home
      </BackButton>
      
      <ContentWrapper>
        <Header>
          <Title>🎯 CV Builder</Title>
          <Subtitle>Create your professional CV from scratch with our step-by-step builder</Subtitle>
        </Header>
        
        <BuilderContainer>
          <StepsPanel>
            <h3 style={{ color: 'white', marginBottom: '20px', fontSize: '1.2rem' }}>Build Steps</h3>
            {steps.map((step) => (
              <StepItem
                key={step.id}
                active={currentStep === step.id}
                completed={completedSteps.has(step.id)}
                onClick={() => handleStepChange(step.id)}
              >
                <div className="step-number">
                  {completedSteps.has(step.id) ? '✓' : step.id + 1}
                </div>
                <div className="step-label">{step.icon} {step.label}</div>
              </StepItem>
            ))}
          </StepsPanel>
          
          <FormPanel>
            {renderStepContent()}
            
            <ButtonGroup>
              <Button 
                onClick={prevStep} 
                disabled={currentStep === 0}
                style={{ background: '#95a5a6' }}
              >
                Previous
              </Button>
              
              {currentStep === steps.length - 1 ? (
                <Button 
                  onClick={saveCV} 
                  disabled={isSaving || !cvData.personalInfo.fullName}
                  style={{ background: '#27ae60' }}
                >
                  {isSaving ? 'Saving...' : 'Save & Upload CV'}
                </Button>
              ) : (
                <Button onClick={nextStep}>
                  Next
                </Button>
              )}
            </ButtonGroup>
          </FormPanel>
          
          <PreviewPanel>
            <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>Live Preview</h3>
            <PreviewCV>
              <h1>{cvData.personalInfo.fullName || 'Your Name'}</h1>
              <div className="contact-info">
                {cvData.personalInfo.phone || 'Phone'} | {cvData.personalInfo.email || 'Email'}
                {cvData.personalInfo.address && <> | {cvData.personalInfo.address}</>}
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
          </PreviewPanel>
        </BuilderContainer>
      </ContentWrapper>
    </PageContainer>
  );
}

export default CVBuilderPage; 