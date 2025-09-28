import asyncio
import time
from typing import Dict, Any, List, Optional
from fastapi import HTTPException

from .explanation_agent import ExplanationAgent
# from .animation_config_agent import AnimationConfigAgent  # COMMENTED OUT - 138s bottleneck
from .code_equation_agent import CodeEquationAgent
from .visualization_agent import VisualizationAgent
from .application_agent import ApplicationAgent
from .summary_agent import SummaryAgent
from .quiz_generation_agent import QuizGenerationAgent


class ContentOrchestrator:
    """
    Orchestrates the execution of specialized content generation agents.
    
    Takes work orders from the Gemini analysis and coordinates parallel execution
    of specialized agents to generate personalized learning content.
    """
    
    def __init__(self):
        # Initialize all specialized agents (video generation & animation removed for performance)
        self.agents = {
            'explanation': ExplanationAgent(),
            # 'animation_config': AnimationConfigAgent(),  # COMMENTED OUT - 138s bottleneck
            'code_equation': CodeEquationAgent(),
            'visualization': VisualizationAgent(),
            'application': ApplicationAgent(),
            'summary': SummaryAgent(),
            'quiz_generation': QuizGenerationAgent()
        }
        
    async def run_single_agent(
        self,
        agent_type: str,
        work_order: Dict[str, Any],
        gemini_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a single agent for debugging/testing purposes.
        
        Args:
            agent_type: Name of the agent to run
            work_order: Work order for the agent
            gemini_analysis: Full Gemini analysis for context
            user_context: User preferences and context
            
        Returns:
            Result from the single agent
        """
        if agent_type not in self.agents:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown agent type: {agent_type}. Available: {list(self.agents.keys())}"
            )
        
        print(f"🔧 Running single agent: {agent_type}")
        start_time = time.time()
        
        try:
            result = await self._execute_agent_safely(
                agent_type, work_order, gemini_analysis, user_context
            )
            execution_time = time.time() - start_time
            
            return {
                "agent_type": agent_type,
                "status": "success",
                "execution_time": execution_time,
                "content": result
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "agent_type": agent_type,
                "status": "failed",
                "execution_time": execution_time,
                "error": str(e)
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
        print(f"🎯 Starting content orchestration with {len(self.agents)} specialized agents...")
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
        
        # Execute agents with staggered start to reduce API rate limiting
        print(f"🚀 Executing {len(tasks)} agents with staggered start...")
        print(f"🔧 Agent types being executed: {', '.join(agent_names)}")
        
        # Intelligent staggering based on available API keys
        from .base_agent import GeminiAPIKeyManager
        api_manager = GeminiAPIKeyManager()
        api_key_count = api_manager.get_client_count()
        
        # Reduce stagger delay if we have multiple API keys
        stagger_delay = 0.2 if api_key_count > 1 else 1.0
        print(f"🔑 Using {api_key_count} API keys with {stagger_delay}s stagger delay")
        
        staggered_tasks = []
        for i, task in enumerate(tasks):
            if i > 0:  # Don't delay the first agent
                staggered_task = self._delayed_execution(task, i * stagger_delay)
                staggered_tasks.append(staggered_task)
            else:
                staggered_tasks.append(task)
        
        # Add timeout and better error handling
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*staggered_tasks, return_exceptions=True),
                timeout=300  # 5 minute timeout
            )
        except asyncio.TimeoutError:
            print("⏱️ TIMEOUT: Some agents took longer than 5 minutes!")
            results = [Exception("Timeout after 5 minutes") for _ in staggered_tasks]
        
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
    
    async def _delayed_execution(self, task, delay_seconds: float):
        """Execute a task after a delay to stagger API calls."""
        await asyncio.sleep(delay_seconds)
        return await task
    
    def _generate_fallback_content(self, agent_name: str) -> Dict[str, Any]:
        """Generate fallback content when an agent fails."""
        fallbacks = {
            'explanation': {
                "explanation": "This topic covers important concepts that build foundational understanding.",
                "key_points": ["Core concept 1", "Core concept 2", "Core concept 3"]
            },
            # 'animation_config': {  # COMMENTED OUT - performance optimization
            #     "config": "// Basic animation configuration\nconst config = { scene: 'basic', duration: 3000 };",
            #     "description": "Simple animation setup"
            # },
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
        
        # Map agent results to learning formats (video generation & animation removed for performance)
        format_mapping = {
            'concept_explanation': 'explanation', 
            # 'static_animation': 'animation_config',  # COMMENTED OUT - performance optimization
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
                "Concept Explanation", 
                # "Static Animation",  # COMMENTED OUT - performance optimization
                "Code/Equations",
                "Visual Diagrams",
                "Practice Problems",
                "Real-world Applications",
                "Summary Cards"
            ],
            "execution_mode": "parallel_async",
            "fallback_strategy": "graceful_degradation"
        }
