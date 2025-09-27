# VTHacks 2025 Backend - EduTransform AI

Educational video processing backend with AI-powered content extraction and personalization. Transform any educational video into 8 personalized learning formats using OpenAI Whisper and GPT-4.

## Features

- **Video Processing**: Upload and extract audio from educational videos
- **AI Transcription**: OpenAI Whisper API for speech-to-text conversion
- **Content Analysis**: GPT-4 powered concept extraction and analysis
- **User Personalization**: Tailor content based on user background (CS student, general, etc.)
- **FastAPI**: Modern, fast web framework with automatic documentation
- **Simple Authentication**: API key-based security
- **CORS Enabled**: Full CORS support for frontend integration
- **AWS Lambda Ready**: Deploy to AWS Lambda with Mangum adapter

## Quick Start

### Prerequisites

- Python 3.9+
- ffmpeg (for video processing)
- OpenAI API key
- Virtual environment (venv)

### Automated Setup

Run the setup script for automatic configuration:

```bash
./setup.sh
```

### Manual Setup

1. **Clone and navigate to the project**

   ```bash
   cd vthacks25-backend
   ```

2. **Install ffmpeg**

   ```bash
   # macOS
   brew install ffmpeg

   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # Windows: Download from https://ffmpeg.org/download.html
   ```

3. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r image/requirements.txt
   ```

5. **Set up environment variables**

   ```bash
   # Create .env file in project root
   cat > .env << EOL
   API_KEY=vth_hackathon_2025_secret_key
   OPENAI_API_KEY=your_openai_api_key_here
   EOL
   ```

6. **Run the application**
   ```bash
   cd image/src
   uvicorn main:app --reload
   ```

### API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

#### Public Endpoints (No Authentication)

- `GET /` - Welcome message
- `GET /health` - Health check

#### Protected Endpoints (Require API Key)

- `GET /protected` - Simple protected endpoint
- `GET /api/data` - Sample data endpoint
- `POST /api/upload-video` - **Video processing endpoint** (main feature)
- `GET /api/processing-status/{job_id}` - Processing status check

### Authentication

This API uses **simple API key authentication** from your `.env` file.

#### Setup Your API Key

1. **Configure**: Set `API_KEY=your_key` in `image/src/.env`
2. **Use**: Include as `X-API-Key` header in requests

#### API Key Usage

```bash
# Public endpoints (no auth needed)
curl http://localhost:8000/
curl http://localhost:8000/health

# Protected endpoints (API key required)
curl -H "X-API-Key: your_key" http://localhost:8000/protected
curl -H "X-API-Key: your_key" http://localhost:8000/api/data
```

#### Interactive API Documentation

Visit http://localhost:8000/docs to use the Swagger UI:

1. Click the **"Authorize"** button (🔒 icon)
2. Enter your API key from `.env` file
3. Click **"Authorize"**
4. Test all endpoints directly in the browser!

### Video Processing API

#### Upload and Process Video

```bash
# Upload a video file for processing
curl -X POST "http://localhost:8000/api/upload-video" \
  -H "X-API-Key: vth_hackathon_2025_secret_key" \
  -F "video=@sample_video.mp4" \
  -F "user_background=CS_student" \
  -F "subject_preference=physics"
```

#### API Response Structure

```json
{
  "transcript": {
    "text": "Welcome to this physics lesson on projectile motion...",
    "language": "en"
  },
  "concepts": {
    "analysis": "GPT-4 analysis of key concepts, learning objectives, and difficulty level",
    "word_count": 1250,
    "estimated_duration": 8
  },
  "user_context": {
    "background": "CS_student",
    "subject_preference": "physics",
    "filename": "sample_video.mp4"
  },
  "status": "success"
}
```

#### Testing the Video Processing

Use the included test script:

```bash
# Test with a sample video
python test_video_upload.py path/to/your/video.mp4
```

#### Frontend Integration

The API is designed for frontend integration with these characteristics:

- **File Upload**: Supports multipart/form-data for video files
- **User Context**: Accepts user background and subject preferences
- **Async Ready**: Built for future async processing implementation
- **Error Handling**: Comprehensive error responses for debugging
- **CORS Enabled**: Ready for web application integration

#### Supported Video Formats

- **File Types**: MP4, AVI, MOV, MKV (any format supported by ffmpeg)
- **Max File Size**: 100MB (configurable for production)
- **Audio Requirements**: Any audio track (automatically extracted)
- **Languages**: Auto-detection via Whisper API (99+ languages supported)

### CORS Support

Full CORS support is enabled for all origins, methods, and headers - perfect for web applications!

## Project Structure

**Super simple structure - everything you need in minimal files:**

```
vthacks25-backend/
├── README.md              # This documentation
├── Plan.md                # Project architecture and implementation guide
├── .gitignore             # Git ignore rules
├── setup.sh               # Automated setup script
├── test_video_upload.py   # Video processing test script
├── .env                   # Environment variables (API keys)
├── venv/                  # Virtual environment
└── image/                 # Application files
    ├── Dockerfile         # For AWS Lambda deployment
    ├── requirements.txt   # Dependencies (7 packages)
    └── src/
        ├── main.py        # FastAPI app with video processing
        └── utils/
            ├── __init__.py
            └── video_processor.py  # Video processing pipeline
```

## Dependencies

Core packages for video processing and API:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `mangum` - AWS Lambda adapter
- `python-dotenv` - Environment variables
- `openai` - OpenAI API client (Whisper & GPT-4)
- `python-multipart` - File upload support
- `ffmpeg-python` - Video processing wrapper

**System Requirement**: ffmpeg must be installed separately

## Docker Deployment

```bash
# Build for AWS Lambda
cd image
docker build -t vthacks25-backend .

# Run locally with Docker
docker run -p 8000:8000 --env-file src/.env vthacks25-backend
```

## AWS CLI Setup

### Prerequisites

- AWS account with access credentials
- No admin privileges required on local machine

### Installation & Configuration

```bash
# Download and install AWS CLI v2 (user-space installation)
curl "https://awscli.amazonaws.com/awscli-exe-macos.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install --install-dir ~/aws-cli --bin-dir ~/aws-cli/bin

# Add to PATH
echo 'export PATH=$HOME/aws-cli/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

# Configure AWS profile
aws2 configure --profile dv-per
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Disable SSL verification if needed (corporate networks)
aws2 configure set ca_bundle "" --profile dv-per

# Test connection
aws2 s3 ls --profile dv-per
```

## AWS Lambda Deployment

This application is configured for AWS Lambda deployment using:

- **Mangum**: ASGI adapter for Lambda
- **AWS Lambda Python Runtime**: Public ECR base image
- **Handler**: `main.handler` (configured in Dockerfile)

The same codebase works for both local development and Lambda deployment.

# how to run:

docker build -t vt25 .  
docker run -p 8000:8000 --env-file .env --entrypoint "" vt25 python main.py
