# VTHacks 2025 Backend - EduTransform AI

 Educational video processing backend with AI-powered content extraction and personalization. Uses Google Gemini for native audio understanding and single-pass content strategy.

## Features

- **Video Processing**: Upload and extract audio from educational videos
- **AI Transcription + Analysis**: Google Gemini (google-genai) native audio understanding
- **Content Strategy**: Single-pass content strategy tailored to user preferences
- **User Personalization**: Tailor content based on user background (CS student, general, etc.)
- **FastAPI**: Modern, fast web framework with automatic documentation
- **Simple Authentication**: API key-based security
- **CORS Enabled**: Full CORS support for frontend integration
- **AWS Lambda Ready**: Deploy to AWS Lambda with Mangum adapter

## Quick Start

### Prerequisites

- Python 3.9+
- ffmpeg (for video processing)
- Google Gemini API key
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
   # macOS (Intel/x86_64)
   brew install ffmpeg

   # macOS (Apple Silicon - if Homebrew unavailable)
   # Download ARM64 build from GitHub and use install script:
   curl -L -o FFmpeg-arm64.zip "https://github.com/ColorsWind/FFmpeg-macOS/releases/download/n5.0.1-patch3/FFmpeg-shared-n5.0.1-OSX-arm64.zip"
   unzip FFmpeg-arm64.zip
   python3 install.py . ./ffmpeg_installed
   cp ./ffmpeg_installed/bin/ffmpeg ~/.local/bin/
   cp ./ffmpeg_installed/bin/ffprobe ~/.local/bin/
   cp -r ./ffmpeg_installed/lib ~/.local/
   # Ensure ~/.local/bin is in your PATH

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
   API_KEY=dv
   GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here
   DYNAMODB_USERS_TABLE=vthacks25-users
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

#### User Authentication Endpoints (No API Key Required)

- `POST /api/auth/signup` - User registration with preferences
- `POST /api/auth/signin` - User authentication (returns JWT token)

#### Protected Endpoints (Require API Key)

- `POST /api/process-video` - Single pipeline: upload -> audio -> Gemini analysis + content strategy
- `POST /api/extract-audio` - Extract audio from uploaded video (utility)
- `POST /api/gemini-transcribe` - Run Gemini on an existing audio path (utility)

#### User Management Endpoints (Require API Key + JWT Token)

- `GET /api/user/profile` - Get current user profile
- `PUT /api/user/preferences` - Update user preferences

### Authentication

This API uses **dual authentication system**:

1. **API Key**: For endpoint access control
2. **JWT Tokens**: For user identification and session management

#### Setup Your API Key

1. **Configure**: Set `API_KEY=your_key` in `.env` file (project root)
2. **Use**: Include as `X-API-Key` header in requests

## User Authentication System

### User Registration (Signup)

Create a new user account with preferences:

```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "X-API-Key: dv" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "username": "johndoe",
    "password": "securepass123",
    "confirmPassword": "securepass123",
    "age": 20,
    "academicLevel": "College",
    "major": "Computer Science",
    "dyslexiaSupport": false,
    "languagePreference": "English",
    "learningStyles": ["visual", "auditory"],
    "metadata": []
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-string",
    "name": "John Doe",
    "username": "johndoe",
    "age": 20,
    "academicLevel": "College",
    "major": "Computer Science",
    "dyslexiaSupport": false,
    "languagePreference": "English",
    "learningStyles": ["visual", "auditory"],
    "metadata": [],
    "created_at": "2025-09-27T20:16:20.930890"
  }
}
```

### User Authentication (Signin)

Authenticate existing user:

```bash
curl -X POST "http://localhost:8000/api/auth/signin" \
  -H "X-API-Key: dv" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepass123"
  }'
```

**Response:** Same format as signup

### User Profile Management

#### Get User Profile

```bash
curl -X GET "http://localhost:8000/api/user/profile" \
  -H "X-API-Key: dv" \
  -H "Authorization: Bearer <jwt_token_from_signup_or_signin>"
```

#### Update User Preferences

```bash
curl -X PUT "http://localhost:8000/api/user/preferences" \
  -H "X-API-Key: dv" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 25,
    "academicLevel": "Graduate",
    "major": "Data Science",
    "dyslexiaSupport": true,
    "languagePreference": "Spanish",
    "learningStyles": ["visual", "kinesthetic"],
    "metadata": ["updated_preferences"]
  }'
```

### Authentication Flow for Frontend

```javascript
// 1. User Signup/Signin
const authResponse = await fetch("/api/auth/signup", {
  method: "POST",
  headers: {
    "X-API-Key": "dv",
    "Content-Type": "application/json",
  },
  body: JSON.stringify(userFormData),
});

const { access_token, user } = await authResponse.json();

// 2. Store token for subsequent requests
localStorage.setItem("jwt_token", access_token);

// 3. Use token for protected endpoints
const updateResponse = await fetch("/api/user/preferences", {
  method: "PUT",
  headers: {
    "X-API-Key": "dv",
    Authorization: `Bearer ${access_token}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify(updatedPreferences),
});
```

### Data Storage

- **Database**: Amazon DynamoDB
- **Table**: `vthacks25-users`
- **User ID**: UUID strings
- **Passwords**: bcrypt hashed
- **Sessions**: JWT tokens (24-hour expiry)

#### User Preferences Structure

The system supports comprehensive user preferences for educational personalization:

```json
{
  "name": "User Name",
  "age": 20,
  "academicLevel": "College",
  "major": "Computer Science",
  "dyslexiaSupport": false,
  "languagePreference": "English",
  "learningStyles": ["visual", "auditory", "kinesthetic"],
  "metadata": []
}
```

**Supported Academic Levels**: Elementary, Middle School, High School, College, Graduate
**Learning Styles**: visual, auditory, kinesthetic, reading/writing
**Languages**: Any language string (English, Spanish, French, etc.)
**Majors**: Any field of study string

#### API Key Usage

```bash
# Include the header on protected endpoints
curl -H "X-API-Key: dv" http://localhost:8000/api/process-video
```

#### Interactive API Documentation

Visit http://localhost:8000/docs to use the Swagger UI:

1. Click the **"Authorize"** button (🔒 icon)
2. Enter your API key from `.env` file
3. Click **"Authorize"**
4. Test all endpoints directly in the browser!

### Video Processing API

#### Single Pipeline (Upload -> Audio -> Gemini)

```bash
curl -X POST "http://localhost:8000/api/process-video" \
  -H "X-API-Key: dv" \
  -H "accept: application/json" \
  -F "video=@sample_video.mp4;type=video/mp4" \
  -F "user_background=general" \
  -F "academic_level=general" \
  -F "mode=speed"
```

#### API Response Structure

```json
{
  "pipeline": "video->audio->gemini",
  "extraction": {
    "audio_path": "/tmp/xyz.wav",
    "video_info": { "duration": 363.3, "format": "mp4" },
    "audio_info": { "sample_rate": 16000, "channels": 1 },
    "extraction_status": "success"
  },
  "analysis": {
    "gemini_analysis": {
      "transcription": "...",
      "educational_analysis": {
        "subject": "Physics",
        "topic": "Projectile Motion",
        "key_concepts": ["Parabolic trajectory", "Kinematic equations"],
        "formulas_mentioned": ["d_x = v_x * t", "d_y = 1/2 * a * t^2"]
      },
      "content_strategy": {
        "target_audience": "AP Physics / Intro College",
        "learning_objectives": ["Define projectile motion", "Apply kinematics"],
        "modules": [{ "title": "Intro to Projectile Motion", "topics": ["..."] }]
      }
    },
    "provider": "google_genai",
    "model": "models/gemini-2.5-flash",
    "work_orders": {
      "video_generation": { "brief": "Create a short intro framing: Physics" },
      "explanation": { "topics": ["Parabolic trajectory", "..."] },
      "animation_config": { "scenes": ["Intro", "Kinematics"], "focus_equations": ["..."] },
      "code_equation": { "examples": ["Compute altitude using dy = 1/2 a t^2"] },
      "visualization": { "charts": ["trajectory_parabola"] },
      "application": { "examples": ["sports", "rockets", "sprinklers"] },
      "summary": { "key_points": ["Parabolic path", "vx constant", "vy changes"] },
      "quiz_generation": { "blueprint": { "num_questions": 8 } }
    }
  }
}
```

#### Testing the Authentication System

Use the included test script:

```bash
# Test complete user authentication flow
python test_user_auth.py
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
- **Language**: Handled by Gemini audio understanding

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

Core packages for user authentication, video processing, and API:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `mangum` - AWS Lambda adapter
- `python-dotenv` - Environment variables
- `google-genai` - Google Gemini Python SDK
- `python-multipart` - File upload support
- `ffmpeg-python` - Video processing wrapper
- `boto3` - AWS SDK for DynamoDB
- `bcrypt` - Password hashing
- `python-jose[cryptography]` - JWT token handling

**System Requirements**:

- ffmpeg must be installed separately
- AWS credentials for DynamoDB (or use local development mode)

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
