import streamlit as st
import os
import json
import tempfile
import google.generativeai as genai
import time
import re
import pandas as pd

# 1. Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
genai.configure(api_key=GOOGLE_API_KEY)

# 2. Prompt for Gemini
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

# 3. Gemini API Call
def analyze_video_with_gemini(video_bytes, prompt_text):
    model = genai.GenerativeModel("models/gemini-1.5-flash")

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
    return response.text, duration

# 4. Extract and parse JSON safely
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            cleaned = match.group(0)
            return json.loads(cleaned)
    except Exception:
        return None
    return None

# 5. Parse into readable format and score table
def parse_json_report(data):
    detailed_sections = []
    metric_table = []

    for section, submetrics in data.items():
        section_block = f"{section}\n" + "-" * len(section)
        for metric, details in submetrics.items():
            score = details.get("score", "N/A")
            rationale = details.get("rationale", "No rationale provided.")
            improvement = details.get("improvement", "No improvement suggested.")

            section_block += f"\n\n{metric} (Score: {score}/10)\n"
            section_block += f"Rationale   : {rationale}\n"
            section_block += f"Improvement : {improvement}\n"

            metric_table.append({
                "Section": section,
                "Metric": metric,
                "Score": score
            })

        detailed_sections.append(section_block)

    return "\n\n".join(detailed_sections), metric_table

# 6. Streamlit UI
st.set_page_config(page_title="Audition Evaluator", layout="wide")
st.title("🎬 Acting Audition Evaluator")

uploaded_video = st.file_uploader("Upload an audition video (MP4)", type=["mp4"])

if uploaded_video is not None:
    st.video(uploaded_video)
    with st.spinner("Analyzing performance with Gemini..."):

        video_bytes = uploaded_video.read()
        prompt = build_prompt_text()
        result_text, process_time = analyze_video_with_gemini(video_bytes, prompt)

        response_data = extract_json(result_text)

        if response_data:
            st.success(f"Analysis completed in {process_time:.2f} seconds.")

            # Save to temp files
            temp_dir = tempfile.mkdtemp()
            json_path = os.path.join(temp_dir, "analysis_result.json")
            txt_path = os.path.join(temp_dir, "analysis_result.txt")

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)

            parsed_text, metric_table = parse_json_report(response_data)

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(parsed_text)

            # Tabs for Output
            tab1, tab2 = st.tabs(["Full Evaluation Report", "Score Overview Table"])

            with tab1:
                st.text_area("Detailed Evaluation", value=parsed_text, height=600)

            with tab2:
                df = pd.DataFrame(metric_table)
                st.dataframe(df, use_container_width=True)

            # Download options
            st.download_button("Download JSON Report", data=json.dumps(response_data, indent=2), file_name="analysis_result.json", mime="application/json")
            st.download_button("Download Text Report", data=parsed_text, file_name="analysis_result.txt", mime="text/plain")

        else:
            st.error("The output from Gemini could not be parsed as valid JSON.")
            st.code(result_text, language='text')

