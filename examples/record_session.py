"""
examples/record_session.py
--------------------------
Demonstrates how to use SessionRecorder as a context manager around a
simulated agent run, then persist the resulting session to disk.

Run from the project root:

    python -m examples.record_session

The session record will be written to records/sessions/.
"""

from __future__ import annotations

import contextlib
import time
from pathlib import Path

from src.recorder import SessionRecorder
from src.schema import ArtifactKind, SessionMetadata
from src.storage import SessionStorage

# ---------------------------------------------------------------------------
# Optional context-manager wrapper around SessionRecorder
# ---------------------------------------------------------------------------

@contextlib.contextmanager
def record_session(session_id: str, agent_name: str, metadata: SessionMetadata | None = None):
    """
    Context manager that starts a SessionRecorder, yields it, then finalises
    and returns the completed AgentSession via the ``session`` attribute of the
    yielded recorder.

    Usage::

        with record_session("my-run-2024-01-01", "my-agent") as recorder:
            recorder.record_message("user", "Do the thing")
            recorder.record_tool_call("c1", "do_thing", {})
            recorder.record_tool_result("c1", "do_thing", duration_ms=42, result="done")

        # recorder.session is now the completed AgentSession
        print(recorder.session.status)
    """
    recorder = SessionRecorder(
        session_id=session_id,
        agent_name=agent_name,
        metadata=metadata,
    )
    recorder.start()
    try:
        yield recorder
    finally:
        recorder.session = recorder.finish()


# ---------------------------------------------------------------------------
# Simulated agent run
# ---------------------------------------------------------------------------

def simulate_agent_run(recorder: SessionRecorder) -> None:
    """Simulate a short agent session that reads a file and writes a fix."""

    recorder.record_message(
        "user",
        "The `calculate_discount()` function in pricing.py has an off-by-one "
        "error. Please fix it.",
    )

    recorder.record_message(
        "assistant",
        "I'll read pricing.py first to understand the current implementation.",
    )

    recorder.record_tool_call("c1", "read_file", {"path": "src/pricing.py"})
    time.sleep(0.02)  # simulate latency
    recorder.record_tool_result(
        "c1",
        "read_file",
        duration_ms=18,
        result=(
            "def calculate_discount(price: float, pct: int) -> float:\n"
            "    return price * (100 - pct) / 100 + 1  # BUG: +1 is wrong\n"
        ),
    )

    recorder.record_message(
        "assistant",
        "Found it — the `+ 1` on line 2 is spurious. I'll remove it and "
        "write the corrected file.",
    )

    recorder.record_tool_call(
        "c2",
        "write_file",
        {
            "path": "src/pricing.py",
            "content": (
                "def calculate_discount(price: float, pct: int) -> float:\n"
                "    return price * (100 - pct) / 100\n"
            ),
        },
    )
    time.sleep(0.01)
    recorder.record_tool_result(
        "c2", "write_file", duration_ms=9, result="wrote 72 bytes to src/pricing.py"
    )

    recorder.record_artifact(
        artifact_id="artifact_01",
        kind=ArtifactKind.file,
        path="src/pricing.py",
        size_bytes=72,
        produced_by_call="c2",
        description="Corrected pricing.py — removed spurious `+ 1` from calculate_discount().",
    )

    recorder.record_tool_call(
        "c3",
        "run_tests",
        {"command": "pytest tests/test_pricing.py -v", "cwd": "."},
    )
    time.sleep(0.05)
    recorder.record_tool_result(
        "c3",
        "run_tests",
        duration_ms=430,
        exit_code=0,
        result="3 passed in 0.38s",
    )

    recorder.record_message(
        "assistant",
        "All 3 tests pass. The off-by-one error has been fixed.",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    storage = SessionStorage(Path(__file__).parent.parent / "records")

    with record_session(
        session_id="fix-calculate-discount-2024-03-15",
        agent_name="claude-3-5-sonnet-20241022",
        metadata=SessionMetadata(
            task="Fix off-by-one error in calculate_discount()",
            tags=["bugfix", "pricing"],
        ),
    ) as recorder:
        simulate_agent_run(recorder)

    session = recorder.session
    print(f"Session finished — status: {session.status}, events: {len(session.events)}")

    path = storage.save_overwrite(session)
    print(f"Saved to {path}")


if __name__ == "__main__":
    main()
