# This file makes summarizer a Python package

try:
    from .summarizer import Summarizer, SummaryStyle, SummaryResult
except ImportError:
    # If imports fail, try alternative
    try:
        from summarizer import Summarizer, SummaryStyle, SummaryResult
    except ImportError as e:
        print(f"Warning: Could not import from summarizer module: {e}")
