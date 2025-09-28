import json
from typing import Dict, Any
from .base_agent import BaseContentAgent


class SummaryAgent(BaseContentAgent):
    """Generates key concept summaries and learning cards."""
    
    async def generate_content(self, work_order: Dict[str, Any], gemini_analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        key_points = work_order.get("key_points", [])
        
        # Get language instruction
        language_instruction = self._get_language_instruction(user_context)
        
        prompt = f"""
        Generate concise summaries and learning cards for educational content.
        
        {user_bg}
        {subject_context}
        {language_instruction}
        
        Key points to summarize: {', '.join(key_points)}
        
        Return as JSON:
        {{
            "executive_summary": "2-3 sentence overview of the entire topic",
            "key_takeaways": [
                {{
                    "concept": "key concept",
                    "summary": "brief explanation",
                    "importance": "why it matters",
                    "memory_aid": "how to remember it"
                }}
            ],
            "learning_cards": [
                {{
                    "front": "question or concept",
                    "back": "answer or explanation",
                    "category": "concept category",
                    "difficulty": "easy/medium/hard"
                }}
            ],
            "review_checklist": ["item1", "item2"],
            "next_learning_steps": "what to study next"
        }}
        
        Output pure JSON only.
        """
        
        try:
            response = await self._call_gemini(prompt)
            result = json.loads(self._strip_code_fences(response))
            result["agent"] = "summary"
            return result
        except:
            return {
                "agent": "summary",
                "executive_summary": f"This topic covers {', '.join(key_points[:3])}, providing fundamental understanding for {user_context.get('major', 'students')}.",
                "key_takeaways": [{"concept": point, "summary": f"Key understanding of {point}", "importance": "Essential for foundational knowledge", "memory_aid": f"Remember {point} as a building block"} for point in key_points[:4]],
                "learning_cards": [{"front": f"What is {point}?", "back": f"Explanation of {point}", "category": "core_concept", "difficulty": "medium"} for point in key_points[:5]],
                "review_checklist": key_points[:6],
                "next_learning_steps": "Practice with examples and explore advanced applications",
                "status": "fallback_generated"
            }
