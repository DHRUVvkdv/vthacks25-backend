#!/usr/bin/env python3
"""
Quick script to test individual agents for performance debugging.
Usage: python test_agent.py <agent_name>
"""
import asyncio
import sys
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the image/src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'image', 'src'))

from agents.orchestrator import ContentOrchestrator

async def test_agent(agent_name: str):
    """Test a single agent with mock data."""
    orchestrator = ContentOrchestrator()
    
    # Mock data for testing
    work_orders = {
        'explanation': {'topics': ['Chemical bonds', 'Electronegativity']},
        # 'animation_config': {'scenes': ['Ionic Bonds', 'Covalent Bonds']},  # COMMENTED OUT - 138s bottleneck
        'code_equation': {'formulas': ['NaCl → Na+ + Cl-']},
        'visualization': {'charts': ['bond_strength_chart']},
        'application': {'examples': ['Salt formation in cooking']},
        'summary': {'key_points': ['Atoms form bonds', 'Electronegativity matters']},
        'quiz_generation': {'blueprint': {'num_questions': 3}}
    }
    
    mock_gemini_analysis = {
        "educational_analysis": {
            "subject": "Chemistry",
            "topic": "Chemical Bonds"
        }
    }
    
    mock_user_context = {
        "major": "Computer Science",
        "academicLevel": "College"
    }
    
    if agent_name not in orchestrator.agents:
        print(f"❌ Unknown agent: {agent_name}")
        print(f"📋 Available agents: {list(orchestrator.agents.keys())}")
        return
    
    work_order = work_orders.get(agent_name, {'test': 'data'})
    
    print(f"🧪 Testing agent: {agent_name}")
    print(f"📋 Work order: {json.dumps(work_order, indent=2)}")
    print("=" * 50)
    
    start_time = time.time()
    try:
        result = await orchestrator.run_single_agent(
            agent_name, work_order, mock_gemini_analysis, mock_user_context
        )
        
        execution_time = time.time() - start_time
        
        print(f"✅ Agent completed in {execution_time:.2f}s")
        print(f"📊 Result status: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'success':
            content = result.get('content', {})
            print(f"📝 Content keys: {list(content.keys()) if isinstance(content, dict) else 'Not a dict'}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"💥 Exception after {execution_time:.2f}s: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_agent.py <agent_name>")
        print("Available agents: explanation, code_equation, visualization, application, summary, quiz_generation")
        print("Note: animation_config disabled for performance (was 138s bottleneck)")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    asyncio.run(test_agent(agent_name))
