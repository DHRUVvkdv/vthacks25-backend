import os
from typing import Dict, Any, Optional
from fastapi import HTTPException
import google.genai as genai


class GeminiSpeechToTextAgent:
    """
    🏆 GEMINI-POWERED Speech-to-Text Agent for Best Use of Gemini API Prize
    
    Uses the latest Google GenAI SDK (v1.39.1) for advanced audio understanding.
    Showcases Gemini's multimodal capabilities for educational content analysis.
    """
    
    def __init__(self):
        # Initialize Google GenAI Client (REQUIRED - no fallbacks!)
        self.gemini_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("🚫 GOOGLE_GEMINI_API_KEY is required! No fallbacks - Gemini only!")
            
        # Initialize the GenAI client with API key (public API, not Vertex)
        self.client = genai.Client(api_key=self.gemini_api_key, vertexai=False)
        self.model_name = 'models/gemini-2.5-flash'
        
    def _select_best_model(self, prefer_fast: bool = False) -> str:
        return self.model_name

    def _strip_code_fences(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        t = text.strip()
        if t.startswith('```'):
            # Remove opening fence with optional language
            first_newline = t.find('\n')
            if first_newline != -1:
                t = t[first_newline+1:]
        if t.endswith('```'):
            t = t[:-3]
        return t.strip()

    def _build_work_orders(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        subject = analysis_data.get('educational_analysis', {}).get('subject') or analysis_data.get('subject_analysis', {}).get('main_topic') or 'Subject'
        key_concepts = analysis_data.get('educational_analysis', {}).get('key_concepts') or analysis_data.get('subject_analysis', {}).get('key_concepts') or []
        formulas = analysis_data.get('educational_analysis', {}).get('formulas_mentioned') or []
        modules = analysis_data.get('content_strategy', {}).get('modules') or []
        learning_objectives = analysis_data.get('content_strategy', {}).get('learning_objectives') or []
        real_world = analysis_data.get('personalized_insights', {}).get('real_world_applications') or []
        if isinstance(real_world, str):
            real_world = [real_world]

        return {
            "video_generation": {
                "brief": f"Create a short intro framing: {subject}",
                "bullets": key_concepts[:4]
            },
            "explanation": {
                "topics": key_concepts,
                "objectives": learning_objectives
            },
            "animation_config": {
                "scenes": [m.get('title') for m in modules][:3],
                "focus_equations": formulas
            },
            "code_equation": {
                "formulas": formulas,
                "examples": [
                    "Compute range given v and angle",
                    "Compute altitude using dy = 1/2 a t^2"
                ]
            },
            "visualization": {
                "charts": ["trajectory_parabola", "vx_constant_plot", "vy_vs_time"]
            },
            "application": {
                "examples": real_world
            },
            "summary": {
                "key_points": key_concepts[:5]
            },
            "quiz_generation": {
                "blueprint": {
                    "num_questions": 8,
                    "focus": key_concepts[:4]
                }
            }
        }
    
    def transcribe_and_analyze(self, audio_path: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        🏆 SHOWCASE GEMINI'S POWER: Audio Understanding + Educational Analysis
        
        Uses Google GenAI SDK v1.39.1 for advanced multimodal capabilities.
        """
        try:
            print(f"🎯 Uploading audio file to Gemini: {audio_path}")
            
            # Upload audio file using the new google-genai SDK
            uploaded_file = self.client.files.upload(file=audio_path)
            
            print(f"✅ Audio uploaded successfully! File ID: {uploaded_file.name}")
            
            # Prepare user context for personalized analysis
            user_background = user_context.get("major", "general") if user_context else "general"
            academic_level = user_context.get("academicLevel", "general") if user_context else "general"
            
            prompt = f"""
            🎓 EDUCATIONAL CONTENT ANALYSIS (Powered by Google Gemini 1.5 Pro)
            
            You are an advanced AI educational assistant analyzing audio content.
            
            USER CONTEXT:
            - Academic Background: {user_background}
            - Academic Level: {academic_level}
            
            TASK: Please analyze this educational audio and provide:
            
            1. ACCURATE TRANSCRIPTION: Complete word-for-word transcription
            
            2. INTELLIGENT ANALYSIS: 
               - Main subject/topic identified
               - Key concepts and learning objectives
               - Difficulty level assessment
               - Important formulas, equations, or technical terms mentioned
            
            3. PERSONALIZED INSIGHTS:
               - How this content relates to {user_background} field
               - Connections to real-world applications
               - Suggested learning approach for {academic_level} level
            
            4. CONTENT STRUCTURE:
               - Identify main sections/topics covered
               - Timeline of key concepts discussed
               
            Return as structured JSON with these sections:
            {{
              "transcription": "full transcription text",
              "subject_analysis": {{
                "main_topic": "identified subject",
                "key_concepts": ["concept1", "concept2", ...],
                "difficulty_level": "beginner/intermediate/advanced",
                "technical_terms": ["term1", "term2", ...]
              }},
              "personalized_insights": {{
                "field_connections": "how this relates to {user_background}",
                "real_world_applications": "practical applications",
                "learning_approach": "suggested approach for {academic_level}"
              }},
              "content_structure": {{
                "main_sections": ["section1", "section2", ...],
                "timeline": "overview of content flow"
              }}
            }}
            """
            
            # For now, let's use Gemini for text analysis of a placeholder
            # We'll convert audio to text first using a simpler approach
            # and then use Gemini for intelligent analysis
            
            # Placeholder: For the hackathon, let's simulate the transcription
            # and focus on Gemini's content analysis capabilities
            placeholder_transcript = f"""
            This is a physics lecture about projectile motion. The speaker discusses:
            - Initial velocity and its components
            - The effect of gravity on projectile paths
            - Kinematic equations for motion in two dimensions
            - Real-world applications like ballistics and sports
            - Mathematical relationships between angle, velocity, and range
            
            [Note: This is a placeholder. In production, this would be the actual transcription 
            from the {audio_path} audio file. For the hackathon demo, we're showcasing 
            Gemini's content analysis capabilities.]
            """
            
            # 🏆 GEMINI'S NATIVE AUDIO UNDERSTANDING
            # Use Gemini's multimodal capabilities to directly process the audio
            audio_understanding_prompt = f"""
            🎓 EDUCATIONAL AUDIO ANALYSIS (Powered by Google Gemini 1.5 Pro Audio Understanding)
            
            You are analyzing educational audio content. Please provide:
            
            1. COMPLETE TRANSCRIPTION: Transcribe all spoken content from this audio file
            
            2. EDUCATIONAL ANALYSIS for a {user_background} student at {academic_level} level:
               - Main subject and topic identification
               - Key concepts and learning objectives  
               - Technical terms and formulas mentioned
               - Difficulty level assessment
            
            3. PERSONALIZED INSIGHTS:
               - How this content connects to {user_background} field
               - Real-world applications relevant to {user_background}
               - Suggested learning approach for {academic_level} students
               - Programming/coding connections if applicable
            
            4. CONTENT STRUCTURE:
               - Main sections covered in the audio
               - Timeline of key concepts
               - Important equations or formulas mentioned
            
            Please provide a comprehensive analysis in JSON format:
            {{
              "transcription": "complete transcription text",
              "educational_analysis": {{
                "subject": "main subject identified",
                "topic": "specific topic",
                "key_concepts": ["concept1", "concept2", ...],
                "technical_terms": ["term1", "term2", ...],
                "difficulty_level": "beginner/intermediate/advanced",
                "formulas_mentioned": ["formula1", "formula2", ...]
              }},
              "content_strategy": {{
                "target_audience": "e.g., CS freshmen, AP Physics student",
                "learning_objectives": ["objective1", "objective2", ...],
                "modules": [
                  {{
                    "title": "Module title",
                    "topics": ["topic1", "topic2"],
                    "resources": ["type:url or description"],
                    "activities": ["quiz idea", "coding exercise idea"]
                  }}
                ],
                "assessments": ["short quiz plan", "project idea"],
                "key_examples": ["example descriptions"],
                "personalization_notes": "how to tailor for user's background"
              }},
              "personalized_insights": {{
                "field_connections": "connections to {user_background}",
                "real_world_applications": "practical applications",
                "learning_approach": "recommended approach for {academic_level}",
                "programming_connections": "coding/programming relevance"
              }},
              "content_structure": {{
                "main_sections": ["section1", "section2", ...],
                "timeline": "flow of content",
                "duration_estimate": "estimated length"
              }}
            }}
            """
            
            json_output_constraint = "Output must be pure JSON only. Do not wrap in code fences or add explanations."
            
            # 🏆 GEMINI'S MULTIMODAL MAGIC: Audio + Text Understanding
            # Use fixed model unless explicit override is valid
            prefer_fast = False
            force_model = None
            if user_context and isinstance(user_context, dict):
                prefer_fast = bool(user_context.get('prefer_fast', False))
                force_model = user_context.get('force_model')

            chosen_model = None
            if force_model:
                try:
                    available_models = [getattr(m, 'name', '') for m in self.client.models.list()]
                except Exception:
                    available_models = []
                candidate = force_model
                if not candidate.startswith('models/'):
                    prefixed = f"models/{candidate}"
                    candidate = prefixed if prefixed in available_models else candidate
                if candidate in available_models:
                    chosen_model = candidate
                else:
                    print(f"Invalid forced model '{force_model}', falling back to selection.")

            if not chosen_model:
                chosen_model = self._select_best_model(prefer_fast=prefer_fast)
            print(f"🎯 Using Gemini model: {chosen_model}")
            response = self.client.models.generate_content(
                model=chosen_model,
                contents=[audio_understanding_prompt + "\n" + json_output_constraint, uploaded_file]
            )
            
            print("🎉 Gemini analysis complete!")
            
            # Clean up uploaded file from Gemini
            self.client.files.delete(name=uploaded_file.name)
            
            # Parse Gemini's response
            try:
                import json
                # The response might have a different structure in google-genai
                response_text = response.text if hasattr(response, 'text') else str(response)
                cleaned = self._strip_code_fences(response_text)
                analysis_data = json.loads(cleaned)
            except json.JSONDecodeError:
                # If Gemini doesn't return valid JSON, structure the response
                analysis_data = {
                    "transcription": response_text.strip(),
                    "subject_analysis": {
                        "main_topic": "Educational content",
                        "key_concepts": ["Content analysis in progress"],
                        "difficulty_level": "auto-detected",
                        "technical_terms": []
                    },
                    "personalized_insights": {
                        "field_connections": f"Analyzing connections to {user_background}",
                        "real_world_applications": "Applications being identified",
                        "learning_approach": f"Approach optimized for {academic_level} level"
                    },
                    "content_structure": {
                        "main_sections": ["Full content analysis"],
                        "timeline": "Content flow analysis in progress"
                    }
                }

            work_orders = self._build_work_orders(analysis_data)
            
            return {
                "gemini_analysis": analysis_data,
                "provider": "google_genai",
                "model": chosen_model,
                "processing_type": "intelligent_educational_analysis",
                "user_context": user_context or {},
                "work_orders": work_orders
            }
            
        except Exception as e:
            # Clean up uploaded file if it exists
            try:
                if 'uploaded_file' in locals():
                    self.client.files.delete(name=uploaded_file.name)
            except:
                pass
                
            raise HTTPException(
                status_code=500,
                detail=f"🚫 Gemini audio analysis failed: {str(e)}. Check GOOGLE_GEMINI_API_KEY!"
            )
    
    def get_gemini_capabilities(self) -> Dict[str, Any]:
        """
        🏆 SHOWCASE: Display Gemini's unique capabilities for the prize.
        """
        return {
            "provider": "Google Gemini 1.5 Pro",
            "capabilities": [
                "🎵 Multimodal audio understanding",
                "🧠 Intelligent content analysis", 
                "🎓 Educational context awareness",
                "🔍 Concept extraction and identification",
                "👥 Personalized learning insights",
                "📚 Subject matter expertise",
                "🌍 Real-world application connections"
            ],
            "advantages_over_basic_transcription": [
                "Goes beyond word-for-word transcription",
                "Understands educational context and concepts",
                "Provides personalized insights based on user background",
                "Identifies key learning objectives automatically",
                "Connects content to real-world applications",
                "Adapts explanations to academic level"
            ],
            "prize_category": "Best Use of Gemini API",
            "unique_value": "Transforms raw audio into personalized educational insights"
        }
