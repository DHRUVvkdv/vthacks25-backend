import json
from typing import Dict, Any
from .base_agent import BaseContentAgent


class VisualizationAgent(BaseContentAgent):
    """Generates visual diagrams and charts."""
    
    async def generate_content(self, work_order: Dict[str, Any], gemini_analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        charts = work_order.get("charts", [])
        
        prompt = f"""
        Generate visual diagram and chart specifications for educational content.
        
        {user_bg}
        {subject_context}
        
        Charts needed: {', '.join(charts)}
        
        Return as JSON:
        {{
            "diagrams": [
                {{
                    "type": "flowchart/concept_map/graph/etc",
                    "title": "diagram title",
                    "description": "what it shows",
                    "elements": ["element1", "element2"],
                    "connections": ["how elements connect"],
                    "svg_code": "basic SVG representation"
                }}
            ],
            "chart_configs": [
                {{
                    "chart_type": "bar/line/pie/scatter",
                    "title": "chart title",
                    "data_structure": {{}},
                    "axes_labels": {{}},
                    "purpose": "educational purpose"
                }}
            ],
            "visual_metaphors": "analogies that can be visualized"
        }}
        
        Output pure JSON only.
        """
        
        try:
            response = await self._call_gemini(prompt)
            result = json.loads(self._strip_code_fences(response))
            result["agent"] = "visualization"
            return result
        except:
            return {
                "agent": "visualization",
                "diagrams": [{"type": "concept_map", "title": f"Visual for {chart}", "description": f"Shows {chart} concepts", "elements": ["concept1", "concept2"], "connections": ["related to"], "svg_code": "<svg><!-- Basic diagram --></svg>"} for chart in charts[:3]],
                "chart_configs": [{"chart_type": "bar", "title": "Educational Chart", "data_structure": {"x": [], "y": []}, "axes_labels": {"x": "Categories", "y": "Values"}, "purpose": "Data visualization"}],
                "visual_metaphors": "Visual analogies to aid understanding",
                "status": "fallback_generated"
            }
