import json
from typing import Dict, Any
from .base_agent import BaseContentAgent


class CodeEquationAgent(BaseContentAgent):
    """Generates code examples and equation explanations."""
    
    async def generate_content(self, work_order: Dict[str, Any], gemini_analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        formulas = work_order.get("formulas", [])
        examples = work_order.get("examples", [])
        
        # Get language instruction
        language_instruction = self._get_language_instruction(user_context)
        
        prompt = f"""
        Generate code examples and equation explanations for educational content.
        
        {user_bg}
        {subject_context}
        {language_instruction}
        
        Formulas to explain: {', '.join(formulas)}
        Code examples needed: {', '.join(examples)}
        
        Return as JSON:
        {{
            "equations": [
                {{
                    "formula": "mathematical formula",
                    "explanation": "what it means",
                    "variables": {{"var": "description"}},
                    "example_calculation": "step by step example"
                }}
            ],
            "code_examples": [
                {{
                    "title": "example title",
                    "language": "python/javascript/etc",
                    "code": "functional code",
                    "explanation": "what the code does",
                    "output": "expected result"
                }}
            ],
            "practical_applications": "how to use these in real scenarios"
        }}
        
        Output pure JSON only.
        """
        
        try:
            response = await self._call_gemini(prompt)
            result = json.loads(self._strip_code_fences(response))
            result["agent"] = "code_equation"
            return result
        except:
            return {
                "agent": "code_equation",
                "equations": [{"formula": f, "explanation": f"Explanation for {f}", "variables": {}, "example_calculation": "Example calculation"} for f in formulas[:3]],
                "code_examples": [{"title": e, "language": "python", "code": f"# {e}\nprint('Example code')", "explanation": f"Code for {e}", "output": "Result"} for e in examples[:3]],
                "practical_applications": "These formulas and code examples apply in real-world scenarios",
                "status": "fallback_generated"
            }
