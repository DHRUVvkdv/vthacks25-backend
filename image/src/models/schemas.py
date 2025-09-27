from pydantic import BaseModel, validator
from typing import List, Optional, Any, Dict
from datetime import datetime

class UserSignupRequest(BaseModel):
    name: str
    username: str
    password: str
    confirmPassword: str
    age: int
    academicLevel: str
    major: str
    dyslexiaSupport: bool = False
    languagePreference: str = "English"
    learningStyles: List[str] = []
    metadata: List[Any] = []
    
    @validator('confirmPassword')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('username')
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v
    
    @validator('age')
    def age_valid(cls, v):
        if v < 5 or v > 120:
            raise ValueError('Age must be between 5 and 120')
        return v

class UserSigninRequest(BaseModel):
    username: str
    password: str

class UserPreferencesUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    academicLevel: Optional[str] = None
    major: Optional[str] = None
    dyslexiaSupport: Optional[bool] = None
    languagePreference: Optional[str] = None
    learningStyles: Optional[List[str]] = None
    metadata: Optional[List[Any]] = None

class UserResponse(BaseModel):
    id: str  # Changed from int to str for DynamoDB UUID
    name: str
    username: str
    age: int
    academicLevel: str
    major: str
    dyslexiaSupport: bool
    languagePreference: str
    learningStyles: List[str]
    metadata: List[Any]
    created_at: str  # Changed from datetime to str for DynamoDB ISO format
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class VideoProcessingRequest(BaseModel):
    user_background: Optional[str] = None
    subject_preference: Optional[str] = None
    
    # These will be populated from user preferences if user is authenticated
    academic_level: Optional[str] = None
    major: Optional[str] = None
    language_preference: Optional[str] = None
    dyslexia_support: Optional[bool] = None
    learning_styles: Optional[List[str]] = None
