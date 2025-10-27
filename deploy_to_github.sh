#!/bin/bash

# Hyperliquid Whale Tracker - GitHub Deployment Helper

echo "🐋 Hyperliquid Whale Tracker - GitHub Deployment"
echo "================================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized!"
else
    echo "✅ Git repository already exists"
fi

# Check if remote exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ GitHub remote already configured"
    REMOTE_URL=$(git remote get-url origin)
    echo "   Remote: $REMOTE_URL"
else
    echo ""
    echo "🔗 GitHub Remote Setup"
    echo "----------------------"
    echo "Please enter your GitHub repository URL:"
    echo "Example: https://github.com/username/hyperliquid-tracker.git"
    read -p "URL: " REPO_URL
    
    if [ ! -z "$REPO_URL" ]; then
        git remote add origin "$REPO_URL"
        echo "✅ Remote added: $REPO_URL"
    else
        echo "❌ No URL provided. Skipping remote setup."
    fi
fi

# Stage all files
echo ""
echo "📝 Staging files..."
git add .

# Check git status
echo ""
echo "📊 Git Status:"
git status --short

# Commit
echo ""
read -p "💬 Enter commit message (default: 'Deploy Hyperliquid Whale Tracker'): " COMMIT_MSG
COMMIT_MSG=${COMMIT_MSG:-"Deploy Hyperliquid Whale Tracker"}

git commit -m "$COMMIT_MSG"

# Push
echo ""
echo "🚀 Pushing to GitHub..."
if git remote get-url origin >/dev/null 2>&1; then
    git branch -M main
    git push -u origin main
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "🎉 Next Steps:"
    echo "1. Go to https://share.streamlit.io"
    echo "2. Click 'New app'"
    echo "3. Select your repository"
    echo "4. Set main file: app_v2.py"
    echo "5. Click 'Deploy'!"
    echo ""
    echo "Your app will be live at: https://YOUR-APP-NAME.streamlit.app"
else
    echo "⚠️  No remote configured. Please add a GitHub remote first."
    echo "   Run: git remote add origin https://github.com/username/repo.git"
fi

echo ""
echo "📚 For more help, see:"
echo "   - QUICKSTART.md"
echo "   - DEPLOYMENT.md"
echo "   - README.md"

