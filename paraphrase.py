"""
Fully self-contained rule-based paraphraser.
No external downloads needed — pure Python.
"""
import random
import re

# Built-in synonym dictionary (common academic/formal words)
SYNONYMS = {
    # Verbs
    "is": ["exists as", "remains", "stands as"],
    "are": ["exist as", "remain", "stand as"],
    "was": ["existed as", "proved to be"],
    "shows": ["demonstrates", "exhibits", "reveals", "illustrates"],
    "show": ["demonstrate", "exhibit", "reveal", "illustrate"],
    "presents": ["offers", "introduces", "puts forward", "delivers"],
    "present": ["offer", "introduce", "put forward", "deliver"],
    "has": ["possesses", "contains", "carries", "holds"],
    "have": ["possess", "contain", "carry", "hold"],
    "makes": ["creates", "builds", "produces", "generates"],
    "make": ["create", "build", "produce", "generate"],
    "uses": ["utilizes", "employs", "applies", "adopts"],
    "use": ["utilize", "employ", "apply", "adopt"],
    "helps": ["assists", "supports", "aids", "enables"],
    "help": ["assist", "support", "aid", "enable"],
    "needs": ["requires", "demands", "necessitates"],
    "need": ["require", "demand", "necessitate"],
    "gives": ["provides", "offers", "supplies", "delivers"],
    "give": ["provide", "offer", "supply", "deliver"],
    "wants": ["desires", "seeks", "aims for", "wishes for"],
    "want": ["desire", "seek", "aim for", "wish for"],
    "asks": ["inquires", "questions", "queries", "poses"],
    "ask": ["inquire", "question", "query", "pose"],
    "thinks": ["believes", "considers", "reckons", "holds the view"],
    "think": ["believe", "consider", "reckon", "hold the view"],
    "uses": ["utilizes", "employs", "applies"],
    "see": ["observe", "witness", "perceive", "note"],
    "know": ["understand", "comprehend", "recognize", "grasp"],
    "likes": ["prefers", "appreciates", "enjoys", "favors"],
    "likes": ["prefers", "appreciates", "enjoys", "favors"],
    "tries": ["attempts", "seeks to", "endeavors to", "makes an effort to"],
    "try": ["attempt", "seek to", "endeavor to", "make an effort to"],
    "happens": ["occurs", "takes place", "transpires", "arises"],
    "happen": ["occur", "take place", "transpire", "arise"],
    "looks": ["appears", "seems", "gives the impression"],
    "look": ["appear", "seem", "give the impression"],
    "includes": ["encompasses", "comprises", "incorporates", "contains"],
    "include": ["encompass", "comprise", "incorporate", "contain"],
    "changes": ["alters", "modifies", "transforms", "shifts"],
    "change": ["alter", "modify", "transform", "shift"],
    "starts": ["begins", "initiates", "commences", "kicks off"],
    "start": ["begin", "initiate", "commence", "kick off"],
    "allows": ["permits", "enables", "facilitates", "grants"],
    "allow": ["permit", "enable", "facilitate", "grant"],
    "shows": ["demonstrates", "exhibits", "reveals", "illustrates"],
    "keeps": ["maintains", "preserves", "retains", "sustains"],
    "keep": ["maintain", "preserve", "retain", "sustain"],
    "brings": ["delivers", "carries", "conveys", "transports"],
    "bring": ["deliver", "carry", "convey", "transport"],
    "works": ["functions", "operates", "performs", "acts"],
    "work": ["function", "operate", "perform", "act"],
    "writes": ["authors", "composes", "creates", "pens"],
    "write": ["author", "compose", "create", "pen"],
    "leads": ["guides", "directs", "steers", "manages"],
    "lead": ["guide", "direct", "steer", "manage"],
    "feels": ["senses", "perceives", "experiences", "registers"],
    "feel": ["sense", "perceive", "experience", "register"],
    "continues": ["persists", "carries on", "proceeds", "sustains"],
    "continue": ["persist", "carry on", "proceed", "sustain"],
    "moves": ["advances", "progresses", "shifts", "proceeds"],
    "move": ["advance", "progress", "shift", "proceed"],
    "appears": ["emerges", "surfaces", "shows up", "comes to light"],
    "appear": ["emerge", "surface", "show up", "come to light"],
    "suggests": ["proposes", "implies", "indicates", "hints at"],
    "suggest": ["propose", "imply", "indicate", "hint at"],
    "lacks": ["lacks", "is without", "is devoid of", "is missing"],
    "lack": ["lack", "is without", "is devoid of", "is missing"],
    "achieves": ["accomplishes", "attains", "realizes", "secures"],
    "achieve": ["accomplish", "attain", "realize", "secure"],

    # Adjectives
    "rapid": ["swift", "quick", "fast", "speedy", "accelerating"],
    "significant": ["notable", "substantial", "considerable", "important", "meaningful"],
    "major": ["significant", "key", "crucial", "important", "principal"],
    "important": ["significant", "crucial", "essential", "vital", "key"],
    "crucial": ["essential", "critical", "vital", "pivotal", "decisive"],
    "essential": ["fundamental", "basic", "core", "vital", "indispensable"],
    "remarkable": ["notable", "outstanding", "exceptional", "impressive", "noteworthy"],
    "impressive": ["striking", "notable", "compelling", "powerful", "remarkable"],
    "nuanced": ["subtle", "delicate", "refined", "sophisticated", "complex"],
    "artificial": ["synthetic", "manufactured", "engineered", "fabricated", "constructed"],
    "modern": ["contemporary", "current", "present-day", "recent", "up-to-date"],
    "artificial": ["synthetic", "manufactured", "engineered", "man-made"],
    "challenging": ["difficult", "demanding", "tough", "arduous", "complex"],
    "challenges": ["difficulties", "obstacles", "hurdles", "barriers", "problems"],
    "opportunities": ["possibilities", "prospects", "chances", "openings", "avenues"],
    "capabilities": ["abilities", "competencies", "skills", "strengths", "capacities"],
    "understanding": ["comprehension", "insight", "knowledge", "awareness", "grasp"],
    "challenges": ["difficulties", "obstacles", "hurdles", "barriers"],
    "impressive": ["remarkable", "notable", "striking", "compelling"],
    "targeted": ["specific", "directed", "aimed", "focused", "precision"],
    "capable": ["able", "competent", "skilled", "proficient", "equipped"],
    "specific": ["particular", "defined", "distinct", "precise", "exact"],
    "artificial": ["synthetic", "engineered", "manufactured", "constructed"],
    "rapid": ["swift", "quick", "fast", "speedy", "brisk"],
    "modern": ["contemporary", "current", "present-day", "new-age"],
    "significant": ["notable", "substantial", "material", "important"],
    "complex": ["intricate", "complex", "complicated", "sophisticated", "elaborate"],
    "necessary": ["required", "needed", "essential", "mandatory", "compulsory"],
    "available": ["accessible", "obtainable", "reachable", "attainable", "usable"],
    "difficult": ["challenging", "demanding", "arduous", "tough", "hard"],
    "possible": ["feasible", "achievable", "attainable", "viable", "conceivable"],
    "simple": ["straightforward", "basic", "elementary", "uncomplicated", "plain"],
    "various": ["several", "numerous", "diverse", "multiple", "different"],
    "several": ["various", "numerous", "multiple", "several", "some"],
    "common": ["prevalent", "widespread", "commonplace", "frequent", "ubiquitous"],
    "previous": ["prior", "earlier", "former", "preceding", "antecedent"],
    "following": ["subsequent", "ensuing", "next", "later", "successive"],
    "additional": ["further", "extra", "supplementary", "added", "more"],
    "different": ["distinct", "varied", "diverse", "dissimilar", "varied"],
    "powerful": ["strong", "potent", "mighty", "formidable", "compelling"],
    "effective": ["efficient", "productive", "successful", "impactful", "potent"],
    "similar": ["comparable", "analogous", "resembling", "like", "akin"],
    "obvious": ["evident", "clear", "apparent", "manifest", "palpable"],
    "primary": ["main", "principal", "chief", "key", "leading"],
    "secondary": ["minor", "lesser", "subordinate", "supporting", "auxiliary"],
    "traditional": ["conventional", "classic", "established", "standard", "orthodox"],
    "certain": ["specific", "particular", "defined", "distinct", "precise"],

    # Adverbs
    "rapidly": ["swiftly", "quickly", "fast", "speedily", "briskly"],
    "significantly": ["notably", "substantially", "considerably", "markedly", "greatly"],
    "particularly": ["especially", "specifically", "particularly", "notably", "distinctively"],
    "especially": ["particularly", "specifically", "notably", "chiefly", "principally"],
    "generally": ["typically", "usually", "ordinarily", "commonly", "largely"],
    "specifically": ["particularly", "especially", "exactly", "precisely", "distinctly"],
    "recently": ["lately", "of late", "recently", "not long ago", "just now"],
    "already": ["previously", "already", "by now", "thus far", "hitherto"],
    "still": ["yet", "continue to", "remain", "persevere", "even now"],

    # Nouns
    "society": ["the public", "the community", "people at large", "civilization"],
    "systems": ["frameworks", "structures", "mechanisms", "networks", "setups"],
    "system": ["framework", "structure", "mechanism", "network", "setup"],
    "research": ["study", "investigation", "inquiry", "examination", "analysis"],
    "technology": ["tech", "innovation", "advancement", "progress", "development"],
    "information": ["data", "facts", "knowledge", "insights", "intel"],
    "example": ["instance", "case", "illustration", "sample", "specimen"],
    "problem": ["issue", "challenge", "difficulty", "obstacle", "concern"],
    "time": ["period", "phase", "era", "juncture", "moment"],
    "way": ["method", "approach", "manner", "means", "technique"],
    "world": ["realm", "sphere", "domain", "arena", "sector"],
    "life": ["existence", "living", "being", "experience", "reality"],
    "fact": ["reality", "truth", "actuality", "certainty", "verity"],
    "hand": ["side", "support", "assistance", "help", "aid"],
    "part": ["element", "component", "aspect", "portion", "segment"],
    "point": ["notion", "idea", "concept", "argument", "thesis"],
    "case": ["instance", "example", "scenario", "situation", "circumstance"],
    "course": ["process", "progression", "sequence", "chain", "path"],
    "matter": ["subject", "topic", "issue", "concern", "question"],
    " result": ["outcome", "consequence", "effect", "finding", "product"],
    "question": ["query", "inquiry", "issue", "matter", "concern"],
    "government": ["state", "authority", "administration", "ruling body", "public office"],
    "number": ["quantity", "amount", "count", "figure", "total"],
    "people": ["individuals", "persons", "folk", "citizens", "population"],
    "things": ["items", "objects", "aspects", "elements", "factors"],
    "countries": ["nations", "states", "lands", "territories", "regions"],
    "development": ["progress", "advancement", "evolution", "growth", "emergence"],
    "methods": ["approaches", "techniques", "strategies", "ways", "means"],
    "idea": ["concept", "notion", "thought", "belief", "viewpoint"],
    "group": ["team", "category", "collective", "body", "cluster"],
    "problems": ["issues", "challenges", "difficulties", "obstacles", "concerns"],
    "work": ["labor", "effort", "task", "job", "undertaking"],
    "data": ["information", "facts", "figures", "statistics", "records"],
    "type": ["kind", "sort", "category", "variety", "classification"],
    "research": ["study", "investigation", "analysis", "examination", "inquiry"],
    "view": ["perspective", "opinion", "stance", "standpoint", "outlook"],
}

CONTRACTIONS = {
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
}

REVERSE_CONTRACTIONS = {v: k for k, v in CONTRACTIONS.items()}

def _get_synonym(word):
    """Get a synonym from the built-in dictionary."""
    wl = word.lower()
    if wl in SYNONYMS:
        synonyms = SYNONYMS[wl]
        # Avoid picking the same word
        candidates = [s for s in synonyms if s.lower() != wl]
        if candidates:
            return random.choice(candidates)
    return None

def _synonym_replace(text, ratio=0.3):
    """Replace ~ratio of words with synonyms, preserving punctuation and structure."""
    result = []
    i = 0
    while i < len(text):
        m = re.match(r"(\w+(?:'\w+)?)", text[i:])
        if m:
            word = m.group(1)
            end = i + len(word)
            punct = text[end:end+1] if end < len(text) else ''

            safe_words = {
                'the','a','an','of','in','to','for','with','on','at','by','from',
                'as','is','are','was','were','be','been','being',
                'and','or','but','if','then','so','than','that','this','these',
                'those','it','its','they','their','them','we','our','us','i','my',
                'you','your','he','she','him','her','his','who','which','what',
                'when','where','why','how','all','each','every','both','few',
                'more','most','some','any','no','not','only','own','same','such',
                'can','will','would','could','should','may','might','must','shall'
            }
            wl = word.lower()
            should_replace = (
                wl not in safe_words and
                len(word) > 2 and
                word.isalpha() and
                random.random() < ratio
            )
            if should_replace:
                syn = _get_synonym(word)
                if syn:
                    if word[0].isupper():
                        syn = syn.capitalize()
                    result.append(syn)
                else:
                    result.append(word)
            else:
                result.append(word)

            # Append the following character (punctuation or space) as-is
            if punct:
                result.append(punct)
                i = end + 1
            else:
                i = end
        else:
            result.append(text[i])
            i += 1

    return ''.join(result)

def _shuffle_sentences(text):
    """Shuffle sentences while keeping the first."""
    # Split preserving sentence-ending punctuation
    parts = re.split(r'([.!?]+\s+)', text)
    sentences = []
    for i in range(0, len(parts)-1, 2):
        sent = (parts[i] + parts[i+1]).strip()
        if sent:
            sentences.append(sent)
    if len(parts) % 2 == 1 and parts[-1].strip():
        sentences.append(parts[-1].strip())
    if len(sentences) <= 1:
        return text
    first = sentences[0]
    rest = sentences[1:]
    random.shuffle(rest)
    return first + ' ' + ' '.join(rest)

def _expand_contractions(text):
    """Expand contractions to formal form."""
    for k, v in CONTRACTIONS.items():
        text = re.sub(r'\b' + re.escape(k) + r'\b', v, text, flags=re.IGNORECASE)
    return text

def _add_contrapositions(text):
    """Add light contrapositions or qualifier insertions."""
    qualifiers = [
        "in many cases, ", "in certain respects, ", "to a considerable extent, ",
        "from one perspective, ", "accordingly, ", "in practical terms, ",
        "from a broader viewpoint, ", "ultimately, "
    ]
    # Insert qualifier after first period
    m = re.search(r'([.!?]\s+)', text)
    if m and len(text) > 50:
        insert_at = m.start() + len(m.group())
        q = random.choice(qualifiers)
        text = text[:insert_at] + ' ' + q + text[insert_at:].lower().capitalize()
    return text

def _split_long_sentences(text, max_len=35):
    """Split very long sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for s in sentences:
        words = s.split()
        if len(words) > max_len:
            # Try to split at conjunctions
            conj_m = re.search(r'\b(and|but|which|that|however|therefore|thus|hence)\b', s[len(words[0])+1:])
            if conj_m:
                split_pos = len(words[0]) + 1 + conj_m.start() + 1
                first = s[:split_pos].strip()
                second = s[split_pos:].strip()
                if first and second:
                    result.append(first.capitalize() + '. ' + second[0].upper() + second[1:])
                    continue
        result.append(s)
    return ' '.join(result)

def paraphrase(text, level='medium'):
    """
    Paraphrase text at different intensity levels.
    light: 20% word swap
    medium: 35% word swap + sentence shuffle
    strong: 50% word swap + contractions + contrapositions + long sentence split
    """
    if not text or len(text.strip()) < 20:
        return text

    random.seed()
    original = text.strip()

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return original

    if not re.search(r'[.!?]$', text):
        text += '.'

    if level == 'light':
        text = _expand_contractions(text)
        text = _synonym_replace(text, ratio=0.20)

    elif level == 'medium':
        text = _expand_contractions(text)
        text = _synonym_replace(text, ratio=0.35)
        text = _shuffle_sentences(text)

    elif level == 'strong':
        text = _expand_contractions(text)
        text = _add_contrapositions(text)
        text = _synonym_replace(text, ratio=0.50)
        text = _split_long_sentences(text)
        text = _shuffle_sentences(text)

    # Fix capitalization
    text = text[0].upper() + text[1:] if len(text) > 1 else text
    text = re.sub(r'\s+([.!?])', r'\1', text)  # no space before punctuation
    text = re.sub(r'([.!?])\s+([a-z])', lambda m: m.group(1) + ' ' + m.group(2).upper(), text)
    text = re.sub(r'\s+', ' ', text).strip()

    # Avoid trivial identity
    if text == original and level != 'light':
        return paraphrase(original, 'medium')

    return text

def paraphrase_multiple(text, n_variants=3, level='medium'):
    """Generate multiple unique paraphrases."""
    variants = []
    seen = set()
    for _ in range(n_variants * 5):
        result = paraphrase(text, level)
        if result and result not in seen and result != text:
            seen.add(result)
            variants.append(result)
            if len(variants) >= n_variants:
                break
    return variants[:n_variants]
