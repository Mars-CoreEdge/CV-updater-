#!/usr/bin/env python3
"""
🔒 Security Check Script
Run this before committing to Git to ensure no sensitive information is included.
"""
import os
import re
import glob

def check_for_api_keys():
    """Check for hardcoded API keys"""
    patterns = [
        r'sk-[a-zA-Z0-9]{48,}',  # OpenAI API keys
        r'sk-proj-[a-zA-Z0-9_-]+',  # OpenAI project keys
        r'sk-[a-zA-Z0-9_-]{20,}',  # General secret keys
    ]
    
    issues = []
    
    # Files to check
    file_patterns = ['**/*.py', '**/*.js', '**/*.md', '**/*.txt', '**/*.json']
    
    for pattern in file_patterns:
        for file_path in glob.glob(pattern, recursive=True):
            # Skip node_modules and other ignored directories
            if any(skip in file_path for skip in ['node_modules', '.git', '__pycache__', '.env']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for api_pattern in patterns:
                    matches = re.findall(api_pattern, content)
                    if matches:
                        for match in matches:
                            # Skip if it's obviously a placeholder
                            if any(placeholder in match.lower() for placeholder in ['hidden', 'your_', 'example', 'placeholder']):
                                continue
                            issues.append(f"🚨 POTENTIAL API KEY in {file_path}: {match[:20]}...")
                            
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")
    
    return issues

def check_for_secrets():
    """Check for other sensitive information"""
    patterns = [
        r'password\s*=\s*["\'][^"\']{8,}["\']',  # Hardcoded passwords
        r'secret\s*=\s*["\'][^"\']{8,}["\']',    # Hardcoded secrets
        r'token\s*=\s*["\'][^"\']{20,}["\']',    # Hardcoded tokens
    ]
    
    issues = []
    
    for pattern in ['**/*.py', '**/*.js']:
        for file_path in glob.glob(pattern, recursive=True):
            if any(skip in file_path for skip in ['node_modules', '.git', '__pycache__']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                for secret_pattern in patterns:
                    matches = re.findall(secret_pattern, content, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            # Skip obvious test/example values
                            if any(test in match.lower() for test in ['test', 'example', 'placeholder', 'your_']):
                                continue
                            issues.append(f"🚨 POTENTIAL SECRET in {file_path}: {match[:30]}...")
                            
            except Exception as e:
                print(f"⚠️ Could not read {file_path}: {e}")
    
    return issues

def check_gitignore():
    """Check if .gitignore is properly configured"""
    required_patterns = ['.env', '*.db', '*api_key*', '*secret*']
    
    if not os.path.exists('.gitignore'):
        return ["❌ No .gitignore file found"]
    
    with open('.gitignore', 'r') as f:
        gitignore_content = f.read()
    
    missing = []
    for pattern in required_patterns:
        if pattern not in gitignore_content:
            missing.append(f"⚠️ Missing from .gitignore: {pattern}")
    
    return missing

def main():
    print("🔒 SECURITY CHECK FOR GIT COMMIT")
    print("=" * 50)
    
    # Check for API keys
    print("🔍 Checking for hardcoded API keys...")
    api_issues = check_for_api_keys()
    
    # Check for other secrets
    print("🔍 Checking for other sensitive information...")
    secret_issues = check_for_secrets()
    
    # Check .gitignore
    print("🔍 Checking .gitignore configuration...")
    gitignore_issues = check_gitignore()
    
    # Report results
    print("\n" + "=" * 50)
    print("📊 SECURITY CHECK RESULTS")
    print("=" * 50)
    
    all_issues = api_issues + secret_issues + gitignore_issues
    
    if not all_issues:
        print("✅ SECURITY CHECK PASSED!")
        print("🎉 No sensitive information detected")
        print("🚀 Safe to commit to Git")
        return True
    else:
        print("❌ SECURITY CHECK FAILED!")
        print(f"🚨 Found {len(all_issues)} issue(s):")
        print()
        
        for issue in all_issues:
            print(f"  {issue}")
        
        print()
        print("🛡️ ACTIONS REQUIRED:")
        print("1. Remove all hardcoded API keys and secrets")
        print("2. Use environment variables instead")
        print("3. Update .gitignore if needed")
        print("4. Run this script again before committing")
        
        return False

if __name__ == "__main__":
    main() 