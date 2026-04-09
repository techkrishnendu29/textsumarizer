from enum import Enum
from dataclasses import dataclass, field


class SummaryStyle(str, Enum):
    BRIEF    = "brief"     # Top 3 sentences via TF-IDF
    BULLET   = "bullet"    # Top 5 sentences as bullet list
    DETAILED = "detailed"  # Top 7 sentences, preserves order
    KEYWORDS = "keywords"  # Key terms + top 3 sentences


@dataclass
class SummaryResult:
    summary: str
    style: SummaryStyle
    input_word_count: int
    output_word_count: int
    sentence_count_in: int
    sentence_count_out: int
    top_keywords: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    def __str__(self) -> str:
        kw_line = ""
        if self.top_keywords:
            kw_line = f"Keywords    : {', '.join(self.top_keywords)}\n"
        return (
            f"\n{'─' * 60}\n"
            f"{self.summary}\n"
            f"{'─' * 60}\n"
            f"Style       : {self.style.value}\n"
            f"Input       : {self.input_word_count} words, {self.sentence_count_in} sentences\n"
            f"Output      : {self.output_word_count} words, {self.sentence_count_out} sentences\n"
            f"{kw_line}"
            f"Time        : {self.elapsed_seconds:.3f}s\n"
        )