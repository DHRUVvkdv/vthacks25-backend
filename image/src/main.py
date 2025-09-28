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
from agents.speech_to_text_agent import GeminiSpeechToTextAgent
from agents.orchestrator import ContentOrchestrator
from models.schemas import (
    UserSignupRequest, UserSigninRequest, UserPreferencesUpdate, 
    UserResponse, AuthResponse, VideoProcessingRequest
)

# Load .env file from project root
load_dotenv(dotenv_path="../../.env")

# Simple API key from environment
API_KEY = os.getenv("API_KEY", "vth_hackathon_2025_secret_key")

app = FastAPI(
    title="VTHacks 2025 Backend - EduTransform AI", 
    version="1.0.0",
    description="Educational video processing backend with AI-powered content extraction and user management",
    tags_metadata=[
        {
            "name": "Health & Status",
            "description": "System health and status endpoints"
        },
        {
            "name": "Authentication", 
            "description": "User signup, signin, and JWT token management"
        },
        {
            "name": "User Management",
            "description": "User profile and preferences management"
        },
        {
            "name": "Video Processing",
            "description": "Video upload and AI-powered content extraction"
        },
        {
            "name": "Legacy",
            "description": "Legacy endpoints for backward compatibility"
        }
    ]
)

# Initialize services
video_processor = VideoProcessor()
auth_manager = AuthManager()
db_client = DynamoDBClient()

# Initialize Gemini agent (for Best Use of Gemini API prize!)
try:
    gemini_agent = GeminiSpeechToTextAgent()
    print("🏆 Google Gemini 1.5 Pro initialized for Best Use of Gemini API!")
except ValueError as e:
    print(f"⚠️ Gemini agent initialization failed: {e}")
    gemini_agent = None

# Initialize Content Orchestrator
try:
    content_orchestrator = ContentOrchestrator()
    print("🎯 Content Orchestrator initialized with 8 specialized agents!")
except Exception as e:
    print(f"⚠️ Content Orchestrator initialization failed: {e}")
    content_orchestrator = None

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
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer()

def validate_api_key(x_api_key: str = Depends(api_key_header)):
    if not x_api_key or x_api_key != API_KEY:
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

# ============= HEALTH & STATUS ENDPOINTS =============

@app.get("/", tags=["Health & Status"])
def root():
    """Welcome message and API information."""
    return {"message": "Welcome to VTHacks 2025 Backend API"}

@app.get("/health", tags=["Health & Status"])
def health():
    """Health check endpoint for monitoring."""
    return {"status": "healthy"}

# ============= LEGACY ENDPOINTS =============

# Removed legacy endpoints

# ============= AUTHENTICATION ENDPOINTS =============

@app.post("/api/auth/signup", response_model=AuthResponse, tags=["Authentication"])
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

@app.post("/api/auth/signin", response_model=AuthResponse, tags=["Authentication"])
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

@app.get("/api/user/profile", response_model=UserResponse, tags=["User Management"])
def get_user_profile(
    user_id: str = Depends(get_current_user_from_token),
    api_key: str = Depends(validate_api_key)
):
    """Get current user's profile. Requires API key + JWT token authentication."""
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

@app.put("/api/user/preferences", response_model=UserResponse, tags=["User Management"])
def update_user_preferences(
    preferences: UserPreferencesUpdate,
    user_id: str = Depends(get_current_user_from_token),
    api_key: str = Depends(validate_api_key)
):
    """Update user preferences. Requires API key + JWT token authentication."""
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

@app.post("/api/extract-audio", tags=["Video Processing"])
async def extract_audio_from_video(
    video: UploadFile = File(...),
    api_key: str = Depends(validate_api_key)
):
    """
    Extract audio from uploaded video file (Step 1 of video processing).
    
    Args:
        video: Video file to extract audio from
        api_key: API authentication key
    
    Returns:
        Dict containing video info, audio info, and extraction metadata
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
        # Extract audio with detailed info
        result = video_processor.extract_audio(temp_video_path, return_info=True)
        
        # Add upload metadata
        result["upload_info"] = {
            "filename": video.filename,
            "content_type": video.content_type,
            "size_bytes": video.size,
            "size_mb": round(video.size / (1024 * 1024), 2) if video.size else 0
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio extraction failed: {str(e)}")
    finally:
        # Cleanup video file
        if os.path.exists(temp_video_path):
            os.unlink(temp_video_path)

@app.post("/api/gemini-transcribe", tags=["Video Processing"])
async def gemini_transcribe_audio(
    audio_file_path: str = Form(...),
    user_background: Optional[str] = Form(default="general"),
    academic_level: Optional[str] = Form(default="general"),
    mode: Optional[str] = Form(default="speed"),
    model: Optional[str] = Form(default=None),
    work_orders_mode: Optional[str] = Form(default="guided"),
    api_key: str = Depends(validate_api_key)
):
    """
    🏆 GEMINI-POWERED: Convert audio to intelligent educational analysis.
    
    This endpoint showcases Google Gemini 1.5 Pro's capabilities for the Best Use of Gemini API prize.
    Goes beyond simple transcription to provide personalized educational insights.
    
    Args:
        audio_file_path: Path to the extracted audio file (from /api/extract-audio)
        user_background: User's field of study (e.g., "Computer Science", "Physics")
        academic_level: User's academic level (e.g., "High School", "College")
        api_key: API authentication key
    
    Returns:
        Dict containing Gemini's intelligent analysis of the educational content
    """
    
    if not gemini_agent:
        raise HTTPException(
            status_code=503,
            detail="🚫 Google Gemini API not available. Please set GOOGLE_GEMINI_API_KEY in .env file."
        )
    
    # Validate audio file exists
    if not os.path.exists(audio_file_path):
        raise HTTPException(
            status_code=400,
            detail="Audio file not found. Use /api/extract-audio first to get the audio_path."
        )
    
    try:
        # Prepare user context for personalized analysis
        user_context = {
            "major": user_background,
            "academicLevel": academic_level,
            "prefer_fast": mode == "speed",
            "force_model": model,
            "work_orders_mode": work_orders_mode
        }
        
        # Use Gemini for intelligent analysis
        result = gemini_agent.transcribe_and_analyze(audio_file_path, user_context)
        
        # Add processing metadata
        result["processing_info"] = {
            "audio_file_processed": audio_file_path,
            "personalization": {
                "user_background": user_background,
                "academic_level": academic_level
            },
            "gemini_features_used": [
                "Multimodal audio understanding",
                "Educational content analysis",
                "Personalized learning insights",
                "Concept extraction",
                "Real-world application mapping"
            ]
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini processing failed: {str(e)}")
    finally:
        # Cleanup audio file after processing
        if os.path.exists(audio_file_path):
            os.unlink(audio_file_path)

@app.get("/api/gemini-capabilities", tags=["Video Processing"])
def get_gemini_capabilities(api_key: str = Depends(validate_api_key)):
    """🏆 SHOWCASE: Display Google Gemini's unique capabilities for the prize."""
    if not gemini_agent:
        return {"error": "Gemini not available", "setup_required": "GOOGLE_GEMINI_API_KEY"}
    
    return gemini_agent.get_gemini_capabilities()

@app.get("/api/orchestrator-info", tags=["Video Processing"])
def get_orchestrator_info(api_key: str = Depends(validate_api_key)):
    """🎯 SHOWCASE: Display Content Orchestrator and specialized agents information."""
    if not content_orchestrator:
        return {"error": "Content orchestrator not available", "setup_required": "GOOGLE_GEMINI_API_KEY"}
    
    return content_orchestrator.get_orchestrator_info()

@app.post("/api/test-single-agent", tags=["Video Processing"])
async def test_single_agent(
    agent_name: str = Form(...),
    test_work_order: str = Form(default='{"brief": "test", "bullets": ["test1", "test2"]}'),
    api_key: str = Depends(validate_api_key)
):
    """🔧 DEBUG: Test a single agent to identify issues."""
    if not content_orchestrator:
        raise HTTPException(status_code=503, detail="Content orchestrator not available")
    
    try:
        import json
        work_order = json.loads(test_work_order)
        
        # Mock context for testing
        mock_gemini_analysis = {
            "educational_analysis": {
                "subject": "Chemistry",
                "topic": "Chemical Bonds"
            }
        }
        mock_user_context = {
            "major": "Computer Science",
            "academicLevel": "College"
        }
        
        print(f"🧪 Testing single agent: {agent_name}")
        
        if agent_name not in content_orchestrator.agents:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {agent_name}")
        
        agent = content_orchestrator.agents[agent_name]
        result = await agent.generate_content(work_order, mock_gemini_analysis, mock_user_context)
        
        return {
            "agent_name": agent_name,
            "status": "success",
            "result": result,
            "test_work_order": work_order
        }
        
    except Exception as e:
        return {
            "agent_name": agent_name,
            "status": "failed",
            "error": str(e),
            "test_work_order": test_work_order
        }

@app.get("/api/view-content/{format_name}", tags=["Video Processing"])
def view_content_format(format_name: str, api_key: str = Depends(validate_api_key)):
    """📺 VIEW: Display generated content in readable format for frontend preview."""
    
    # This would normally come from a database or cache
    # For now, return a sample of what each format looks like
    
    sample_formats = {
        "hook_video": {
            "script": "Ready to unlock the secrets of projectile motion? Whether you're a computer science student or just curious about physics, this topic will change how you see moving objects forever! Today we'll explore how objects fly through the air, from basketball shots to rocket launches, using the same principles that power video game physics engines. Let's dive into the fascinating world of parabolic trajectories and discover the math behind the motion!",
            "hook_line": "Ready to unlock the secrets of projectile motion?",
            "estimated_duration": "45 seconds",
            "visual_suggestions": ["animated projectile paths", "split-screen comparisons"]
        },
        "concept_explanation": {
            "main_explanation": "Projectile motion is like programming a video game character's jump - you have horizontal movement (constant velocity) and vertical movement (affected by gravity). Think of it as two separate functions running simultaneously: one for X-coordinates and one for Y-coordinates.",
            "key_concepts": [
                {
                    "concept": "Horizontal Motion",
                    "explanation": "Moves at constant velocity, like a car on cruise control",
                    "analogy": "Like updating x-position in a game loop with constant velocity",
                    "example": "A ball thrown horizontally maintains its horizontal speed"
                }
            ]
        },
        "static_animation": {
            "javascript_code": "// Three.js Projectile Motion Animation\nconst scene = new THREE.Scene();\nconst camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);\n\n// Create projectile\nconst geometry = new THREE.SphereGeometry(0.1, 32, 32);\nconst material = new THREE.MeshPhongMaterial({color: 0xff6b6b});\nconst projectile = new THREE.Mesh(geometry, material);\n\n// Animation parameters\nlet t = 0;\nconst v0x = 10; // initial horizontal velocity\nconst v0y = 15; // initial vertical velocity\nconst g = -9.81; // gravity\n\nfunction animate() {\n    t += 0.01;\n    \n    // Update position using kinematic equations\n    projectile.position.x = v0x * t;\n    projectile.position.y = v0y * t + 0.5 * g * t * t;\n    \n    if (projectile.position.y < 0) t = 0; // Reset when hits ground\n    \n    renderer.render(scene, camera);\n    requestAnimationFrame(animate);\n}",
            "description": "Interactive 3D visualization showing parabolic trajectory with real physics"
        },
        "practice_problems": {
            "questions": [
                {
                    "question": "In a video game, a character jumps with initial velocity 20 m/s horizontally and 15 m/s vertically. How far does the character travel horizontally before landing?",
                    "options": ["30.6 m", "45.2 m", "61.2 m", "52.8 m"],
                    "correct_answer": "61.2 m",
                    "explanation": "Use kinematic equations: time of flight = 2*v0y/g, then horizontal distance = v0x * time"
                }
            ]
        }
    }
    
    if format_name not in sample_formats:
        raise HTTPException(status_code=404, detail=f"Format '{format_name}' not found")
    
    return {
        "format_name": format_name,
        "content": sample_formats[format_name],
        "frontend_usage": {
            "hook_video": "Display script with video player UI, show visual suggestions as thumbnails",
            "concept_explanation": "Render as expandable cards with analogies highlighted",
            "static_animation": "Embed Three.js code in canvas component with play/pause controls",
            "practice_problems": "Interactive quiz component with immediate feedback"
        }.get(format_name, "Render as structured content with appropriate UI components")
    }

# Removed Gemini debug models endpoint

@app.post("/api/process-video", tags=["Video Processing"])
async def process_video_pipeline(
    video: UploadFile = File(...),
    user_background: Optional[str] = Form(default="general"),
    academic_level: Optional[str] = Form(default="general"),
    mode: Optional[str] = Form(default="speed"),
    model: Optional[str] = Form(default=None),
    work_orders_mode: Optional[str] = Form(default="guided"),
    api_key: str = Depends(validate_api_key)
):
    """
    Single pipeline: upload video -> extract audio -> Gemini Flash analysis + content strategy.
    """
    if not gemini_agent:
        raise HTTPException(status_code=503, detail="Gemini not available")

    if not video.content_type or not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    if video.size and video.size > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video file too large (max 100MB)")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        content = await video.read()
        temp_video.write(content)
        temp_video_path = temp_video.name

    try:
        extraction = video_processor.extract_audio(temp_video_path, return_info=True)
        audio_path = extraction["audio_path"] if isinstance(extraction, dict) else extraction

        user_context = {
            "major": user_background,
            "academicLevel": academic_level,
            "prefer_fast": mode == "speed",
            "force_model": model,
            "work_orders_mode": work_orders_mode
        }

        analysis = gemini_agent.transcribe_and_analyze(audio_path, user_context)
        return {
            "pipeline": "video->audio->gemini",
            "extraction": extraction,
            "analysis": analysis,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
    finally:
        if os.path.exists(temp_video_path):
            os.unlink(temp_video_path)

@app.post("/api/process-video-complete", tags=["Video Processing"])
async def process_video_complete_pipeline(
    video: UploadFile = File(...),
    user_background: Optional[str] = Form(default="general"),
    academic_level: Optional[str] = Form(default="general"),
    mode: Optional[str] = Form(default="speed"),
    model: Optional[str] = Form(default=None),
    work_orders_mode: Optional[str] = Form(default="guided"),
    auth_token: Optional[str] = Form(default=None),
    api_key: str = Depends(validate_api_key)
):
    """
    🚀 COMPLETE PIPELINE: Video → Audio → Gemini Analysis → 8 Specialized Agents → Learning Formats
    
    This is the full EduTransform AI pipeline that generates all 8 personalized learning formats:
    1. Hook Video, 2. Concept Explanation, 3. Static Animation, 4. Code/Equations,
    5. Visual Diagrams, 6. Practice Problems, 7. Real-world Applications, 8. Summary Cards
    
    🔑 Authentication Enhancement:
    - If auth_token (JWT) is provided, user preferences will be automatically retrieved
    - User preferences override form parameters for enhanced personalization
    - Includes: major, academicLevel, dyslexiaSupport, languagePreference, learningStyles, age
    - Falls back to form parameters if auth_token is invalid/missing
    """
    if not gemini_agent or not content_orchestrator:
        missing = []
        if not gemini_agent:
            missing.append("Gemini agent")
        if not content_orchestrator:
            missing.append("Content orchestrator")
        raise HTTPException(
            status_code=503, 
            detail=f"Required services not available: {', '.join(missing)}"
        )

    if not video.content_type or not video.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    if video.size and video.size > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Video file too large (max 100MB)")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        content = await video.read()
        temp_video.write(content)
        temp_video_path = temp_video.name

    try:
        print("🎬 Step 1: Extracting audio from video...")
        extraction = video_processor.extract_audio(temp_video_path, return_info=True)
        audio_path = extraction["audio_path"] if isinstance(extraction, dict) else extraction

        # Build user context - start with form parameters as defaults
        user_context = {
            "major": user_background,
            "academicLevel": academic_level,
            "prefer_fast": mode == "speed",
            "force_model": model,
            "work_orders_mode": work_orders_mode
        }
        
        # If auth_token provided, get user profile and merge preferences
        if auth_token:
            try:
                print("👤 Getting user profile from auth token...")
                user_id = get_current_user_id(f"Bearer {auth_token}")
                if user_id:
                    user_profile = db_client.get_user_by_id(user_id)
                    if user_profile and 'preferences' in user_profile:
                        prefs = user_profile['preferences']
                        # Override defaults with user preferences
                        user_context.update({
                            "major": prefs.get('major', user_context["major"]),
                            "academicLevel": prefs.get('academicLevel', user_context["academicLevel"]),
                            "dyslexiaSupport": prefs.get('dyslexiaSupport', False),
                            "languagePreference": prefs.get('languagePreference', 'English'),
                            "learningStyles": prefs.get('learningStyles', []),
                            "age": prefs.get('age'),
                            "userName": user_profile.get('name'),
                            "userId": user_id
                        })
                        print(f"✅ Enhanced context with user preferences for: {user_profile.get('name')}")
                    else:
                        print("⚠️ User profile not found or missing preferences")
                else:
                    print("⚠️ Invalid auth token - user ID not found")
            except Exception as e:
                print(f"⚠️ Error retrieving user profile: {str(e)} - continuing with form parameters")
                # Continue with form parameters if auth fails

        print("🧠 Step 2: Gemini analysis and work order generation...")
        analysis = gemini_agent.transcribe_and_analyze(audio_path, user_context)
        
        print("🎯 Step 3: Orchestrating 8 specialized content agents...")
        work_orders = analysis.get("work_orders", {})
        gemini_analysis = analysis.get("gemini_analysis", {})
        
        # Run the complete orchestration
        orchestration_result = await content_orchestrator.orchestrate_content_generation(
            work_orders=work_orders,
            gemini_analysis=gemini_analysis,
            user_context=user_context
        )
        
        print("🎉 Complete pipeline finished successfully!")
        
        return {
            "pipeline": "video->audio->gemini->orchestrator->8_agents",
            "extraction": extraction,
            "gemini_analysis": analysis,
            "content_generation": orchestration_result,
            "processing_summary": {
                "total_steps": 3,
                "video_processed": True,
                "gemini_analysis_complete": True,
                "agents_executed": orchestration_result.get("orchestration_summary", {}).get("total_agents", 0),
                "learning_formats_generated": len(orchestration_result.get("learning_formats", {}))
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Complete pipeline failed: {str(e)}")
    finally:
        if os.path.exists(temp_video_path):
            os.unlink(temp_video_path)

@app.get("/api/processing-status/{job_id}", tags=["Video Processing"])
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