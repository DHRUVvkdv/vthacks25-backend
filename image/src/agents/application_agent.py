import json
from typing import Dict, Any
from .base_agent import BaseContentAgent


class ApplicationAgent(BaseContentAgent):
    """Generates real-world applications and examples."""
    
    async def generate_content(self, work_order: Dict[str, Any], gemini_analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        examples = work_order.get("examples", [])
        
        prompt = f"""
        Generate real-world applications and practical examples for educational content.
        
        {user_bg}
        {subject_context}
        
        Application examples: {', '.join(examples) if isinstance(examples, list) else str(examples)}
        
        Return as JSON:
        {{
            "real_world_applications": [
                {{
                    "application": "specific real-world use",
                    "description": "detailed explanation",
                    "industry": "relevant industry/field",
                    "example_scenario": "concrete example",
                    "connection_to_concept": "how it relates to the topic"
                }}
            ],
            "career_connections": "how this applies to user's career path",
            "everyday_examples": ["example1", "example2"],
            "case_studies": [
                {{
                    "title": "case study title",
                    "description": "brief case study",
                    "outcome": "what happened",
                    "lesson": "key learning"
                }}
            ],
            "future_implications": "where this field is heading"
        }}
        
        Output pure JSON only.
        """
        
        try:
            response = await self._call_gemini(prompt)
            result = json.loads(self._strip_code_fences(response))
            result["agent"] = "application"
            return result
        except:
            return {
                "agent": "application",
                "real_world_applications": [{"application": "Practical use in industry", "description": "How this concept applies in professional settings", "industry": user_context.get("major", "Various fields"), "example_scenario": "Real-world scenario", "connection_to_concept": "Direct application of learned concepts"}],
                "career_connections": f"This directly applies to careers in {user_context.get('major', 'your field')}",
                "everyday_examples": ["Daily life example 1", "Daily life example 2"],
                "case_studies": [{"title": "Real Application", "description": "How this was used successfully", "outcome": "Positive results", "lesson": "Key takeaway"}],
                "future_implications": "This field continues to evolve and create new opportunities",
                "status": "fallback_generated"
            }
