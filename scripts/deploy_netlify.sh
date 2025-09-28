#!/bin/bash

# Amazon Review Intelligence Suite - Netlify Deployment Script
# This script builds and deploys the React frontend to Netlify

set -e

echo "🌐 Amazon Review Intelligence Suite - Netlify Deployment"
echo "======================================================="

# Check if we're in the right directory
if [ ! -d "frontend" ]; then
    echo "❌ Frontend directory not found. Please run this script from the project root."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp env.example .env
    echo "📝 Please edit .env file with your API URL before deploying"
    echo "   Current API URL: http://localhost:8000"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
fi

# Build the project
echo "🔨 Building React app..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build completed successfully"
else
    echo "❌ Build failed"
    exit 1
fi

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo "📥 Installing Netlify CLI..."
    npm install -g netlify-cli
fi

# Deploy to Netlify
echo "🚀 Deploying to Netlify..."
echo ""

# Check if user is logged in to Netlify
if ! netlify status &> /dev/null; then
    echo "🔐 Please log in to Netlify..."
    netlify login
fi

# Deploy
echo "Deploying to Netlify..."
netlify deploy --prod --dir=build

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Update your API URL in Netlify environment variables"
    echo "2. Configure CORS on your backend for your Netlify domain"
    echo "3. Test your deployed application"
    echo ""
    echo "🔗 Your app should be live at the URL shown above"
else
    echo "❌ Deployment failed"
    exit 1
fi
