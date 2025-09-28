#!/usr/bin/env python3
"""
Debug script to test agents one by one and identify issues.
Run this from the project root to test individual agents.
"""

import requests
import json
import time

API_KEY = "vth_hackathon_2025_secret_key"
BASE_URL = "http://localhost:8000"

def test_single_agent(agent_name: str, work_order: dict = None):
    """Test a single agent with logging."""
    print(f"\n🧪 Testing {agent_name} agent...")
    
    if work_order is None:
        work_order = {"brief": "test content", "bullets": ["concept1", "concept2"]}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/test-single-agent",
            headers={"X-API-Key": API_KEY},
            data={
                "agent_name": agent_name,
                "test_work_order": json.dumps(work_order)
            },
            timeout=60  # 1 minute timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success":
                print(f"✅ {agent_name} agent PASSED")
                return True
            else:
                print(f"❌ {agent_name} agent FAILED: {result['error']}")
                return False
        else:
            print(f"❌ {agent_name} agent HTTP ERROR: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏱️ {agent_name} agent TIMEOUT (>60s)")
        return False
    except Exception as e:
        print(f"🚨 {agent_name} agent EXCEPTION: {str(e)}")
        return False

def test_all_agents():
    """Test all agents individually."""
    agents = [
        "video_generation",
        "explanation", 
        "animation_config",
        "code_equation",
        "visualization",
        "application",
        "summary",
        "quiz_generation"
    ]
    
    results = {}
    
    for agent in agents:
        start_time = time.time()
        success = test_single_agent(agent)
        elapsed = time.time() - start_time
        
        results[agent] = {
            "success": success,
            "time": elapsed
        }
        
        print(f"⏱️ {agent}: {elapsed:.2f}s")
        time.sleep(1)  # Brief pause between tests
    
    print("\n📊 SUMMARY:")
    print("=" * 50)
    
    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)
    
    print(f"Overall: {passed}/{total} agents passed")
    
    for agent, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{agent:20} {status:8} {result['time']:6.2f}s")
    
    return results

def check_server():
    """Check if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server responded with {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not reachable: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Agent Debug Tool")
    print("=" * 50)
    
    if not check_server():
        print("\n💡 Make sure to start the server first:")
        print("cd image && python src/main.py")
        exit(1)
    
    print("\n🚀 Starting agent tests...")
    results = test_all_agents()
    
    failed_agents = [agent for agent, result in results.items() if not result["success"]]
    
    if failed_agents:
        print(f"\n🔍 Failed agents to investigate: {', '.join(failed_agents)}")
        print("\nTo debug a specific agent, check the server logs when running:")
        for agent in failed_agents[:3]:  # Show first 3
            print(f"  python debug_agents.py --single {agent}")
    else:
        print("\n🎉 All agents passed! The orchestrator should work.")
