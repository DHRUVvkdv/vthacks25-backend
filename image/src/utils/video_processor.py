import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Union

import ffmpeg
import openai
from fastapi import HTTPException


class VideoProcessor:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def extract_audio(self, video_path: str, return_info: bool = False) -> Union[str, Dict[str, Any]]:
        """Extract audio from video file using ffmpeg."""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                audio_path = temp_audio.name
            
            # Get video info first
            probe = ffmpeg.probe(video_path)
            video_info = {
                "duration": float(probe['format']['duration']),
                "size": int(probe['format']['size']),
                "format": probe['format']['format_name'],
                "streams": len(probe['streams'])
            }
            
            # Extract audio using ffmpeg-python
            # Optimized settings for speech-to-text APIs:
            # - 16kHz sample rate (optimal for speech recognition)
            # - mono channel (reduces file size)
            # - PCM 16-bit (uncompressed, high quality)
            (
                ffmpeg
                .input(video_path)
                .output(
                    audio_path, 
                    acodec='pcm_s16le',  # 16-bit PCM
                    ar=16000,            # 16kHz sample rate
                    ac=1                 # mono channel
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # Get audio file info
            audio_size = os.path.getsize(audio_path)
            
            if return_info:
                return {
                    "audio_path": audio_path,
                    "video_info": video_info,
                    "audio_info": {
                        "path": audio_path,
                        "size_bytes": audio_size,
                        "size_mb": round(audio_size / (1024 * 1024), 2),
                        "sample_rate": 16000,
                        "channels": 1,
                        "format": "WAV (PCM 16-bit)"
                    },
                    "extraction_status": "success"
                }
            
            return audio_path
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            raise HTTPException(
                status_code=500, 
                detail=f"Audio extraction failed: {error_msg}"
            )
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio using OpenAI Whisper API."""
        try:
            with open(audio_path, "rb") as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"
                )
            
            return {
                "text": transcript.text,
                "language": "en"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {str(e)}"
            )
    
    def extract_concepts(self, transcript: str) -> Dict[str, Any]:
        """Extract key concepts from transcript using GPT-4."""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an educational content analyzer. Extract key concepts, topics, 
                        and learning objectives from educational video transcripts. Return a structured analysis."""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this educational video transcript and extract:
                        1. Main subject/topic
                        2. Key concepts (5-10 main ideas)
                        3. Learning objectives
                        4. Difficulty level (beginner/intermediate/advanced)
                        5. Estimated duration in minutes
                        
                        Transcript: {transcript[:3000]}...
                        
                        Return as structured JSON."""
                    }
                ],
                temperature=0.3
            )
            
            # Parse the response - for now return a structured format
            content = response.choices[0].message.content
            
            return {
                "analysis": content,
                "word_count": len(transcript.split()),
                "estimated_duration": max(1, len(transcript.split()) // 150)  # ~150 words per minute
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Concept extraction failed: {str(e)}"
            )
    
    def process_video(self, video_path: str) -> Dict[str, Any]:
        """Complete video processing pipeline."""
        audio_path = None
        try:
            # Step 1: Extract audio
            audio_path = self.extract_audio(video_path)
            
            # Step 2: Transcribe audio
            transcript_data = self.transcribe_audio(audio_path)
            
            # Step 3: Extract concepts
            concepts_data = self.extract_concepts(transcript_data["text"])
            
            return {
                "transcript": transcript_data,
                "concepts": concepts_data,
                "status": "success"
            }
            
        finally:
            # Cleanup temporary files
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)
            if os.path.exists(video_path):
                os.unlink(video_path)
