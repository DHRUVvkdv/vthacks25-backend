# COMPLETELY DISABLED - PERFORMANCE OPTIMIZATION
# This agent was causing performance issues and was not essential for core functionality.

# import json
# from typing import Dict, Any
# from .base_agent import BaseContentAgent


# class VideoGenerationAgent(BaseContentAgent):
#     """
#     Generates engaging video scripts and hook content.
#     
#     Creates compelling introductory video scripts that grab attention
#     and introduce the educational topic in an engaging way.
#     """
#     
#     async def generate_content(
#         self, 
#         work_order: Dict[str, Any], 
#         gemini_analysis: Dict[str, Any],
#         user_context: Dict[str, Any]
#     ) -> Dict[str, Any]:
#         """Generate video script and hook content."""
#         
#         print("📹 VideoGenerationAgent: Extracting context...")
#         # Extract context
#         user_bg = self._get_user_background_context(user_context)
#         subject_context = self._get_subject_context(gemini_analysis)
#         
#         brief = work_order.get("brief", "Create engaging video intro")
#         bullets = work_order.get("bullets", [])
#         
#         print(f"📹 VideoGenerationAgent: Brief='{brief}', Bullets={len(bullets)} items")
#         
#         # Get language instruction
#         language_instruction = self._get_language_instruction(user_context)
#         
#         # Build personalized prompt
#         prompt = f"""
#         Create an engaging 30-60 second video script for an educational hook video.
#         
#         {user_bg}
#         {subject_context}
#         {language_instruction}
#         
#         Brief: {brief}
#         Key concepts to highlight: {', '.join(bullets)}
#         
#         The script should:
#         1. Hook the viewer in the first 5 seconds
#         2. Connect to the user's background and interests
#         3. Preview the key concepts they'll learn
#         4. Create excitement about the topic
#         5. Be conversational and energetic
#         
#         Return as JSON:
#         {{
#             "script": "Full video script with timing cues",
#             "hook_line": "Opening hook sentence",
#             "key_preview": "Preview of what they'll learn",
#             "call_to_action": "Ending that motivates learning",
#             "estimated_duration": "30-60 seconds",
#             "visual_suggestions": ["suggestion1", "suggestion2"],
#             "tone": "energetic/conversational/professional"
#         }}
#         
#         Output pure JSON only.
#         """
#         
#         try:
#             print("📹 VideoGenerationAgent: Calling Gemini API...")
#             response = await self._call_gemini(prompt)
#             print("📹 VideoGenerationAgent: Cleaning and parsing response...")
#             cleaned_response = self._strip_code_fences(response)
#             result = json.loads(cleaned_response)
#             
#             # Add metadata
#             result["agent"] = "video_generation"
#             result["personalization"] = {
#                 "user_background": user_context.get("major", "general"),
#                 "academic_level": user_context.get("academicLevel", "general")
#             }
#             
#             return result
#             
#         except json.JSONDecodeError:
#             # Fallback if JSON parsing fails
#             return {
#                 "agent": "video_generation",
#                 "script": f"Welcome! Today we're diving into {subject_context.split(': ')[1] if ': ' in subject_context else 'an exciting topic'}. Whether you're a {user_context.get('major', 'student')} or just curious about the world around you, this topic will change how you see things. Let's explore {', '.join(bullets[:3])} together!",
#                 "hook_line": "Ready to see the world differently?",
#                 "key_preview": f"You'll master {', '.join(bullets[:2])}",
#                 "call_to_action": "Let's get started!",
#                 "estimated_duration": "45 seconds",
#                 "visual_suggestions": ["animated text", "concept illustrations"],
#                 "tone": "energetic",
#                 "status": "fallback_generated"
#             }
#         except Exception as e:
#             raise Exception(f"Video generation failed: {str(e)}")