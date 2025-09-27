#!/bin/bash
# Setup script for VTHacks 2025 Backend

echo "🚀 Setting up VTHacks 2025 Backend..."

# Check if Python 3.9+ is available
python_version=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1,2)
if [[ $(echo "$python_version >= 3.9" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.9+ required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is required but not installed."
    echo "Please install ffmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

echo "✅ ffmpeg is installed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r image/requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << EOL
# VTHacks 2025 Backend Configuration
API_KEY=vth_hackathon_2025_secret_key
JWT_SECRET_KEY=vthacks_2025_jwt_secret_key_for_demo

# 🏆 GOOGLE GEMINI API (for Best Use of Gemini API prize!)
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key_here

# OpenAI API (optional - using Gemini as primary)
OPENAI_API_KEY=your_openai_api_key_here

# AWS Configuration (for DynamoDB)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here

# DynamoDB Table Name
DYNAMODB_USERS_TABLE=vthacks25-users

# Optional: Customize these values
ENVIRONMENT=development
LOG_LEVEL=INFO
EOL
    echo "📝 Created .env file. Please update the following keys:"
    echo "   🏆 GOOGLE_GEMINI_API_KEY: Your Google Gemini API key (REQUIRED for prize!)"
    echo "   - OPENAI_API_KEY: Your OpenAI API key (optional)"
    echo "   - AWS_ACCESS_KEY_ID: Your AWS access key"
    echo "   - AWS_SECRET_ACCESS_KEY: Your AWS secret key"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your OpenAI API key"
echo "2. Start the server: cd image/src && uvicorn main:app --reload"
echo "3. Test with: python test_video_upload.py <video_file>"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"
