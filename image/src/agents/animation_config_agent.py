import json
from typing import Dict, Any
from .base_agent import BaseContentAgent


class AnimationConfigAgent(BaseContentAgent):
    """
    Generates Three.js animation configurations and code.
    
    Creates static animations and visualizations to help users
    understand complex concepts through visual representation.
    """
    
    async def generate_content(
        self, 
        work_order: Dict[str, Any], 
        gemini_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate Three.js animation configuration."""
        
        # Extract context
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        scenes = work_order.get("scenes", [])
        focus_equations = work_order.get("focus_equations", [])
        
        # Get subject for animation type selection
        educational_analysis = gemini_analysis.get("educational_analysis", {})
        subject = educational_analysis.get("subject", "").lower()
        
        # Get language instruction
        language_instruction = self._get_language_instruction(user_context)
        
        prompt = f"""
        Create a Three.js animation configuration for educational visualization.
        
        {user_bg}
        {subject_context}
        {language_instruction}
        
        Scenes to animate: {', '.join(scenes)}
        Key equations/formulas: {', '.join(focus_equations)}
        
        Generate appropriate animations for the subject area:
        - Physics: particle motion, force vectors, wave animations
        - Chemistry: molecular bonds, electron movement, reactions
        - Math: function graphs, geometric transformations, calculus concepts
        - Biology: cell processes, ecosystem dynamics, genetic flows
        - Computer Science: algorithm visualizations, data structures, sorting
        
        Return as JSON:
        {{
            "animation_config": {{
                "scene_setup": "Three.js scene initialization code",
                "objects": [
                    {{
                        "name": "object name",
                        "type": "sphere/box/line/custom",
                        "properties": {{}},
                        "animation": "animation description"
                    }}
                ],
                "camera_config": {{}},
                "lighting": {{}},
                "materials": {{}}
            }},
            "javascript_code": "Complete Three.js code for the animation",
            "animation_description": "What the animation shows",
            "educational_purpose": "How this helps learning",
            "interaction_hints": ["Click to rotate", "Scroll to zoom"],
            "duration_seconds": 10,
            "complexity_level": "beginner/intermediate/advanced"
        }}
        
        Make the code functional and ready to run in a web browser.
        Output pure JSON only.
        """
        
        try:
            response = await self._call_gemini(prompt)
            cleaned_response = self._strip_code_fences(response)
            result = json.loads(cleaned_response)
            
            # Add metadata
            result["agent"] = "animation_config"
            result["personalization"] = {
                "user_background": user_context.get("major", "general"),
                "subject_focus": subject,
                "scenes_count": len(scenes)
            }
            
            return result
            
        except json.JSONDecodeError:
            # Fallback animation config
            return {
                "agent": "animation_config",
                "animation_config": {
                    "scene_setup": "const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);",
                    "objects": [
                        {
                            "name": "concept_sphere",
                            "type": "sphere",
                            "properties": {"radius": 1, "color": "0x3498db"},
                            "animation": "gentle rotation to show concept"
                        }
                    ],
                    "camera_config": {"position": [0, 0, 5]},
                    "lighting": {"ambient": "0x404040", "directional": "0xffffff"},
                    "materials": {"basic": "MeshBasicMaterial", "phong": "MeshPhongMaterial"}
                },
                "javascript_code": f"// Basic Three.js animation for {subject}\nconst scene = new THREE.Scene();\nconst geometry = new THREE.SphereGeometry(1, 32, 32);\nconst material = new THREE.MeshPhongMaterial({{color: 0x3498db}});\nconst sphere = new THREE.Mesh(geometry, material);\nscene.add(sphere);\n// Animation loop\nfunction animate() {{\n    requestAnimationFrame(animate);\n    sphere.rotation.y += 0.01;\n    renderer.render(scene, camera);\n}}",
                "animation_description": f"A simple 3D visualization demonstrating {', '.join(scenes[:2])}",
                "educational_purpose": "Visual representation helps understand abstract concepts",
                "interaction_hints": ["Mouse to rotate view", "Scroll to zoom"],
                "duration_seconds": 15,
                "complexity_level": "beginner",
                "status": "fallback_generated"
            }
        except Exception as e:
            raise Exception(f"Animation config generation failed: {str(e)}")
