"""
AI Vocabulary phrase database — phrases commonly used by AI models.
Data sourced from GPTZero's published research on AI word frequency.
Frequency = how many times more likely AI uses this vs humans.
"""
from dataclasses import dataclass

@dataclass
class AIPhrase:
    phrase: str
    frequency: str  # e.g. "182x"
    example: str
    example_with_highlight: str  # bold the phrase

AI_VOCABULARY = [
    AIPhrase("provide a valuable insight", "182x",
             "The study aims to provide a valuable insight into consumer behavior.",
             "The study aims to <strong>provide a valuable insight</strong> into consumer behavior."),
    AIPhrase("left an indelible mark", "111x",
             "The artist's work left an indelible mark on the cultural landscape.",
             "The artist's work <strong>left an indelible mark</strong> on the cultural landscape."),
    AIPhrase("a stark reminder", "88x",
             "The abandoned house stood as a stark reminder of the neighborhood's former glory.",
             "The abandoned house stood as <strong>a stark reminder</strong> of the neighborhood's former glory."),
    AIPhrase("a nuanced understanding", "77x",
             "Her experience gave her a nuanced understanding of the complexities involved.",
             "Her experience gave her <strong>a nuanced understanding</strong> of the complexities involved."),
    AIPhrase("significant role in shaping", "70x",
             "Parents play a significant role in shaping their children's values and beliefs.",
             "Parents play <strong>a significant role in shaping</strong> their children's values and beliefs."),
    AIPhrase("the complex interplay", "69x",
             "Scientists study the complex interplay between genes and environmental factors.",
             "Scientists study <strong>the complex interplay</strong> between genes and environmental factors."),
    AIPhrase("broad implication", "64x",
             "The study's findings have a broad implication for understanding climate change.",
             "The study's findings have <strong>a broad implication</strong> for understanding climate change."),
    AIPhrase("an unwavering commitment", "59x",
             "Her success is a result of an unwavering commitment to her goals.",
             "Her success is a result of <strong>an unwavering commitment</strong> to her goals."),
    AIPhrase("endure a legacy", "58x",
             "Artists often endure a legacy that influences generations to come.",
             "Artists often <strong>endure a legacy</strong> that influences generations to come."),
    AIPhrase("underscore the importance", "53x",
             "Recent studies underscore the importance of early childhood education.",
             "Recent studies <strong>underscore the importance</strong> of early childhood education."),
    AIPhrase("delve into the intricacies", "51x",
             "This paper will delve into the intricacies of machine learning algorithms.",
             "This paper will <strong>delve into the intricacies</strong> of machine learning algorithms."),
    AIPhrase("navigate the complexities", "49x",
             "Leaders must navigate the complexities of a rapidly changing global economy.",
             "Leaders must <strong>navigate the complexities</strong> of a rapidly changing global economy."),
    AIPhrase("plays a crucial role", "47x",
             "Education plays a crucial role in personal and societal development.",
             "Education <strong>plays a crucial role</strong> in personal and societal development."),
    AIPhrase("a multifaceted phenomenon", "45x",
             "Climate change is a multifaceted phenomenon affecting every aspect of life.",
             "Climate change is <strong>a multifaceted phenomenon</strong> affecting every aspect of life."),
    AIPhrase("pivotal role in", "43x",
             "Renewable energy plays a pivotal role in reducing carbon emissions.",
             "Renewable energy plays <strong>a pivotal role</strong> in reducing carbon emissions."),
    AIPhrase("shed light on", "41x",
             "The research aims to shed light on the underlying causes of the disease.",
             "The research aims to <strong>shed light on</strong> the underlying causes of the disease."),
    AIPhrase("in the realm of", "39x",
             "Advances in the realm of artificial intelligence are accelerating rapidly.",
             "Advances <strong>in the realm of</strong> artificial intelligence are accelerating rapidly."),
    AIPhrase("a testament to", "37x",
             "The success of the project is a testament to effective teamwork.",
             "The success of the project is <strong>a testament to</strong> effective teamwork."),
    AIPhrase("realm of human experience", "35x",
             "Art exists in the realm of human experience and emotional expression.",
             "Art exists <strong>in the realm of</strong> human experience and emotional expression."),
    AIPhrase(" tapestry of", "33x",
             "The city is a rich tapestry of diverse cultures and traditions.",
             "The city is a rich <strong>tapestry of</strong> diverse cultures and traditions."),
    AIPhrase("underpinned by", "31x",
             "The theory is underpinned by decades of empirical research.",
             "The theory is <strong>underpinned by</strong> decades of empirical research."),
    AIPhrase("multifaceted approach", "29x",
             "We need a multifaceted approach to address climate change effectively.",
             "We need <strong>a multifaceted approach</strong> to address climate change effectively."),
    AIPhrase("comprehensive analysis", "27x",
             "The report provides a comprehensive analysis of market trends and consumer behavior.",
             "The report provides <strong>a comprehensive analysis</strong> of market trends and consumer behavior."),
    AIPhrase("meticulous attention to detail", "25x",
             "The architect's meticulous attention to detail is evident in every element of the building.",
             "The architect's <strong>meticulous attention to detail</strong> is evident in every element of the building."),
    AIPhrase("foster meaningful dialogue", "23x",
             "The conference aims to foster meaningful dialogue between researchers and practitioners.",
             "The conference aims to <strong>foster meaningful dialogue</strong> between researchers and practitioners."),
    AIPhrase("groundbreaking discovery", "21x",
             "The scientists announced a groundbreaking discovery in the field of quantum physics.",
             "The scientists announced a <strong>groundbreaking discovery</strong> in the field of quantum physics."),
    AIPhrase("deeply rooted in", "19x",
             "The cultural traditions are deeply rooted in centuries of history and practice.",
             "The cultural traditions are <strong>deeply rooted in</strong> centuries of history and practice."),
    AIPhrase("strive to understand", "17x",
             "Researchers strive to understand the fundamental mechanisms underlying consciousness.",
             "Researchers <strong>strive to understand</strong> the fundamental mechanisms underlying consciousness."),
    AIPhrase("enhance our understanding", "15x",
             "This study aims to enhance our understanding of cellular processes.",
             "This study aims to <strong>enhance our understanding</strong> of cellular processes."),
    AIPhrase("in essence", "14x",
             "In essence, the theory explains how species adapt to their environments over time.",
             "<strong>In essence</strong>, the theory explains how species adapt to their environments over time."),
    AIPhrase("ever-evolving landscape", "12x",
             "The ever-evolving landscape of technology presents both opportunities and challenges.",
             "The <strong>ever-evolving landscape</strong> of technology presents both opportunities and challenges."),
    AIPhrase("central to understanding", "11x",
             "Statistical analysis is central to understanding patterns in large datasets.",
             "Statistical analysis is <strong>central to understanding</strong> patterns in large datasets."),
    AIPhrase("illuminate the path", "10x",
             "These findings illuminate the path toward more sustainable business practices.",
             "These findings <strong>illuminate the path</strong> toward more sustainable business practices."),
    AIPhrase("as a means to", "9x",
             "The program uses interactive learning as a means to engage students more effectively.",
             "The program uses interactive learning <strong>as a means to</strong> engage students more effectively."),
    AIPhrase("it is worth noting", "8x",
             "It is worth noting that these results are consistent with previous studies.",
             "<strong>It is worth noting</strong> that these results are consistent with previous studies."),
    AIPhrase("an array of", "7x",
             "The library contains an array of resources spanning multiple disciplines.",
             "The library contains <strong>an array of</strong> resources spanning multiple disciplines."),
    AIPhrase("a wide array of", "7x",
             "The curriculum offers a wide array of courses to meet diverse student interests.",
             "The curriculum offers <strong>a wide array of</strong> courses to meet diverse student interests."),
    AIPhrase("serves as a crucial", "6x",
             "Access to clean water serves as a crucial determinant of public health outcomes.",
             "Access to clean water <strong>serves as a crucial</strong> determinant of public health outcomes."),
    AIPhrase("drives the need for", "5x",
             "Population growth drives the need for sustainable agricultural practices.",
             "Population growth <strong>drives the need for</strong> sustainable agricultural practices."),
    AIPhrase("in today's rapidly", "5x",
             "In today's rapidly shifting geopolitical landscape, international cooperation is essential.",
             "<strong>In today's rapidly</strong> shifting geopolitical landscape, international cooperation is essential."),
    AIPhrase("the ever-expanding", "4x",
             "The ever-expanding volume of digital data presents new challenges for privacy and security.",
             "The <strong>ever-expanding</strong> volume of digital data presents new challenges for privacy and security."),
]

# Additional AI phrases for detection (not all have frequency data)
AI_PHRASE_PATTERNS = [
    r"\bprovide a valuable insight\b",
    r"\bleft an indelible mark\b",
    r"\ba stark reminder\b",
    r"\ba nuanced understanding\b",
    r"\bsignificant role in shaping\b",
    r"\bthe complex interplay\b",
    r"\bbroad implication\b",
    r"\ban unwavering commitment\b",
    r"\bendure a legacy\b",
    r"\bunderscore the importance\b",
    r"\bdelve into the intricacies\b",
    r"\bnavigate the complexities\b",
    r"\bplays a crucial role\b",
    r"\ba multifaceted phenomenon\b",
    r"\bpivotal role in\b",
    r"\bshed light on\b",
    r"\bin the realm of\b",
    r"\ba testament to\b",
    r"\brealm of human experience\b",
    r"\btapestry of\b",
    r"\bunderpinned by\b",
    r"\bmultifaceted approach\b",
    r"\bcomprehensive analysis\b",
    r"\bmeticulous attention to detail\b",
    r"\bfoster meaningful dialogue\b",
    r"\bgroundbreaking discovery\b",
    r"\bdeeply rooted in\b",
    r"\bstrive to understand\b",
    r"\benhance our understanding\b",
    r"\bin essence\b",
    r"\bever-evolving landscape\b",
    r"\bcentral to understanding\b",
    r"\billuminate the path\b",
    r"\bas a means to\b",
    r"\bit is worth noting\b",
    r"\ban array of\b",
    r"\ba wide array of\b",
    r"\bserves as a crucial\b",
    r"\bdrives the need for\b",
    r"\bin today's rapidly\b",
    r"\bever-expanding\b",
    r"\bcommendable effort\b",
    r"\bin light of the fact\b",
    r"\bthe crux of the matter\b",
    r"\bit is imperative that\b",
    r"\bthe fact that\b",
    r"\bin conclusion\b",
    r"\bto summarize\b",
    r"\bdrives innovation\b",
    r"\btranscend boundaries\b",
    r"\brevolutionize the way we\b",
    r"\bparadigm shift\b",
    r"\bgame-changer\b",
    r"\bcutting-edge\b",
    r"\bnext-generation\b",
    r"\bpowerful tool\b",
    r"\bseamless integration\b",
    r"\bholistic approach\b",
    r"\bdeep dive\b",
    r"\bleverage\b",  # corporate speak
    r"\bsynergy\b",
    r"\boptimize\b",
    r"\bstreamline\b",
    r"\bempower\b",
    r"\brevolutionize\b",
    r"\btransformative\b",
    r"\bpioneering\b",
    r"\bunprecedented\b",
    r"\bbottom line\b",
    r"\bgame changer\b",
    r"\bgame-changer\b",
]

import re

def find_ai_phrases(text):
    """Find AI phrases in text, return list of (phrase, start, end, phrase_data)."""
    found = []
    text_lower = text.lower()
    for phrase_data in AI_VOCABULARY:
        pattern = re.compile(re.escape(phrase_data.phrase.lower()), re.IGNORECASE)
        for m in pattern.finditer(text):
            found.append({
                'phrase': phrase_data.phrase,
                'frequency': phrase_data.frequency,
                'example': phrase_data.example,
                'start': m.start(),
                'end': m.end(),
                'highlighted': phrase_data.example_with_highlight,
            })
    return found

def scan_text_for_ai_vocabulary(text):
    """Scan text and return AI vocabulary report."""
    found = find_ai_phrases(text)
    total_phrases = len(found)
    unique_phrases = len(set(f['phrase'] for f in found))

    # Deduplicate by phrase text
    seen = set()
    unique_found = []
    for f in found:
        if f['phrase'] not in seen:
            seen.add(f['phrase'])
            unique_found.append(f)

    return {
        'total_occurrences': total_phrases,
        'unique_phrases': unique_phrases,
        'phrases_found': unique_found,
        'risk_level': 'High' if unique_phrases >= 5 else 'Medium' if unique_phrases >= 2 else 'Low',
        'suggestion': 'Consider revising these phrases to develop a more original writing voice.'
                     if unique_phrases >= 3 else
                     'Minor use of formulaic phrases detected.' if unique_phrases >= 1 else
                     'No AI vocabulary patterns detected. Your writing sounds authentic!'
    }
