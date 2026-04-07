"""
Writing Analyzer - statistics and readability metrics for text.
"""
import re
import math

def count_syllables(word):
    """Rough syllable count using vowel groups."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    count = 0
    vowels = 'aeiou'
    prev_is_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    if word.endswith('e'):
        count -= 1
    return max(1, count)

def flesch_kincaid(text):
    """Calculate Flesch-Kincaid reading ease and grade level."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return {'reading_ease': 0, 'grade_level': 0, 'label': 'Unknown'}

    words = re.findall(r'\b[a-zA-Z]+\b', text)
    if not words:
        return {'reading_ease': 0, 'grade_level': 0, 'label': 'Unknown'}

    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(w) for w in words)

    avg_sentence_length = total_words / total_sentences if total_sentences else 0
    avg_syllables_per_word = total_syllables / total_words if total_words else 0

    reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    reading_ease = max(0, min(100, reading_ease))

    grade_level = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
    grade_level = max(0, grade_level)

    if reading_ease >= 90:
        label = "Very Easy"
    elif reading_ease >= 70:
        label = "Easy"
    elif reading_ease >= 50:
        label = "Moderate"
    elif reading_ease >= 30:
        label = "Difficult"
    else:
        label = "Very Difficult"

    return {
        'reading_ease': round(reading_ease, 1),
        'grade_level': round(grade_level, 1),
        'label': label,
        'avg_sentence_length': round(avg_sentence_length, 1),
        'avg_syllables_per_word': round(avg_syllables_per_word, 1),
    }

def analyze_writing(text):
    """Comprehensive writing analysis."""
    if not text or len(text.strip()) < 10:
        return None

    text = text.strip()

    # Basic counts
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    total_words = len(words)

    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    total_sentences = len(sentences)

    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    total_paragraphs = len(paragraphs)

    # Character counts
    total_chars = len(text)
    chars_no_spaces = len(text.replace(' ', ''))

    # Unique words
    word_freq = {}
    for w in words:
        wl = w.lower()
        word_freq[wl] = word_freq.get(wl, 0) + 1

    unique_words = len(word_freq)
    unique_ratio = unique_words / total_words if total_words else 0

    # Average word length
    avg_word_len = sum(len(w) for w in words) / total_words if total_words else 0

    # Sentence lengths
    sentence_lengths = [len(re.findall(r'\b[a-zA-Z]+\b', s)) for s in sentences]
    avg_sentence_len = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    max_sentence_len = max(sentence_lengths) if sentence_lengths else 0
    min_sentence_len = min(sentence_lengths) if sentence_lengths else 0

    # Readability
    readability = flesch_kincaid(text)

    # Most common words (excluding stop words)
    stop_words = {
        'the','a','an','of','to','in','for','is','on','that','this','and','it',
        'with','as','by','at','from','or','be','are','was','were','has','have',
        'had','not','but','they','their','we','our','you','your','his','her',
        'its','who','which','what','when','where','why','how','all','each',
        'can','will','would','could','should','may','might','must','shall'
    }
    content_words = {w: c for w, c in word_freq.items() if w not in stop_words and len(w) > 3}
    top_words = sorted(content_words.items(), key=lambda x: x[1], reverse=True)[:10]

    # Tone detection (simple heuristic)
    formal_words = {'therefore','thus','hence','moreover','furthermore','consequently','however','although','whereas','nonetheless'}
    informal_words = {'really','very','just','pretty','quite','sort of','kind of','basically','literally','actually'}
    formal_count = sum(1 for w in words if w.lower() in formal_words)
    informal_count = sum(1 for w in words if w.lower() in informal_words)

    if formal_count > informal_count + 2:
        tone = 'Formal'
    elif informal_count > formal_count + 2:
        tone = 'Informal'
    else:
        tone = 'Balanced'

    # Burstiness (variation in sentence length)
    if len(sentence_lengths) > 1:
        mean_len = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        std_dev = math.sqrt(variance)
        burstiness = round(std_dev / mean_len if mean_len else 0, 2) if mean_len else 0
    else:
        burstiness = 0

    # Flag issues
    issues = []
    if avg_sentence_len > 25:
        issues.append("Sentences are very long. Try breaking them up.")
    if unique_ratio < 0.4:
        issues.append("High word repetition. Consider using more varied vocabulary.")
    if burstiness < 0.3:
        issues.append("Sentence length is very uniform. Vary sentence structure for more natural writing.")
    if informal_count > total_words * 0.05:
        issues.append("Tone is informal. Consider a more formal register for academic writing.")
    if max_sentence_len > 40:
        issues.append("Some sentences are extremely long. Break them into shorter ones.")

    return {
        'total_words': total_words,
        'total_sentences': total_sentences,
        'total_paragraphs': total_paragraphs,
        'total_chars': total_chars,
        'chars_no_spaces': chars_no_spaces,
        'unique_words': unique_words,
        'unique_ratio': round(unique_ratio * 100, 1),
        'avg_word_length': round(avg_word_len, 1),
        'avg_sentence_length': round(avg_sentence_len, 1),
        'max_sentence_length': max_sentence_len,
        'min_sentence_length': min_sentence_len,
        'readability': readability,
        'tone': tone,
        'burstiness': burstiness,
        'top_words': [{'word': w, 'count': c} for w, c in top_words],
        'issues': issues,
    }
