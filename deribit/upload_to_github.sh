#!/bin/bash

# GitHub Upload Helper Script for Deribit Skill
# This script automates the GitHub upload process

echo "=========================================="
echo "Deribit Skill - GitHub Upload Helper"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed!"
    echo ""
    echo "Please install git first:"
    echo "  macOS: brew install git"
    echo "  Ubuntu: sudo apt-get install git"
    echo "  Windows: https://git-scm.com/download/win"
    echo ""
    exit 1
fi

echo "✓ Git is installed"
echo ""

# Get user information
echo "Please enter your GitHub information:"
read -p "GitHub Username: " github_username
read -p "Repository Name: " repo_name

echo ""
echo "Repository will be created at:"
echo "  https://github.com/$github_username/$repo_name"
echo ""

read -p "Continue? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Setting up git..."

# Configure git (if not already configured)
if ! git config user.name > /dev/null; then
    read -p "Your Name: " user_name
    git config --global user.name "$user_name"
fi

if ! git config user.email > /dev/null; then
    read -p "Your Email: " user_email
    git config --global user.email "$user_email"
fi

# Initialize git repository
echo ""
echo "Initializing git repository..."
git init

# Add all files
echo "Adding files..."
git add .

# Commit
echo "Creating commit..."
git commit -m "Add Deribit trading skill for Claude agents"

# Add remote
echo "Adding remote repository..."
git remote add origin "https://github.com/$github_username/$repo_name.git"

# Set main branch
git branch -M main

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Create the repository on GitHub:"
echo "   → Go to: https://github.com/new"
echo "   → Repository name: $repo_name"
echo "   → Click 'Create repository'"
echo ""
echo "2. Push your code:"
echo "   git push -u origin main"
echo ""
echo "3. When prompted for password, use a Personal Access Token:"
echo "   → Go to: https://github.com/settings/tokens"
echo "   → Click 'Generate new token (classic)'"
echo "   → Select 'repo' scope"
echo "   → Copy the token and use it as password"
echo ""
echo "Repository URL (after upload):"
echo "  https://github.com/$github_username/$repo_name/tree/main/deribit"
echo ""
