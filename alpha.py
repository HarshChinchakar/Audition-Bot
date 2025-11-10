import os
import json
import google.generativeai as genai

# ----------------------------------------
# 1. Set up Gemini API
# ----------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyA5UJsnkYvIUbwwF5hd80RY0lJgHNLuZjQ")
genai.configure(api_key=GOOGLE_API_KEY)

# ----------------------------------------
# 2. Load local MP4 video file into bytes
# ----------------------------------------
def load_video_as_bytes(filepath):
    if not os.path.exists(filepath):
        print("❌ File not found:", filepath)
        return None
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return None


# 3. Prompt for Deep Acting Evaluation


# First basic version (Brief)
# _____________________________________________________________________________________________

# def build_prompt_text():
#     return """
# Analyze the provided video of an acting audition based on the following metrics.
# Provide your analysis in a structured format (e.g., JSON or clear headings).

# 1. Facial Expressions & Emotions:
#    - Detected Emotions: What primary emotions (e.g., happiness, sadness, anger, fear, surprise, neutrality) are displayed? Note any significant shifts.
#    - Micro-expressions: (If observable) Are there any brief, involuntary facial expressions that reveal underlying emotions? Describe them.
#    - Consistency: Are the facial expressions consistent with the likely intended emotion of the scene or monologue?

# 2. Gestures & Body Language:
#    - Gesture Analysis: Describe the use of hand movements, posture, and overall body language.
#    - Expressiveness: How effectively do gestures convey the character's emotions and intentions?
#    - Synchronization: Are gestures generally coordinated with spoken words or emotional beats?

# 3. Voice & Speech Analysis:
#    - Clarity: Comment on the pronunciation, enunciation, and overall speech clarity.
#    - Modulation: Analyze pitch, tone, and volume variations. Do they support emotional delivery?
#    - Pacing: Describe the speech rate and use of pauses. Does it feel natural or effective for the performance?
#    - Emotion in Voice: What emotional cues are detected in the voice?

# 4. Timing & Delivery:
#    - Cue Timing (if applicable for dialogue): How is the timing of reactions and responses?
#    - Scene Pacing: Evaluate the overall rhythm and flow of the performance segment.
#    - Synchronization: How well aligned are speech, expressions, and gestures in terms of timing?

# 5. Stage Presence & Confidence:
#    - Engagement: Does the performer appear engaging?
#    - Confidence: Comment on posture, eye contact (if discernible), and overall presence.
#    - Authenticity: How believable is the performance in this segment?

# 6. Overall Performance Evaluation:
#    - Emotional Impact: What is the overall emotional resonance of the performance?
#    - Character Portrayal: How convincingly does the performer seem to embody a character (even if it's a general read)?
#    - Consistency: Is the performance consistent in its quality and choices throughout the video?

# Please provide a detailed breakdown for each point. Format your response as structured JSON.
# """






# A detailed evaluation prompt (No comparison - only singular metrics)

def build_prompt_text():
    return """
    Important:
- DO NOT explain the response outside of the JSON.
- Only return the valid JSON block.
- Do not add extra commentary.
- Ensure the output is valid JSON syntax using double quotes only.
You are a professional casting evaluator assisting in reviewing an acting audition video.

Please analyze the provided performance across the following **six main parameters**, each with its sub-metrics.

Rate each sub-metric **on a scale of 0 to 10**, and provide both a **brief rationale** and a **suggested improvement**, if applicable.

Return your response in **Text pointer with brief explaination format** using this structure:
{
  "Facial Expressions & Emotions": {
    "Detected Emotions": {"score": X, "rationale": "...", "improvement": "..."},
    "Micro-expressions": {"score": X, ...},
    "Consistency": {...}
  },
  ...
  "Overall Performance": {
    "Emotional Impact": {...},
    "Character Portrayal": {...},
    "Consistency": {...}
  }
}

Now evaluate based on:

---

### 1. Facial Expressions & Emotions:
- **Detected Emotions**: Are the dominant emotions clearly identifiable and appropriate for the scene?
- **Micro-expressions**: Are fleeting expressions visible? Do they reflect nuanced internal emotion?
- **Consistency**: Are the emotions expressed consistently with the scene's tone and the character’s arc?

---

### 2. Gestures & Body Language:
- **Gesture Quality**: Are hand movements and posture used purposefully?
- **Expressiveness**: How well do gestures support emotional intent?
- **Physical Coordination**: Are physical actions well-timed with emotional or verbal beats?

---

### 3. Voice & Speech:
- **Clarity**: Is speech articulate and free of slurring or mumbling?
- **Modulation**: Is tone/pitch/volume used effectively to show emotion?
- **Pacing & Rhythm**: Is speech delivery appropriately timed for dramatic impact?
- **Emotional Inflection**: Does the voice convincingly convey feeling?

---

### 4. Timing & Delivery:
- **Beat Awareness**: Are pauses and reactions aligned with emotional pacing?
- **Dialogue Timing**: For scenes with dialogue, are responses naturally timed?
- **Sync with Movement**: Is delivery synchronized with gestures and facial cues?

---

### 5. Stage Presence & Character Engagement:
- **Confidence**: Does the actor appear grounded, focused, and comfortable?
- **Authenticity**: Does the character portrayal feel believable?
- **Engagement**: Does the actor hold the viewer’s attention throughout?

---

### 6. Overall Performance:
- **Emotional Impact**: Does the performance leave a lasting emotional impression?
- **Character Immersion**: Does the actor disappear into the role?
- **Scene Cohesion**: Is the performance consistent from start to finish?

---

Make your evaluation realistic and professional — like a casting director's scoring sheet.
Avoid generic feedback; aim for constructive, personalized insights for improvement.
"""















import time

# ----------------------------------------
# 4. Call Gemini API with video + prompt
# ----------------------------------------
def analyze_video(video_bytes, prompt_text):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        print("\n[R] Sending request to Gemini...")

        start_time = time.time()

        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [
                    {"mime_type": "video/mp4", "data": video_bytes},
                    {"text": prompt_text}
                ]}
            ],
            generation_config={
                "response_mime_type": "text/plain"
            }
        )

        end_time = time.time()
        duration = end_time - start_time
        print(f"\n⏱[T] Total processing time: {duration:.2f} seconds")

        return response.text
    except Exception as e:
        print("[E] Gemini API Error:", e)
        return None

# ----------------------------------------
# 5. Entry Point
# ----------------------------------------
if __name__ == "__main__":
    print("[I] Acting Audition Evaluation (Local MP4 File)\n")
    filepath = input("Enter path to the local .mp4 file: ").strip()

    video_bytes = load_video_as_bytes(filepath)
    if not video_bytes:
        print("[E] Video could not be loaded.")
        exit()

    prompt_text = build_prompt_text()
    result = analyze_video(video_bytes, prompt_text)

    if result:
        print("\n[O] Gemini Response:\n")
        try:
            structured = json.loads(result)
            print(json.dumps(structured, indent=2))

            # Save to file
            json_filename = os.path.splitext(os.path.basename(filepath))[0] + "_analysis.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(structured, f, indent=2, ensure_ascii=False)
            print(f"\n[O] Result saved to: {json_filename}")

        except json.JSONDecodeError:
            print("[E] Could not parse JSON. Raw output:\n")
            print(result)
            fallback_filename = "gemini_raw_output.txt"
            with open(fallback_filename, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"\n[O] Raw text saved to: {fallback_filename}")

    else:
        print("[E] No response received from Gemini.")
