import asyncio
import os
import time
from typing import Any, Dict, Optional
from google.genai import types
from .base_agent import BaseContentAgent


class GeminiVideoGenerationAgent(BaseContentAgent):
    """
    Generates actual videos using Gemini's Veo 3 video generation model.
    
    Creates videos based on prompts by sending requests to Gemini's Veo 3 model
    and polling for completion, then downloading the generated video.
    """
    
    def __init__(self):
        super().__init__()
        # Override model for video generation
        self.video_model_name = 'veo-3.0-fast-generate-001'
    
    async def generate_content(
        self, 
        work_order: Dict[str, Any], 
        gemini_analysis: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate actual video using Gemini Veo 3 model."""
        
        print("🎬 GeminiVideoGenerationAgent: Starting video generation...")
        
        # Extract context for video prompt
        user_bg = self._get_user_background_context(user_context)
        subject_context = self._get_subject_context(gemini_analysis)
        
        brief = work_order.get("brief", "Create educational video")
        bullets = work_order.get("bullets", [])
        
        print(f"🎬 GeminiVideoGenerationAgent: Brief='{brief}', Concepts={len(bullets)} items")
        
        # Create video prompt based on educational content
        video_prompt = self._create_video_prompt(brief, bullets, subject_context, user_context)
        
        try:
            print("🎬 GeminiVideoGenerationAgent: Sending video generation request to Veo 3...")
            config = self._build_generation_config(work_order)
            image_input = await self._prepare_image_input(work_order)
            operation = self.client.models.generate_videos(
                model=self._select_video_model(work_order),
                prompt=video_prompt,
                config=config,
                image=image_input,
            )
            operation_ref = types.GenerateVideosOperation(name=operation.name)
            max_wait_time = 360
            start_time = time.time()
            poll_interval = 10
            while not operation_ref.done:
                elapsed = time.time() - start_time
                if elapsed > max_wait_time:
                    raise TimeoutError(f"Video generation timeout after {max_wait_time} seconds")
                print(f"🎬 GeminiVideoGenerationAgent: Waiting for completion... ({elapsed:.0f}s elapsed)")
                await asyncio.sleep(poll_interval)
                operation_ref = await asyncio.to_thread(self.client.operations.get, operation_ref)
            if not getattr(operation_ref, "response", None):
                raise RuntimeError("Gemini Veo returned no response")
            if not getattr(operation_ref.response, "generated_videos", None):
                raise RuntimeError("Gemini Veo returned no videos")
            generated_video = operation_ref.response.generated_videos[0]
            # Per docs: client.files.download(file=generated_video.video) then save
            self.client.files.download(file=generated_video.video)
            video_filename = f"gemini_video_{int(time.time())}.mp4"
            video_path = os.path.join(os.getcwd(), "generated_videos", video_filename)
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            generated_video.video.save(video_path)
            result = {
                "agent": "gemini_video_generation",
                "video_path": video_path,
                "video_prompt": video_prompt,
                "duration_estimate": "8 seconds",
                "resolution": config.resolution or "720p",
                "aspect_ratio": config.aspect_ratio or "16:9",
                "generation_time": time.time() - start_time,
                "status": "success",
                "personalization": {
                    "user_background": user_context.get("major", "general"),
                    "academic_level": user_context.get("academicLevel", "general")
                },
                "educational_context": {
                    "subject": subject_context,
                    "key_concepts": bullets[:5]
                }
            }
            print(f"🎬 GeminiVideoGenerationAgent: Video saved to {video_path}")
            print(f"🎬 GeminiVideoGenerationAgent: File size: {os.path.getsize(video_path) / (1024 * 1024):.2f} MB")
            return result

        except Exception as e:
            print(f"🎬 GeminiVideoGenerationAgent: Error - {str(e)}")
            return {
                "agent": "gemini_video_generation",
                "status": "failed",
                "error": str(e),
                "video_path": None,
                "video_prompt": video_prompt,
                "fallback_suggestion": "Consider using the VideoGenerationAgent for script generation instead",
                "personalization": {
                    "user_background": user_context.get("major", "general"),
                    "academic_level": user_context.get("academicLevel", "general")
                }
            }

    def _build_generation_config(self, work_order: Dict[str, Any]) -> types.GenerateVideosConfig:
        aspect_ratio = work_order.get("aspect_ratio", "16:9")
        # Default to lower quality per request (720p) unless explicitly overridden
        resolution = work_order.get("resolution", "720p")
        # Very strong negative prompt to completely avoid any text elements
        default_neg = (
            "low quality, blurry, distorted, cartoon, text, captions, subtitles, watermark, logo, lower-third, "
            "posterized, written words, letters, numbers, typography, titles, labels, signs, banners, "
            "text overlays, annotations, descriptions, words on screen, readable text, writing, inscriptions, "
            "character text, font, script, handwriting, printed text, digital text, any visible text elements"
        )
        negative_prompt = work_order.get("negative_prompt", default_neg)
        person_generation = work_order.get("person_generation")
        seed = work_order.get("seed")
        return types.GenerateVideosConfig(
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            person_generation=person_generation,
            seed=seed,
        )

    def _select_video_model(self, work_order: Dict[str, Any]) -> str:
        # Prefer fast model for speed/cost unless explicitly turned off
        explicit_model = work_order.get("model")
        if explicit_model:
            return explicit_model
        if work_order.get("fast", True):
            return 'veo-3.0-fast-generate-001'
        return self.video_model_name

    async def _prepare_image_input(self, work_order: Dict[str, Any]) -> Optional[types.Image]:
        image_path = work_order.get("initial_image_path")
        image_bytes = work_order.get("initial_image_bytes")
        image_base64 = work_order.get("initial_image_base64")
        if image_bytes:
            return types.Image(image_bytes=image_bytes, mime_type=work_order.get("initial_image_mime", "image/png"))
        if image_base64:
            return types.Image(image_bytes=image_base64, mime_type=work_order.get("initial_image_mime", "image/png"))
        if image_path and os.path.exists(image_path):
            data = await asyncio.to_thread(self._read_binary_file, image_path)
            return types.Image(image_bytes=data, mime_type=work_order.get("initial_image_mime", self._guess_mime_type(image_path)))
        return None

    @staticmethod
    def _read_binary_file(path: str) -> bytes:
        with open(path, "rb") as file:
            return file.read()

    @staticmethod
    def _guess_mime_type(path: str) -> str:
        extension = os.path.splitext(path)[1].lower()
        if extension in {".jpg", ".jpeg"}:
            return "image/jpeg"
        if extension == ".png":
            return "image/png"
        if extension == ".webp":
            return "image/webp"
        return "image/png"
    
    def _create_video_prompt(
        self, 
        brief: str, 
        bullets: list, 
        subject_context: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Create an effective video prompt for Veo 3 with no text overlays."""
        
        # Extract subject and topic
        major = user_context.get("major", "general")
        academic_level = user_context.get("academicLevel", "general")
        
        # Build educational video prompt focused on pure visuals
        prompt_parts = []
        
        # Base scene description - emphasize visual-only content
        prompt_parts.append("A professional educational video with pure visual demonstrations")
        prompt_parts.append("no text overlays, no captions, no written words visible")
        
        # Add subject-specific visual elements (avoiding text-based descriptions)
        if "physics" in subject_context.lower():
            prompt_parts.append("showing physics concepts through visual demonstrations, animated objects in motion, forces and interactions")
        elif "math" in subject_context.lower():
            prompt_parts.append("displaying mathematical concepts through geometric shapes, visual patterns, and animated demonstrations")
        elif "computer science" in subject_context.lower() or "programming" in brief.lower():
            prompt_parts.append("featuring visual representations of algorithms, data flow animations, and computational processes")
        elif "biology" in subject_context.lower():
            prompt_parts.append("illustrating biological processes through animated cellular activities and organic structures")
        elif "chemistry" in subject_context.lower():
            prompt_parts.append("demonstrating chemical processes through molecular animations and reaction visualizations")
        else:
            prompt_parts.append("with clear visual demonstrations and animated educational graphics")
        
        # Add key concepts through visual descriptions only
        if bullets:
            key_concepts = bullets[:3]  # Limit to 3 main concepts
            prompt_parts.append(f"visually demonstrating concepts related to: {', '.join(key_concepts)}")
        
        # Add style and quality requirements - emphasize visual-only nature
        prompt_parts.extend([
            "Clean, modern visual-only educational style",
            "High quality visuals with excellent lighting and clarity",
            "Professional visual presentation with smooth animations",
            "Seamless transitions between visual demonstrations",
            "Engaging visual storytelling without any text elements",
            "Pure visual communication through demonstrations and animations"
        ])
        
        # Combine all parts
        video_prompt = ". ".join(prompt_parts) + "."
        
        print(f"🎬 Generated text-free video prompt: {video_prompt}")
        return video_prompt
