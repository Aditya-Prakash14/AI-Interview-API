#!/bin/bash

# AI Interview API - Render Deployment Helper Script
# This script helps prepare and deploy your application to Render

set -e  # Exit on any error

echo "🚀 AI Interview API - Render Deployment Helper"
echo "=============================================="

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ This is not a Git repository. Please initialize Git first:"
    echo "   git init"
    echo "   git add ."
    echo "   git commit -m 'Initial commit'"
    echo "   git remote add origin <your-github-repo-url>"
    echo "   git push -u origin main"
    exit 1
fi

echo "✅ Git repository detected"

# Check if render.yaml exists
if [ ! -f "render.yaml" ]; then
    echo "❌ render.yaml not found. This file is required for Render deployment."
    exit 1
fi

echo "✅ render.yaml configuration found"

# Check if requirements-prod.txt exists
if [ ! -f "requirements-prod.txt" ]; then
    echo "❌ requirements-prod.txt not found. This file is required for production deployment."
    exit 1
fi

echo "✅ Production requirements file found"

# Check if main_prod.py exists
if [ ! -f "app/main_prod.py" ]; then
    echo "❌ app/main_prod.py not found. This file is required for production deployment."
    exit 1
fi

echo "✅ Production FastAPI app found"

# Validate render.yaml
echo "🔍 Validating render.yaml configuration..."

if grep -q "OPENAI_API_KEY" render.yaml; then
    echo "✅ OpenAI API key configuration found"
else
    echo "⚠️  OpenAI API key not configured in render.yaml"
fi

if grep -q "healthCheckPath: /health" render.yaml; then
    echo "✅ Health check endpoint configured"
else
    echo "⚠️  Health check endpoint not configured"
fi

# Check git status
echo "📋 Checking Git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes. Committing them now..."
    git add .
    git commit -m "Prepare for Render deployment - $(date)"
    echo "✅ Changes committed"
else
    echo "✅ Working directory is clean"
fi

# Check if remote origin exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Git remote origin configured"
    REPO_URL=$(git remote get-url origin)
    echo "   Repository: $REPO_URL"
else
    echo "❌ Git remote origin not configured. Please add your GitHub repository:"
    echo "   git remote add origin <your-github-repo-url>"
    echo "   git push -u origin main"
    exit 1
fi

# Push to remote
echo "📤 Pushing to remote repository..."
CURRENT_BRANCH=$(git branch --show-current)
git push origin $CURRENT_BRANCH

echo "✅ Code pushed to remote repository"

# Provide deployment instructions
echo ""
echo "🎉 Your code is ready for Render deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to https://render.com and sign up/login"
echo "2. Click 'New +' and select 'Web Service'"
echo "3. Connect your GitHub account and select this repository"
echo "4. Render will automatically detect the render.yaml configuration"
echo "5. Set your OPENAI_API_KEY in the environment variables"
echo "6. Click 'Create Web Service'"
echo ""
echo "🔧 Required Environment Variables to set manually:"
echo "   - OPENAI_API_KEY: Your OpenAI API key"
echo ""
echo "🔄 Auto-configured by Render:"
echo "   - SECRET_KEY: Auto-generated secure key"
echo "   - ADMIN_PASSWORD: Auto-generated secure password"
echo "   - DATABASE_URL: Auto-configured PostgreSQL connection"
echo ""
echo "📱 After deployment, your app will be available at:"
echo "   https://your-app-name.onrender.com"
echo ""
echo "📚 For detailed instructions, see: RENDER_DEPLOYMENT.md"
echo ""
echo "🆘 Need help? Check the troubleshooting section in RENDER_DEPLOYMENT.md"

# Optional: Open Render website
read -p "🌐 Would you like to open Render.com in your browser? (y/n): " open_browser
if [[ $open_browser =~ ^[Yy]$ ]]; then
    if command -v open &> /dev/null; then
        open "https://render.com"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "https://render.com"
    else
        echo "Please open https://render.com in your browser"
    fi
fi

echo ""
echo "✨ Deployment preparation complete!"
