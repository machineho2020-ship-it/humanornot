"""
Enhanced readability and writing quality metrics.
Coleman-Liau Index, SMOG Index approximation, sentence complexity.
"""
import re
import math

def flesch_kincaid(text):
    """Flesch-Kincaid Reading Ease and Grade Level."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return {'reading_ease': 0, 'grade_level': 0, 'label': 'Unknown'}

    words = re.findall(r'\b[a-zA-Z]+\b', text)
    if not words:
        return {'reading_ease': 0, 'grade_level': 0, 'label': 'Unknown'}

    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(_syllable_count(w) for w in words)

    avg_sentence_length = total_words / total_sentences if total_sentences else 0
    avg_syllables_per_word = total_syllables / total_words if total_words else 0

    reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    reading_ease = max(0, min(100, reading_ease))

    grade_level = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
    grade_level = max(0, grade_level)

    if reading_ease >= 90: label = "Very Easy — 5th grade"
    elif reading_ease >= 70: label = "Easy — Middle school"
    elif reading_ease >= 50: label = "Moderate — High school"
    elif reading_ease >= 30: label = "Difficult — College"
    else: label = "Very Difficult — Graduate"

    return {
        'reading_ease': round(reading_ease, 1),
        'grade_level': round(grade_level, 1),
        'label': label,
        'avg_sentence_length': round(avg_sentence_length, 1),
        'avg_syllables_per_word': round(avg_syllables_per_word, 1),
    }

def coleman_liau(text):
    """Coleman-Liau Index — based on character count, not syllables."""
    letters = len(re.findall(r'[a-zA-Z]', text))
    words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    sentences = max(1, len(re.split(r'[.!?]+', text)) - 1)

    L = (letters / words * 100) if words else 0
    S = (sentences / words * 100) if words else 0

    index = (0.0588 * L) - (0.296 * S) - 15.8
    index = max(0, index)

    grade = math.ceil(index)
    if grade <= 5: label = f"Grade {grade} — Elementary"
    elif grade <= 8: label = f"Grade {grade} — Middle School"
    elif grade <= 12: label = f"Grade {grade} — High School"
    elif grade <= 16: label = f"College — Grade {grade}"
    else: label = f"Graduate — Grade {grade}+"

    return {
        'index': round(index, 1),
        'grade': grade,
        'label': label,
        'letter_percent': round(L, 1),
    }

def smog_index(text):
    """Approximate SMOG Index (requires 30+ sentences for accuracy)."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    polysyllable_words = sum(1 for w in re.findall(r'\b[a-zA-Z]+\b', text) if _syllable_count(w) >= 3)
    n_sentences = len(sentences)
    if n_sentences < 1:
        return {'smog': 0, 'label': 'Unknown'}

    smog = 1.043 * math.sqrt(polysyllable_words * (30 / n_sentences)) + 3.1291 if n_sentences > 0 else 0
    smog = max(0, smog)
    grade = math.ceil(smog)
    label = f"Grade {grade} — " + ("Easy" if grade <= 8 else "College" if grade <= 12 else "Advanced")

    return {'smog': round(smog, 1), 'grade': grade, 'label': label, 'polysyllable_words': polysyllable_words}

def _syllable_count(word):
    """Rough syllable count."""
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

def analyze_writing_v2(text):
    """Comprehensive writing analysis with all readability metrics."""
    if not text or len(text.strip()) < 20:
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

    chars_no_spaces = len(text.replace(' ', ''))

    # Unique words
    word_freq = {}
    for w in words:
        wl = w.lower()
        word_freq[wl] = word_freq.get(wl, 0) + 1

    unique_words = len(word_freq)
    unique_ratio = unique_words / total_words if total_words else 0

    avg_word_len = sum(len(w) for w in words) / total_words if total_words else 0

    # Sentence lengths
    sent_lens = [len(re.findall(r'\b[a-zA-Z]+\b', s)) for s in sentences]
    avg_sent_len = sum(sent_lens) / len(sent_lens) if sent_lens else 0
    max_sent_len = max(sent_lens) if sent_lens else 0
    min_sent_len = min(sent_lens) if sent_lens else 0

    # Readability metrics
    fk = flesch_kincaid(text)
    cl = coleman_liau(text)
    smog = smog_index(text)

    # Overall readability verdict
    all_grades = [fk['grade_level'], cl['grade'], smog.get('grade', 0)]
    avg_grade = sum(all_grades) / len(all_grades)
    overall_label = (
        "Very Easy" if fk['reading_ease'] >= 80 else
        "Easy" if fk['reading_ease'] >= 60 else
        "Moderate" if fk['reading_ease'] >= 40 else
        "Difficult"
    )

    # Sentence complexity breakdown
    short_sents = sum(1 for l in sent_lens if l <= 10)
    med_sents = sum(1 for l in sent_lens if 10 < l <= 20)
    long_sents = sum(1 for l in sent_lens if l > 20)

    # Word repetition issues
    repeated = {w: c for w, c in word_freq.items() if c > 3 and len(w) > 4}
    repeated_sorted = sorted(repeated.items(), key=lambda x: x[1], reverse=True)[:5]

    # Stop word ratio (overuse of common words)
    stop_words = {
        'the','a','an','of','to','in','for','is','on','that','this','and','it',
        'with','as','by','at','from','or','be','are','was','were','has','have',
        'had','not','but','they','their','we','our','you','your','its','been'
    }
    stop_count = sum(1 for w in words if w.lower() in stop_words)
    stop_ratio = stop_count / total_words if total_words else 0

    # Issues
    issues = []
    if fk['reading_ease'] < 30:
        issues.append("Very difficult to read. Consider simplifying vocabulary and sentence structure.")
    if avg_sent_len > 25:
        issues.append("Sentences are very long. Try breaking them into shorter pieces.")
    if unique_ratio < 0.4:
        issues.append("High word repetition. Vary your vocabulary to keep readers engaged.")
    if stop_ratio > 0.55:
        issues.append("Too many common filler words. This can make writing feel generic.")
    if long_sents > total_sentences * 0.4:
        issues.append("Many very long sentences. Mix in shorter sentences for rhythm.")

    return {
        'total_words': total_words,
        'total_sentences': total_sentences,
        'total_paragraphs': total_paragraphs,
        'unique_words': unique_words,
        'unique_ratio': round(unique_ratio * 100, 1),
        'avg_word_length': round(avg_word_len, 1),
        'avg_sentence_length': round(avg_sent_len, 1),
        'sentence_breakdown': {
            'short': short_sents,  # ≤10 words
            'medium': med_sents,    # 11-20 words
            'long': long_sents,    # >20 words
        },
        'readability': {
            'flesch_kincaid': fk,
            'coleman_liau': cl,
            'smog': smog,
        },
        'overall_label': overall_label,
        'avg_grade_level': round(avg_grade, 1),
        'stop_word_ratio': round(stop_ratio * 100, 1),
        'repeated_words': [{'word': w, 'count': c} for w, c in repeated_sorted],
        'issues': issues,
    }
