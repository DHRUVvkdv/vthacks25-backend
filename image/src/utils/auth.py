import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional
import os
from fastapi import HTTPException, status

# Simple JWT configuration for hackathon
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "vthacks_2025_jwt_secret_key_for_demo")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class AuthManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except JWTError as e:
            if "expired" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

def get_current_user_id(authorization: Optional[str] = None) -> Optional[str]:
    """Extract user ID from JWT token (optional for hackathon demo)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    token = authorization.split(" ")[1]
    try:
        payload = AuthManager.verify_token(token)
        return payload.get("user_id")
    except (HTTPException, JWTError):
        return None
