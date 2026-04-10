import math
from collections import defaultdict
from preprocessor import meaningful_tokens, split_sentences, tokenize


# ── TF-IDF ─────────────────────────────────────────────────────────────────

class TFIDFScorer:
    """
    Treats each sentence as a 'document' and scores it by the sum of
    TF-IDF weights of its meaningful tokens.
    """

    def __init__(self, sentences: list[str]):
        self._sentences = sentences
        self._token_lists = [meaningful_tokens(s) for s in sentences]
        self._idf = self._compute_idf()

    # ── private ────────────────────────────────────────────────────────────

    def _compute_idf(self) -> dict[str, float]:
        n = len(self._token_lists)
        df: dict[str, int] = defaultdict(int)
        for tokens in self._token_lists:
            for term in set(tokens):
                df[term] += 1
        return {
            term: math.log((n + 1) / (freq + 1)) + 1
            for term, freq in df.items()
        }

    def _tf(self, tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        counts: dict[str, int] = defaultdict(int)
        for t in tokens:
            counts[t] += 1
        return {t: c / len(tokens) for t, c in counts.items()}

    # ── public ─────────────────────────────────────────────────────────────

    def score(self) -> list[float]:
        scores = []
        for tokens in self._token_lists:
            tf = self._tf(tokens)
            score = sum(tf.get(t, 0) * self._idf.get(t, 0) for t in tokens)
            scores.append(score)
        return scores


# ── TextRank ───────────────────────────────────────────────────────────────

def _cosine_similarity(v1: dict[str, float], v2: dict[str, float]) -> float:
    shared = set(v1) & set(v2)
    if not shared:
        return 0.0
    dot = sum(v1[w] * v2[w] for w in shared)
    mag1 = math.sqrt(sum(x ** 2 for x in v1.values()))
    mag2 = math.sqrt(sum(x ** 2 for x in v2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot / (mag1 * mag2)


def _sentence_vector(tokens: list[str]) -> dict[str, float]:
    counts: dict[str, float] = defaultdict(float)
    for t in tokens:
        counts[t] += 1.0
    return dict(counts)


class TextRankScorer:
    """
    Builds a sentence-similarity graph, then runs power-iteration
    to compute a PageRank-style importance score per sentence.
    """

    def __init__(self, sentences: list[str], damping: float = 0.85, iterations: int = 30):
        self._sentences = sentences
        self._damping = damping
        self._iterations = iterations
        self._token_lists = [meaningful_tokens(s) for s in sentences]

    def score(self) -> list[float]:
        n = len(self._sentences)
        if n == 0:
            return []
        if n == 1:
            return [1.0]

        vectors = [_sentence_vector(t) for t in self._token_lists]

        # Build similarity matrix
        matrix: list[list[float]] = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = _cosine_similarity(vectors[i], vectors[j])

        # Normalise rows
        for i in range(n):
            row_sum = sum(matrix[i])
            if row_sum > 0:
                matrix[i] = [x / row_sum for x in matrix[i]]

        # Power iteration
        scores = [1.0 / n] * n
        for _ in range(self._iterations):
            new_scores = [
                (1 - self._damping) / n
                + self._damping * sum(matrix[j][i] * scores[j] for j in range(n))
                for i in range(n)
            ]
            if max(abs(new_scores[i] - scores[i]) for i in range(n)) < 1e-6:
                break
            scores = new_scores

        return scores


# ── Keyword extractor ──────────────────────────────────────────────────────

def extract_keywords(text: str, top_n: int = 8) -> list[str]:
    """Return the top_n most significant keywords via TF-IDF over the whole text."""
    sentences = split_sentences(text)
    if not sentences:
        return []
    scorer = TFIDFScorer(sentences)
    idf = scorer._idf

    from preprocessor import word_frequencies
    tokens = meaningful_tokens(text)
    tf = word_frequencies(tokens)

    tfidf = {word: tf[word] * idf.get(word, 1.0) for word in tf}
    ranked = sorted(tfidf, key=lambda w: tfidf[w], reverse=True)
    return ranked[:top_n]
