import re
from collections import Counter

FILLER_WORDS = [
    "um", "uh", "like", "you know", "actually", "basically",
    "so", "well", "i mean", "kind of", "sort of"
]


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def analyze_fillers(transcript):
    """
    Detect filler words and return count details.
    """
    cleaned = clean_text(transcript)

    filler_counts = Counter()
    total_fillers = 0

    for filler in FILLER_WORDS:
        # Match phrase safely
        pattern = r"\b" + re.escape(filler) + r"\b"
        matches = re.findall(pattern, cleaned)
        count = len(matches)
        if count > 0:
            filler_counts[filler] = count
            total_fillers += count

    return {
        "total_fillers": total_fillers,
        "filler_breakdown": dict(filler_counts)
    }


def calculate_wpm(transcript, duration_seconds):
    """
    Calculate words per minute.
    """
    words = transcript.split()
    word_count = len(words)

    if duration_seconds <= 0:
        return 0, word_count

    wpm = (word_count / duration_seconds) * 60
    return round(wpm, 2), word_count


def calculate_fluency_score(total_fillers, wpm):
    """
    Basic fluency score out of 100.
    Ideal WPM for interviews: roughly 110–160
    """
    score = 100

    # Penalize too many fillers
    score -= total_fillers * 3

    # Penalize speaking too slow or too fast
    if wpm < 90:
        score -= 15
    elif 90 <= wpm < 110:
        score -= 5
    elif 110 <= wpm <= 160:
        score -= 0
    elif 160 < wpm <= 190:
        score -= 8
    else:
        score -= 15

    # Keep in bounds
    score = max(0, min(100, score))
    return score


def calculate_hesitation_score(total_fillers, word_count):
    """
    Simple hesitation ratio based on filler density.
    Lower is better.
    """
    if word_count == 0:
        return 0

    hesitation_ratio = total_fillers / word_count
    hesitation_score = round(hesitation_ratio * 100, 2)
    return hesitation_score


def generate_audio_feedback(fluency_score, wpm, total_fillers):
    feedback = []

    if fluency_score >= 85:
        feedback.append("Excellent fluency and communication clarity.")
    elif fluency_score >= 70:
        feedback.append("Good communication, but there is room for improvement.")
    else:
        feedback.append("Fluency needs improvement. Practice speaking more smoothly and confidently.")

    if wpm < 100:
        feedback.append("You are speaking a bit slowly. Try maintaining a more natural interview pace.")
    elif wpm > 170:
        feedback.append("You are speaking a bit fast. Slow down slightly for better clarity.")
    else:
        feedback.append("Your speaking pace is within a good interview range.")

    if total_fillers == 0:
        feedback.append("Great job! No filler words detected.")
    elif total_fillers <= 3:
        feedback.append("A few filler words were detected. Reducing them will improve confidence.")
    else:
        feedback.append("Multiple filler words detected. Practice structured speaking to reduce hesitation.")

    return feedback