#!/bin/bash

# AI Interview API Deployment Script
# This script helps deploy the application to various platforms

set -e

echo "🚀 AI Interview API Deployment Script"
echo "======================================"

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        echo "❌ Git is not installed. Please install Git first."
        exit 1
    fi
    
    echo "✅ Requirements check passed"
}

# Build Docker image
build_docker() {
    echo "🐳 Building Docker image..."
    docker build -t ai-interview-api:latest .
    echo "✅ Docker image built successfully"
}

# Test Docker image locally
test_docker() {
    echo "🧪 Testing Docker image locally..."
    
    # Stop any existing container
    docker stop ai-interview-api-test 2>/dev/null || true
    docker rm ai-interview-api-test 2>/dev/null || true
    
    # Run container for testing
    docker run -d \
        --name ai-interview-api-test \
        -p 8001:8000 \
        -e SECRET_KEY="test-secret-key-for-local-testing-only" \
        -e OPENAI_API_KEY="your-openai-key-here" \
        -e ADMIN_PASSWORD="testadmin123" \
        -e DEBUG="true" \
        ai-interview-api:latest
    
    # Wait for container to start
    sleep 10
    
    # Test health endpoint
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ Docker container is running and healthy"
        docker stop ai-interview-api-test
        docker rm ai-interview-api-test
    else
        echo "❌ Docker container health check failed"
        docker logs ai-interview-api-test
        docker stop ai-interview-api-test
        docker rm ai-interview-api-test
        exit 1
    fi
}

# Deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        echo "📦 Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    echo "🔐 Please login to Railway (if not already logged in):"
    railway login
    
    echo "📁 Initializing Railway project..."
    railway init
    
    echo "🔧 Setting up environment variables..."
    echo "Please set the following environment variables in Railway dashboard:"
    echo "- SECRET_KEY (generate a strong 32+ character key)"
    echo "- OPENAI_API_KEY (your OpenAI API key)"
    echo "- ADMIN_PASSWORD (secure admin password)"
    echo "- DATABASE_URL (will be auto-generated when you add PostgreSQL)"
    
    echo "📊 Adding PostgreSQL database..."
    railway add postgresql
    
    echo "🚀 Deploying application..."
    railway up
    
    echo "✅ Deployment to Railway completed!"
    echo "🌐 Your API will be available at the Railway-provided URL"
}

# Deploy to Heroku
deploy_heroku() {
    echo "🟣 Deploying to Heroku..."
    
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI is not installed. Please install it first."
        exit 1
    fi
    
    echo "🔐 Please login to Heroku:"
    heroku login
    
    echo "📁 Creating Heroku app..."
    read -p "Enter your app name (or press Enter for auto-generated): " app_name
    
    if [ -z "$app_name" ]; then
        heroku create
    else
        heroku create "$app_name"
    fi
    
    echo "📊 Adding PostgreSQL database..."
    heroku addons:create heroku-postgresql:mini
    
    echo "🔧 Setting environment variables..."
    read -p "Enter your OpenAI API key: " openai_key
    read -p "Enter admin password: " admin_password
    
    heroku config:set OPENAI_API_KEY="$openai_key"
    heroku config:set ADMIN_PASSWORD="$admin_password"
    heroku config:set SECRET_KEY="$(openssl rand -base64 32)"
    heroku config:set DEBUG="false"
    
    echo "🚀 Deploying to Heroku..."
    git add .
    git commit -m "Deploy to Heroku" || true
    git push heroku main
    
    echo "✅ Deployment to Heroku completed!"
    heroku open
}

# Deploy to DigitalOcean App Platform
deploy_digitalocean() {
    echo "🌊 Deploying to DigitalOcean App Platform..."
    
    if ! command -v doctl &> /dev/null; then
        echo "❌ DigitalOcean CLI is not installed. Please install it first."
        exit 1
    fi
    
    echo "🔐 Please authenticate with DigitalOcean:"
    doctl auth init
    
    echo "📁 Creating app spec..."
    cat > .do/app.yaml << EOF
name: ai-interview-api
services:
- name: api
  source_dir: /
  github:
    repo: your-username/ai-interview-api
    branch: main
  run_command: uvicorn app.main_prod:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: SECRET_KEY
    value: "your-secret-key-here"
  - key: OPENAI_API_KEY
    value: "your-openai-key-here"
  - key: ADMIN_PASSWORD
    value: "your-admin-password-here"
  - key: DEBUG
    value: "false"
databases:
- name: ai-interview-db
  engine: PG
  version: "13"
EOF
    
    echo "🚀 Creating DigitalOcean app..."
    doctl apps create .do/app.yaml
    
    echo "✅ Deployment to DigitalOcean initiated!"
    echo "🌐 Check your DigitalOcean dashboard for deployment status"
}

# Main menu
main_menu() {
    echo ""
    echo "Select deployment option:"
    echo "1) Build and test Docker image locally"
    echo "2) Deploy to Railway (Recommended)"
    echo "3) Deploy to Heroku"
    echo "4) Deploy to DigitalOcean App Platform"
    echo "5) Exit"
    echo ""
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            check_requirements
            build_docker
            test_docker
            ;;
        2)
            check_requirements
            build_docker
            deploy_railway
            ;;
        3)
            check_requirements
            deploy_heroku
            ;;
        4)
            check_requirements
            deploy_digitalocean
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please try again."
            main_menu
            ;;
    esac
}

# Run main menu
main_menu
