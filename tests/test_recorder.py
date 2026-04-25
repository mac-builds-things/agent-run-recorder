"""
Stub test suite for SessionRecorder.

Run with:  pytest tests/test_recorder.py -v
"""

from src.recorder import AgentSession, SessionEvent, SessionRecorder
from src.schema import EventType


def test_recorder_creates_session():
    """SessionRecorder.finish() returns an AgentSession with the expected IDs."""
    recorder = SessionRecorder(session_id="test-session", agent_name="test-agent")
    recorder.start()
    session = recorder.finish()
    assert isinstance(session, AgentSession)
    assert session.session_id == "test-session"
    assert session.agent_name == "test-agent"


def test_recorder_captures_events():
    """Events recorded between start() and finish() appear in the session."""
    recorder = SessionRecorder(session_id="capture-test", agent_name="test-agent")
    recorder.start()
    recorder.record_message("user", "Hello")
    recorder.record_tool_call("c1", "read_file", {"path": "foo.py"})
    recorder.record_tool_result("c1", "read_file", duration_ms=10, result="def foo(): ...")
    session = recorder.finish()
    assert len(session.events) == 3
    assert session.events[0].type == EventType.message
    assert session.events[1].type == EventType.tool_call
    assert session.events[2].type == EventType.tool_result


def test_recorder_ends_session():
    """A finished session has a non-null finished_at and 'completed' status."""
    recorder = SessionRecorder(session_id="end-test", agent_name="test-agent")
    recorder.start()
    session = recorder.finish()
    assert session.finished_at is not None
    assert session.status == "completed"
    assert session.duration_ms is not None and session.duration_ms >= 0


def test_recorder_assigns_ids():
    """Each recorded event receives a unique, monotonically increasing seq number."""
    recorder = SessionRecorder(session_id="seq-test", agent_name="test-agent")
    recorder.start()
    recorder.record_message("user", "step 1")
    recorder.record_message("assistant", "step 2")
    recorder.record_message("user", "step 3")
    session = recorder.finish()
    seqs = [e.seq for e in session.events]
    assert seqs == sorted(seqs), "seq numbers must be monotonically increasing"
    assert len(set(seqs)) == len(seqs), "seq numbers must be unique"
