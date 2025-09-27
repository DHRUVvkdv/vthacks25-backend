from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# SQLite database for hackathon simplicity
DATABASE_URL = "sqlite:///./vthacks_users.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    age = Column(Integer)
    academic_level = Column(String(50))
    major = Column(String(100))
    dyslexia_support = Column(Boolean, default=False)
    language_preference = Column(String(50), default="English")
    learning_styles = Column(JSON)  # Store as JSON array
    metadata = Column(JSON)  # Store additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VideoProcessingHistory(Base):
    __tablename__ = "video_processing_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Foreign key to users
    filename = Column(String(255))
    transcript = Column(Text)
    concepts = Column(JSON)
    user_context = Column(JSON)
    processing_status = Column(String(50), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
