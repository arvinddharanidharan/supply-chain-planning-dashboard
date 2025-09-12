#!/bin/bash

echo "🚀 Pushing Supply Chain Dashboard to GitHub..."
echo ""
echo "⚠️  Replace 'YOUR_USERNAME' with your actual GitHub username before running!"
echo ""

# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/supply-chain-planning-dashboard.git

# Push to main branch
git branch -M main
git push -u origin main

echo ""
echo "✅ Repository pushed successfully!"
echo "🔗 View at: https://github.com/YOUR_USERNAME/supply-chain-planning-dashboard"