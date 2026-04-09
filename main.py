
import sys
import argparse
from summarizer import Summarizer, SummaryStyle


STYLES = [s.value for s in SummaryStyle]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="summarizer",
        description="Summarize text using pure-Python NLP (no external dependencies).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text", "-t", type=str, help="Inline text to summarize.")
    source.add_argument("--file", "-f", type=str, help="Path to a .txt file to summarize.")
    source.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode: paste text line-by-line (type 'END' to finish)."
    )
    parser.add_argument(
        "--style", "-s",
        choices=STYLES,
        default=SummaryStyle.BRIEF.value,
        help=f"Summary style. Choices: {STYLES}. Default: brief.",
    )
    return parser


def get_interactive_input() -> str:
    """
    Interactive mode: collect multi-line text input from user.
    Type 'END' on a new line to finish.
    """
    print("\n" + "=" * 60)
    print("Interactive Mode: Paste or type your text below.")
    print("Type 'END' on a new line when finished.")
    print("=" * 60 + "\n")
    
    lines = []
    try:
        while True:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
    except EOFError:
        # Handle Ctrl+D gracefully
        pass
    
    return "\n".join(lines).strip()


def resolve_input(args: argparse.Namespace) -> tuple[str | None, str | None]:
    if args.text:
        return args.text, None
    if args.file:
        return None, args.file
    if args.interactive:
        return get_interactive_input(), None
    if not sys.stdin.isatty():
        return sys.stdin.read(), None
    return None, None


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    text, file_path = resolve_input(args)
    if not text and not file_path:
        parser.print_help()
        sys.exit(1)

    try:
        summarizer = Summarizer()
        style = SummaryStyle(args.style)

        result = (
            summarizer.summarize_file(file_path, style)
            if file_path
            else summarizer.summarize(text, style)
        )
        print(result)

    except FileNotFoundError as e:
        print(f"[File Error] {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"[Input Error] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()