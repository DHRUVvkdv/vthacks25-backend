from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum
import os
import tempfile
from typing import Optional
from dotenv import load_dotenv

from utils.video_processor import VideoProcessor
from utils.auth import AuthManager, get_current_user_id
from utils.dynamodb_client import DynamoDBClient
from models.schemas import (
    UserSignupRequest, UserSigninRequest, UserPreferencesUpdate, 
    UserResponse, AuthResponse, VideoProcessingRequest
)

# Load .env file from project root
load_dotenv(dotenv_path="../../.env")

# Simple API key from environment
API_KEY = os.getenv("API_KEY", "vth_hackathon_2025_secret_key")

app = FastAPI(title="VTHacks 2025 Backend - EduTransform AI", version="1.0.0")

# Initialize services
video_processor = VideoProcessor()
auth_manager = AuthManager()
db_client = DynamoDBClient()

# Create DynamoDB table if it doesn't exist (for local development)
try:
    db_client.create_table_if_not_exist()
except Exception as e:
    print(f"Note: Could not create DynamoDB table (normal for AWS deployment): {e}")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Security schemes
api_key_header = APIKeyHeader(name="X-API-Key")
bearer_scheme = HTTPBearer()

def validate_api_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """Get current user ID from Bearer token."""
    user_id = get_current_user_id(f"Bearer {credentials.credentials}")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user_id

# Public endpoints
@app.get("/")
def root():
    return {"message": "Welcome to VTHacks 2025 Backend API"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Protected endpoints (require API key)
@app.get("/protected")
def protected(api_key: str = Depends(validate_api_key)):
    return {"message": "You accessed a protected endpoint!", "authenticated": True}

@app.get("/api/data")
def get_data(api_key: str = Depends(validate_api_key)):
    return {"data": ["item1", "item2", "item3"], "status": "success"}

# ============= USER MANAGEMENT ENDPOINTS =============

@app.post("/api/auth/signup", response_model=AuthResponse)
def signup_user(user_data: UserSignupRequest):
    """
    User signup with preferences. Creates account and returns auth token.
    No API key required for signup.
    """
    # Check if username already exists
    existing_user = db_client.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password
    password_hash = auth_manager.hash_password(user_data.password)
    
    # Prepare user data for DynamoDB
    user_db_data = {
        'name': user_data.name,
        'username': user_data.username,
        'password_hash': password_hash,
        'age': user_data.age,
        'academic_level': user_data.academicLevel,
        'major': user_data.major,
        'dyslexia_support': user_data.dyslexiaSupport,
        'language_preference': user_data.languagePreference,
        'learning_styles': user_data.learningStyles,
        'metadata': user_data.metadata
    }
    
    # Create new user in DynamoDB
    new_user = db_client.create_user(user_db_data)
    
    # Create access token
    access_token = auth_manager.create_access_token(
        data={"user_id": new_user['userId'], "username": new_user['username']}
    )
    
    # Convert to response model
    user_response = UserResponse(
        id=new_user['userId'],
        name=new_user['name'],
        username=new_user['username'],
        age=new_user['preferences']['age'],
        academicLevel=new_user['preferences']['academicLevel'],
        major=new_user['preferences']['major'],
        dyslexiaSupport=new_user['preferences']['dyslexiaSupport'],
        languagePreference=new_user['preferences']['languagePreference'],
        learningStyles=new_user['preferences']['learningStyles'],
        metadata=new_user['preferences']['metadata'],
        created_at=new_user['createdAt']
    )
    
    return AuthResponse(access_token=access_token, user=user_response)

@app.post("/api/auth/signin", response_model=AuthResponse)
def signin_user(signin_data: UserSigninRequest):
    """
    User signin. Returns auth token if credentials are valid.
    No API key required for signin.
    """
    # Find user
    user = db_client.get_user_by_username(signin_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not auth_manager.verify_password(signin_data.password, user['passwordHash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token = auth_manager.create_access_token(
        data={"user_id": user['userId'], "username": user['username']}
    )
    
    # Convert to response model
    user_response = UserResponse(
        id=user['userId'],
        name=user['name'],
        username=user['username'],
        age=user['preferences']['age'],
        academicLevel=user['preferences']['academicLevel'],
        major=user['preferences']['major'],
        dyslexiaSupport=user['preferences']['dyslexiaSupport'],
        languagePreference=user['preferences']['languagePreference'],
        learningStyles=user['preferences']['learningStyles'],
        metadata=user['preferences']['metadata'],
        created_at=user['createdAt']
    )
    
    return AuthResponse(access_token=access_token, user=user_response)

@app.get("/api/user/profile", response_model=UserResponse)
def get_user_profile(
    user_id: str = Depends(get_current_user_from_token),
    api_key: str = Depends(validate_api_key)
):
    """Get current user's profile. Requires authentication."""
    user = db_client.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        id=user['userId'],
        name=user['name'],
        username=user['username'],
        age=user['preferences']['age'],
        academicLevel=user['preferences']['academicLevel'],
        major=user['preferences']['major'],
        dyslexiaSupport=user['preferences']['dyslexiaSupport'],
        languagePreference=user['preferences']['languagePreference'],
        learningStyles=user['preferences']['learningStyles'],
        metadata=user['preferences']['metadata'],
        created_at=user['createdAt']
    )

@app.put("/api/user/preferences", response_model=UserResponse)
def update_user_preferences(
    preferences: UserPreferencesUpdate,
    user_id: str = Depends(get_current_user_from_token),
    api_key: str = Depends(validate_api_key)
):
    """Update user preferences. Requires authentication."""
    # Get current user to verify existence
    current_user = db_client.get_user_by_id(user_id)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update only provided fields
    update_data = preferences.dict(exclude_unset=True)
    updated_user = db_client.update_user_preferences(user_id, update_data)
    
    return UserResponse(
        id=updated_user['userId'],
        name=updated_user['name'],
        username=updated_user['username'],
        age=updated_user['preferences']['age'],
        academicLevel=updated_user['preferences']['academicLevel'],
        major=updated_user['preferences']['major'],
        dyslexiaSupport=updated_user['preferences']['dyslexiaSupport'],
        languagePreference=updated_user['preferences']['languagePreference'],
        learningStyles=updated_user['preferences']['learningStyles'],
        metadata=updated_user['preferences']['metadata'],
        created_at=updated_user['createdAt']
    )

@app.post("/api/upload-video")
async def upload_video(
    video: UploadFile = File(...),
    user_background: Optional[str] = Form(default="general"),
    subject_preference: Optional[str] = Form(default="auto-detect"),
    api_key: str = Depends(validate_api_key)
):
    """
    Upload and process educational video for content extraction.
    
    Args:
        video: Video file to process
        user_background: User's academic background (e.g., "CS_student", "general")
        subject_preference: Subject context preference
        api_key: API authentication key
    
    Returns:
        Dict containing transcript, extracted concepts, and processing metadata
    """
    
    # Validate file type
    if not video.content_type or not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Check file size (limit to 100MB for hackathon)
    if video.size and video.size > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video file too large (max 100MB)")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        content = await video.read()
        temp_video.write(content)
        temp_video_path = temp_video.name
    
    try:
        # Process the video
        result = video_processor.process_video(temp_video_path)
        
        # Add user context to result
        result["user_context"] = {
            "background": user_background,
            "subject_preference": subject_preference,
            "filename": video.filename
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")

@app.get("/api/processing-status/{job_id}")
def get_processing_status(job_id: str, api_key: str = Depends(validate_api_key)):
    """Get status of video processing job (for future async implementation)."""
    # Placeholder for async job status tracking
    return {"job_id": job_id, "status": "completed", "message": "Sync processing complete"}

# Lambda handler
handler = Mangum(app)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)