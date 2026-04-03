import sounddevice as sd
import soundfile as sf
import cv2
import os
import time


def record_audio(duration=10, sample_rate=44100, output_path="backend/data/interview_audio.wav"):
    """
    Records audio from microphone and saves as WAV file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"Recording audio for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()

    sf.write(output_path, audio_data, sample_rate)
    print(f"Audio saved to {output_path}")

    return output_path


def record_video(duration=10, output_path="backend/data/interview_video.mp4"):
    """
    Records video from webcam and saves as MP4 file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Could not access webcam.")

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 20.0

    # MP4-compatible codec (best common choice)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    if not out.isOpened():
        cap.release()
        raise Exception("Could not initialize video writer for MP4.")

    print(f"Recording video for {duration} seconds...")
    start_time = time.time()

    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if not ret:
            break

        out.write(frame)

        cv2.imshow("Recording Video - Press Q to stop early", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    if not os.path.exists(output_path):
        raise Exception("Video file was not created.")

    if os.path.getsize(output_path) == 0:
        raise Exception("Video file is empty.")

    print(f"Video saved to {output_path}")
    return output_path