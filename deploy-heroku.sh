#!/bin/bash

# AI Interview API - Heroku Deployment Script
# This script automates the deployment process to Heroku

set -e  # Exit on any error

echo "🚀 Starting AI Interview API deployment to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   macOS: brew tap heroku/brew && brew install heroku"
    echo "   Linux: curl https://cli-assets.heroku.com/install.sh | sh"
    echo "   Or download from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Heroku CLI is available"

# Login to Heroku
echo "🔐 Logging into Heroku..."
heroku login

# Get app name from user
read -p "Enter your Heroku app name (must be unique): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ App name is required"
    exit 1
fi

# Create Heroku app
echo "📦 Creating Heroku app: $APP_NAME"
heroku create $APP_NAME

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:mini --app $APP_NAME

# Set environment variables
echo "🔧 Setting environment variables..."
echo "Please provide the following environment variables:"

read -p "Enter your SECRET_KEY (32+ characters): " SECRET_KEY
read -p "Enter your OPENAI_API_KEY: " OPENAI_API_KEY
read -p "Enter your ADMIN_PASSWORD: " ADMIN_PASSWORD
read -p "Enter your ADMIN_EMAIL (optional, default: admin@example.com): " ADMIN_EMAIL

# Set default admin email if not provided
if [ -z "$ADMIN_EMAIL" ]; then
    ADMIN_EMAIL="admin@example.com"
fi

# Validate required variables
if [ -z "$SECRET_KEY" ] || [ -z "$OPENAI_API_KEY" ] || [ -z "$ADMIN_PASSWORD" ]; then
    echo "❌ SECRET_KEY, OPENAI_API_KEY, and ADMIN_PASSWORD are required"
    exit 1
fi

# Set environment variables
echo "Setting SECRET_KEY..."
heroku config:set SECRET_KEY="$SECRET_KEY" --app $APP_NAME

echo "Setting OPENAI_API_KEY..."
heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY" --app $APP_NAME

echo "Setting ADMIN_PASSWORD..."
heroku config:set ADMIN_PASSWORD="$ADMIN_PASSWORD" --app $APP_NAME

echo "Setting ADMIN_EMAIL..."
heroku config:set ADMIN_EMAIL="$ADMIN_EMAIL" --app $APP_NAME

echo "Setting production flags..."
heroku config:set DEBUG="false" --app $APP_NAME
heroku config:set LOG_LEVEL="INFO" --app $APP_NAME

echo "✅ Environment variables set successfully"

# Add Heroku remote if not exists
if ! git remote | grep -q heroku; then
    echo "🔗 Adding Heroku remote..."
    heroku git:remote -a $APP_NAME
fi

# Deploy the application
echo "🚀 Deploying to Heroku..."
git push heroku main

echo "🎉 Deployment completed successfully!"
echo "📱 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📚 API Documentation: https://$APP_NAME.herokuapp.com/docs"
echo "🔧 Admin Panel: https://$APP_NAME.herokuapp.com/admin"

# Show app info
heroku info --app $APP_NAME

# Show recent logs
echo "📋 Recent logs:"
heroku logs --tail --app $APP_NAME
