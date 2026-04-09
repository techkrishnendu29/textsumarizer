

import re
import string
from collections import Counter


# ── Stop words ─────────────────────────────────────────────────────────────

STOP_WORDS: frozenset[str] = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "ought", "used", "it", "its", "this", "that", "these", "those", "i",
    "me", "my", "we", "our", "you", "your", "he", "she", "his", "her",
    "they", "their", "them", "who", "which", "what", "when", "where",
    "why", "how", "if", "then", "than", "so", "as", "not", "no", "nor",
    "yet", "both", "either", "neither", "each", "few", "more", "most",
    "other", "some", "such", "up", "out", "about", "into", "through",
    "during", "before", "after", "above", "below", "between", "very",
    "just", "also", "there", "here", "now", "only", "over", "own",
    "same", "too", "s", "t", "re", "ve", "ll", "d", "m",
})


# ── Stemmer ────────────────────────────────────────────────────────────────

def _stem(word: str) -> str:
    """Minimal suffix-stripping stemmer (no external deps)."""
    if len(word) <= 3:
        return word
    for suffix in ("ational", "tional", "enci", "anci", "izer", "ising",
                   "izing", "ation", "ness", "ment", "ful", "ous", "ive",
                   "ing", "ies", "ers", "ed", "er", "es", "ly", "er", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) > 2:
            return word[: -len(suffix)]
    return word


# ── Public API ─────────────────────────────────────────────────────────────

def split_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving reasonable boundaries."""
    text = re.sub(r"\s+", " ", text.strip())
    pattern = re.compile(
        r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s"
    )
    sentences = pattern.split(text)
    return [s.strip() for s in sentences if s.strip()]


def tokenize(text: str) -> list[str]:
    """Lowercase, remove punctuation, split into tokens."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text.split()


def remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]


def stem_tokens(tokens: list[str]) -> list[str]:
    return [_stem(t) for t in tokens]


def meaningful_tokens(text: str) -> list[str]:
    """Full pipeline: tokenise → remove stops → stem."""
    return stem_tokens(remove_stopwords(tokenize(text)))


def word_frequencies(tokens: list[str]) -> dict[str, float]:
    """Normalised word frequency map (max = 1.0)."""
    counts = Counter(tokens)
    if not counts:
        return {}
    max_count = max(counts.values())
    return {word: count / max_count for word, count in counts.items()}