import cv2
import os


def analyze_face(video_path):
    """
    Analyze face presence, approximate eye contact, and smile frequency from video.
    Returns structured metrics + feedback.
    """

    if not os.path.exists(video_path):
        raise Exception(f"Video file not found: {video_path}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise Exception("Could not open video file for analysis.")

    # Load Haar cascades from OpenCV
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_eye.xml"
    )
    smile_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_smile.xml"
    )

    total_frames = 0
    face_frames = 0
    eye_contact_frames = 0
    smile_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        total_frames += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(60, 60)
        )

        if len(faces) > 0:
            face_frames += 1

            # Take the largest face (main speaker)
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            x, y, w, h = largest_face

            face_roi_gray = gray[y:y+h, x:x+w]

            # Detect eyes inside face ROI
            eyes = eye_cascade.detectMultiScale(
                face_roi_gray,
                scaleFactor=1.1,
                minNeighbors=8,
                minSize=(20, 20)
            )

            # Approx eye contact: if 2+ eyes visible, assume looking reasonably at camera
            if len(eyes) >= 2:
                eye_contact_frames += 1

            # Detect smile inside lower half of face
            lower_face_gray = face_roi_gray[h//2:, :]
            smiles = smile_cascade.detectMultiScale(
                lower_face_gray,
                scaleFactor=1.7,
                minNeighbors=20,
                minSize=(25, 25)
            )

            if len(smiles) > 0:
                smile_frames += 1

    cap.release()

    if total_frames == 0:
        raise Exception("No frames could be read from the video.")

    face_presence_pct = round((face_frames / total_frames) * 100, 2)
    eye_contact_pct = round((eye_contact_frames / total_frames) * 100, 2)
    smile_pct = round((smile_frames / total_frames) * 100, 2)

    confidence_score = calculate_confidence_score(
        face_presence_pct, eye_contact_pct, smile_pct
    )

    feedback = generate_face_feedback(
        face_presence_pct, eye_contact_pct, smile_pct, confidence_score
    )

    return {
        "total_frames": total_frames,
        "face_frames": face_frames,
        "eye_contact_frames": eye_contact_frames,
        "smile_frames": smile_frames,
        "face_presence_pct": face_presence_pct,
        "eye_contact_pct": eye_contact_pct,
        "smile_pct": smile_pct,
        "confidence_score": confidence_score,
        "feedback": feedback
    }


def calculate_confidence_score(face_presence_pct, eye_contact_pct, smile_pct):
    """
    Weighted confidence score out of 100.
    """
    score = (
        face_presence_pct * 0.4 +
        eye_contact_pct * 0.4 +
        smile_pct * 0.2
    )

    return round(min(score, 100), 2)


def generate_face_feedback(face_presence_pct, eye_contact_pct, smile_pct, confidence_score):
    feedback = []

    # Face presence
    if face_presence_pct >= 90:
        feedback.append("Excellent camera presence throughout the interview.")
    elif face_presence_pct >= 70:
        feedback.append("Good face visibility, but try to stay centered more consistently.")
    else:
        feedback.append("Your face was not visible consistently. Maintain better camera positioning.")

    # Eye contact
    if eye_contact_pct >= 75:
        feedback.append("Strong eye contact detected. This reflects confidence and engagement.")
    elif eye_contact_pct >= 50:
        feedback.append("Moderate eye contact. Try looking at the camera more often.")
    else:
        feedback.append("Low eye contact detected. Improve camera focus for stronger interview presence.")

    # Smile
    if smile_pct >= 20:
        feedback.append("Good positive facial expression. Smiling helps create a confident impression.")
    elif smile_pct > 0:
        feedback.append("A slight smile was detected. A warmer expression can improve approachability.")
    else:
        feedback.append("No smile detected. A natural slight smile can make you appear more confident and friendly.")

    # Confidence score
    if confidence_score >= 80:
        feedback.append("Overall visual confidence is excellent.")
    elif confidence_score >= 60:
        feedback.append("Visual confidence is good, but can be improved with stronger eye contact and posture.")
    else:
        feedback.append("Visual confidence needs improvement. Focus on posture, camera alignment, and facial engagement.")

    return feedback