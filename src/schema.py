"""
Pydantic models for the agent-run-recorder session data format.

These models mirror the JSON Schema in records/schema/session-schema.json.
They are used by SessionRecorder for structured event creation and by
TimelineRenderer / SessionStorage for deserialization.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------


class EventType(str, Enum):
    """All recognised event types in a session record."""

    tool_call = "tool_call"
    tool_result = "tool_result"
    message = "message"
    artifact = "artifact"
    error = "error"


class ArtifactKind(str, Enum):
    """Kinds of artifact that a session can produce."""

    file = "file"
    snippet = "snippet"
    data = "data"
    image = "image"


# ---------------------------------------------------------------------------
# Event payloads
# ---------------------------------------------------------------------------


class ToolCallPayload(BaseModel):
    """Payload for an EventType.tool_call event."""

    call_id: str = Field(..., description="Unique identifier for this call, matched by its tool_result")
    tool: str = Field(..., description="Tool name as registered with the agent")
    args: dict[str, Any] = Field(default_factory=dict, description="Arguments passed to the tool")


class ToolResultPayload(BaseModel):
    """Payload for an EventType.tool_result event."""

    call_id: str = Field(..., description="Matches the call_id in the corresponding tool_call event")
    tool: str = Field(..., description="Tool name, for convenience when reading the record")
    duration_ms: int = Field(..., ge=0, description="Wall-clock time for the tool invocation in milliseconds")
    exit_code: int | None = Field(None, description="Exit code for command-like tools; null if not applicable")
    result: Any = Field(..., description="The tool's return value; may be a string, dict, or null")
    error: str | None = Field(None, description="Error message if the tool raised an exception")


class TokenCounts(BaseModel):
    """Token usage for a single model response."""

    input: int = Field(..., ge=0)
    output: int = Field(..., ge=0)
    cache_read: int | None = Field(None, ge=0)
    cache_write: int | None = Field(None, ge=0)


class MessagePayload(BaseModel):
    """Payload for an EventType.message event."""

    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message text content")
    token_counts: TokenCounts | None = Field(None, description="Token usage; populated for assistant messages")


class ArtifactPayload(BaseModel):
    """Payload for an EventType.artifact event."""

    artifact_id: str = Field(..., description="Unique identifier for this artifact within the session")
    kind: ArtifactKind
    path: str | None = Field(None, description="File path, if the artifact is a file on disk")
    size_bytes: int | None = Field(None, ge=0)
    produced_by_call: str | None = Field(None, description="call_id of the tool_call that produced this artifact")
    description: str | None = Field(None, description="Human-readable description of what this artifact is")
    content: str | None = Field(None, description="Inline content for small artifacts; null for large files")


class ErrorPayload(BaseModel):
    """Payload for an EventType.error event."""

    message: str = Field(..., description="Error message")
    exception_type: str | None = Field(None, description="Python exception class name")
    traceback: str | None = Field(None, description="Full traceback, if available")
    recoverable: bool = Field(True, description="Whether the session continued after this error")


# ---------------------------------------------------------------------------
# Core event model
# ---------------------------------------------------------------------------


PayloadType = ToolCallPayload | ToolResultPayload | MessagePayload | ArtifactPayload | ErrorPayload


class SessionEvent(BaseModel):
    """A single event in an agent session."""

    seq: int = Field(..., ge=1, description="Monotonically increasing sequence number")
    type: EventType
    ts: datetime = Field(..., description="UTC timestamp of the event")
    payload: PayloadType = Field(..., discriminator=None)

    model_config = {"arbitrary_types_allowed": True}


# ---------------------------------------------------------------------------
# Session summary (computed, stored for quick access)
# ---------------------------------------------------------------------------


class SessionSummary(BaseModel):
    """Aggregated statistics for a completed session, stored in the record."""

    total_events: int = Field(..., ge=0)
    tool_calls: int = Field(..., ge=0)
    tool_failures: int = Field(..., ge=0)
    artifacts_produced: int = Field(..., ge=0)
    token_input_total: int = Field(..., ge=0)
    token_output_total: int = Field(..., ge=0)


# ---------------------------------------------------------------------------
# Session metadata and top-level record
# ---------------------------------------------------------------------------


class SessionMetadata(BaseModel):
    """Arbitrary metadata attached to a session at creation time."""

    model: str | None = None
    task: str | None = None
    tags: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)


class AgentSession(BaseModel):
    """
    The top-level session record.  This is the object serialised to JSON
    and stored in the records/ directory.
    """

    session_id: str = Field(..., description="Unique session identifier (slug-like, human-readable)")
    schema_version: str = Field("1.0.0", description="Version of the session record schema")
    agent_name: str = Field(..., description="Name or identifier of the agent that ran this session")
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: int | None = Field(None, ge=0)
    status: str = Field("in_progress", description="'in_progress', 'completed', 'failed', or 'interrupted'")
    metadata: SessionMetadata = Field(default_factory=SessionMetadata)
    summary: SessionSummary | None = None
    events: list[SessionEvent] = Field(default_factory=list)
