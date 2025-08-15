#!/bin/bash

# Universal GitHub sync script for any repository
# Automatically detects repository name and syncs to GitHub
# Usage: ./push_to_github.sh [custom-repo-name]

# Configuration
GITHUB_USERNAME="zirakkk"

# Get repository name
if [ "$1" ]; then
    REPO_NAME="$1"
else
    # Auto-detect from current directory name
    CURRENT_DIR=$(basename "$(pwd)")
    # Convert to GitHub naming convention (lowercase, replace spaces/underscores with hyphens)
    REPO_NAME=$(echo "$CURRENT_DIR" | tr '[:upper:]' '[:lower:]' | sed 's/[_ ]/-/g')
fi

echo "=== GitHub Sync for Repository: $REPO_NAME ==="
echo "🔒 ONE-WAY SYNC: Local → GitHub (never pulls from GitHub)"
echo "GitHub URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

# Create comprehensive .gitignore if it doesn't exist
if [ ! -f .gitignore ]; then
    echo "Creating comprehensive .gitignore..."
    cat > .gitignore << 'EOF'
# Large data and result folders (common ML/AI patterns)
checkpoints/
classification_maps/
data/dataset/
data/datasets/
Extras/
results/
outputs/
logs/
models/
weights/
*.h5
*.hdf5

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/
.venv/

# Jupyter Notebook
.ipynb_checkpoints

# PyTorch
*.pth
*.pt
*.pkl
*.pickle

# TensorFlow
*.pb
*.tflite

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
*.tmp
*.temp
*.log
*.bak
*.backup

# Config files with sensitive data
.env
.env.local
config.ini
secrets.json

# Large files
*.zip
*.tar.gz
*.rar
*.7z
EOF
    echo "✅ Comprehensive .gitignore created"
fi

# Initialize git or check existing repository
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
    
    # Set up basic git config if not set
    if [ -z "$(git config user.name)" ]; then
        echo "Setting up basic git configuration..."
        git config user.name "$GITHUB_USERNAME"
        git config user.email "$GITHUB_USERNAME@users.noreply.github.com"
        echo "✅ Git config set"
    fi
    
    echo "✅ Git repository initialized"
else
    # Check if existing .git belongs to current project
    echo "Existing git repository found. Checking compatibility..."
    
    # Get expected remote URL for current project
    EXPECTED_REMOTE="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    
    # Check current remote
    if git remote get-url origin > /dev/null 2>&1; then
        CURRENT_REMOTE=$(git remote get-url origin)
        
        if [ "$CURRENT_REMOTE" != "$EXPECTED_REMOTE" ]; then
            echo ""
            echo "⚠️  GIT REPOSITORY MISMATCH DETECTED!"
            echo "Current git remote: $CURRENT_REMOTE"
            echo "Expected for '$REPO_NAME': $EXPECTED_REMOTE"
            echo ""
            echo "This suggests the .git folder belongs to a different project."
            echo ""
            echo "Choose an option:"
            echo "1) Fresh start - Delete .git and create new repository (recommended)"
            echo "2) Update remote URL - Keep git history but change remote"
            echo "3) Cancel - Exit without changes"
            echo ""
            read -p "Enter choice (1-3): " -n 1 -r
            echo
            
            case $REPLY in
                1)
                    echo "🗑️  Removing old .git folder..."
                    rm -rf .git
                    echo "Initializing fresh git repository..."
                    git init
                    git branch -M main
                    
                    # Set up basic git config if not set
                    if [ -z "$(git config user.name)" ]; then
                        echo "Setting up basic git configuration..."
                        git config user.name "$GITHUB_USERNAME"
                        git config user.email "$GITHUB_USERNAME@users.noreply.github.com"
                        echo "✅ Git config set"
                    fi
                    
                    echo "✅ Fresh git repository created"
                    ;;
                2)
                    echo "Updating remote URL..."
                    git remote set-url origin "$EXPECTED_REMOTE"
                    echo "✅ Remote URL updated (keeping git history)"
                    ;;
                3)
                    echo "❌ Operation cancelled"
                    exit 1
                    ;;
                *)
                    echo "❌ Invalid choice. Operation cancelled"
                    exit 1
                    ;;
            esac
        else
            echo "✅ Git repository matches current project"
        fi
    else
        echo "No remote found. Adding remote for current project..."
        git remote add origin "$EXPECTED_REMOTE"
        echo "✅ Remote added"
    fi
fi

# Remote is now handled in the git initialization section above

# Check for existing staged changes first
if ! git diff --staged --quiet; then
    echo "⚠️  You have existing staged changes:"
    git diff --staged --name-only | head -10
    if [ $(git diff --staged --name-only | wc -l) -gt 10 ]; then
        echo "... and $(( $(git diff --staged --name-only | wc -l) - 10 )) more files"
    fi
    echo ""
    echo "Choose an option:"
    echo "1) Commit existing staged changes and continue"
    echo "2) Reset staged changes and stage fresh"
    echo "3) Cancel operation"
    echo ""
    read -p "Enter choice (1-3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            echo "Committing existing staged changes..."
            COMMIT_MESSAGE="Commit staged changes - $(date '+%Y-%m-%d %H:%M:%S')"
            git commit -m "$COMMIT_MESSAGE"
            echo "✅ Staged changes committed"
            ;;
        2)
            echo "Resetting staged changes..."
            git reset HEAD .
            echo "✅ Staged changes reset"
            ;;
        3)
            echo "❌ Operation cancelled"
            exit 1
            ;;
        *)
            echo "❌ Invalid choice. Operation cancelled"
            exit 1
            ;;
    esac
fi

# Stage all current files
echo "Staging current files..."
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo "No new changes to commit"
    # Check if we need to push existing commits
    if git log origin/main..HEAD --oneline 2>/dev/null | grep -q .; then
        echo "Found local commits to push..."
        echo "Pushing to GitHub..."
        if git push origin main; then
            echo "✅ Successfully pushed local commits!"
        else
            echo "❌ Push failed"
            read -p "Try force push? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git push origin main --force && echo "✅ Force push successful!"
            fi
        fi
    else
        echo "✅ Repository is up to date"
    fi
else
    # Show what will be committed
    echo "New files to be committed:"
    git diff --staged --name-only | head -10
    if [ $(git diff --staged --name-only | wc -l) -gt 10 ]; then
        echo "... and $(( $(git diff --staged --name-only | wc -l) - 10 )) more files"
    fi
    
    # Commit changes
    echo "Committing new changes..."
    COMMIT_MESSAGE="Update repository - $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MESSAGE"
    
    # Push to GitHub
    echo "Pushing to GitHub..."
    if git push origin main; then
        echo "✅ Successfully synced to GitHub!"
    else
        echo "❌ Push failed. This might be because:"
        echo "   1. Repository '$REPO_NAME' doesn't exist on GitHub"
        echo "   2. Authentication issues"
        echo "   3. Network connectivity"
        echo ""
        echo "Please ensure:"
        echo "   - Repository exists at: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
        echo "   - You have push permissions"
        echo "   - Your authentication is set up"
        echo ""
        read -p "Try force push? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if git push origin main --force; then
                echo "✅ Force push successful!"
            else
                echo "❌ Force push also failed. Please check your setup."
                echo ""
                echo "Quick fixes:"
                echo "1. Create repository: https://github.com/new"
                echo "2. Set repository name to: $REPO_NAME"
                echo "3. Run this script again"
            fi
        fi
    fi
fi

echo ""
echo "=== Sync Complete ==="
echo "Repository: $REPO_NAME"
echo "GitHub URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""