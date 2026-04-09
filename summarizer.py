

import time
from models import SummaryStyle, SummaryResult
from preprocessor import split_sentences, tokenize
from scorer import TFIDFScorer, TextRankScorer, extract_keywords


# ── Helpers ────────────────────────────────────────────────────────────────

def _word_count(text: str) -> int:
    return len(text.split())


def _pick_sentences(
    sentences: list[str],
    scores: list[float],
    n: int,
    preserve_order: bool = True,
) -> list[str]:
    """Select top-n sentences by score, optionally restoring original order."""
    indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    chosen_indices = sorted(
        (idx for idx, _ in indexed[:n]),
        key=lambda i: i if preserve_order else -scores[i],
    )
    return [sentences[i] for i in chosen_indices]


# ── Summarizer class ───────────────────────────────────────────────────────

class Summarizer:

    # How many sentences each style extracts
    _SENTENCE_COUNTS: dict[SummaryStyle, int] = {
        SummaryStyle.BRIEF:    3,
        SummaryStyle.BULLET:   5,
        SummaryStyle.DETAILED: 7,
        SummaryStyle.KEYWORDS: 3,
    }

    def summarize(self, text: str, style: SummaryStyle = SummaryStyle.BRIEF) -> SummaryResult:
        if not text or not text.strip():
            raise ValueError("Input text must not be empty.")

        start = time.perf_counter()

        sentences = split_sentences(text.strip())
        if not sentences:
            raise ValueError("Could not detect any sentences in the input.")

        n_out = min(self._SENTENCE_COUNTS[style], len(sentences))
        keywords = extract_keywords(text, top_n=8)

        # ── Choose scorer per style ────────────────────────────────────────
        if style == SummaryStyle.BRIEF:
            scorer = TextRankScorer(sentences)
            scores = scorer.score()
            picked = _pick_sentences(sentences, scores, n_out, preserve_order=True)
            summary = " ".join(picked)

        elif style == SummaryStyle.BULLET:
            scorer = TFIDFScorer(sentences)
            scores = scorer.score()
            picked = _pick_sentences(sentences, scores, n_out, preserve_order=True)
            summary = "\n".join(f"• {s}" for s in picked)

        elif style == SummaryStyle.DETAILED:
            scorer = TFIDFScorer(sentences)
            scores = scorer.score()
            picked = _pick_sentences(sentences, scores, n_out, preserve_order=True)
            summary = " ".join(picked)

        elif style == SummaryStyle.KEYWORDS:
            scorer = TFIDFScorer(sentences)
            scores = scorer.score()
            picked = _pick_sentences(sentences, scores, n_out, preserve_order=True)
            kw_line = "Keywords: " + ", ".join(keywords)
            summary = kw_line + "\n\n" + " ".join(picked)

        elapsed = time.perf_counter() - start

        return SummaryResult(
            summary=summary,
            style=style,
            input_word_count=_word_count(text),
            output_word_count=_word_count(summary),
            sentence_count_in=len(sentences),
            sentence_count_out=len(picked),
            top_keywords=keywords,
            elapsed_seconds=elapsed,
        )

    def summarize_file(self, path: str, style: SummaryStyle = SummaryStyle.BRIEF) -> SummaryResult:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return self.summarize(text, style)