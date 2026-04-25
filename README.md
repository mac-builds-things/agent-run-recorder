# agent-run-recorder

*Record, store, and render structured timelines of AI agent coding sessions.*

## Example output

```
$ python render_timeline.py records/examples/example-session.json

session  refactor-authenticate-2024-03-15
agent    claude-3-5-sonnet-20241022
task     Refactor the authenticate() function in auth.py …
status   completed  (2m 46s)

14:22:01.003  ▎ user        Refactor the authenticate() function in auth.py …
14:22:03.441  ▎ assistant   I'll start by reading the current auth.py …
14:22:03.501  ▶ tool_call   read_file          src/auth.py
14:22:03.618  ◀ tool_result read_file          117 ms  exit:—
14:22:07.219  ▎ assistant   Now I can see the existing implementation …
14:22:07.311  ▶ tool_call   run_tests          pytest tests/test_auth.py -v
14:22:14.802  ◀ tool_result run_tests          7491 ms  exit:0
14:22:14.901  ▶ tool_call   write_file         src/auth.py
14:22:15.044  ◀ tool_result write_file         143 ms  exit:—
14:22:15.045  ★ artifact    src/auth.py        810 bytes

tokens  in:3842  out:1204  tool calls:4  failures:0
```

## Usage

```sh
# Record a new session (wraps your agent invocation)
python record_session.py --agent <cmd> --task "description" --out records/

# Render a recorded session as a terminal timeline
python render_timeline.py records/examples/example-session.json
```

## Session format

Events are stored as a JSON array. Each event has a `seq`, `type`, `ts`, and `payload`:

```json
{
  "session_id": "refactor-authenticate-2024-03-15",
  "schema_version": "1.0.0",
  "agent_name": "claude-3-5-sonnet-20241022",
  "started_at": "2024-03-15T14:22:01.003Z",
  "status": "completed",
  "events": [
    { "seq": 1, "type": "message",     "ts": "2024-03-15T14:22:01.003Z",
      "payload": { "role": "user", "content": "Refactor the authenticate() …" } },
    { "seq": 3, "type": "tool_call",   "ts": "2024-03-15T14:22:03.501Z",
      "payload": { "call_id": "call_01", "tool": "read_file", "args": { "path": "src/auth.py" } } },
    { "seq": 4, "type": "tool_result", "ts": "2024-03-15T14:22:03.618Z",
      "payload": { "call_id": "call_01", "tool": "read_file", "duration_ms": 117, "exit_code": null } },
    { "seq": 10, "type": "artifact",   "ts": "2024-03-15T14:22:15.045Z",
      "payload": { "kind": "file", "path": "src/auth.py", "size_bytes": 810 } }
  ]
}
```

## How it works

- Sessions are plain JSON files — one file per run, schema-validated, human-readable.
- The recorder wraps any agent process and captures stdin/stdout events with microsecond timestamps.
- The renderer replays events in order, computing durations from adjacent timestamps and formatting tool I/O inline.

## Schema

Schema definition lives at `records/schema/session-schema.json`.

**Status:** early-stage, schema at v1.0.0, API unstable.
