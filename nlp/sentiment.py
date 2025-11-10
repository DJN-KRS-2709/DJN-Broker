from typing import List, Dict
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Ensure VADER lexicon is available
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

_sia = SentimentIntensityAnalyzer()

def score_texts(items: List[Dict], text_key: str = "title") -> List[Dict]:
    """Append 'sentiment' dict with compound score in [-1,1]."""
    out = []
    for it in items:
        text = (it.get(text_key) or "") + " " + (it.get("content") or "")
        score = _sia.polarity_scores(text)
        it2 = dict(it)
        it2["sentiment"] = score
        out.append(it2)
    return out
