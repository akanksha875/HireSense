import streamlit as st
import os

from backend.audio.recorder import record_interview
from backend.audio.transcriber import transcribe_audio
from backend.audio.filler_analysis import (
    analyze_fillers,
    calculate_wpm,
    calculate_fluency_score,
    calculate_hesitation_score,
    generate_audio_feedback
)
from backend.video.face_analyzer import analyze_face
from backend.analysis.scorer import calculate_final_score, generate_final_feedback
from backend.nlp.relevance_checker import calculate_relevance_score, generate_relevance_feedback

st.set_page_config(page_title="Multimodal Interview Intelligence System", layout="wide")

st.title("🎤 Multimodal Interview Intelligence System")
st.subheader("AI-Powered Interview Analysis for Voice, Face, NLP, and Confidence")


# Ensure data folder exists
os.makedirs("backend/data", exist_ok=True)

# Session state initialization
if "audio_results" not in st.session_state:
    st.session_state.audio_results = None

if "video_results" not in st.session_state:
    st.session_state.video_results = None

if "nlp_results" not in st.session_state:
    st.session_state.nlp_results = None

if "recording_done" not in st.session_state:
    st.session_state.recording_done = False

# ---------------- INTERVIEW QUESTION INPUT ----------------
st.markdown("## ❓ Interview Question Input")
interview_question = st.text_area(
    "Enter the interview question that the candidate is answering:",
    placeholder="Example: Tell me about yourself and your experience with machine learning.",
    height=100
)

# Duration input
duration = st.slider("Select Interview Recording Duration (seconds)", min_value=5, max_value=60, value=10)

st.markdown("---")

# ---------------- SINGLE INTERVIEW RECORDING ----------------
st.markdown("## 🎥 Record Interview (Audio + Video Together)")
st.info("Look at the webcam and speak your answer naturally. A webcam window will open. Avoid pressing Q unless necessary—let the full duration complete for best sync.")

if st.button("Start Interview Recording"):
    with st.spinner(f"Recording interview for {duration} seconds..."):
        try:
            audio_path, video_path = record_interview(duration=duration)

            st.session_state.recording_done = True
            st.session_state.audio_results = None
            st.session_state.video_results = None
            st.session_state.nlp_results = None

            st.success("Interview recording complete! Audio and video were captured together.")

            # Show audio preview
            if os.path.exists(audio_path):
                with open(audio_path, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/wav")

            # Show video preview
            if os.path.exists(video_path):
                with open(video_path, "rb") as video_file:
                    st.video(video_file.read())

            st.write("**Saved Files:**")
            st.write(f"- Audio: {audio_path}")
            st.write(f"- Video: {video_path}")

        except Exception as e:
            st.error(f"Interview recording failed: {str(e)}")

st.markdown("---")

# ---------------- AUDIO + NLP ANALYSIS ----------------
st.markdown("## 🧠 Audio + NLP Analysis")

if st.button("Analyze Audio + NLP"):
    audio_path = "backend/data/interview_audio.wav"

    if not os.path.exists(audio_path):
        st.error("No interview audio found. Please record the interview first.")
    else:
        with st.spinner("Transcribing audio with Whisper and analyzing speech + NLP relevance..."):
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

                # Step 5: Audio Feedback
                audio_feedback = generate_audio_feedback(fluency_score, wpm, total_fillers)

                # Store audio results
                st.session_state.audio_results = {
                    "transcript": transcript,
                    "total_fillers": total_fillers,
                    "filler_breakdown": filler_breakdown,
                    "wpm": wpm,
                    "word_count": word_count,
                    "fluency_score": fluency_score,
                    "hesitation_score": hesitation_score,
                    "feedback": audio_feedback
                }

                # Step 6: NLP relevance scoring (only if question provided)
                if interview_question.strip():
                    relevance_score = calculate_relevance_score(interview_question, transcript)
                    relevance_feedback = generate_relevance_feedback(relevance_score)

                    st.session_state.nlp_results = {
                        "question": interview_question,
                        "relevance_score": relevance_score,
                        "feedback": relevance_feedback
                    }
                else:
                    st.session_state.nlp_results = None

                st.success("Audio + NLP analysis complete!")

            except Exception as e:
                st.error(f"Audio/NLP analysis failed: {str(e)}")

# ---------------- DISPLAY AUDIO RESULTS ----------------
if st.session_state.audio_results:
    audio = st.session_state.audio_results

    st.markdown("### 📝 Transcript")
    st.text_area("Transcribed Text", audio["transcript"], height=180)

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric("Words", audio["word_count"])

    with metric2:
        st.metric("WPM", audio["wpm"])

    with metric3:
        st.metric("Fluency Score", f'{audio["fluency_score"]}/100')

    with metric4:
        st.metric("Hesitation Score", f'{audio["hesitation_score"]}%')

    st.markdown("### 🔎 Filler Word Analysis")
    st.write(f"**Total Fillers Detected:** {audio['total_fillers']}")

    if audio["filler_breakdown"]:
        st.json(audio["filler_breakdown"])
    else:
        st.success("No filler words detected 🎉")

    st.markdown("### 💬 Communication Feedback")
    for item in audio["feedback"]:
        st.write(f"- {item}")

st.markdown("---")

# ---------------- DISPLAY NLP RESULTS ----------------
st.markdown("## 🧠 NLP Relevance Analysis")

if st.session_state.nlp_results:
    nlp = st.session_state.nlp_results

    st.write(f"**Interview Question:** {nlp['question']}")
    st.metric("Relevance Score", f"{nlp['relevance_score']}/100")

    st.markdown("### 💬 Answer Relevance Feedback")
    for item in nlp["feedback"]:
        st.write(f"- {item}")
else:
    st.info("Enter an interview question before analyzing audio to generate NLP relevance scoring.")

st.markdown("---")

# ---------------- VIDEO ANALYSIS ----------------
st.markdown("## 👁️ Video Analysis")

if st.button("Analyze Video"):
    video_path = "backend/data/interview_video.mp4"

    if not os.path.exists(video_path):
        st.error("No interview video found. Please record the interview first.")
    else:
        with st.spinner("Analyzing facial presence, eye contact, and confidence signals..."):
            try:
                result = analyze_face(video_path)

                # Store results
                st.session_state.video_results = result

                st.success("Video analysis complete!")

            except Exception as e:
                st.error(f"Video analysis failed: {str(e)}")

# ---------------- DISPLAY VIDEO RESULTS ----------------
if st.session_state.video_results:
    video = st.session_state.video_results

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric("Total Frames", video["total_frames"])

    with metric2:
        st.metric("Face Presence", f'{video["face_presence_pct"]}%')

    with metric3:
        st.metric("Eye Contact", f'{video["eye_contact_pct"]}%')

    with metric4:
        st.metric("Confidence Score", f'{video["confidence_score"]}/100')

    st.markdown("### 😊 Facial Expression Metrics")
    st.write(f"**Smile Frequency:** {video['smile_pct']}%")
    st.write(f"**Face Detected Frames:** {video['face_frames']} / {video['total_frames']}")
    st.write(f"**Eye Contact Frames:** {video['eye_contact_frames']} / {video['total_frames']}")
    st.write(f"**Smile Frames:** {video['smile_frames']} / {video['total_frames']}")

    st.markdown("### 💬 Video Feedback")
    for item in video["feedback"]:
        st.write(f"- {item}")

st.markdown("---")

# ---------------- FINAL MULTIMODAL SCORE ----------------
st.markdown("## 🧮 Final Interview Score")

if st.button("Generate Final Interview Score"):
    if not st.session_state.audio_results:
        st.error("Please analyze Audio + NLP first.")
    elif not st.session_state.video_results:
        st.error("Please analyze Video first.")
    else:
        audio = st.session_state.audio_results
        video = st.session_state.video_results

        # Use real NLP score if available, else fallback
        if st.session_state.nlp_results:
            nlp_score = st.session_state.nlp_results["relevance_score"]
        else:
            nlp_score = 50  # fallback if no question provided

        final_score = calculate_final_score(
            audio_fluency_score=audio["fluency_score"],
            hesitation_score=audio["hesitation_score"],
            video_confidence_score=video["confidence_score"],
            nlp_score=nlp_score
        )

        final_feedback = generate_final_feedback(final_score)

        st.success("Final multimodal interview score generated!")

        st.metric("🎯 Final Interview Score", f"{final_score}/100")

        if final_score >= 80:
            st.success("✅ Interview Readiness: Strong")
        elif final_score >= 60:
            st.warning("⚠️ Interview Readiness: Moderate")
        else:
            st.error("❌ Interview Readiness: Needs Improvement")

        st.markdown("### 💬 Overall Interview Feedback")
        for item in final_feedback:
            st.write(f"- {item}")

        if not st.session_state.nlp_results:
            st.info("No interview question was provided, so NLP score fallback value (50) was used.")

st.markdown("---")

st.success("🚀 Unified Multimodal Interview Recording + Analysis is now active!")