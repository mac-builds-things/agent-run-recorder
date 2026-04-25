# agent-run-recorder

> Capture, store, and replay AI agent sessions as structured timelines — for debugging, auditing, and sharing agent work.

---

## Why This Exists

AI agent sessions are ephemeral and opaque. You run an agent, it does things, and when the process ends you're left with a final output (if you're lucky) and no clear record of what happened in between. Tool calls get lost. Intermediate reasoning evaporates. Artifacts produced mid-session disappear from view.

This project makes agent sessions **persistent, searchable, and human-readable**.

Every tool call, model response, artifact write, and error is captured as a structured event in a session record. Those records can be rendered as readable timelines, diffed against other sessions, stored for auditing, or replayed for debugging.

---

## What Makes It Interesting

- **Structured event capture** — each event has a type, timestamp, duration, token counts, and a typed payload; no unstructured log scraping
- **Timeline rendering** — sessions render to readable, color-coded terminal output with collapsible tool calls and artifact summaries
- **Artifact tracking** — files written, code generated, and data produced during a session are linked to the events that produced them
- **Session summaries** — auto-generated summaries of what an agent accomplished, what it tried, and where it got stuck
- **Schema-first design** — all session records validate against a published JSON Schema; tooling can be built on top with confidence
- **File-based persistence** — sessions are stored as plain JSON; no database required; works with git, grep, and standard tooling

---

## Quickstart

```bash
pip install -r requirements.txt
```

### Record a session

```python
from src.recorder import SessionRecorder, EventType

recorder = SessionRecorder(session_id="my-first-session", agent_name="my-agent")
recorder.start()

recorder.record_event(
    event_type=EventType.tool_call,
    payload={"tool": "read_file", "args": {"path": "src/main.py"}},
)
recorder.record_event(
    event_type=EventType.tool_result,
    payload={"tool": "read_file", "result": "def main(): ...", "duration_ms": 12},
)
recorder.record_event(
    event_type=EventType.message,
    payload={"role": "assistant", "content": "I can see the main function. Let me refactor it."},
)

session = recorder.finish()
session.save("records/")
```

### Render a timeline

```python
from src.storage import SessionStorage
from src.timeline import TimelineRenderer

session = SessionStorage("records/").load("my-first-session")
TimelineRenderer().render(session)
```

---

## Example Workflow

```
$ python examples/record_session.py
[recorder] Session started: refactor-utils-2024-01-15
[recorder] 23 events captured
[recorder] 4 artifacts tracked
[recorder] Session saved: records/sessions/refactor-utils-2024-01-15.json

$ python examples/render_timeline.py records/sessions/refactor-utils-2024-01-15.json
```

See [EXAMPLE.md](EXAMPLE.md) for a detailed walkthrough of a full recorded session — the event stream, timeline rendering, artifacts, and summary output.

---

## Project Structure

```
agent-run-recorder/
├── src/
│   ├── recorder.py      # Core recording: AgentSession, SessionRecorder, EventType
│   ├── timeline.py      # Renders a session as a readable terminal timeline
│   ├── schema.py        # Pydantic models for the session data format
│   └── storage.py       # File-based session persistence
├── records/
│   ├── schema/
│   │   └── session-schema.json    # JSON Schema for session records
│   └── examples/
│       └── example-session.json   # A realistic example session record
├── examples/
│   ├── record_session.py          # How to wrap an agent run with the recorder
│   └── render_timeline.py         # How to render a stored session
└── tests/
    └── test_recorder.py
```

---

## What This Demonstrates

- **Session tracing** — capturing structured events from an agent process, similar to distributed tracing but for agentic workloads
- **Event sourcing patterns** — the session record is an append-only event log; state can be reconstructed by replaying events
- **Agent observability** — making the interior of an agent run inspectable after the fact, not just during
- **Schema-first tooling** — anchoring a data format in JSON Schema so that independent renderers, analyzers, and storage backends can interoperate

---

## Status

Early-stage / concept implementation. The schema design and data model are the main artifacts; the Python stubs are well-typed and ready to have bodies filled in. Intended as a foundation to build on, not a production library.

