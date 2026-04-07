"""
AI Summarizer — uses HuggingFace Inference API for text summarization.
"""
import requests
import os

HF_API_KEY = os.environ.get("HF_API_KEY", "").strip()
HF_SUMMARY_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
HF_HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Accept": "application/json"
} if HF_API_KEY else {"Accept": "application/json"}

def summarize_text(text, max_length=150, min_length=50):
    """
    Summarize text using BART model via HuggingFace Inference API.
    Falls back to extractive summary if API unavailable.
    """
    if not text or len(text.strip()) < 50:
        return None

    # Truncate to model limit
    text = text[:2000]

    try:
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False,
            }
        }
        resp = requests.post(HF_SUMMARY_URL, json=payload, headers=HF_HEADERS, timeout=30)
        if resp.status_code == 503:
            import time; time.sleep(2)
            resp = requests.post(HF_SUMMARY_URL, json=payload, headers=HF_HEADERS, timeout=30)
        if resp.ok:
            result = resp.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('summary_text', '') or result[0].get('generated_text', '')
            elif isinstance(result, dict):
                return result.get('summary_text', '') or result.get('generated_text', '')
    except Exception:
        pass

    # Fallback: extractive summarization (key sentences)
    return extractive_summary(text, target_sentences=3)

def extractive_summary(text, target_sentences=3):
    """Simple extractive summarization — pick most important sentences."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if len(sentences) <= target_sentences:
        return ' '.join(sentences)

    # Score sentences by word overlap with first sentence (title-like) and length
    scored = []
    first_words = set(sentences[0].lower().split()) if sentences else set()
    for i, sent in enumerate(sentences):
        words = set(sent.lower().split())
        # Prefer sentences with unique vocabulary
        unique_overlap = len(words - first_words)
        # Penalize very long or very short
        length_score = min(len(sent.split()), 30) / 30
        score = unique_overlap * 0.7 + length_score * 0.3
        # First sentence gets slight boost
        if i == 0:
            score += 2
        scored.append((score, i, sent))

    scored.sort(reverse=True)
    top = sorted(scored[:target_sentences], key=lambda x: x[1])  # maintain original order
    return ' '.join(s[2] for s in top)

def summarize(text, length="medium"):
    """
    Summarize text at different lengths.
    length: 'short' (1-2 sentences), 'medium' (3 sentences), 'long' (paragraph)
    """
    if length == "short":
        return summarize_text(text, max_length=50, min_length=20)
    elif length == "long":
        return summarize_text(text, max_length=250, min_length=100)
    else:
        return summarize_text(text, max_length=150, min_length=50)
