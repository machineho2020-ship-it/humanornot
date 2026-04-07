"""
AI Humanizer — rewrites AI-generated text to sound more naturally human.
Uses rule-based transformations + sentence restructuring.
"""
import random
import re

# Phrases to replace with more natural alternatives
AI_TO_HUMAN = {
    "it is important to note": "interestingly",
    "it is worth noting": "notably",
    "it should be noted": "notably",
    "in conclusion": "overall",
    "to summarize": "in short",
    "as previously stated": "as mentioned",
    "in this regard": "here",
    "with this in mind": "with that in mind",
    "in the realm of": "in",
    "plays a crucial role": "is key to",
    "plays a vital role": "is central to",
    "plays an important role": "matters for",
    "a comprehensive analysis": "a detailed look",
    "provides valuable insights": "offers key insights",
    "a multifaceted approach": "a broad approach",
    "demonstrates remarkable": "shows notable",
    "exhibits exceptional": "shows strong",
    "is characterized by": "has",
    "has the ability to": "can",
    "in order to": "to",
    "due to the fact that": "because",
    "at this point in time": "now",
    "in the event that": "if",
    "a large number of": "many",
    "a significant number of": "considerably",
    "the vast majority of": "most",
    "it is apparent that": "clearly",
    "it is evident that": "clearly",
    "has been shown to": "appears to",
    "serves as a means of": "helps",
    "on a daily basis": "daily",
    "takes into consideration": "considers",
    "comes to the conclusion": "concludes",
    "draws the conclusion": "concludes",
    "is of great importance": "matters greatly",
    "is essential for": "matters for",
    "is necessary for": "is needed for",
    "utilizes": "uses",
    "implement": "do",
    "facilitate": "help",
    "subsequently": "then",
    "consequently": "so",
    "nevertheless": "still",
    "notwithstanding": "despite",
    "notwithstanding the fact": "even though",
    "a plethora of": "many",
    "a wide array of": "many",
    "an array of": "a range of",
    "takes into account": "considers",
    "in close proximity to": "near",
    "in the vicinity of": "near",
    "the majority of": "most",
    "a considerable amount of": "much",
    "in addition to": "besides",
    "as a consequence of": "because of",
    "owing to the fact that": "since",
    "for the purpose of": "to",
    "in spite of the fact that": "even though",
    "at the present time": "now",
    "at this moment in time": "now",
    "undergoes a process of": "goes through",
    "the process of": "",
    "it is expected that": "likely",
    "it is possible that": "maybe",
    "it is likely that": "probably",
    "it is possible that": "could be",
    "it would appear that": "it seems",
    "it would seem that": "it seems",
    "has the capacity to": "can",
    "possesses the ability to": "can",
    "make an endeavor to": "try to",
    "render assistance": "help",
    "engage in": "do",
    "undertake an examination": "examine",
    "bring to a conclusion": "conclude",
    "constitutes": "is",
    "effectuate": "do",
    "facilitate": "help",
    "in an effort to": "to",
    "on a continual basis": "continuously",
    "from time to time": "sometimes",
    "time and again": "often",
    "on frequent occasions": "often",
    "with regularity": "regularly",
    "the utilization of": "using",
    "the implementation of": "using",
    "the utilization": "use",
    "in a manner that is": "that is",
    "in a way that": "so that",
    "at which point": "where",
    "for the reason that": "since",
    "for this purpose": "to do this",
    "to all intents and purposes": "basically",
    "by and large": "mostly",
    "on the whole": "mostly",
    "it goes without saying": "of course",
    "needless to say": "of course",
    "as is well known": "as everyone knows",
    "it is well known that": "many",
    "is widely regarded as": "is seen as",
    "is generally accepted": "is usually seen as",
    "it is generally believed": "many believe",
    "there can be little doubt": "clearly",
    "it is beyond dispute": "clearly",
    "unquestionably": "clearly",
    "indisputably": "clearly",
}

# Transition phrases that make writing feel mechanical
ROBOTIC_TRANSITIONS = [
    "furthermore", "moreover", "additionally", "in addition",
    "consequently", "as a result", "therefore", "thus",
    "hence", "accordingly", "in conclusion", "to summarize",
    "in this case", "in other words", "that is to say",
]

def _remove_adverbial_padding(text):
    """Remove overly formal adverbial phrases."""
    patterns = [
        (r'\bin order to\b', 'to'),
        (r'\bdue to the fact that\b', 'because'),
        (r'\bat this point in time\b', 'now'),
        (r'\bin the event that\b', 'if'),
        (r'\bfor the purpose of\b', 'to'),
        (r'\bwith regard to\b', 'about'),
        (r'\bin reference to\b', 'about'),
        (r'\btakes into consideration\b', 'considers'),
        (r'\bhas the ability to\b', 'can'),
        (r'\bmakes an attempt to\b', 'tries to'),
        (r'\bplaces emphasis on\b', 'emphasizes'),
        (r'\bbrings to a conclusion\b', 'concludes'),
    ]
    for old, new in patterns:
        text = re.sub(old, new, text, flags=re.IGNORECASE)
    return text

def _humanize_sentence_start(text):
    """Start sentences with varied structures, not always subject."""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for i, sent in enumerate(sentences):
        sent = sent.strip()
        if not sent:
            continue
        if i == 0:
            result.append(sent)
            continue
        words = sent.split()
        if len(words) < 3:
            result.append(sent)
            continue
        # Randomly restructure sentence openings sometimes
        r = random.random()
        if r < 0.25 and words[0].lower() in ('the', 'a', 'an'):
            # Move article to later position
            result.append(' '.join(words[1:]) + ', ' + words[0].lower() + ',')
        elif r < 0.4:
            # Add a short qualifier before
            qualifiers = ['Actually,', 'Notably,', 'Sure enough,', 'Even so,', 'Even then,']
            result.append(qualifiers[random.randint(0, len(qualifiers)-1)] + ' ' + sent[0].lower() + sent[1:])
        else:
            result.append(sent)
    return ' '.join(result)

def _replace_formal_phrases(text):
    """Replace formal AI-sounding phrases with natural alternatives."""
    result = text
    for ai_phrase, human_phrase in AI_TO_HUMAN.items():
        pattern = re.compile(re.escape(ai_phrase), re.IGNORECASE)
        result = pattern.sub(human_phrase, result)
    return result

def _vary_sentence_openers(text):
    """Add variety to how sentences begin."""
    openers = {
        'but': ['However,', 'Yet,', 'Still,'],
        'and': ['Also,', 'Along with that,', 'As well,'],
    }
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        first_word = sent.split()[0].lower() if sent.split() else ''
        if first_word in openers and random.random() < 0.4:
            replacement = openers[first_word][random.randint(0, len(openers[first_word])-1)]
            sent = replacement + ' ' + sent[len(first_word):]
        result.append(sent)
    return ' '.join(result)

def _add_speech_patterns(text):
    """Add slight speech patterns — contractions, casual forms."""
    # Expand contractions (reverse them for more human feel)
    contractions = {
        "do not": "don't",
        "cannot": "can't",
        "will not": "won't",
        "is not": "isn't",
        "are not": "aren't",
        "was not": "wasn't",
        "were not": "weren't",
        "has not": "hasn't",
        "have not": "haven't",
        "had not": "hadn't",
        "would not": "wouldn't",
        "could not": "couldn't",
        "should not": "shouldn't",
        "does not": "doesn't",
        "did not": "didn't",
    }
    for formal, casual in contractions.items():
        text = re.sub(r'\b' + formal + r'\b', casual, text, flags=re.IGNORECASE)
    return text

def _shorten_sentences(text):
    """Break up very long sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for sent in sentences:
        words = sent.split()
        if len(words) > 35:
            # Try to split at conjunctions
            split_at = len(words)
            for conj in [' and ', ' but ', ' or ', ', which ', ', that ', ', however ', ' therefore ']:
                idx = sent.lower().find(conj)
                if idx > 0 and idx < len(sent) - 10:
                    parts = sent.split(conj.strip(), 1)
                    if len(parts) == 2:
                        result.append(parts[0].strip() + '.')
                        result.append(parts[1].strip().capitalize() + '.')
                        break
            else:
                result.append(sent)
        else:
            result.append(sent)
    return ' '.join(result)

def humanize(text, level='medium'):
    """
    Rewrite AI text to sound more naturally human.
    level: 'light' (subtle changes) | 'medium' | 'strong' (maximum rewording)
    """
    if not text or len(text.strip()) < 20:
        return text

    random.seed()
    text = text.strip()

    if level == 'light':
        text = _replace_formal_phrases(text)
        text = _add_speech_patterns(text)

    elif level == 'medium':
        text = _replace_formal_phrases(text)
        text = _remove_adverbial_padding(text)
        text = _add_speech_patterns(text)
        text = _vary_sentence_openers(text)
        text = _humanize_sentence_start(text)

    elif level == 'strong':
        text = _replace_formal_phrases(text)
        text = _remove_adverbial_padding(text)
        text = _add_speech_patterns(text)
        text = _vary_sentence_openers(text)
        text = _humanize_sentence_start(text)
        text = _shorten_sentences(text)

    # Fix spacing and punctuation
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    text = re.sub(r'([.!?])\s*([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
    text = text.strip()
    text = text[0].upper() + text[1:] if len(text) > 1 else text

    return text

def humanize_multiple(text, n_variants=3, level='medium'):
    """Generate multiple humanized variants."""
    variants = []
    seen = set()
    for _ in range(n_variants * 5):
        result = humanize(text, level)
        if result and result not in seen and result != text:
            seen.add(result)
            variants.append(result)
            if len(variants) >= n_variants:
                break
    return variants[:n_variants]
