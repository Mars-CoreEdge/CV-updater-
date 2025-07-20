import React, { useState, useEffect } from 'react';
import axios from 'axios';

const APITest = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [testResults, setTestResults] = useState([]);

  const testAPI = async () => {
    setLoading(true);
    setError(null);
    setTestResults([]);

    try {
      // Test 1: Backend connection
      console.log('Testing backend connection...');
      const testResponse = await axios.get('http://localhost:8081/test');
      setTestResults(prev => [...prev, `✅ Backend connection: ${testResponse.data.status}`]);

      // Test 2: Projects list endpoint
      console.log('Testing projects list endpoint...');
      const projectsResponse = await axios.get('http://localhost:8081/projects/list');
      setTestResults(prev => [...prev, `✅ Projects endpoint: ${projectsResponse.data.projects?.length || 0} projects found`]);
      
      if (projectsResponse.data.projects) {
        setProjects(projectsResponse.data.projects);
        console.log('Projects data:', projectsResponse.data.projects);
      }

      // Test 3: Projects endpoint (fallback)
      console.log('Testing projects fallback endpoint...');
      const projectsFallbackResponse = await axios.get('http://localhost:8081/projects/');
      setTestResults(prev => [...prev, `✅ Projects fallback endpoint: ${projectsFallbackResponse.data.projects?.length || 0} projects found`]);

    } catch (err) {
      console.error('API test error:', err);
      setError(err.message);
      setTestResults(prev => [...prev, `❌ Error: ${err.message}`]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    testAPI();
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>API Test Results</h2>
      
      <button 
        onClick={testAPI} 
        disabled={loading}
        style={{ 
          padding: '10px 20px', 
          marginBottom: '20px',
          backgroundColor: loading ? '#ccc' : '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Testing...' : 'Test API Again'}
      </button>

      {error && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#f8d7da', 
          color: '#721c24', 
          border: '1px solid #f5c6cb',
          borderRadius: '5px',
          marginBottom: '20px'
        }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      <div style={{ marginBottom: '20px' }}>
        <h3>Test Results:</h3>
        {testResults.map((result, index) => (
          <div key={index} style={{ 
            padding: '5px 0',
            fontFamily: 'monospace',
            fontSize: '14px'
          }}>
            {result}
          </div>
        ))}
      </div>

      {projects.length > 0 && (
        <div>
          <h3>Projects Found ({projects.length}):</h3>
          {projects.map((project, index) => (
            <div key={index} style={{ 
              border: '1px solid #ddd',
              padding: '15px',
              marginBottom: '10px',
              borderRadius: '5px',
              backgroundColor: '#f9f9f9'
            }}>
              <h4>{project.title || 'Untitled Project'}</h4>
              <p><strong>ID:</strong> {project.id || 'No ID'}</p>
              <p><strong>Description:</strong> {project.description || 'No description'}</p>
              <p><strong>Duration:</strong> {project.duration || 'No duration'}</p>
              <p><strong>Technologies:</strong> {project.technologies?.join(', ') || 'No technologies'}</p>
              <p><strong>Highlights:</strong> {project.highlights?.length || 0} items</p>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#e9ecef', borderRadius: '5px' }}>
        <h4>Debug Information:</h4>
        <p><strong>Backend URL:</strong> http://localhost:8081</p>
        <p><strong>Projects List Endpoint:</strong> /projects/list</p>
        <p><strong>Projects Endpoint:</strong> /projects/</p>
        <p><strong>Current Time:</strong> {new Date().toLocaleString()}</p>
      </div>
    </div>
  );
};

export default APITest; 