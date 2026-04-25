"""
examples/render_timeline.py
---------------------------
Loads a session record from disk and renders it as a colour-coded terminal
timeline using the Rich library.

Usage (from the project root):

    # Render the bundled example session
    python -m examples.render_timeline

    # Render a specific session by ID
    python -m examples.render_timeline fix-calculate-discount-2024-03-15

    # Render a session from an explicit file path
    python -m examples.render_timeline --file records/examples/example-session.json

    # Render plain text (no ANSI colours) — useful for piping
    python -m examples.render_timeline --plain
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.storage import SessionStorage
from src.timeline import TimelineRenderer


RECORDS_ROOT = Path(__file__).parent.parent / "records"
EXAMPLE_SESSION_PATH = RECORDS_ROOT / "examples" / "example-session.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render an agent session as a terminal timeline."
    )
    parser.add_argument(
        "session_id",
        nargs="?",
        default=None,
        help="Session ID to load from records/sessions/. Omit to use the bundled example.",
    )
    parser.add_argument(
        "--file",
        metavar="PATH",
        default=None,
        help="Load from an explicit JSON file path instead of looking up by session ID.",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        default=False,
        help="Render as plain text (no ANSI colour codes).",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        default=False,
        help="Show full tool result and message content (not truncated).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    storage = SessionStorage(RECORDS_ROOT)
    renderer = TimelineRenderer(
        output_format="text" if args.plain else "rich",
        show_full_content=args.full,
    )

    if args.file:
        # Load from an explicit path
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"error: file not found: {file_path}", file=sys.stderr)
            return 1
        session = storage.load_from_path(file_path)

    elif args.session_id:
        # Look up by session ID in the sessions/ subdirectory
        try:
            session = storage.load(args.session_id)
        except FileNotFoundError:
            available = storage.list_sessions()
            print(
                f"error: session '{args.session_id}' not found.\n"
                f"Available sessions: {available or '(none)'}",
                file=sys.stderr,
            )
            return 1

    else:
        # Fall back to the bundled example session
        if not EXAMPLE_SESSION_PATH.exists():
            print(
                f"error: example session not found at {EXAMPLE_SESSION_PATH}",
                file=sys.stderr,
            )
            return 1
        session = storage.load_from_path(EXAMPLE_SESSION_PATH)

    renderer.render(session)
    return 0


if __name__ == "__main__":
    sys.exit(main())
