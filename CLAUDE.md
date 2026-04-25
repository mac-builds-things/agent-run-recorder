# agent-run-recorder

## Project

Python 3.11+, pydantic + rich. Core classes:

- `AgentSession`, `SessionEvent`, `EventType` enum, `SessionRecorder` — `src/recorder.py`
- Schema models — `src/schema.py`
- Timeline renderer — `src/timeline.py`
- File-based storage — `src/storage.py`

Sessions stored as JSON in `records/`. Reference schema in `records/schema/session-schema.json`.

## Commands

```bash
python -m pytest tests/                    # Run tests
python examples/record_session.py          # Record an example session
python examples/render_timeline.py         # Render a stored session
```

## Schema overview

A session is a JSON object:

```json
{
  "id": "session-YYYYMMDD-NNN",
  "agent_name": "...",
  "task": "...",
  "started_at": "<iso8601>",
  "ended_at": "<iso8601>",
  "events": [],
  "artifacts": [],
  "summary": "..."
}
```

Each event has:

```json
{
  "id": "<uuid>",
  "type": "<EventType>",
  "timestamp": "<iso8601>",
  "data": {}
}
```

`EventType` values: `tool_call`, `tool_result`, `message`, `artifact`, `error`.

## Adding a new event type

1. Add to `EventType` enum in `src/schema.py`
2. Add handler in `src/recorder.py`
3. Update `records/schema/session-schema.json` to include the new type
4. Add to the timeline renderer in `src/timeline.py`

## Conventions

- Session IDs use format: `session-YYYYMMDD-NNN`
- Events are append-only: never modify a recorded event
- Artifacts are referenced by path, not embedded in the session JSON
- The summary is generated at session end, not during recording

## Agent notes

When debugging a recorded session, start with `render_timeline.py` — it gives you the most readable view. The raw JSON in `records/examples/` shows the full schema. When adding recorder integration to an agent, wrap the agent loop with `SessionRecorder` as a context manager (see `examples/record_session.py`).
