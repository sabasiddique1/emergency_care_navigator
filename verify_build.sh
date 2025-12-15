#!/bin/bash
# Build verification script for Vercel deployment

echo "🔍 Verifying build configuration..."
echo ""

# Check required files
echo "📁 Checking required files..."
files=(
    "api/app.py"
    "app/api_server.py"
    "pyproject.toml"
    "requirements.txt"
    "vercel.json"
    "frontend/package.json"
)

missing=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        missing=$((missing + 1))
    fi
done

if [ $missing -gt 0 ]; then
    echo ""
    echo "❌ Missing $missing required file(s)"
    exit 1
fi

echo ""
echo "🐍 Testing Python package build..."
if python3 -m build --wheel > /dev/null 2>&1; then
    echo "  ✓ Python package builds successfully"
    rm -rf dist/ build/ *.egg-info 2>/dev/null
else
    echo "  ✗ Python package build failed"
    exit 1
fi

echo ""
echo "⚛️  Testing Frontend build..."
cd frontend
if npm run build > /dev/null 2>&1; then
    echo "  ✓ Frontend builds successfully"
else
    echo "  ✗ Frontend build failed"
    exit 1
fi
cd ..

echo ""
echo "✅ All builds verified successfully!"
echo ""
echo "📋 Deployment Checklist:"
echo "  [ ] Set JWT_SECRET_KEY in Vercel environment variables"
echo "  [ ] Set GEMINI_API_KEY (optional) in Vercel environment variables"
echo "  [ ] Deploy to Vercel"
echo ""
echo "🚀 Ready to deploy!"

