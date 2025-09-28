#!/usr/bin/env python3
"""
Standalone test script for the GeminiVideoGenerationAgent.
Run this to test the video generation functionality separately.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add the image/src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "image" / "src"))

from agents.gemini_video_generation_agent import GeminiVideoGenerationAgent


async def test_gemini_video_agent():
    """Test the GeminiVideoGenerationAgent with sample data."""
    print("🎬 Testing GeminiVideoGenerationAgent...")
    print("=" * 60)
    
    # Check if API key is available
    if not os.getenv("GOOGLE_GEMINI_API_KEY"):
        print("❌ GOOGLE_GEMINI_API_KEY environment variable is required")
        print("💡 Set it with: export GOOGLE_GEMINI_API_KEY='your-api-key'")
        return False
    
    try:
        # Initialize the agent
        print("🔧 Initializing GeminiVideoGenerationAgent...")
        agent = GeminiVideoGenerationAgent()
        print("✅ Agent initialized successfully")
        
        # Prepare test data using projectile motion physics content
        work_order = {
            "brief": "Create a short intro framing: Physics",
            "bullets": [
                "Projectile motion (parabolic trajectory)",
                "Independence of horizontal and vertical motion",
                "Constant horizontal velocity (assuming no air resistance)",
                "Vertical motion under constant gravitational acceleration (free fall)"
            ]
        }
        
        gemini_analysis = {
            "educational_analysis": {
                "subject": "Physics",
                "topic": "Projectile Motion",
                "difficulty_level": "intermediate"
            }
        }
        
        user_context = {
            "major": "Computer Science",
            "academicLevel": "undergraduate",
            "prefer_fast": True
        }
        
        print("\n📋 Test Parameters:")
        print(f"   Work Order: {work_order['brief']}")
        print(f"   Subject: {gemini_analysis['educational_analysis']['subject']}")
        print(f"   User Background: {user_context['major']} {user_context['academicLevel']}")
        print(f"   Key Concepts: {len(work_order['bullets'])} items")
        
        # Test the video generation
        print(f"\n🚀 Starting video generation test at {time.strftime('%H:%M:%S')}...")
        start_time = time.time()
        
        result = await agent.generate_content(
            work_order=work_order,
            gemini_analysis=gemini_analysis,
            user_context=user_context
        )
        
        execution_time = time.time() - start_time
        print(f"⏱️ Test completed in {execution_time:.2f} seconds")
        
        # Analyze results
        print("\n📊 RESULTS ANALYSIS:")
        print("=" * 40)
        
        if result.get("status") == "success":
            print("✅ Video generation SUCCESSFUL!")
            print(f"   Video Path: {result.get('video_path', 'Not provided')}")
            print(f"   Resolution: {result.get('resolution', 'Unknown')}")
            print(f"   Aspect Ratio: {result.get('aspect_ratio', 'Unknown')}")
            print(f"   Generation Time: {result.get('generation_time', 0):.2f}s")
            
            # Check if video file exists
            video_path = result.get('video_path')
            if video_path and os.path.exists(video_path):
                file_size = os.path.getsize(video_path)
                print(f"   File Size: {file_size / (1024*1024):.2f} MB")
                print(f"   File exists: ✅")
            else:
                print(f"   File exists: ❌")
            
            print(f"\n📝 Video Prompt Used:")
            print(f"   {result.get('video_prompt', 'Not provided')}")
            
        elif result.get("status") == "failed":
            print("❌ Video generation FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            print(f"   Fallback suggestion: {result.get('fallback_suggestion', 'None')}")
        else:
            print("⚠️ Unexpected result status")
        
        # Display full result (truncated)
        print(f"\n🔍 Full Result Keys: {list(result.keys())}")
        
        return result.get("status") == "success"
        
    except Exception as e:
        print(f"🚨 EXCEPTION during test: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🎯 Gemini Video Generation Agent Test")
    print("=" * 60)
    
    success = await test_gemini_video_agent()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED - Agent is working correctly!")
        print("💡 You can now integrate it into the orchestrator")
    else:
        print("💥 TEST FAILED - Check the errors above")
        print("🔧 Debug the agent before integration")
    
    print("\n📝 Next Steps:")
    if success:
        print("   1. Review generated video quality")
        print("   2. Test with different prompts/contexts")
        print("   3. Add to orchestrator when satisfied")
    else:
        print("   1. Check API key configuration")
        print("   2. Verify Gemini Veo 3 model access")
        print("   3. Review error messages and fix issues")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
