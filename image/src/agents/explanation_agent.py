import json
from typing import Dict, Any
from .base_agent import BaseContentAgent


class ExplanationAgent(BaseContentAgent):
    """
    Generates personalized explanations with analogies and connections.
    
    Creates detailed explanations tailored to the user's background,
    using appropriate analogies and connecting to their field of study.
    """
    
    async def generate_content(
        self, 
        work_order: Dict[str, Any], 
        gemini_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized explanations."""
        
        # Extract context
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        topics = work_order.get("topics", [])
        objectives = work_order.get("objectives", [])
        
        # Get additional context from Gemini analysis
        personalized_insights = gemini_analysis.get("personalized_insights", {})
        field_connections = personalized_insights.get("field_connections", "")
        
        # Get language instruction
        language_instruction = self._get_language_instruction(user_context)
        
        prompt = f"""
        Create a comprehensive yet accessible explanation of the educational content.
        
        {user_bg}
        {subject_context}
        {language_instruction}
        
        Topics to explain: {', '.join(topics)}
        Learning objectives: {', '.join(objectives)}
        
        Field connections: {field_connections}
        
        Your explanation should:
        1. Use analogies relevant to the user's background
        2. Connect concepts to their field of study
        3. Build from simple to complex concepts
        4. Include practical examples
        5. Be engaging and conversational
        6. Address common misconceptions
        
        Return as JSON:
        {{
            "main_explanation": "Comprehensive explanation of the topic",
            "key_concepts": [
                {{
                    "concept": "concept name",
                    "explanation": "detailed explanation",
                    "analogy": "relevant analogy for user's background",
                    "example": "concrete example"
                }}
            ],
            "connections_to_user_field": "How this relates to user's background",
            "common_misconceptions": ["misconception 1", "misconception 2"],
            "difficulty_progression": "How concepts build on each other",
            "practical_applications": ["application 1", "application 2"],
            "next_steps": "What to learn next"
        }}
        
        Output pure JSON only.
        """
        
        try:
            response = await self._call_gemini(prompt)
            cleaned_response = self._strip_code_fences(response)
            result = json.loads(cleaned_response)
            
            # Add metadata
            result["agent"] = "explanation"
            result["personalization"] = {
                "user_background": user_context.get("major", "general"),
                "academic_level": user_context.get("academicLevel", "general"),
                "topics_covered": len(topics),
                "objectives_addressed": len(objectives)
            }
            
            return result
            
        except json.JSONDecodeError:
            # Fallback explanation
            return {
                "agent": "explanation",
                "main_explanation": f"This topic covers {', '.join(topics[:3])}. These concepts are fundamental to understanding how things work in the real world and connect directly to {user_context.get('major', 'your field of study')}.",
                "key_concepts": [
                    {
                        "concept": topic,
                        "explanation": f"Understanding {topic} helps build foundational knowledge",
                        "analogy": f"Think of this like a building block in {user_context.get('major', 'your studies')}",
                        "example": f"A practical example would be how {topic} applies in everyday situations"
                    } for topic in topics[:3]
                ],
                "connections_to_user_field": field_connections or f"This directly applies to {user_context.get('major', 'your field')}",
                "common_misconceptions": ["Students often confuse related concepts", "The terminology can be challenging at first"],
                "difficulty_progression": "Concepts build logically from basic to advanced",
                "practical_applications": ["Real-world problem solving", "Professional applications"],
                "next_steps": "Practice with examples and explore advanced topics",
                "status": "fallback_generated"
            }
        except Exception as e:
            raise Exception(f"Explanation generation failed: {str(e)}")
