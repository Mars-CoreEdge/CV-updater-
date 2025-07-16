#!/usr/bin/env python3
"""
🧪 Test: Append to Existing CV Fields
Verifies that new data is added to existing CV sections rather than overwriting them.
"""
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def upload_base_cv():
    """Upload a CV with existing content in multiple sections"""
    base_cv = """
JOHN DOE
Software Developer
Email: john.doe@example.com
Phone: +1-555-123-4567

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
        files = {'file': ('base_cv.txt', base_cv, 'text/plain')}
        response = requests.post(f"{API_BASE_URL}/upload-cv/", files=files)
        return response.status_code == 200, base_cv
    except:
        return False, ""

def get_current_cv():
    """Get current CV content"""
    try:
        response = requests.get(f"{API_BASE_URL}/cv/current/")
        if response.status_code == 200:
            return response.json().get('content', '')
        return None
    except:
        return None

def send_chat_message(message):
    """Send a chat message and get response"""
    try:
        response = requests.post(f"{API_BASE_URL}/chat/", json={"message": message})
        if response.status_code == 200:
            return response.json().get('response', '')
        return None
    except:
        return None

def test_append_functionality():
    """Test that new data appends to existing sections"""
    
    print("🧪 TESTING: APPEND TO EXISTING CV FIELDS")
    print("=" * 60)
    
    # Step 1: Upload base CV with existing content
    print("1. Uploading base CV with existing content...")
    success, original_cv = upload_base_cv()
    if not success:
        print("❌ Failed to upload base CV")
        return
    
    print("✅ Base CV uploaded")
    time.sleep(1)
    
    # Step 2: Get initial CV content
    initial_cv = get_current_cv()
    if not initial_cv:
        print("❌ Could not retrieve initial CV")
        return
    
    print("✅ Initial CV retrieved")
    print(f"📊 Initial CV length: {len(initial_cv)} characters")
    
    # Verify initial content exists
    initial_skills = ["Python", "JavaScript", "React"]
    initial_experience = ["TechCorp", "Software Developer"]
    initial_education = ["Bachelor", "Computer Science"]
    
    print("\n📋 Verifying initial content exists:")
    for skill in initial_skills:
        if skill in initial_cv:
            print(f"  ✅ Initial skill found: {skill}")
        else:
            print(f"  ❌ Initial skill missing: {skill}")
    
    # Step 3: Add new skills (should append, not replace)
    print("\n2. Adding new skills to existing skills section...")
    chat_response = send_chat_message("I learned Docker, Kubernetes, and TypeScript")
    
    if chat_response:
        print("✅ Chat response received")
        print(f"📝 Response: {chat_response[:100]}...")
    else:
        print("❌ No chat response")
        return
    
    time.sleep(1)
    
    # Step 4: Get updated CV and verify append behavior
    updated_cv = get_current_cv()
    if not updated_cv:
        print("❌ Could not retrieve updated CV")
        return
    
    print("\n🔍 VERIFICATION: Checking if content was appended...")
    print("=" * 60)
    
    # Check that original skills are still there
    original_preserved = True
    for skill in initial_skills:
        if skill in updated_cv:
            print(f"✅ Original skill preserved: {skill}")
        else:
            print(f"❌ Original skill LOST: {skill}")
            original_preserved = False
    
    # Check that new skills were added
    new_skills = ["Docker", "Kubernetes", "TypeScript"]
    new_added = True
    for skill in new_skills:
        if skill in updated_cv:
            print(f"✅ New skill added: {skill}")
        else:
            print(f"❌ New skill NOT added: {skill}")
            new_added = False
    
    # Step 5: Test experience appending
    print("\n3. Adding new experience to existing experience section...")
    chat_response = send_chat_message("I worked as Senior Developer at NewCorp for 2 years")
    time.sleep(1)
    
    final_cv = get_current_cv()
    
    # Check original experience preserved
    original_exp_preserved = "TechCorp" in final_cv and "Software Developer" in final_cv
    new_exp_added = "NewCorp" in final_cv and "Senior Developer" in final_cv
    
    if original_exp_preserved:
        print("✅ Original experience preserved: TechCorp")
    else:
        print("❌ Original experience LOST: TechCorp")
    
    if new_exp_added:
        print("✅ New experience added: NewCorp")
    else:
        print("❌ New experience NOT added: NewCorp")
    
    # Step 6: Test education appending
    print("\n4. Adding new education to existing education section...")
    chat_response = send_chat_message("I studied Master of Computer Science at MIT")
    time.sleep(1)
    
    final_cv = get_current_cv()
    
    # Check original education preserved
    original_edu_preserved = "Bachelor" in final_cv and "University of Technology" in final_cv
    new_edu_added = "Master" in final_cv and "MIT" in final_cv
    
    if original_edu_preserved:
        print("✅ Original education preserved: Bachelor")
    else:
        print("❌ Original education LOST: Bachelor")
    
    if new_edu_added:
        print("✅ New education added: Master")
    else:
        print("❌ New education NOT added: Master")
    
    # Step 7: Final verification
    print("\n" + "=" * 60)
    print("📊 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    
    print(f"📈 CV Growth: {len(initial_cv)} → {len(final_cv)} characters ({len(final_cv) - len(initial_cv):+d})")
    
    if len(final_cv) > len(initial_cv):
        print("✅ CV content INCREASED (good - content was appended)")
    else:
        print("❌ CV content DID NOT INCREASE (bad - content may have been replaced)")
    
    # Overall assessment
    tests_passed = 0
    total_tests = 6
    
    if original_preserved:
        tests_passed += 1
    if new_added:
        tests_passed += 1
    if original_exp_preserved:
        tests_passed += 1
    if new_exp_added:
        tests_passed += 1
    if original_edu_preserved:
        tests_passed += 1
    if new_edu_added:
        tests_passed += 1
    
    percentage = (tests_passed / total_tests) * 100
    
    print(f"\n🎯 APPEND FUNCTIONALITY: {tests_passed}/{total_tests} ({percentage:.1f}%)")
    
    if percentage >= 90:
        print("\n🎉 EXCELLENT! Data is properly appended to existing fields!")
        print("✅ Original content preserved")
        print("✅ New content added successfully")
        print("✅ No data overwriting detected")
    elif percentage >= 70:
        print("\n✅ GOOD! Most append operations working correctly")
        print("⚠️ Some minor issues detected")
    else:
        print("\n❌ ISSUES DETECTED! Content may be overwritten instead of appended")
        print("🔧 Review the create_cv_item() and smart_section_integration() functions")
    
    # Show current CV sections for debugging
    print("\n📋 FINAL CV CONTENT PREVIEW:")
    print("-" * 40)
    cv_lines = final_cv.split('\n')
    in_skills = False
    in_experience = False
    
    for line in cv_lines:
        line_upper = line.upper().strip()
        if 'SKILL' in line_upper:
            in_skills = True
            print(f"\n{line}")
        elif line_upper.isupper() and len(line_upper) > 3:
            in_skills = False
            in_experience = 'EXPERIENCE' in line_upper
            print(f"\n{line}")
        elif in_skills and line.strip():
            print(f"  {line}")
        elif in_experience and line.strip() and len(cv_lines) < 50:  # Limit output
            print(f"  {line}")
        
        if len([l for l in cv_lines[:cv_lines.index(line)+1] if l.strip()]) > 20:
            print("  ... (truncated)")
            break

if __name__ == "__main__":
    test_append_functionality() 