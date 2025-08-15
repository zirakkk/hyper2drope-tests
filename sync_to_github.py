#!/usr/bin/env python3
"""
GitHub Repository Sync Script for Hyper2DRoPE-Tests
This script creates/updates a GitHub repository following GitHub naming conventions
Excludes specified folders and pushes only relevant code files
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=".")
        if result.returncode != 0:
            print(f"Error in {description}:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        else:
            if result.stdout.strip():
                print(f"Success: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"Exception in {description}: {str(e)}")
        return False

def create_gitignore():
    """Create/update .gitignore file with excluded folders"""
    gitignore_content = """# Exclude large data and result folders
checkpoints/
classification_maps/
data/dataset/
Extras/
results/

# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so

# Virtual environments
venv/
env/
ENV/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Jupyter Notebook checkpoints
.ipynb_checkpoints/

# Model files (if any large ones exist)
*.pth
*.pt
*.model

# Log files
*.log

# Temporary files
*.tmp
*.temp
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("Created/updated .gitignore file")

def setup_git_repository():
    """Initialize git repository if not already initialized"""
    if not os.path.exists('.git'):
        print("Initializing git repository...")
        if not run_command("git init", "Initialize git repository"):
            return False
        
        if not run_command("git branch -M main", "Set default branch to main"):
            return False
    else:
        print("Git repository already exists")
    
    return True

def setup_github_remote():
    """Setup GitHub remote repository"""
    repo_name = "hyper2drope-tests"  # Following GitHub naming conventions (lowercase, hyphens)
    
    # Check if remote already exists
    result = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Setting up GitHub remote repository: {repo_name}")
        print("Please ensure you have:")
        print("1. Created a GitHub repository named 'hyper2drope-tests'")
        print("2. Have proper GitHub authentication (SSH key or personal access token)")
        
        # Try SSH first, fallback to HTTPS
        ssh_url = f"git@github.com:zirakkk/{repo_name}.git"
        https_url = f"https://github.com/zirakkk/{repo_name}.git"
        
        print(f"Please replace zirakkk with your actual GitHub username")
        print(f"SSH URL: {ssh_url}")
        print(f"HTTPS URL: {https_url}")
        
        username = input("Enter your GitHub username: ").strip()
        
        if username:
            ssh_url = f"git@github.com:{username}/{repo_name}.git"
            https_url = f"https://github.com/{username}/{repo_name}.git"
            
            # Try SSH first
            print("Trying SSH connection...")
            if run_command(f"git remote add origin {ssh_url}", "Add SSH remote"):
                print("SSH remote added successfully")
                return True
            else:
                print("SSH failed, trying HTTPS...")
                # Remove failed remote and try HTTPS
                run_command("git remote remove origin", "Remove failed SSH remote")
                if run_command(f"git remote add origin {https_url}", "Add HTTPS remote"):
                    print("HTTPS remote added successfully")
                    return True
                else:
                    print("Failed to add remote. Please add manually:")
                    print(f"git remote add origin {ssh_url}")
                    print("or")
                    print(f"git remote add origin {https_url}")
                    return False
        else:
            print("Username not provided. Please add remote manually.")
            return False
    else:
        print(f"Remote origin already exists: {result.stdout.strip()}")
        return True

def sync_repository():
    """Sync local repository with GitHub"""
    print(f"\nStarting repository sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create/update .gitignore
    create_gitignore()
    
    # Add all files (respecting .gitignore)
    if not run_command("git add .", "Stage all files"):
        return False
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    
    if result.stdout.strip():
        # There are changes to commit
        commit_message = f"Update repository - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        if not run_command(f'git commit -m "{commit_message}"', "Commit changes"):
            return False
        
        # Push to GitHub
        if not run_command("git push -u origin main", "Push to GitHub"):
            print("Push failed. This might be because:")
            print("1. Remote repository doesn't exist")
            print("2. Authentication issues")
            print("3. Remote URL is incorrect")
            print("\nTrying force push...")
            if not run_command("git push -u origin main --force", "Force push to GitHub"):
                return False
        
        print("\n✅ Repository successfully synced to GitHub!")
    else:
        print("No changes to commit")
        # Still try to push in case remote is behind
        run_command("git push origin main", "Push to GitHub (no new commits)")
        print("✅ Repository is up to date")
    
    return True

def main():
    """Main function"""
    print("=" * 60)
    print("GitHub Repository Sync for Hyper2DRoPE-Tests")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("Error: This script should be run from the Hyper2DRoPE-Tests root directory")
        print("Please navigate to the project root and run the script again")
        return False
    
    # Setup git repository
    if not setup_git_repository():
        print("Failed to setup git repository")
        return False
    
    # Setup GitHub remote
    if not setup_github_remote():
        print("Failed to setup GitHub remote")
        return False
    
    # Sync repository
    if not sync_repository():
        print("Failed to sync repository")
        return False
    
    print("\n" + "=" * 60)
    print("✅ GitHub sync completed successfully!")
    print("=" * 60)
    print("\nExcluded folders (via .gitignore):")
    print("  - checkpoints/")
    print("  - classification_maps/")
    print("  - data/dataset/")
    print("  - Extras/")
    print("  - results/")
    print("\nNext time, just run this script to update your GitHub repository!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)