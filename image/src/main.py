from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from mangum import Mangum
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Simple API key from environment
API_KEY = os.getenv("API_KEY", "vth_hackathon_2025_secret_key")

app = FastAPI(title="VTHacks 2025 Backend", version="1.0.0")

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# API Key security
api_key_header = APIKeyHeader(name="X-API-Key")

def validate_api_key(x_api_key: str = Depends(api_key_header)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

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

# Lambda handler
handler = Mangum(app)

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)