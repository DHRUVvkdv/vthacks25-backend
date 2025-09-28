import json
from typing import Dict, Any
from .base_agent import BaseContentAgent


class QuizGenerationAgent(BaseContentAgent):
    """Generates personalized quiz questions and assessments."""
    
    async def generate_content(self, work_order: Dict[str, Any], gemini_analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        blueprint = work_order.get("blueprint", {})
        num_questions = blueprint.get("num_questions", 5)
        focus_areas = blueprint.get("focus", [])
        
        # Get language instruction
        language_instruction = self._get_language_instruction(user_context)
        
        prompt = f"""
        Generate personalized quiz questions for educational assessment.
        
        {user_bg}
        {subject_context}
        {language_instruction}
        
        Number of questions: {num_questions}
        Focus areas: {', '.join(focus_areas)}
        
        Create questions at appropriate difficulty for the user's academic level.
        Include variety: multiple choice, true/false, short answer.
        
        Return as JSON:
        {{
            "quiz_metadata": {{
                "title": "quiz title",
                "description": "what this quiz covers",
                "estimated_time": "time in minutes",
                "difficulty_level": "beginner/intermediate/advanced"
            }},
            "questions": [
                {{
                    "id": 1,
                    "type": "multiple_choice/true_false/short_answer",
                    "question": "question text",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "correct option or answer",
                    "explanation": "why this is correct",
                    "difficulty": "easy/medium/hard",
                    "concept_tested": "which concept this tests"
                }}
            ],
            "answer_key": [
                {{
                    "question_id": 1,
                    "correct_answer": "answer",
                    "explanation": "detailed explanation",
                    "common_mistakes": ["mistake1", "mistake2"]
                }}
            ],
            "scoring_guide": "how to interpret results"
        }}
        
        Output pure JSON only.
        """
        
        try:
            response = await self._call_gemini(prompt)
            result = json.loads(self._strip_code_fences(response))
            result["agent"] = "quiz_generation"
            return result
        except:
            return {
                "agent": "quiz_generation",
                "quiz_metadata": {
                    "title": f"Assessment: {subject_context.split(': ')[1] if ': ' in subject_context else 'Educational Content'}",
                    "description": f"Test your understanding of {', '.join(focus_areas[:3])}",
                    "estimated_time": f"{max(2, num_questions)} minutes",
                    "difficulty_level": user_context.get("academicLevel", "intermediate").lower()
                },
                "questions": [
                    {
                        "id": i+1,
                        "type": "multiple_choice",
                        "question": f"Which of the following best describes {focus_areas[i % len(focus_areas)] if focus_areas else 'the main concept'}?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "Option A",
                        "explanation": "This is the correct understanding of the concept",
                        "difficulty": "medium",
                        "concept_tested": focus_areas[i % len(focus_areas)] if focus_areas else "main_concept"
                    } for i in range(min(num_questions, 5))
                ],
                "answer_key": [
                    {
                        "question_id": i+1,
                        "correct_answer": "Option A",
                        "explanation": "Detailed explanation of the correct answer",
                        "common_mistakes": ["Confusing with related concept", "Misunderstanding terminology"]
                    } for i in range(min(num_questions, 5))
                ],
                "scoring_guide": "Score interpretation: 80%+ Excellent, 60-79% Good, Below 60% Needs Review",
                "status": "fallback_generated"
            }
