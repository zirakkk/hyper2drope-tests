#!/bin/bash

# Universal GitHub pull script for any repository
# Downloads/updates repository from GitHub to local machine
# Usage: ./pull_from_github.sh [custom-repo-name]

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

echo "=== GitHub Pull for Repository: $REPO_NAME ==="
echo "🔽 ONE-WAY SYNC: GitHub → Local (overwrites local changes)"
echo "GitHub URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"

REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Check if we're in a git repository
if [ ! -d .git ]; then
    # Not a git repository - clone from GitHub
    echo ""
    echo "📥 First time setup: Cloning repository from GitHub..."
    
    # Check if directory is empty (except for this script and common files)
    FILE_COUNT=$(find . -maxdepth 1 -type f ! -name "pull_from_github.sh" ! -name ".DS_Store" ! -name "Thumbs.db" | wc -l)
    
    if [ $FILE_COUNT -gt 0 ]; then
        echo "⚠️  Warning: Current directory is not empty!"
        echo "Files in directory:"
        ls -la | grep -v "pull_from_github.sh" | grep -v "^total" | tail -n +2
        echo ""
        read -p "Continue with clone? This may overwrite files (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Clone cancelled"
            exit 1
        fi
    fi
    
    echo "Cloning from: $REMOTE_URL"
    
    # Clone to temporary directory first
    TEMP_DIR="/tmp/github_clone_$$"
    if git clone "$REMOTE_URL" "$TEMP_DIR"; then
        echo "✅ Successfully cloned repository"
        
        # Move contents to current directory
        echo "Moving files to current directory..."
        
        # Move all files including hidden ones
        if [ "$(ls -A "$TEMP_DIR")" ]; then
            mv "$TEMP_DIR"/* . 2>/dev/null || true
            mv "$TEMP_DIR"/.[!.]* . 2>/dev/null || true
            mv "$TEMP_DIR"/..?* . 2>/dev/null || true
        fi
        
        # Clean up temp directory
        rm -rf "$TEMP_DIR"
        
        echo "✅ Repository cloned and set up successfully!"
        echo ""
        echo "Repository contents:"
        ls -la
    else
        echo "❌ Failed to clone repository"
        echo "This might be because:"
        echo "   1. Repository '$REPO_NAME' doesn't exist on GitHub"
        echo "   2. Repository is private and you don't have access"
        echo "   3. Network connectivity issues"
        echo "   4. Authentication issues"
        echo ""
        echo "Please check:"
        echo "   - Repository exists at: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
        echo "   - You have read access to the repository"
        echo "   - Repository name is correct"
        rm -rf "$TEMP_DIR" 2>/dev/null || true
        exit 1
    fi
    
else
    # Already a git repository - pull updates
    echo ""
    echo "📥 Updating existing repository from GitHub..."
    
    # Check if remote exists and matches
    if git remote get-url origin > /dev/null 2>&1; then
        CURRENT_REMOTE=$(git remote get-url origin)
        if [ "$CURRENT_REMOTE" != "$REMOTE_URL" ]; then
            echo "⚠️  Remote URL mismatch!"
            echo "Current remote: $CURRENT_REMOTE"
            echo "Expected remote: $REMOTE_URL"
            echo ""
            read -p "Update remote URL? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git remote set-url origin "$REMOTE_URL"
                echo "✅ Remote URL updated"
            else
                echo "❌ Keeping current remote URL"
            fi
        fi
    else
        echo "Adding remote origin: $REMOTE_URL"
        git remote add origin "$REMOTE_URL"
    fi
    
    # Check for local uncommitted changes
    if ! git diff --quiet || ! git diff --staged --quiet; then
        echo "⚠️  You have local uncommitted changes:"
        echo ""
        echo "Modified files:"
        git status --porcelain
        echo ""
        echo "Choose an option:"
        echo "1) Stash local changes and pull (recommended)"
        echo "2) Hard reset and pull (⚠️  DESTROYS local changes)"
        echo "3) Cancel pull"
        echo ""
        read -p "Enter choice (1-3): " -n 1 -r
        echo
        
        case $REPLY in
            1)
                echo "Stashing local changes..."
                git stash push -m "Auto-stash before pull - $(date '+%Y-%m-%d %H:%M:%S')"
                echo "✅ Local changes stashed"
                ;;
            2)
                echo "⚠️  WARNING: This will permanently delete your local changes!"
                read -p "Are you absolutely sure? Type 'yes' to confirm: " confirm
                if [ "$confirm" = "yes" ]; then
                    git reset --hard HEAD
                    git clean -fd
                    echo "✅ Local changes reset"
                else
                    echo "❌ Pull cancelled"
                    exit 1
                fi
                ;;
            3)
                echo "❌ Pull cancelled"
                exit 1
                ;;
            *)
                echo "❌ Invalid choice. Pull cancelled"
                exit 1
                ;;
        esac
    fi
    
    # Fetch and pull from GitHub
    echo "Fetching latest changes from GitHub..."
    if git fetch origin; then
        echo "✅ Fetch successful"
        
        echo "Pulling changes from main branch..."
        if git pull origin main; then
            echo "✅ Successfully updated from GitHub!"
            
            # Show what changed
            echo ""
            echo "Recent commits:"
            git log --oneline -5
            
        else
            echo "❌ Pull failed"
            echo "This might be due to:"
            echo "   1. Merge conflicts"
            echo "   2. Branch differences"
            echo "   3. Network issues"
            echo ""
            echo "Trying force pull..."
            read -p "Force pull from GitHub? This will overwrite local branch (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git reset --hard origin/main
                echo "✅ Force pull successful!"
            else
                echo "❌ Pull cancelled"
                exit 1
            fi
        fi
    else
        echo "❌ Fetch failed"
        echo "Please check your network connection and repository access"
        exit 1
    fi
fi

echo ""
echo "=== Pull Complete ==="
echo "Repository: $REPO_NAME"
echo "GitHub URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo "Local directory: $(pwd)"
echo ""
echo "💡 Tip: Run this script anytime to get latest updates from GitHub!"
echo "