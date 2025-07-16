#!/usr/bin/env python3
"""
🧪 Comprehensive CRUD Operations Test
Tests all Create, Read, Update, Delete operations on CV content
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test if backend API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except:
        return False

def upload_test_cv():
    """Upload a test CV for testing"""
    sample_cv = """
JOHN DOE
Software Developer
Email: john@example.com

SKILLS
• Python
• JavaScript
• React

EXPERIENCE
Software Developer at TechCorp (2022-2024)
• Developed web applications
• Led team of 3 developers

EDUCATION
Bachelor of Computer Science, University of Technology (2020)

PROJECTS
E-commerce Website
• Built with React and Node.js
    """
    
    try:
        files = {'file': ('test_cv.txt', sample_cv, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload-cv/", files=files)
        return response.status_code == 200
    except:
        return False

def test_crud_operation(operation_type, message, expected_keywords):
    """Test a specific CRUD operation"""
    try:
        response = requests.post(f"{API_BASE_URL}/chat/", json={"message": message})
        
        if response.status_code != 200:
            return False, f"API error: {response.status_code}"
        
        result = response.json()
        chat_response = result.get('response', '').lower()
        
        # Check if expected keywords are in response
        found_keywords = [kw for kw in expected_keywords if kw.lower() in chat_response]
        
        success = len(found_keywords) > 0
        return success, chat_response
        
    except Exception as e:
        return False, str(e)

def get_cv_content():
    """Get current CV content"""
    try:
        response = requests.get(f"{API_BASE_URL}/cv/current/")
        if response.status_code == 200:
            return response.json().get('content', '')
        return None
    except:
        return None

def main():
    print("🧪 COMPREHENSIVE CRUD OPERATIONS TEST")
    print("=" * 60)
    
    # Test API connection
    if not test_api_connection():
        print("❌ Backend API not running. Start with: cd backend && python main_enhanced.py")
        return
    
    print("✅ Backend API connected")
    
    # Upload test CV
    if not upload_test_cv():
        print("❌ Failed to upload test CV")
        return
    
    print("✅ Test CV uploaded")
    time.sleep(1)
    
    # Test all CRUD operations
    crud_tests = [
        # CREATE OPERATIONS
        {
            'type': 'CREATE',
            'name': 'Add Skill',
            'message': 'I learned Docker and Kubernetes',
            'expected': ['successfully', 'added', 'docker', 'kubernetes']
        },
        {
            'type': 'CREATE', 
            'name': 'Add Experience',
            'message': 'I worked as Senior Developer at NewCorp for 2 years',
            'expected': ['successfully', 'added', 'experience', 'newcorp']
        },
        {
            'type': 'CREATE',
            'name': 'Add Education',
            'message': 'I studied Master of Computer Science at MIT',
            'expected': ['successfully', 'added', 'education', 'master']
        },
        {
            'type': 'CREATE',
            'name': 'Add Project',
            'message': 'I built a mobile app using React Native',
            'expected': ['successfully', 'added', 'project', 'mobile']
        },
        {
            'type': 'CREATE',
            'name': 'Add Contact',
            'message': 'My phone number is +1-555-123-4567',
            'expected': ['successfully', 'added', 'contact', '555']
        },
        
        # READ OPERATIONS
        {
            'type': 'READ',
            'name': 'Show Skills',
            'message': 'show my skills',
            'expected': ['skills', 'python', 'javascript', 'docker']
        },
        {
            'type': 'READ',
            'name': 'Show Experience', 
            'message': 'show my experience',
            'expected': ['experience', 'techcorp', 'developer']
        },
        {
            'type': 'READ',
            'name': 'Show Education',
            'message': 'show my education',
            'expected': ['education', 'bachelor', 'computer']
        },
        {
            'type': 'READ',
            'name': 'Show Projects',
            'message': 'show my projects',
            'expected': ['projects', 'website', 'e-commerce']
        },
        {
            'type': 'READ',
            'name': 'Show Full CV',
            'message': 'show my cv',
            'expected': ['john doe', 'skills', 'experience']
        },
        
        # UPDATE OPERATIONS
        {
            'type': 'UPDATE',
            'name': 'Update Skills',
            'message': 'update my skills section with Vue.js and Angular',
            'expected': ['successfully', 'updated', 'skills']
        },
        {
            'type': 'UPDATE',
            'name': 'Update Experience',
            'message': 'update my experience at TechCorp to include machine learning',
            'expected': ['successfully', 'updated', 'experience']
        },
        
        # DELETE OPERATIONS
        {
            'type': 'DELETE',
            'name': 'Remove Skill',
            'message': 'remove JavaScript skill',
            'expected': ['successfully', 'removed', 'javascript']
        },
        {
            'type': 'DELETE',
            'name': 'Remove Experience',
            'message': 'remove job at TechCorp',
            'expected': ['successfully', 'removed', 'techcorp']
        }
    ]
    
    print(f"\n🎯 Running {len(crud_tests)} CRUD operation tests...")
    print("-" * 60)
    
    results = {'CREATE': [], 'READ': [], 'UPDATE': [], 'DELETE': []}
    
    for i, test in enumerate(crud_tests, 1):
        print(f"\n{i:2d}. Testing {test['type']}: {test['name']}")
        print(f"    Message: \"{test['message']}\"")
        
        success, response = test_crud_operation(
            test['type'], 
            test['message'], 
            test['expected']
        )
        
        if success:
            print(f"    ✅ PASSED")
            results[test['type']].append(True)
        else:
            print(f"    ❌ FAILED")
            print(f"    Response: {response[:100]}...")
            results[test['type']].append(False)
        
        time.sleep(0.5)  # Small delay between tests
    
    # Test CV Generation
    print(f"\n{len(crud_tests)+1:2d}. Testing CV Generation")
    success, response = test_crud_operation('UTILITY', 'generate cv', ['successfully', 'generated', 'cv'])
    if success:
        print("    ✅ PASSED")
    else:
        print("    ❌ FAILED")
        print(f"    Response: {response[:100]}...")
    
    # Test Help Command
    print(f"\n{len(crud_tests)+2:2d}. Testing Help Command")
    success, response = test_crud_operation('UTILITY', 'help', ['create', 'read', 'update', 'delete'])
    if success:
        print("    ✅ PASSED")
    else:
        print("    ❌ FAILED")
    
    # Final CV Check
    print(f"\n{len(crud_tests)+3:2d}. Checking Final CV Content")
    final_cv = get_cv_content()
    if final_cv and len(final_cv) > 100:
        print("    ✅ PASSED - CV content retrieved")
        print(f"    CV Length: {len(final_cv)} characters")
    else:
        print("    ❌ FAILED - Could not retrieve CV content")
    
    # Results Summary
    print("\n" + "=" * 60)
    print("📊 CRUD OPERATIONS TEST RESULTS")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for operation, test_results in results.items():
        if test_results:
            operation_passed = sum(test_results)
            operation_total = len(test_results)
            total_tests += operation_total
            passed_tests += operation_passed
            
            percentage = (operation_passed / operation_total) * 100
            status = "✅" if percentage == 100 else "⚠️" if percentage >= 50 else "❌"
            
            print(f"{status} {operation:6s}: {operation_passed:2d}/{operation_total:2d} ({percentage:5.1f}%)")
    
    overall_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print("-" * 60)
    print(f"🎯 OVERALL: {passed_tests:2d}/{total_tests:2d} ({overall_percentage:5.1f}%)")
    
    if overall_percentage >= 90:
        print("\n🎉 EXCELLENT! Almost all CRUD operations working perfectly!")
        print("✅ Your AI CV Assistant has full CRUD capabilities")
    elif overall_percentage >= 70:
        print("\n✅ GOOD! Most CRUD operations working correctly")
        print("⚠️ Some operations may need fine-tuning")
    elif overall_percentage >= 50:
        print("\n⚠️ PARTIAL SUCCESS - About half the operations working")
        print("❌ Significant issues need to be addressed")
    else:
        print("\n❌ MAJOR ISSUES - Most CRUD operations failing")
        print("🔧 Backend or frontend needs debugging")
    
    print("\n💡 Next Steps:")
    print("1. Start frontend: cd frontend && npm start")
    print("2. Upload a CV")
    print("3. Try the test commands that passed")
    print("4. Use visual CRUD indicators in chat")
    print("5. Check CV panel for real-time updates")
    
    print("\n🎯 Visual Features to Test:")
    print("• Color-coded chat bubbles for CRUD operations")
    print("• CRUD operation badges on AI responses")
    print("• Real-time CV refresh after changes")
    print("• Quick action buttons for common operations")

if __name__ == "__main__":
    main() 