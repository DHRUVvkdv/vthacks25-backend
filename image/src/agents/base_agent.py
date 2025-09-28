import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import google.genai as genai


class BaseContentAgent(ABC):
    """
    Base class for all specialized content generation agents.
    
    Provides common functionality like Gemini client access and standardized interfaces.
    """
    
    def __init__(self):
        # Initialize Gemini client (shared across agents)
        self.gemini_api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY is required for content agents")
            
        self.client = genai.Client(api_key=self.gemini_api_key, vertexai=False)
        self.model_name = 'models/gemini-2.5-flash'
        
    @abstractmethod
    async def generate_content(
        self, 
        work_order: Dict[str, Any], 
        gemini_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate content based on work order and context.
        
        Args:
            work_order: Specific instructions for this agent
            gemini_analysis: Full analysis from Gemini for context
            user_context: User preferences and background
            
        Returns:
            Generated content specific to this agent's purpose
        """
        pass
    
    def _get_user_background_context(self, user_context: Dict[str, Any]) -> str:
        """Extract user background for personalization."""
        major = user_context.get("major", "general")
        academic_level = user_context.get("academicLevel", "general")
        return f"User background: {major} student at {academic_level} level"
    
    def _get_language_instruction(self, user_context: Dict[str, Any]) -> str:
        """Extract language preference and create instruction for LLM."""
        language_preference = user_context.get("languagePreference", "English")
        if language_preference and language_preference.lower() != "english":
            return f"\n\nIMPORTANT: Respond in {language_preference} language. All content, explanations, and text should be in {language_preference}."
        return ""
    
    def _get_subject_context(self, gemini_analysis: Dict[str, Any]) -> str:
        """Extract subject and topic from Gemini analysis."""
        educational_analysis = gemini_analysis.get("educational_analysis", {})
        subject = educational_analysis.get("subject", "General")
        topic = educational_analysis.get("topic", "Educational content")
        return f"Subject: {subject}, Topic: {topic}"
    
    async def _call_gemini(self, prompt: str) -> str:
        """Make a call to Gemini with error handling."""
        import asyncio
        start_time = time.time()
        try:
            print(f"🤖 Making Gemini API call... (prompt length: {len(prompt)} chars)")
            
            # Run the synchronous Gemini call in a thread pool to make it truly async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt]
                )
            )
            
            api_time = time.time() - start_time
            print(f"✅ Gemini API call completed in {api_time:.2f}s")
            return response.text if hasattr(response, 'text') else str(response)
        except Exception as e:
            api_time = time.time() - start_time
            print(f"❌ Gemini API call FAILED after {api_time:.2f}s: {str(e)}")
            raise Exception(f"Gemini API call failed: {str(e)}")
    
    def _strip_code_fences(self, text: str) -> str:
        """Remove code fences from Gemini responses."""
        if not isinstance(text, str):
            return text
        t = text.strip()
        if t.startswith('```'):
            first_newline = t.find('\n')
            if first_newline != -1:
                t = t[first_newline+1:]
        if t.endswith('```'):
            t = t[:-3]
        return t.strip()
