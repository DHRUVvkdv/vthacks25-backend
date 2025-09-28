import asyncio
import os
import time
from typing import Any, Dict, Optional
import fal_client
from .base_agent import BaseContentAgent


class FastWanVideoGenerationAgent(BaseContentAgent):
    """
    Generates videos using fal.ai's LTXV-13B-098-Distilled model.
    
    Much faster and cheaper than Gemini Veo 3 - generates 5-second videos quickly
    instead of 51+ seconds. Optimized for educational content without text overlays.
    """
    
    def __init__(self):
        super().__init__()
        # Using the cheaper and faster LTXV model
        self.model_id = "fal-ai/ltxv-13b-098-distilled"  # Cheap and fast model
        self.fallback_model = "fal-ai/wan/v2.2-5b/text-to-video"  # Fallback option
    
    async def generate_content(
        self, 
        work_order: Dict[str, Any], 
        gemini_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate video using FastWan model via fal.ai."""
        
        print("🚀 FalAiVideoGenerationAgent: Starting ultra-fast video generation with LTXV-13B...")
        
        # Check if FAL_KEY is available
        if not os.getenv("FAL_KEY"):
            return {
                "agent": "fal_ai_video_generation",
                "status": "failed",
                "error": "FAL_KEY environment variable is required. Get it from https://fal.ai/dashboard",
                "video_path": None,
                "setup_instructions": [
                    "1. Sign up at https://fal.ai",
                    "2. Go to https://fal.ai/dashboard",
                    "3. Generate an API key",
                    "4. Set: export FAL_KEY='your-api-key-here'"
                ]
            }
        
        # Extract context for video prompt
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        brief = work_order.get("brief", "Create educational video")
        bullets = work_order.get("bullets", [])
        
        print(f"🚀 FastWanVideoGenerationAgent: Brief='{brief}', Concepts={len(bullets)} items")
        
        # Create optimized prompt for FastWan (text-free focus)
        video_prompt = self._create_fastwan_prompt(brief, bullets, subject_context, user_context)
        
        try:
            print("🚀 FastWanVideoGenerationAgent: Sending request to FastWan via fal.ai...")
            start_time = time.time()
            
            # Configure FastWan parameters
            config = self._build_fastwan_config(work_order)
            
            # Subscribe to fal.ai with progress logging
            def on_queue_update(update):
                if isinstance(update, fal_client.InProgress):
                    for log in update.logs:
                        print(f"🚀 LTXV Progress: {log['message']}")
            
            # Submit to fal.ai using subscribe for progress tracking
            output = await asyncio.to_thread(
                fal_client.subscribe,
                self._select_model(work_order),
                arguments={
                    "prompt": video_prompt,
                    **config
                },
                with_logs=True,
                on_queue_update=on_queue_update
            )
            
            generation_time = time.time() - start_time
            print(f"🚀 FastWanVideoGenerationAgent: Generation completed in {generation_time:.2f}s")
            
            # Download and save video
            video_url = output.get("video", {}).get("url")
            if not video_url:
                raise RuntimeError("No video URL returned from FastWan")
            
            video_filename = f"fastwan_video_{int(time.time())}.mp4"
            video_path = os.path.join(os.getcwd(), "generated_videos", video_filename)
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            
            # Download video
            await self._download_video(video_url, video_path)
            
            result_data = {
                "agent": "fal_ai_video_generation",
                "video_path": video_path,
                "video_prompt": video_prompt,
                "duration_estimate": f"{config.get('duration', 5)} seconds",
                "resolution": f"{config.get('resolution', '720p')}",
                "aspect_ratio": config.get("aspect_ratio", "16:9"),
                "generation_time": generation_time,
                "status": "success",
                "model_used": self._select_model(work_order),
                "personalization": {
                    "user_background": user_context.get("major", "general"),
                    "academic_level": user_context.get("academicLevel", "general")
                },
                "educational_context": {
                    "subject": subject_context,
                    "key_concepts": bullets[:5]
                },
                "performance": {
                    "speed_improvement": "~3-10x faster than Gemini Veo 3",
                    "target_time": "5-16 seconds",
                    "actual_time": f"{generation_time:.2f}s"
                }
            }
            
            print(f"🚀 FastWanVideoGenerationAgent: Video saved to {video_path}")
            if os.path.exists(video_path):
                file_size = os.path.getsize(video_path) / (1024 * 1024)
                print(f"🚀 FastWanVideoGenerationAgent: File size: {file_size:.2f} MB")
                result_data["file_size_mb"] = file_size
            
            return result_data

        except Exception as e:
            print(f"🚀 FastWanVideoGenerationAgent: Error - {str(e)}")
            return {
                "agent": "fal_ai_video_generation",
                "status": "failed",
                "error": str(e),
                "video_path": None,
                "video_prompt": video_prompt,
                "generation_time": time.time() - start_time if 'start_time' in locals() else 0,
                "fallback_suggestion": "Try the Gemini agent or check your FAL_KEY",
                "personalization": {
                    "user_background": user_context.get("major", "general"),
                    "academic_level": user_context.get("academicLevel", "general")
                }
            }

    def _build_fastwan_config(self, work_order: Dict[str, Any]) -> Dict[str, Any]:
        """Build video generation configuration for fal.ai LTXV model."""
        config = {
            "negative_prompt": work_order.get("negative_prompt", "worst quality, inconsistent motion, blurry, jittery, distorted, text, captions, words, letters"),
            "resolution": work_order.get("resolution", "720p"),
            "aspect_ratio": work_order.get("aspect_ratio", "16:9"),
            "num_frames": work_order.get("num_frames", 121),  # ~5 seconds at 24fps
            "first_pass_num_inference_steps": work_order.get("first_pass_steps", 8),
            "second_pass_num_inference_steps": work_order.get("second_pass_steps", 8),
            "second_pass_skip_initial_steps": work_order.get("skip_initial_steps", 5),
            "frame_rate": work_order.get("frame_rate", 24),
            "expand_prompt": work_order.get("expand_prompt", False),
            "reverse_video": work_order.get("reverse_video", False),
            "enable_safety_checker": work_order.get("enable_safety_checker", True),
            "enable_detail_pass": work_order.get("enable_detail_pass", False),
            "temporal_adain_factor": work_order.get("temporal_adain_factor", 0.5),
            "tone_map_compression_ratio": work_order.get("tone_map_compression_ratio", 0),
            "loras": work_order.get("loras", [])
        }
        
        # Remove None values
        return {k: v for k, v in config.items() if v is not None}

    def _select_model(self, work_order: Dict[str, Any]) -> str:
        """Select video model based on requirements."""
        # Use explicit model if specified
        if work_order.get("model"):
            return work_order["model"]
        
        # Default to Wan 2.2 5B model for text-to-video
        return self.model_id

    def _create_fastwan_prompt(
        self, 
        brief: str, 
        bullets: list, 
        subject_context: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Create highly specific and concrete prompt for FastWan video generation."""
        
        # Check if this is projectile motion content
        if "physics" in subject_context.lower() and any("projectile" in bullet.lower() for bullet in bullets):
            # Very specific projectile motion prompt
            video_prompt = (
                "A red ball is launched from the left side of the screen at a 45-degree angle upward. "
                "The ball follows a perfect curved parabolic path through the air against a clean white background. "
                "The ball moves smoothly from left to right while simultaneously rising then falling due to gravity. "
                "Show the complete arc: ball starts low on the left, rises to peak height in the middle, then falls down to the right side. "
                "The motion is smooth and realistic with proper physics - horizontal velocity stays constant while vertical motion shows acceleration due to gravity. "
                "Camera is stationary showing the full trajectory path. "
                "No text, no labels, no captions, no words anywhere in the video. "
                "Professional educational demonstration with excellent lighting and clarity. "
                "Duration: 5 seconds showing the complete projectile motion from launch to landing."
            )
        elif "physics" in subject_context.lower():
            # General physics demonstration
            video_prompt = (
                "A blue sphere demonstrates physics principles through clear motion. "
                "The object moves in a predictable pattern showing force and motion relationships. "
                "Clean laboratory-style background with professional lighting. "
                "Smooth realistic motion with proper physics simulation. "
                "No text overlays, no captions, pure visual demonstration. "
                "Educational style suitable for university students. "
                "5 seconds of clear physics demonstration."
            )
        elif "math" in subject_context.lower():
            # Mathematical visualization
            video_prompt = (
                "Geometric shapes demonstrate mathematical concepts through motion and transformation. "
                "Clean minimalist background with precise geometric animations. "
                "Shapes move, rotate, or transform to illustrate mathematical relationships. "
                "Professional educational style with smooth transitions. "
                "No text, no numbers visible, pure geometric visualization. "
                "5 seconds of mathematical concept demonstration."
            )
        else:
            # Generic educational content
            video_prompt = (
                "Educational demonstration showing clear visual concepts through motion and animation. "
                "Clean professional background with excellent lighting. "
                "Smooth, purposeful movements that illustrate the educational topic. "
                "No text overlays, no captions, pure visual storytelling. "
                "University-level educational presentation style. "
                "5 seconds of engaging visual demonstration."
            )
        
        print(f"🚀 Generated concrete prompt: {video_prompt}")
        return video_prompt

    async def _download_video(self, video_url: str, video_path: str) -> None:
        """Download video from URL to local path."""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url)
            response.raise_for_status()
            
            with open(video_path, "wb") as f:
                f.write(response.content)
