def calculate_final_score(audio_fluency_score, hesitation_score, video_confidence_score, nlp_score=80):
    """
    Combine audio, video, and NLP scores into a final interview score.
    
    Weights:
    - Audio Fluency: 35%
    - Hesitation Penalty (converted): 15%
    - Video Confidence: 30%
    - NLP Relevance: 20%
    """

    # Convert hesitation score (lower is better) into a positive score
    hesitation_positive_score = max(0, 100 - hesitation_score)

    final_score = (
        audio_fluency_score * 0.35 +
        hesitation_positive_score * 0.15 +
        video_confidence_score * 0.30 +
        nlp_score * 0.20
    )

    return round(min(final_score, 100), 2)


def generate_final_feedback(final_score):
    """
    Generate overall interview performance feedback.
    """
    feedback = []

    if final_score >= 85:
        feedback.append("Excellent overall interview performance. You demonstrated strong communication and confident presence.")
    elif final_score >= 70:
        feedback.append("Good overall interview performance. You are doing well, with some room for refinement.")
    elif final_score >= 55:
        feedback.append("Average interview performance. Improvement is needed in communication clarity, confidence, or content delivery.")
    else:
        feedback.append("Interview performance needs significant improvement. Focus on fluency, confidence, and structured answering.")

    if final_score >= 80:
        feedback.append("You are close to being interview-ready for professional settings.")
    elif final_score >= 60:
        feedback.append("With focused practice, you can become interview-ready soon.")
    else:
        feedback.append("Consistent mock interview practice is strongly recommended before real interviews.")

    return feedback