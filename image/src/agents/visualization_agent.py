import json
from typing import Dict, Any, List
from .base_agent import BaseContentAgent
from models.chart_schemas import StandardizedChartConfig


class VisualizationAgent(BaseContentAgent):
    """Generates visual diagrams and charts using standardized schema."""

    async def generate_content(self, work_order: Dict[str, Any], gemini_analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        charts = work_order.get("charts", [])
        num_charts = len(charts) if charts else 3
        
        # Get the standardized template for AI to follow
        chart_template = StandardizedChartConfig.get_json_template_for_ai()
        
        prompt = f"""
        Generate visual diagrams and chart specifications for educational content.
        
        {user_bg}
        {subject_context}
        
        Charts needed: {', '.join(charts) if charts else 'Generate appropriate charts for the content'}
        
        You must generate exactly {num_charts} charts following this EXACT structure for each chart:
        {chart_template}
        
        Return as JSON:
        {{
            "diagrams": [
                {{
                    "type": "concept_diagram|flowchart|process_diagram|etc",
                    "title": "clear diagram title",
                    "description": "what this diagram illustrates",
                    "elements": ["key elements shown in the diagram"],
                    "connections": ["how elements connect or relate"],
                    "svg_code": "complete SVG code with proper dimensions and styling"
                }}
            ],
            "chart_configs": [
                // Generate {num_charts} charts using the template structure above
                // Fill in appropriate values for the educational content
                // Make sure each chart has a unique chart_id
            ],
            "visual_metaphors": "describe visual analogies that help understanding"
        }}
        
        CRITICAL REQUIREMENTS: 
        - Follow the chart template structure EXACTLY
        - Generate real educational data, not placeholder values
        - Each chart must have a unique chart_id
        - Choose appropriate chart_type (line, scatter, bar, pie)
        - Use proper data_format (points, function, categories)
        - Include meaningful annotations
        - FOR DATA POINTS: Always provide AT LEAST 10 data points in the "points" array
        - FOR FUNCTIONS: Ensure the mathematical expression is complete and valid
        - FOR CATEGORIES: Provide at least 5-8 categories with corresponding values
        - Make data points realistic and educational, not just sequential numbers
        
        Output pure JSON only.
        """
        
        try:
            response = await self._call_gemini(prompt)
            result = json.loads(self._strip_code_fences(response))
            result["agent"] = "visualization"
            result["schema_version"] = "1.0"
            return result
            
        except Exception as e:
            # Simple fallback without validation crashes
            fallback_chart = StandardizedChartConfig.get_fallback_chart()
            
            return {
                "agent": "visualization",
                "diagrams": [{
                    "type": "concept_diagram", 
                    "title": "Educational Concept Overview",
                    "description": "Visual overview of key concepts",
                    "elements": ["concept1", "concept2", "concept3"], 
                    "connections": ["relates to", "builds upon", "leads to"],
                    "svg_code": "<svg width='400' height='300' viewBox='0 0 400 300'><rect x='10' y='10' width='380' height='280' fill='#f8f9fa' stroke='#dee2e6'/><text x='200' y='150' text-anchor='middle' font-size='16'>Educational Diagram</text></svg>"
                }],
                "chart_configs": [fallback_chart],
                "visual_metaphors": "Visual representations help understand concepts through standardized charts and diagrams",
                "status": "fallback_generated",
                "schema_version": "1.0"
            }
