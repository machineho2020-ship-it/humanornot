"""
Pure Python rule-based paraphraser using NLTK WordNet + TextBlob.
No external API needed — runs locally.
"""
import random
import re
from textblob import TextBlob

try:
    import nltk
    from nltk.corpus import wordnet as wn
    _WN_OK = True
except ImportError:
    _WN_OK = False

# Contractions map
CONTractions = {
    "don't": "do not", "won't": "will not", "can't": "cannot",
    "i'm": "i am", "you're": "you are", "he's": "he is",
    "she's": "she is", "it's": "it is", "we're": "we are",
    "they're": "they are", "i've": "i have", "you've": "you have",
    "we've": "we have", "they've": "they have", "i'll": "i will",
    "you'll": "you will", "he'll": "he will", "she'll": "she will",
    "we'll": "we will", "they'll": "they will", "isn't": "is not",
    "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "hasn't": "has not", "haven't": "have not", "hadn't": "had not",
    "wouldn't": "would not", "couldn't": "could not", "shouldn't": "should not",
    "doesn't": "does not", "didn't": "did not", "let's": "let us",
    "that's": "that is", "what's": "what is", "who's": "who is",
    "here's": "here is", "there's": "there is", "how's": "how is",
    "we'd": "we would", "i'd": "i would", "you'd": "you would",
    "they'd": "they would", "he'd": "he would", "she'd": "she would",
    "it'd": "it would", "we'd": "we had", "i'd": "i had",
    "you'd": "you had", "they'd": "they had", "he'd": "he had",
}

EXPANSIONS = {v: k for k, v in CONTractions.items()}

# Transitions
TRANSITIONS = [
    "Additionally, ", "Moreover, ", "Furthermore, ", "In addition, ",
    "Consequently, ", "As a result, ", "Thus, ", "Hence, ",
    "Nevertheless, ", "However, ", "On the other hand, ",
    "In contrast, ", "Meanwhile, ", "Subsequently, ",
    "Notably, ", "Significantly, ", "Importantly, ",
    "Specifically, ", "In particular, ", "For instance, ",
    "For example, ", "Indeed, ", "Certainly, ",
]

def _get_synonym(word, pos=None):
    """Get a synonym for word from WordNet, avoiding similar forms."""
    if not _WN_OK or not word or len(word) < 3:
        return None
    try:
        wn_pos = {'NN': wn.NOUN, 'VB': wn.VERB, 'JJ': wn.ADJ, 'RB': wn.ADV}.get(pos, wn.NOUN)
        synsets = wn.synsets(word, pos=wn_pos)
        if not synsets:
            synsets = wn.synsets(word)
        if not synsets:
            return None
        # Pick a synonym that's different enough
        for syn in synsets:
            for lemma in syn.lemmas():
                if lemma.name().lower() != word.lower() and '_' not in lemma.name():
                    return lemma.name().replace('_', ' ')
        return None
    except Exception:
        return None

def _get_best_pos(word):
    """Simple heuristic POS tagging."""
    common_verbs = {'is','are','was','were','have','has','had','do','does','did','will','would','can','could','should','may','might','must'}
    common_adj = {'rapid','significant','major','important','crucial','essential','remarkable','impressive','nuanced','artificial','modern','recent'}
    word_lower = word.lower()
    if word_lower in common_verbs: return 'VB'
    if word_lower in common_adj: return 'JJ'
    return 'NN'

def _synonym_replace(text, ratio=0.3):
    """Replace ~ratio of words with synonyms, preserving punctuation and structure."""
    # Use regex to find all word+punctuation tokens
    tokens = re.findall(r"(\w+(?:'\w+)?)", text)
    blob = TextBlob(text)
    tags = blob.tags
    tag_dict = {w.lower(): t for w, t in tags}

    result_parts = []
    pos = 0
    i = 0
    while i < len(text):
        m = re.match(r"(\w+(?:'\w+)?)", text[i:])
        if m:
            word = m.group(1)
            rest = text[i + len(word):]
            # Check if we should replace
            pos_tag = tag_dict.get(word.lower(), _get_best_pos(word))
            if random.random() < ratio and len(word) > 3 and word.isalpha():
                syn = _get_synonym(word.lower(), pos_tag)
                if syn and syn.lower() != word.lower():
                    if word[0].isupper():
                        syn = syn.capitalize()
                    result_parts.append(syn)
                else:
                    result_parts.append(word)
            else:
                result_parts.append(word)
            # Append non-word characters (punctuation, spaces) as-is
            j = i + len(word)
            while j < len(text) and not re.match(r"\w", text[j]):
                result_parts.append(text[j])
                j += 1
            i = j
        else:
            result_parts.append(text[i])
            i += 1

    result = ''.join(result_parts).strip()
    # Restore trailing punctuation from original
    if text and text[-1] in '.!?' and result and result[-1] not in '.!?':
        result += text[-1]
    return result

def _shuffle_sentences(text):
    """Shuffle sentences in a paragraph-like block."""
    # Split into sentences while keeping the delimiter
    parts = re.split(r'([.!?]\s+)', text)
    sentences = []
    for i in range(0, len(parts)-1, 2):
        sentences.append(parts[i] + parts[i+1])
    if len(parts) % 2 == 1 and parts[-1].strip():
        sentences.append(parts[-1])
    if len(sentences) <= 1:
        return text
    # Keep first sentence, shuffle the rest
    first = sentences[0]
    rest = sentences[1:]
    random.shuffle(rest)
    return first + ' ' + ' '.join(rest)

def _split_long_sentence(sentence, max_len=25):
    """Split a long sentence on conjunctions."""
    conjunctions = [' and ', ' but ', ' or ', ', which ', ', that ', ', however ', ', therefore ']
    parts = [sentence]
    words = sentence.split()
    if len(words) > max_len:
        for conj in conjunctions:
            if conj in sentence.lower():
                sub_parts = sentence.lower().split(conj.strip())
                if len(sub_parts) > 1:
                    result = sub_parts[0].strip().capitalize()
                    for i, part in enumerate(sub_parts[1:]):
                        result += '. ' + part.strip().capitalize() + '.'
                    return result
    return sentence

def _swap_pronouns(text):
    """Basic pronoun normalization."""
    text = re.sub(r'\bI\b', 'this writer', text)
    text = re.sub(r'\bmy\b', 'this writer\'s', text)
    text = re.sub(r'\bwe\b', 'they', text)
    text = re.sub(r'\bour\b', 'their', text)
    return text

def _expand_contract(text):
    """Expand contractions."""
    for k, v in CONTractions.items():
        text = re.sub(r'\b' + re.escape(k) + r'\b', v, text, flags=re.IGNORECASE)
    return text

def _add_filler(text):
    """Add natural filler words."""
    fillers = ['really ', 'quite ', 'rather ', 'somewhat ', 'fairly ', 'pretty ']
    words = text.split()
    if len(words) < 10:
        return text
    # Add filler before an adjective
    adj_pattern = re.compile(r'\b(rapid|significant|major|important|crucial|essential)\b', re.IGNORECASE)
    def add_filler(m):
        return m.group(0) + ' ' + random.choice(fillers)
    return adj_pattern.sub(add_filler, text)

def paraphrase(text, level='medium'):
    """
    Paraphrase text at different levels.
    level: 'light' (15% word swap), 'medium' (30% word swap + sentence shuffle), 'strong' (50% + all transforms)
    Returns: paraphrased string
    """
    if not text or len(text.strip()) < 20:
        return text

    random.seed()  # Fresh randomness each time
    text = text.strip()
    original = text

    # Ensure period at end
    if not re.search(r'[.!?]$', text):
        text += '.'

    if level == 'light':
        text = _expand_contract(text)
        text = _synonym_replace(text, ratio=0.15)
        text = text[0].upper() + text[1:] if len(text) > 1 else text

    elif level == 'medium':
        text = _expand_contract(text)
        text = _synonym_replace(text, ratio=0.30)
        # Sentence shuffle
        text = _shuffle_sentences(text)
        text = text[0].upper() + text[1:] if len(text) > 1 else text

    elif level == 'strong':
        text = _expand_contract(text)
        text = _add_filler(text)
        text = _synonym_replace(text, ratio=0.50)
        # Swap pronouns
        text = _swap_pronouns(text)
        # Split long sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        new_sentences = [_split_long_sentence(s) for s in sentences]
        text = ' '.join(new_sentences)
        # Sentence shuffle
        if len(new_sentences) > 2:
            first = new_sentences[0]
            rest = new_sentences[1:]
            random.shuffle(rest)
            text = first + ' ' + ' '.join(rest)
        text = text[0].upper() + text[1:] if len(text) > 1 else text

    # Ensure proper spacing after periods
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\s+([A-Z])', r'. \1', text)

    # Avoid identical to original
    if text.strip() == original.strip() and level != 'light':
        return paraphrase(text, 'medium')

    return text.strip()

def paraphrase_multiple(text, n_variants=3, level='medium'):
    """Generate n_variants different paraphrases of the text."""
    variants = []
    seen = set()
    for _ in range(n_variants * 3):  # max attempts
        result = paraphrase(text, level)
        if result not in seen and result != text:
            seen.add(result)
            variants.append(result)
            if len(variants) >= n_variants:
                break
    return variants[:n_variants]
