from typing import Dict, Any, List, Optional, Union

class StandardizedChartConfig:
    """General chart configuration schema that AI can fill with any subject content"""
    
    @staticmethod
    def get_standard_schema() -> Dict[str, Any]:
        """Returns the standardized chart configuration schema for AI to follow"""
        return {
            "chart_id": "unique_identifier_string",
            "chart_type": "line|scatter|bar|pie", 
            "title": "descriptive_chart_title",
            "description": "educational_purpose_and_what_chart_shows",
            "data_format": "points|function|categories",
            "data": {
                "points": [
                    {"x": "number_or_string", "y": "number", "label": "optional_point_label"}
                ],
                "function": {
                    "expression": "mathematical_expression_as_string",
                    "parameters": {"parameter_name": "parameter_value"},
                    "domain": {"min": "min_value", "max": "max_value"}
                },
                "categories": {
                    "labels": ["category_names"],
                    "values": ["corresponding_numeric_values"]
                }
            },
            "axes": {
                "x_axis": "x_axis_label_with_description",
                "y_axis": "y_axis_label_with_description",
                "x_unit": "optional_unit_string",
                "y_unit": "optional_unit_string"
            },
            "annotations": [
                {
                    "type": "point|line|range",
                    "coordinates": {"x": "number", "y": "number"} or "special_position_descriptor",
                    "label": "annotation_text",
                    "style": {"color": "hex_color", "size": "number"}
                }
            ],
            "styling": {
                "colors": ["hex_color_array"],
                "line_style": "solid|dashed|dotted",
                "point_size": "number"
            }
        }

    @staticmethod
    def get_json_template_for_ai() -> str:
        """Returns a JSON template string that AI should follow exactly"""
        return '''
        {
            "chart_id": "generate_unique_id_based_on_content",
            "chart_type": "choose_from: line, scatter, bar, pie",
            "title": "clear_descriptive_title",
            "description": "explain_what_this_chart_shows_educationally", 
            "data_format": "choose_from: points, function, categories",
            "data": {
                "points": [
                    {"x": 0, "y": 0, "label": "point1"},
                    {"x": 1, "y": 2, "label": "point2"},
                    {"x": 2, "y": 4, "label": "point3"},
                    {"x": 3, "y": 6, "label": "point4"},
                    {"x": 4, "y": 8, "label": "point5"},
                    {"x": 5, "y": 10, "label": "point6"},
                    {"x": 6, "y": 12, "label": "point7"},
                    {"x": 7, "y": 14, "label": "point8"},
                    {"x": 8, "y": 16, "label": "point9"},
                    {"x": 9, "y": 18, "label": "point10"},
                    {"x": 10, "y": 20, "label": "point11"}
                ],
                "function": {
                    "expression": "y = f(x) mathematical expression",
                    "parameters": {"param1": "value1"},
                    "domain": {"min": 0, "max": 10}
                },
                "categories": {
                    "labels": ["Category A", "Category B", "Category C", "Category D", "Category E", "Category F"],
                    "values": [10, 20, 15, 25, 30, 18]
                }
            },
            "axes": {
                "x_axis": "X Axis Label",
                "y_axis": "Y Axis Label",
                "x_unit": "optional unit",
                "y_unit": "optional unit"
            },
            "annotations": [
                {
                    "type": "point",
                    "coordinates": {"x": 5, "y": 10},
                    "label": "Important Point",
                    "style": {"color": "#ff0000", "size": 5}
                }
            ],
            "styling": {
                "colors": ["#2563eb", "#16a34a", "#dc2626"],
                "line_style": "solid",
                "point_size": 4
            }
        }
        '''


    @staticmethod
    def get_fallback_chart() -> Dict[str, Any]:
        """Returns a valid fallback chart configuration"""
        return {
            "chart_id": "fallback_educational_chart",
            "chart_type": "line",
            "title": "Educational Data Visualization",
            "description": "Standard chart for educational content visualization",
            "data_format": "points",
            "data": {
                "points": [
                    {"x": 0, "y": 0, "label": "Point 1"},
                    {"x": 1, "y": 2, "label": "Point 2"},
                    {"x": 2, "y": 4, "label": "Point 3"},
                    {"x": 3, "y": 6, "label": "Point 4"},
                    {"x": 4, "y": 8, "label": "Point 5"},
                    {"x": 5, "y": 10, "label": "Point 6"},
                    {"x": 6, "y": 12, "label": "Point 7"},
                    {"x": 7, "y": 14, "label": "Point 8"},
                    {"x": 8, "y": 16, "label": "Point 9"},
                    {"x": 9, "y": 18, "label": "Point 10"}
                ]
            },
            "axes": {
                "x_axis": "X Values",
                "y_axis": "Y Values",
                "x_unit": "",
                "y_unit": ""
            },
            "annotations": [],
            "styling": {
                "colors": ["#2563eb"],
                "line_style": "solid",
                "point_size": 4
            }
        }
