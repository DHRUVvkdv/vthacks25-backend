# EduTransform AI - 16 Hour Implementation Guide

## 🎯 **MVP Description**

Transform educational videos from ANY subject into 8 personalized learning formats for students with ANY academic background using intelligent content adaptation.

**Demo Flow:** Upload educational video + user preferences → AI extracts content → Generate 8 personalized formats → Display learning hub

**Demo Focus:** CS student learning projectile motion physics with programming analogies

## 🤖 **10-Agent System Architecture**

```
Video Upload + User Preferences → Orchestrator Agent → Content Strategy Agent
                                                              ↓
                                    Parallel Content Generation Agents:
                                    ├─ Video Generation Agent
                                    ├─ Animation Config Agent
                                    ├─ Visualization Agent
                                    ├─ Explanation Agent
                                    ├─ Code/Equation Agent
                                    ├─ Application Agent
                                    ├─ Summary Agent
                                    └─ Quiz Generation Agent
```

**Core Agents:**

- **Orchestrator Agent** - Coordinates entire workflow
- **Content Strategy Agent** - Plans personalized content based on subject + user background

**Specialized Content Agents:**

- **Video Generation Agent** - Creates engaging intro scripts -> VIDEO FORMAT
- **Explanation Agent** - Background-appropriate analogies and explanations -> TEXT ONLY
- **Animation Config Agent** - Three.js visualization code -> Javascript code showing projectile motion
- **Code/Equation Agent** - Formulas, calculations, and code examples -> ```TEXT
- **Visualization Agent** - Diagrams, charts, and visual content -> GRAPH
- **Application Agent** - Real-world examples relevant to user background -> TEXT ONLY
- **Summary Agent** - Key concepts with personalized connections -> TEXT ONLY
- **Quiz Generation Agent** - Contextualized assessment questions -> JSON TEXT FORMAT

## 📋 **8 Content Formats (Subject-Agnostic)**

1. **Hook Video** ← Video Generation Agent
2. **Concept Explanation** ← Explanation Agent
3. **Static Animation** ← Animation Config Agent
4. **Code/Equations** ← Code/Equation Agent
5. **Visual Diagrams** ← Visualization Agent
6. **Practice Problems** ← Quiz Generation Agent
7. **Real-world Applications** ← Application Agent
8. **Summary Cards** ← Summary Agent

**Demo Example (CS + Physics):**

- Hook Video: "Physics in Game Development"
- Explanation: Programming analogies for projectile motion
- Animation: Three.js physics simulation
- Code/Equations: Physics calculations in Python/JavaScript

## 💻 **Tech Stack & Implementation**

**Backend (FastAPI + Python)**

- Video upload handling and audio extraction (ffmpeg)
- OpenAI Whisper API for speech-to-text transcription ($0.006/minute)
- OpenAI GPT-4 API integration for all content agents
- Agent orchestration system
- Subject-agnostic content generation pipeline

**Frontend (Next.js + React)**

- Video upload interface with user preference selection
- Universal learning hub for any subject
- Three.js static animations
- Responsive design

**Key APIs & Libraries**

- OpenAI Whisper API for video transcription (99+ languages, $0.006/minute)
- OpenAI GPT-4 API for intelligent content generation
- ffmpeg for video processing and audio extraction
- Three.js for 3D animations
- Tailwind CSS for styling

## 🛠️ **Agent Implementation Details**

### **Video Processing Pipeline**

```python
import subprocess
import openai

def process_video(video_file_path):
    # 1. Extract audio using ffmpeg
    audio_path = "temp_audio.wav"
    subprocess.run([
        "ffmpeg", "-i", video_file_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", audio_path
    ])

    # 2. Transcribe with OpenAI Whisper API
    with open(audio_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            language="en"  # Optional: auto-detect if omitted
        )

    # 3. Extract key concepts for content generation
    concepts = extract_subject_concepts(transcript["text"])
    return {"transcript": transcript["text"], "concepts": concepts}
```

### **Agent 2: Content Strategist**

```python
def create_strategy(concepts, persona="CS_student"):
    strategy = generate_cs_analogies(concepts)
    return format_generation_plan(strategy)
```

### **Specialized Content Agents (Agents 3-10)**

```python
# Agent 3: Hook Video Generator
def generate_hook_video(concepts, strategy):
    return create_engaging_script_with_cs_hooks(concepts)

# Agent 4: Explanation Generator
def generate_explanation(concepts, strategy):
    return create_cs_analogies_explanation(concepts)

# Agent 5: Animation Generator
def generate_animation(concepts, strategy):
    return generate_threejs_code(concepts)  # Static visualization

# Agent 6: Code Example Generator
def generate_code_examples(concepts, strategy):
    return create_physics_code_samples(concepts)

# Agent 7: Diagram Generator
def generate_diagrams(concepts, strategy):
    return create_annotated_diagrams(concepts)

# Agent 8: Problem Generator
def generate_problems(concepts, strategy):
    return create_cs_contextualized_questions(concepts)

# Agent 9: Application Generator
def generate_applications(concepts, strategy):
    return create_gamedev_examples(concepts)

# Agent 10: Summary Generator
def generate_summary(concepts, strategy):
    return create_key_concept_cards(concepts)
```

## ⏱️ **16-Hour Implementation Timeline**

### **Hours 1-4: Foundation Setup**

**Backend Dev:** FastAPI setup, video upload endpoint, ffmpeg + OpenAI Whisper API integration
**Frontend Dev:** Next.js project, video upload interface, user preference selection
**Mixed Dev:** Database schema, agent orchestration structure

### **Hours 5-8: Core Agents**

**Backend Dev:** Video processing pipeline + Content Strategy Agent
**Frontend Dev:** Learning hub layout, content display components
**Mixed Dev:** Agents 3-6 (Video Generation, Explanation, Animation Config, Code/Equation)

### **Hours 9-12: Remaining Content Agents**

**Backend Dev:** Agents 7-10 (Visualization, Application, Summary, Quiz Generation)
**Frontend Dev:** Three.js static animation display, content renderers
**Mixed Dev:** Complete all 8 content formats, API integration

### **Hours 13-16: Polish & Demo**

**All Devs:** Bug fixes, UI polish, demo content preparation, presentation setup

## 🎯 **MVP Success Criteria**

✅ Upload physics video → Extract transcript  
✅ Generate 8 different CS-personalized content formats  
✅ Display static Three.js animation visualization
✅ Working assessment with CS-contextualized questions  
✅ Responsive web interface  
✅ Demo-ready with sample physics content

## 🔧 **Technical Implementation Guide**

### **Required APIs & Setup**

```bash
# Backend Requirements
pip install fastapi uvicorn openai python-multipart ffmpeg-python
export OPENAI_API_KEY="your-key-here"
# Install ffmpeg system dependency: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)

# Frontend Requirements
npx create-next-app@latest frontend
npm install three @react-three/fiber @react-three/drei
```

### **Key File Structure**

```
backend/
├── agents/
│   ├── orchestrator.py
│   ├── content_strategy.py
│   ├── video_generation.py
│   ├── explanation.py
│   ├── animation_config.py
│   ├── code_equation.py
│   ├── visualization.py
│   ├── application.py
│   ├── summary.py
│   └── quiz_generation.py
├── main.py
└── utils/video_processor.py

frontend/
├── components/
│   ├── UploadInterface.tsx
│   ├── LearningHub.tsx
│   └── StaticAnimation.tsx
├── pages/
│   ├── index.tsx
│   └── results.tsx
└── utils/api.ts
```

### **Sample Physics Content for Testing**

- Khan Academy projectile motion video (10-15 minutes)
- MIT OpenCourseWare physics lectures
- YouTube physics demonstrations

### **Demo Script Outline**

1. **Upload:** "Here's a boring physics lecture about projectile motion"
2. **Processing:** "Our agents analyze and personalize for CS students"
3. **Results:** "8 different formats with programming analogies"
4. **Visualization:** "Static Three.js animation with code annotations"
5. **Assessment:** "Quiz questions using game development scenarios"

## 🚀 **Quick Start Commands**

```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend
cd frontend && npm run dev

# Test Upload
curl -X POST "http://localhost:8000/upload" -F "video=@test_physics.mp4"
```
