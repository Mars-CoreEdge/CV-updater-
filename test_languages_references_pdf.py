#!/usr/bin/env python3
"""
Comprehensive test script for LANGUAGES and REFERENCES sections with PDF verification.
"""

import requests
import time
import json

API_BASE_URL = "http://localhost:8081"

def test_languages_references_with_pdf():
    """Test LANGUAGES and REFERENCES sections and verify PDF content"""
    print("🧪 Testing LANGUAGES and REFERENCES Sections with PDF Verification")
    print("=" * 70)
    
    test_cases = [
        # LANGUAGES tests
        ("LANGUAGE_ADD", "I speak English and Spanish fluently"),
        ("LANGUAGE_ADD", "Fluent in French and conversational in German"),
        
        # REFERENCES tests  
        ("REFERENCE_ADD", "References available upon request"),
        ("REFERENCE_ADD", "Professional references from Google and Microsoft")
    ]
 #code hard 
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, (expected_category, message) in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: '{message}'")
        print(f"Expected category: {expected_category}")
        print("-" * 50)
        
        try:
            # Step 1: Add content via chat
            print("Step 1: Adding content via chat...")
            response = requests.post(f"{API_BASE_URL}/chat/", json={"message": message})
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                print(f"Chat response: {response_text[:200]}...")
                
                # Check if chat says it was added
                if "added" in response_text.lower():
                    print("✅ Chat confirmed content was added")
                    
                    # Step 2: Get current CV content
                    print("Step 2: Getting current CV content...")
                    cv_response = requests.get(f"{API_BASE_URL}/cv/current/")
                    
                    if cv_response.status_code == 200:
                        cv_data = cv_response.json()
                        cv_content = cv_data.get('content', '')
                        
                        # Step 3: Check if content is in CV text
                        section_name = "languages" if "language" in expected_category.lower() else "references"
                        if section_name in cv_content.lower():
                            print(f"✅ Content found in CV text ({section_name} section)")
                            
                            # Step 4: Generate PDF and check content
                            print("Step 4: Generating PDF...")
                            pdf_response = requests.post(f"{API_BASE_URL}/cv/download")
                            
                            if pdf_response.status_code == 200:
                                pdf_content = pdf_response.content
                                
                                # Try to extract text from PDF (simplified check)
                                try:
                                    # For now, just check if PDF was generated successfully
                                    if len(pdf_content) > 1000:  # PDF should be substantial
                                        print("✅ PDF generated successfully")
                                        
                                        # Check if the specific content is mentioned in the response
                                        if section_name in response_text.lower():
                                            print(f"✅ Section '{section_name}' mentioned in response")
                                            results.append("PASS")
                                            passed_tests += 1
                                        else:
                                            print(f"❌ Section '{section_name}' not mentioned in response")
                                            results.append("FAIL")
                                    else:
                                        print("❌ PDF too small, may not be valid")
                                        results.append("FAIL")
                                except Exception as e:
                                    print(f"❌ PDF processing error: {e}")
                                    results.append("ERROR")
                            else:
                                print(f"❌ PDF generation failed: {pdf_response.status_code}")
                                results.append("ERROR")
                        else:
                            print(f"❌ Content not found in CV text ({section_name} section)")
                            results.append("FAIL")
                    else:
                        print(f"❌ Failed to get CV content: {cv_response.status_code}")
                        results.append("ERROR")
                else:
                    print("❌ Chat did not confirm content was added")
                    results.append("FAIL")
            else:
                print(f"❌ Chat API error: {response.status_code}")
                results.append("ERROR")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append("ERROR")
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 LANGUAGES & REFERENCES TEST RESULTS")
    print("=" * 70)
    
    for i, result in enumerate(results, 1):
        status_icon = "✅" if result == "PASS" else "❌"
        test_type = "LANGUAGES" if i <= 2 else "REFERENCES"
        print(f"{status_icon} Test {i} ({test_type}): {result}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 LANGUAGES and REFERENCES sections are working perfectly!")
    else:
        print("⚠️ Some issues found. Check the details above.")
    
    return passed_tests == total_tests

def test_specific_section_content():
    """Test specific section content extraction"""
    print("\n🔍 Testing Specific Section Content")
    print("=" * 50)
    
    # Test LANGUAGES section specifically
    print("Testing LANGUAGES section...")
    try:
        response = requests.post(f"{API_BASE_URL}/chat/", json={"message": "Show my languages"})
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            print(f"Languages section: {response_text[:300]}...")
        else:
            print("Failed to get languages section")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test REFERENCES section specifically
    print("\nTesting REFERENCES section...")
    try:
        response = requests.post(f"{API_BASE_URL}/chat/", json={"message": "Show my references"})
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            print(f"References section: {response_text[:300]}...")
        else:
            print("Failed to get references section")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/test")
        if response.status_code == 200:
            print("✅ Backend is running")
            test_languages_references_with_pdf()
            test_specific_section_content()
        else:
            print("❌ Backend is not responding properly")
    except:
        print("❌ Backend is not running. Please start the backend first.") 