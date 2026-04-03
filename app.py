import streamlit as st
import os

from backend.audio.recorder import record_audio, record_video
from backend.audio.transcriber import transcribe_audio
from backend.audio.filler_analysis import (
    analyze_fillers,
    calculate_wpm,
    calculate_fluency_score,
    calculate_hesitation_score,
    generate_audio_feedback
)
from backend.video.face_analyzer import analyze_face

st.set_page_config(page_title="Multimodal Interview Intelligence System", layout="wide")

st.title("🎤 Multimodal Interview Intelligence System")
st.subheader("AI-Powered Interview Analysis for Voice, Face, NLP, and Confidence")

st.markdown("""
### Phase 4: Audio + Video Intelligence
This module supports:
- 🎙️ Audio Recording
- 📹 Video Recording
- 📝 Speech-to-Text (Whisper)
- 🧠 Filler Word Detection
- ⚡ Fluency Scoring
- ⏱️ Speaking Speed Analysis
- 👁️ Face Presence Detection
- 👀 Eye Contact Approximation
- 😊 Smile Detection
- 💯 Visual Confidence Scoring
""")

# Ensure data folder exists
os.makedirs("backend/data", exist_ok=True)

# Duration input
duration = st.slider("Select Recording Duration (seconds)", min_value=5, max_value=60, value=10)

col1, col2 = st.columns(2)

# ---------------- AUDIO RECORDING ----------------
with col1:
    st.markdown("## 🎙️ Audio Recording")
    if st.button("Record Audio"):
        with st.spinner(f"Recording audio for {duration} seconds..."):
            try:
                audio_path = record_audio(duration=duration)
                st.success(f"Audio recording complete! Saved at: {audio_path}")

                with open(audio_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/wav")

            except Exception as e:
                st.error(f"Audio recording failed: {str(e)}")

# ---------------- VIDEO RECORDING ----------------
with col2:
    st.markdown("## 📹 Video Recording")
    if st.button("Record Video"):
        st.warning("A webcam window will open. Press 'Q' to stop early if needed.")
        with st.spinner(f"Recording video for {duration} seconds..."):
            try:
                video_path = record_video(duration=duration)
                st.success(f"Video recording complete! Saved at: {video_path}")

                st.write("Video file exists:", os.path.exists(video_path))
                st.write("Video file size (bytes):", os.path.getsize(video_path))
                st.info(f"Video saved successfully at: {video_path}")

                with open(video_path, "rb") as video_file:
                    st.video(video_file.read())

            except Exception as e:
                st.error(f"Video recording failed: {str(e)}")

st.markdown("---")

# ---------------- AUDIO ANALYSIS ----------------
st.markdown("## 🧠 Audio Analysis")

if st.button("Analyze Audio"):
    audio_path = "backend/data/interview_audio.wav"

    if not os.path.exists(audio_path):
        st.error("No audio file found. Please record audio first.")
    else:
        with st.spinner("Transcribing audio with Whisper and analyzing speech..."):
            try:
                # Step 1: Transcribe
                transcript = transcribe_audio(audio_path)

                # Step 2: Analyze fillers
                filler_result = analyze_fillers(transcript)
                total_fillers = filler_result["total_fillers"]
                filler_breakdown = filler_result["filler_breakdown"]

                # Step 3: WPM
                wpm, word_count = calculate_wpm(transcript, duration)

                # Step 4: Fluency + hesitation
                fluency_score = calculate_fluency_score(total_fillers, wpm)
                hesitation_score = calculate_hesitation_score(total_fillers, word_count)

                # Step 5: Feedback
                feedback = generate_audio_feedback(fluency_score, wpm, total_fillers)

                # ---------------- DISPLAY RESULTS ----------------
                st.success("Audio analysis complete!")

                st.markdown("### 📝 Transcript")
                st.text_area("Transcribed Text", transcript, height=180)

                metric1, metric2, metric3, metric4 = st.columns(4)

                with metric1:
                    st.metric("Words", word_count)

                with metric2:
                    st.metric("WPM", wpm)

                with metric3:
                    st.metric("Fluency Score", f"{fluency_score}/100")

                with metric4:
                    st.metric("Hesitation Score", f"{hesitation_score}%")

                st.markdown("### 🔎 Filler Word Analysis")
                st.write(f"**Total Fillers Detected:** {total_fillers}")

                if filler_breakdown:
                    st.json(filler_breakdown)
                else:
                    st.success("No filler words detected 🎉")

                st.markdown("### 💬 Communication Feedback")
                for item in feedback:
                    st.write(f"- {item}")

            except Exception as e:
                st.error(f"Audio analysis failed: {str(e)}")

st.markdown("---")

# ---------------- VIDEO ANALYSIS ----------------
st.markdown("## 👁️ Video Analysis")

if st.button("Analyze Video"):
    video_path = "backend/data/interview_video.mp4"

    if not os.path.exists(video_path):
        st.error("No video file found. Please record video first.")
    else:
        with st.spinner("Analyzing facial presence, eye contact, and confidence signals..."):
            try:
                result = analyze_face(video_path)

                st.success("Video analysis complete!")

                metric1, metric2, metric3, metric4 = st.columns(4)

                with metric1:
                    st.metric("Total Frames", result["total_frames"])

                with metric2:
                    st.metric("Face Presence", f'{result["face_presence_pct"]}%')

                with metric3:
                    st.metric("Eye Contact", f'{result["eye_contact_pct"]}%')

                with metric4:
                    st.metric("Confidence Score", f'{result["confidence_score"]}/100')

                st.markdown("### 😊 Facial Expression Metrics")
                st.write(f"**Smile Frequency:** {result['smile_pct']}%")
                st.write(f"**Face Detected Frames:** {result['face_frames']} / {result['total_frames']}")
                st.write(f"**Eye Contact Frames:** {result['eye_contact_frames']} / {result['total_frames']}")
                st.write(f"**Smile Frames:** {result['smile_frames']} / {result['total_frames']}")

                st.markdown("### 💬 Video Feedback")
                for item in result["feedback"]:
                    st.write(f"- {item}")

            except Exception as e:
                st.error(f"Video analysis failed: {str(e)}")

st.markdown("---")

st.info("Next Phase: Multimodal Fusion (Audio + Video + NLP Relevance + Final Interview Score)")