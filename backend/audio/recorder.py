import os
import cv2
import time
import queue
import threading
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

# Ensure data folder exists
os.makedirs("backend/data", exist_ok=True)


def record_audio_only(duration=10, sample_rate=44100):
    """
    Records only audio and saves it as WAV.
    """
    audio_path = "backend/data/interview_audio.wav"

    print(f"[AUDIO] Recording for {duration} seconds...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    write(audio_path, sample_rate, recording)
    print(f"[AUDIO] Saved to {audio_path}")

    return audio_path


def record_video_only(duration=10, fps=20.0):
    """
    Records only video and saves it as MP4.
    Press Q to stop early.
    """
    video_path = "backend/data/interview_video.avi"

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not access webcam.")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # AVI codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))

    print(f"[VIDEO] Recording for {duration} seconds...")
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out.write(frame)
        cv2.imshow("Recording Video - Press Q to stop", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[VIDEO] Stopped early by user.")
            break

        if time.time() - start_time >= duration:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
        raise Exception("Video file was not saved correctly.")

    print(f"[VIDEO] Saved to {video_path}")
    return video_path


def _audio_thread_worker(duration, sample_rate, result_queue):
    """
    Worker thread for audio recording.
    """
    try:
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )
        sd.wait()
        result_queue.put(("audio", audio_data, None))
    except Exception as e:
        result_queue.put(("audio", None, e))


def _video_thread_worker(duration, fps, result_queue):
    """
    Worker thread for video recording.
    Press Q to stop early.
    """
    video_path = "backend/data/interview_video.mp4"

    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise Exception("Could not access webcam.")

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(video_path, fourcc, fps, (frame_width, frame_height))

        start_time = time.time()
        stopped_early = False

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            out.write(frame)
            cv2.imshow("Interview Recording - Press Q to stop early", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                stopped_early = True
                break

            if time.time() - start_time >= duration:
                break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        if not os.path.exists(video_path) or os.path.getsize(video_path) == 0:
            raise Exception("Video file was not saved correctly.")

        result_queue.put(("video", video_path, stopped_early, None))

    except Exception as e:
        result_queue.put(("video", None, False, e))


def record_interview(duration=10, sample_rate=44100, fps=20.0):
    """
    Records audio and video simultaneously.
    Saves:
      - backend/data/interview_audio.wav
      - backend/data/interview_video.mp4

    Returns:
      (audio_path, video_path)
    """
    audio_path = "backend/data/interview_audio.wav"
    video_path = "backend/data/interview_video.mp4"

    # Clean old files if present
    if os.path.exists(audio_path):
        os.remove(audio_path)
    if os.path.exists(video_path):
        os.remove(video_path)

    audio_queue = queue.Queue()
    video_queue = queue.Queue()

    audio_thread = threading.Thread(
        target=_audio_thread_worker,
        args=(duration, sample_rate, audio_queue)
    )

    video_thread = threading.Thread(
        target=_video_thread_worker,
        args=(duration, fps, video_queue)
    )

    print("[INTERVIEW] Starting simultaneous audio + video recording...")

    audio_thread.start()
    video_thread.start()

    # Wait for both to finish
    audio_thread.join()
    video_thread.join()

    # Get audio result
    audio_result = audio_queue.get()
    _, audio_data, audio_error = audio_result

    if audio_error:
        raise Exception(f"Audio recording failed: {audio_error}")

    # Save audio after recording completes
    write(audio_path, sample_rate, audio_data)

    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        raise Exception("Audio file was not saved correctly.")

    # Get video result
    video_result = video_queue.get()
    _, saved_video_path, stopped_early, video_error = video_result

    if video_error:
        raise Exception(f"Video recording failed: {video_error}")

    print(f"[INTERVIEW] Audio saved to {audio_path}")
    print(f"[INTERVIEW] Video saved to {saved_video_path}")

    if stopped_early:
        print("[INTERVIEW] Recording was stopped early by user via Q key.")

    return audio_path, saved_video_path


# Backward-compatible aliases (so old imports won't break immediately)
def record_audio(duration=10, sample_rate=44100):
    return record_audio_only(duration=duration, sample_rate=sample_rate)


def record_video(duration=10, fps=20.0):
    return record_video_only(duration=duration, fps=fps)

