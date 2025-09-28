import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import google.genai as genai
import threading


class GeminiAPIKeyManager:
    """
    Manages multiple Gemini API keys for round-robin usage to bypass rate limits.
    Thread-safe implementation for true parallelization.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.api_keys = self._load_api_keys()
            self.clients = self._create_clients()
            self.current_index = 0
            self.usage_lock = threading.Lock()
            self.initialized = True
            print(f"🔑 GeminiAPIKeyManager initialized with {len(self.api_keys)} API keys")
    
    def _load_api_keys(self) -> List[str]:
        """Load all available API keys from environment variables."""
        keys = []
        
        # Primary key
        primary_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        if primary_key:
            keys.append(primary_key)
        
        # Secondary keys (GOOGLE_GEMINI_API_KEY_2, GOOGLE_GEMINI_API_KEY_3, etc.)
        for i in range(2, 10):  # Support up to 10 keys
            key = os.getenv(f"GOOGLE_GEMINI_API_KEY_{i}")
            if key:
                keys.append(key)
        
        if not keys:
            raise ValueError("At least one GOOGLE_GEMINI_API_KEY is required")
        
        return keys
    
    def _create_clients(self) -> List[genai.Client]:
        """Create Gemini clients for each API key."""
        clients = []
        for i, api_key in enumerate(self.api_keys):
            try:
                client = genai.Client(api_key=api_key, vertexai=False)
                clients.append(client)
                print(f"✅ API key {i+1} client created successfully")
            except Exception as e:
                print(f"❌ Failed to create client for API key {i+1}: {str(e)}")
        
        if not clients:
            raise ValueError("No valid Gemini clients could be created")
        
        return clients
    
    def get_next_client(self) -> genai.Client:
        """Get the next client in round-robin fashion (thread-safe)."""
        with self.usage_lock:
            client = self.clients[self.current_index]
            key_index = self.current_index + 1
            self.current_index = (self.current_index + 1) % len(self.clients)
            print(f"🔄 Using API key {key_index}/{len(self.clients)}")
            return client
    
    def get_client_count(self) -> int:
        """Get the number of available clients."""
        return len(self.clients)


class BaseContentAgent(ABC):
    """
    Base class for all specialized content generation agents.
    
    Provides common functionality like Gemini client access and standardized interfaces.
    """
    
    def __init__(self):
        # Initialize API key manager for round-robin client usage
        self.api_manager = GeminiAPIKeyManager()
        self.model_name = 'models/gemini-2.5-flash'
        print(f"🔧 Agent initialized with {self.api_manager.get_client_count()} API keys available")
        
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
        """Make a call to Gemini with round-robin API key selection and error handling."""
        import asyncio
        start_time = time.time()
        
        # Get next available client (round-robin)
        client = self.api_manager.get_next_client()
        
        try:
            print(f"🤖 Making Gemini API call... (prompt length: {len(prompt)} chars)")
            
            # Run the synchronous Gemini call in a thread pool to make it truly async
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
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
