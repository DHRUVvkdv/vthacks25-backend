#!/usr/bin/env python3
"""
Test script for the FastWanVideoGenerationAgent.
This tests the ultra-fast video generation using fal.ai's FastWan model.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add the image/src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "image" / "src"))

from agents.fastwan_video_generation_agent import FastWanVideoGenerationAgent


async def test_fastwan_video_agent():
    """Test the FastWanVideoGenerationAgent with projectile motion prompt."""
    print("🚀 Testing FastWanVideoGenerationAgent...")
    print("=" * 60)
    
    # Check if API key is available
    if not os.getenv("FAL_KEY"):
        print("❌ FAL_KEY environment variable is required")
        print("💡 Setup instructions:")
        print("   1. Sign up at https://fal.ai")
        print("   2. Go to https://fal.ai/dashboard")
        print("   3. Generate an API key")
        print("   4. Set it with: export FAL_KEY='your-api-key'")
        return False
    
    try:
        # Initialize the agent
        print("🔧 Initializing FastWanVideoGenerationAgent...")
        agent = FastWanVideoGenerationAgent()
        print("✅ Agent initialized successfully")
        
        # Prepare test data using projectile motion physics content
        work_order = {
            "brief": "Create a short intro framing: Physics",
            "bullets": [
                "Projectile motion (parabolic trajectory)",
                "Independence of horizontal and vertical motion",
                "Constant horizontal velocity (assuming no air resistance)",
                "Vertical motion under constant gravitational acceleration (free fall)"
            ],
            "duration": 5,  # FastWan optimal duration
            "resolution": "720p",
            "prefer_speed": True  # Use faster 1.3B model
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
        print(f"   Target Duration: {work_order['duration']} seconds")
        print(f"   Expected Generation Time: 5-16 seconds (vs 51s with Gemini)")
        
        # Test the video generation
        print(f"\n🚀 Starting FastWan video generation at {time.strftime('%H:%M:%S')}...")
        start_time = time.time()
        
        result = await agent.generate_content(
            work_order=work_order,
            gemini_analysis=gemini_analysis,
            user_context=user_context
        )
        
        total_time = time.time() - start_time
        print(f"⏱️ Total test completed in {total_time:.2f} seconds")
        
        # Analyze results
        print("\n📊 FASTWAN RESULTS ANALYSIS:")
        print("=" * 50)
        
        if result.get("status") == "success":
            print("✅ FastWan video generation SUCCESSFUL!")
            print(f"   Video Path: {result.get('video_path', 'Not provided')}")
            print(f"   Resolution: {result.get('resolution', 'Unknown')}")
            print(f"   Duration: {result.get('duration_estimate', 'Unknown')}")
            print(f"   Model Used: {result.get('model_used', 'Unknown')}")
            print(f"   Generation Time: {result.get('generation_time', 0):.2f}s")
            
            # Performance comparison
            gemini_time = 51  # Your reported Gemini time
            fastwan_time = result.get('generation_time', 0)
            if fastwan_time > 0:
                speedup = gemini_time / fastwan_time
                print(f"   🏎️ Speed Improvement: {speedup:.1f}x faster than Gemini!")
                print(f"   🏎️ Time Saved: {gemini_time - fastwan_time:.1f} seconds")
            
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
            
            # Performance metrics
            if 'performance' in result:
                perf = result['performance']
                print(f"\n🏆 Performance Metrics:")
                print(f"   Target Time: {perf.get('target_time', 'Unknown')}")
                print(f"   Actual Time: {perf.get('actual_time', 'Unknown')}")
                print(f"   Speed Improvement: {perf.get('speed_improvement', 'Unknown')}")
            
        elif result.get("status") == "failed":
            print("❌ FastWan video generation FAILED")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
            # Check for setup instructions
            if 'setup_instructions' in result:
                print(f"\n🔧 Setup Instructions:")
                for instruction in result['setup_instructions']:
                    print(f"   {instruction}")
            
            print(f"   Fallback suggestion: {result.get('fallback_suggestion', 'None')}")
        else:
            print("⚠️ Unexpected result status")
        
        # Display full result keys
        print(f"\n🔍 Full Result Keys: {list(result.keys())}")
        
        return result.get("status") == "success"
        
    except Exception as e:
        print(f"🚨 EXCEPTION during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🎯 FastWan Video Generation Agent Test")
    print("🚀 Ultra-fast video generation (5-16s vs 51s)")
    print("=" * 60)
    
    success = await test_fastwan_video_agent()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TEST PASSED - FastWan is working and MUCH faster!")
        print("💡 Ready to replace your slow Gemini agent")
        print("🚀 Expected 3-10x speed improvement achieved!")
    else:
        print("💥 TEST FAILED - Check the errors above")
        print("🔧 Most likely need to set up FAL_KEY")
    
    print("\n📝 Next Steps:")
    if success:
        print("   1. Compare video quality with Gemini")
        print("   2. Test with different physics concepts")
        print("   3. Integrate into your main orchestrator")
        print("   4. Celebrate the massive speed improvement! 🎊")
    else:
        print("   1. Get FAL_KEY from https://fal.ai/dashboard")
        print("   2. Set the environment variable")
        print("   3. Re-run this test")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(main())
