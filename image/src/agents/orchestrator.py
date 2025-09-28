import asyncio
import time
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from .video_generation_agent import VideoGenerationAgent
from .explanation_agent import ExplanationAgent
from .animation_config_agent import AnimationConfigAgent
from .code_equation_agent import CodeEquationAgent
from .visualization_agent import VisualizationAgent
from .application_agent import ApplicationAgent
from .summary_agent import SummaryAgent
from .quiz_generation_agent import QuizGenerationAgent


class ContentOrchestrator:
    """
    Orchestrates the execution of specialized content generation agents.
    
    Takes work orders from the Gemini analysis and coordinates parallel execution
    of 8 specialized agents to generate personalized learning content.
    """
    
    def __init__(self):
        # Initialize all specialized agents
        self.agents = {
            'video_generation': VideoGenerationAgent(),
            'explanation': ExplanationAgent(),
            'animation_config': AnimationConfigAgent(),
            'code_equation': CodeEquationAgent(),
            'visualization': VisualizationAgent(),
            'application': ApplicationAgent(),
            'summary': SummaryAgent(),
            'quiz_generation': QuizGenerationAgent()
        }
        
    async def orchestrate_content_generation(
        self, 
        work_orders: Dict[str, Any], 
        gemini_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrate parallel execution of content generation agents.
        
        Args:
            work_orders: Work orders from Gemini analysis
            gemini_analysis: Full Gemini analysis for context
            user_context: User preferences and context
            
        Returns:
            Dictionary with generated content from all agents
        """
        start_time = time.time()
        print("🎯 Starting content orchestration with 8 specialized agents...")
        print(f"⏰ Orchestration started at: {time.strftime('%H:%M:%S')}")
        
        # Prepare tasks for parallel execution
        tasks = []
        agent_names = []
        agent_start_times = {}
        
        for agent_type, order in work_orders.items():
            if agent_type in self.agents:
                print(f"📋 Queuing {agent_type} agent with work order: {str(order)[:100]}...")
                task = self._execute_agent_safely(
                    agent_type, 
                    order, 
                    gemini_analysis, 
                    user_context
                )
                tasks.append(task)
                agent_names.append(agent_type)
                agent_start_times[agent_type] = time.time()
            else:
                print(f"⚠️  Unknown agent type: {agent_type}")
        
        # Execute all agents in parallel with detailed logging
        print(f"🚀 Executing {len(tasks)} agents in parallel...")
        print(f"🔧 Agent types being executed: {', '.join(agent_names)}")
        
        # Add timeout and better error handling
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=300  # 5 minute timeout
            )
        except asyncio.TimeoutError:
            print("⏱️ TIMEOUT: Some agents took longer than 5 minutes!")
            results = [Exception("Timeout after 5 minutes") for _ in tasks]
        
        # Process results and handle any failures
        content_results = {}
        successful_agents = 0
        failed_agents = []
        
        for i, result in enumerate(results):
            agent_name = agent_names[i]
            execution_time = time.time() - agent_start_times[agent_name]
            
            if isinstance(result, Exception):
                print(f"❌ Agent {agent_name} FAILED after {execution_time:.2f}s: {str(result)}")
                failed_agents.append(agent_name)
                content_results[agent_name] = {
                    "status": "failed",
                    "error": str(result),
                    "execution_time": execution_time,
                    "fallback_content": self._generate_fallback_content(agent_name)
                }
            else:
                print(f"✅ Agent {agent_name} SUCCESS in {execution_time:.2f}s")
                successful_agents += 1
                content_results[agent_name] = {
                    "status": "success",
                    "execution_time": execution_time,
                    "content": result
                }
        
        total_time = time.time() - start_time
        orchestration_summary = {
            "total_agents": len(tasks),
            "successful_agents": successful_agents,
            "failed_agents": len(failed_agents),
            "failed_agent_names": failed_agents,
            "execution_mode": "parallel",
            "total_execution_time": total_time,
            "average_agent_time": total_time / len(tasks) if tasks else 0
        }
        
        print(f"🎉 Content orchestration complete! {successful_agents}/{len(tasks)} agents successful")
        print(f"⏱️ Total orchestration time: {total_time:.2f} seconds")
        
        return {
            "orchestration_summary": orchestration_summary,
            "content": content_results,
            "learning_formats": self._structure_learning_formats(content_results)
        }
    
    async def _execute_agent_safely(
        self, 
        agent_type: str, 
        work_order: Dict[str, Any],
        gemini_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Any:
        """Execute a single agent with error handling."""
        agent_start = time.time()
        try:
            print(f"🔄 {agent_type} agent STARTING...")
            agent = self.agents[agent_type]
            print(f"🔧 {agent_type} agent initialized, calling generate_content...")
            
            result = await agent.generate_content(work_order, gemini_analysis, user_context)
            
            agent_time = time.time() - agent_start
            print(f"✅ {agent_type} agent COMPLETED in {agent_time:.2f}s")
            return result
        except Exception as e:
            agent_time = time.time() - agent_start
            print(f"🚨 ERROR in {agent_type} agent after {agent_time:.2f}s: {str(e)}")
            print(f"🔍 {agent_type} work_order keys: {list(work_order.keys()) if work_order else 'None'}")
            raise e
    
    def _generate_fallback_content(self, agent_name: str) -> Dict[str, Any]:
        """Generate fallback content when an agent fails."""
        fallbacks = {
            'video_generation': {
                "script": "Introduction to the educational topic",
                "hook": "Let's explore this fascinating subject together!",
                "duration": "30 seconds"
            },
            'explanation': {
                "explanation": "This topic covers important concepts that build foundational understanding.",
                "key_points": ["Core concept 1", "Core concept 2", "Core concept 3"]
            },
            'animation_config': {
                "config": "// Basic animation configuration\nconst config = { scene: 'basic', duration: 3000 };",
                "description": "Simple animation setup"
            },
            'code_equation': {
                "code_examples": ["// Basic example\nconsole.log('Hello, learning!');"],
                "equations": ["Basic formula: a + b = c"]
            },
            'visualization': {
                "charts": ["basic_concept_diagram"],
                "description": "Conceptual visualization"
            },
            'application': {
                "examples": ["Real-world application examples to be added"],
                "connections": "Practical applications in everyday life"
            },
            'summary': {
                "key_points": ["Main concept", "Important detail", "Key takeaway"],
                "summary": "Summary of key learning objectives"
            },
            'quiz_generation': {
                "questions": [
                    {
                        "question": "What is the main topic covered?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct": 0,
                        "explanation": "Basic comprehension question"
                    }
                ]
            }
        }
        
        return fallbacks.get(agent_name, {"content": "Fallback content generated"})
    
    def _structure_learning_formats(self, content_results: Dict[str, Any]) -> Dict[str, Any]:
        """Structure the results into the 8 learning formats for the frontend."""
        formats = {}
        
        # Map agent results to learning formats
        format_mapping = {
            'hook_video': 'video_generation',
            'concept_explanation': 'explanation', 
            'static_animation': 'animation_config',
            'code_equations': 'code_equation',
            'visual_diagrams': 'visualization',
            'practice_problems': 'quiz_generation',
            'real_world_applications': 'application',
            'summary_cards': 'summary'
        }
        
        for format_name, agent_name in format_mapping.items():
            if agent_name in content_results:
                formats[format_name] = content_results[agent_name]
            else:
                formats[format_name] = {
                    "status": "not_generated",
                    "content": self._generate_fallback_content(agent_name)
                }
        
        return formats
    
    def get_orchestrator_info(self) -> Dict[str, Any]:
        """Get information about the orchestrator and available agents."""
        return {
            "orchestrator": "ContentOrchestrator",
            "available_agents": list(self.agents.keys()),
            "supported_formats": [
                "Hook Video",
                "Concept Explanation", 
                "Static Animation",
                "Code/Equations",
                "Visual Diagrams",
                "Practice Problems",
                "Real-world Applications",
                "Summary Cards"
            ],
            "execution_mode": "parallel_async",
            "fallback_strategy": "graceful_degradation"
        }
