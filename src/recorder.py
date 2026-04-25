"""
Core recording primitives for agent-run-recorder.

Usage::

    from src.recorder import SessionRecorder, EventType

    recorder = SessionRecorder(session_id="my-session", agent_name="my-agent")
    recorder.start()

    recorder.record_tool_call("call_01", "read_file", {"path": "foo.py"})
    recorder.record_tool_result("call_01", "read_file", duration_ms=14, result="def foo(): ...")
    recorder.record_message("assistant", "I can see the function. Let me refactor it.")

    session = recorder.finish()
    session.save("records/")
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from src.schema import (
    AgentSession,
    ArtifactKind,
    ArtifactPayload,
    ErrorPayload,
    EventType,
    MessagePayload,
    SessionEvent,
    SessionMetadata,
    SessionSummary,
    TokenCounts,
    ToolCallPayload,
    ToolResultPayload,
)

# Re-export EventType so callers can do `from src.recorder import EventType`
__all__ = ["SessionRecorder", "EventType", "AgentSession", "SessionEvent"]


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class SessionRecorder:
    """
    Records events from an agent session into an AgentSession object.

    Thread-safety: not guaranteed; designed for single-threaded agent loops.
    """

    def __init__(
        self,
        session_id: str,
        agent_name: str,
        metadata: SessionMetadata | None = None,
    ) -> None:
        self._session_id = session_id
        self._agent_name = agent_name
        self._metadata = metadata or SessionMetadata()
        self._events: list[SessionEvent] = []
        self._seq = 0
        self._started_at: datetime | None = None
        self._started_wall: float | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Mark the session as started.  Must be called before recording events."""
        self._started_at = _utcnow()
        self._started_wall = time.monotonic()

    def finish(self) -> AgentSession:
        """
        Finalise the session, compute summary statistics, and return the
        AgentSession record ready for serialisation.
        """
        if self._started_at is None:
            raise RuntimeError("SessionRecorder.start() must be called before finish()")

        finished_at = _utcnow()
        duration_ms = int((time.monotonic() - self._started_wall) * 1000)  # type: ignore[operator]

        summary = self._compute_summary()

        return AgentSession(
            session_id=self._session_id,
            agent_name=self._agent_name,
            started_at=self._started_at,
            finished_at=finished_at,
            duration_ms=duration_ms,
            status="completed",
            metadata=self._metadata,
            summary=summary,
            events=list(self._events),
        )

    # ------------------------------------------------------------------
    # Event recording helpers
    # ------------------------------------------------------------------

    def record_tool_call(
        self,
        call_id: str,
        tool: str,
        args: dict[str, Any] | None = None,
    ) -> SessionEvent:
        """Record that the agent invoked a tool."""
        return self._append(
            EventType.tool_call,
            ToolCallPayload(call_id=call_id, tool=tool, args=args or {}),
        )

    def record_tool_result(
        self,
        call_id: str,
        tool: str,
        duration_ms: int,
        result: Any = None,
        exit_code: int | None = None,
        error: str | None = None,
    ) -> SessionEvent:
        """Record the result (or failure) of a tool invocation."""
        return self._append(
            EventType.tool_result,
            ToolResultPayload(
                call_id=call_id,
                tool=tool,
                duration_ms=duration_ms,
                result=result,
                exit_code=exit_code,
                error=error,
            ),
        )

    def record_message(
        self,
        role: str,
        content: str,
        token_counts: TokenCounts | None = None,
    ) -> SessionEvent:
        """Record a user, assistant, or system message."""
        return self._append(
            EventType.message,
            MessagePayload(role=role, content=content, token_counts=token_counts),
        )

    def record_artifact(
        self,
        artifact_id: str,
        kind: ArtifactKind,
        path: str | None = None,
        size_bytes: int | None = None,
        produced_by_call: str | None = None,
        description: str | None = None,
        content: str | None = None,
    ) -> SessionEvent:
        """Record that an artifact (file, snippet, data) was produced."""
        return self._append(
            EventType.artifact,
            ArtifactPayload(
                artifact_id=artifact_id,
                kind=kind,
                path=path,
                size_bytes=size_bytes,
                produced_by_call=produced_by_call,
                description=description,
                content=content,
            ),
        )

    def record_error(
        self,
        message: str,
        exception_type: str | None = None,
        traceback: str | None = None,
        recoverable: bool = True,
    ) -> SessionEvent:
        """Record an error that occurred during the session."""
        return self._append(
            EventType.error,
            ErrorPayload(
                message=message,
                exception_type=exception_type,
                traceback=traceback,
                recoverable=recoverable,
            ),
        )

    def record_event(
        self,
        event_type: EventType,
        payload: Any,
    ) -> SessionEvent:
        """
        Low-level method for recording a pre-constructed payload.
        Prefer the typed helpers above when possible.
        """
        return self._append(event_type, payload)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def _append(self, event_type: EventType, payload: Any) -> SessionEvent:
        event = SessionEvent(
            seq=self._next_seq(),
            type=event_type,
            ts=_utcnow(),
            payload=payload,
        )
        self._events.append(event)
        return event

    def _compute_summary(self) -> SessionSummary:
        tool_calls = sum(1 for e in self._events if e.type == EventType.tool_call)
        tool_failures = sum(
            1
            for e in self._events
            if e.type == EventType.tool_result
            and isinstance(e.payload, ToolResultPayload)
            and (e.payload.exit_code not in (None, 0) or e.payload.error is not None)
        )
        artifacts_produced = sum(1 for e in self._events if e.type == EventType.artifact)
        token_input_total = sum(
            e.payload.token_counts.input
            for e in self._events
            if e.type == EventType.message
            and isinstance(e.payload, MessagePayload)
            and e.payload.token_counts is not None
        )
        token_output_total = sum(
            e.payload.token_counts.output
            for e in self._events
            if e.type == EventType.message
            and isinstance(e.payload, MessagePayload)
            and e.payload.token_counts is not None
        )
        return SessionSummary(
            total_events=len(self._events),
            tool_calls=tool_calls,
            tool_failures=tool_failures,
            artifacts_produced=artifacts_produced,
            token_input_total=token_input_total,
            token_output_total=token_output_total,
        )
