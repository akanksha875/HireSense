from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_relevance_score(question: str, answer: str):
    """
    Calculates semantic similarity between question and answer.
    Returns:
        similarity_score (float): cosine similarity in percentage (0-100)
    """
    if not question or not answer:
        return 0.0

    # Encode both texts
    question_embedding = model.encode(question, convert_to_tensor=True)
    answer_embedding = model.encode(answer, convert_to_tensor=True)

    # Cosine similarity
    similarity = util.cos_sim(question_embedding, answer_embedding).item()

    # Convert similarity to 0-100 range
    score = max(0, min(100, round(similarity * 100, 2)))

    return score


def generate_relevance_feedback(score: float):
    """
    Generates feedback based on semantic relevance score.
    """
    feedback = []

    if score >= 80:
        feedback.append("Excellent answer relevance. Your response is highly aligned with the interview question.")
    elif score >= 60:
        feedback.append("Good answer relevance. Your response is mostly related to the question, but could be more focused.")
    elif score >= 40:
        feedback.append("Moderate relevance. Some parts of your answer align with the question, but it may need better structure and clarity.")
    else:
        feedback.append("Low relevance. Your answer seems off-topic or insufficiently aligned with the question.")

    return feedback