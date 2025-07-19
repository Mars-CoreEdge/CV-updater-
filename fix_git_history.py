#!/usr/bin/env python3
"""
Script to help remove API keys from Git history
"""

import subprocess
import sys

def run_command(command):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔒 Git History Security Fix")
    print("=" * 40)
    
    print("\n⚠️  WARNING: This will rewrite Git history!")
    print("   This is necessary to remove the API key from the repository.")
    print("   Make sure you have a backup of your work.")
    
    response = input("\nDo you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("❌ Operation cancelled.")
        return
    
    print("\n🔄 Removing API key from Git history...")
    
    # Step 1: Create a new branch from the clean commit
    print("\n1. Creating new branch from clean commit...")
    success, stdout, stderr = run_command("git checkout -b secure-optimize 1bfa25f")
    if not success:
        print(f"❌ Error creating branch: {stderr}")
        return
    print("✅ Created secure-optimize branch")
    
    # Step 2: Cherry-pick the latest commit (without API key)
    print("\n2. Applying latest changes...")
    success, stdout, stderr = run_command("git cherry-pick ff0da5b")
    if not success:
        print(f"❌ Error cherry-picking: {stderr}")
        print("   You may need to resolve conflicts manually.")
        return
    print("✅ Applied latest changes")
    
    # Step 3: Force push the new branch
    print("\n3. Pushing secure branch...")
    success, stdout, stderr = run_command("git push origin secure-optimize --force")
    if not success:
        print(f"❌ Error pushing: {stderr}")
        return
    print("✅ Pushed secure branch")
    
    print("\n🎉 Success! Your repository is now secure.")
    print("\n📋 Next steps:")
    print("1. Go to GitHub and create a Pull Request from 'secure-optimize' to 'main'")
    print("2. Merge the Pull Request")
    print("3. Delete the old 'optimize' branch")
    print("4. Rename 'secure-optimize' to 'optimize'")
    
    print("\n🔑 Don't forget to set up your environment variables:")
    print("   export OPENAI_API_KEY='your-api-key-here'")

if __name__ == "__main__":
    main() 