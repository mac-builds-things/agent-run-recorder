# Example: A Recorded Agent Session

This walkthrough shows a complete recorded session in which an agent refactors a utility module. It covers the raw event stream, the rendered timeline, the artifacts captured, and the final session summary.

---

## The Task

The user asked an agent to:

> "Refactor `src/utils.py` — it has grown too large. Split it into focused modules, add type hints throughout, and make sure nothing breaks."

The agent ran for about 90 seconds, made 14 tool calls, wrote 5 files, and ran tests twice.

---

## The Event Stream

Below is the structured event log as stored in `records/examples/example-session.json` (abbreviated for readability). Each event has a monotonically increasing sequence number, a UTC timestamp, a type, and a typed payload.

```json
[
  {
    "seq": 1,
    "type": "message",
    "ts": "2024-01-15T14:32:01.004Z",
    "payload": {
      "role": "user",
      "content": "Refactor src/utils.py — it has grown too large. Split it into focused modules, add type hints, and make sure nothing breaks."
    }
  },
  {
    "seq": 2,
    "type": "message",
    "ts": "2024-01-15T14:32:01.891Z",
    "payload": {
      "role": "assistant",
      "content": "I'll start by reading the current utils.py to understand its contents and identify logical groupings.",
      "token_counts": { "input": 312, "output": 28 }
    }
  },
  {
    "seq": 3,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:01.904Z",
    "payload": {
      "call_id": "call_01",
      "tool": "read_file",
      "args": { "path": "src/utils.py" }
    }
  },
  {
    "seq": 4,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:01.917Z",
    "payload": {
      "call_id": "call_01",
      "tool": "read_file",
      "duration_ms": 13,
      "result": "# 347 lines of mixed utilities: string helpers, file I/O, date parsing, retry logic, config loading"
    }
  },
  {
    "seq": 5,
    "type": "message",
    "ts": "2024-01-15T14:32:03.210Z",
    "payload": {
      "role": "assistant",
      "content": "The file has four clear domains: string helpers (lines 1–89), file I/O utilities (90–178), date/time parsing (179–251), and retry/backoff logic (252–347). I'll split these into src/string_utils.py, src/file_utils.py, src/date_utils.py, and src/retry.py. I'll also write a thin src/utils.py that re-exports everything for backward compatibility.",
      "token_counts": { "input": 1847, "output": 94 }
    }
  },
  {
    "seq": 6,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:03.225Z",
    "payload": {
      "call_id": "call_02",
      "tool": "write_file",
      "args": { "path": "src/string_utils.py", "content": "..." }
    }
  },
  {
    "seq": 7,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:03.388Z",
    "payload": {
      "call_id": "call_02",
      "tool": "write_file",
      "duration_ms": 163,
      "result": "ok"
    }
  },
  {
    "seq": 8,
    "type": "artifact",
    "ts": "2024-01-15T14:32:03.390Z",
    "payload": {
      "artifact_id": "artifact_01",
      "kind": "file",
      "path": "src/string_utils.py",
      "size_bytes": 2841,
      "produced_by_call": "call_02",
      "description": "String utility functions extracted from src/utils.py with full type annotations"
    }
  },
  {
    "seq": 9,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:03.401Z",
    "payload": {
      "call_id": "call_03",
      "tool": "write_file",
      "args": { "path": "src/file_utils.py", "content": "..." }
    }
  },
  {
    "seq": 10,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:03.541Z",
    "payload": {
      "call_id": "call_03",
      "tool": "write_file",
      "duration_ms": 140,
      "result": "ok"
    }
  },
  {
    "seq": 11,
    "type": "artifact",
    "ts": "2024-01-15T14:32:03.543Z",
    "payload": {
      "artifact_id": "artifact_02",
      "kind": "file",
      "path": "src/file_utils.py",
      "size_bytes": 3104,
      "produced_by_call": "call_03",
      "description": "File I/O utilities with typed return values and error handling"
    }
  },
  {
    "seq": 12,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:03.555Z",
    "payload": {
      "call_id": "call_04",
      "tool": "write_file",
      "args": { "path": "src/date_utils.py", "content": "..." }
    }
  },
  {
    "seq": 13,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:03.692Z",
    "payload": {
      "call_id": "call_04",
      "tool": "write_file",
      "duration_ms": 137,
      "result": "ok"
    }
  },
  {
    "seq": 14,
    "type": "artifact",
    "ts": "2024-01-15T14:32:03.694Z",
    "payload": {
      "artifact_id": "artifact_03",
      "kind": "file",
      "path": "src/date_utils.py",
      "size_bytes": 2197,
      "produced_by_call": "call_04",
      "description": "Date/time parsing and formatting utilities"
    }
  },
  {
    "seq": 15,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:03.705Z",
    "payload": {
      "call_id": "call_05",
      "tool": "write_file",
      "args": { "path": "src/retry.py", "content": "..." }
    }
  },
  {
    "seq": 16,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:03.851Z",
    "payload": {
      "call_id": "call_05",
      "tool": "write_file",
      "duration_ms": 146,
      "result": "ok"
    }
  },
  {
    "seq": 17,
    "type": "artifact",
    "ts": "2024-01-15T14:32:03.853Z",
    "payload": {
      "artifact_id": "artifact_04",
      "kind": "file",
      "path": "src/retry.py",
      "size_bytes": 1988,
      "produced_by_call": "call_05",
      "description": "Retry/backoff decorator and helpers"
    }
  },
  {
    "seq": 18,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:03.864Z",
    "payload": {
      "call_id": "call_06",
      "tool": "write_file",
      "args": { "path": "src/utils.py", "content": "# backward-compat re-export shim\nfrom src.string_utils import *\nfrom src.file_utils import *\nfrom src.date_utils import *\nfrom src.retry import *\n" }
    }
  },
  {
    "seq": 19,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:03.983Z",
    "payload": {
      "call_id": "call_06",
      "tool": "write_file",
      "duration_ms": 119,
      "result": "ok"
    }
  },
  {
    "seq": 20,
    "type": "artifact",
    "ts": "2024-01-15T14:32:03.985Z",
    "payload": {
      "artifact_id": "artifact_05",
      "kind": "file",
      "path": "src/utils.py",
      "size_bytes": 124,
      "produced_by_call": "call_06",
      "description": "Backward-compatible re-export shim — replaces the original 347-line file"
    }
  },
  {
    "seq": 21,
    "type": "message",
    "ts": "2024-01-15T14:32:04.991Z",
    "payload": {
      "role": "assistant",
      "content": "All four modules written. Now running the existing test suite to confirm nothing broke.",
      "token_counts": { "input": 2201, "output": 19 }
    }
  },
  {
    "seq": 22,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:05.003Z",
    "payload": {
      "call_id": "call_07",
      "tool": "run_command",
      "args": { "cmd": "python -m pytest tests/ -q" }
    }
  },
  {
    "seq": 23,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:16.442Z",
    "payload": {
      "call_id": "call_07",
      "tool": "run_command",
      "duration_ms": 11439,
      "exit_code": 1,
      "result": "FAILED tests/test_date_utils.py::test_parse_iso_with_tz — AssertionError: expected UTC offset +05:30, got +0530"
    }
  },
  {
    "seq": 24,
    "type": "message",
    "ts": "2024-01-15T14:32:18.103Z",
    "payload": {
      "role": "assistant",
      "content": "One test failure in date_utils. The original format_tz_offset function produced '+05:30' (with colon) but my rewrite produces '+0530'. Fixing the formatting in src/date_utils.py.",
      "token_counts": { "input": 2544, "output": 48 }
    }
  },
  {
    "seq": 25,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:18.118Z",
    "payload": {
      "call_id": "call_08",
      "tool": "edit_file",
      "args": {
        "path": "src/date_utils.py",
        "edit": "fix format_tz_offset to insert colon between hours and minutes in offset string"
      }
    }
  },
  {
    "seq": 26,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:18.241Z",
    "payload": {
      "call_id": "call_08",
      "tool": "edit_file",
      "duration_ms": 123,
      "result": "ok"
    }
  },
  {
    "seq": 27,
    "type": "tool_call",
    "ts": "2024-01-15T14:32:18.254Z",
    "payload": {
      "call_id": "call_09",
      "tool": "run_command",
      "args": { "cmd": "python -m pytest tests/ -q" }
    }
  },
  {
    "seq": 28,
    "type": "tool_result",
    "ts": "2024-01-15T14:32:28.891Z",
    "payload": {
      "call_id": "call_09",
      "tool": "run_command",
      "duration_ms": 10637,
      "exit_code": 0,
      "result": "47 passed in 10.63s"
    }
  },
  {
    "seq": 29,
    "type": "message",
    "ts": "2024-01-15T14:32:30.002Z",
    "payload": {
      "role": "assistant",
      "content": "All 47 tests pass. The refactor is complete:\n\n- `src/utils.py` (347 lines) → 4 focused modules + thin re-export shim\n- All functions have type hints\n- Backward compatibility preserved via the shim\n- One bug caught and fixed during refactor (timezone offset formatting)\n\nNew module sizes: string_utils 89 lines, file_utils 98 lines, date_utils 71 lines, retry 63 lines.",
      "token_counts": { "input": 2801, "output": 112 }
    }
  }
]
```

---

## The Rendered Timeline

When you run `python examples/render_timeline.py records/examples/example-session.json`, the terminal output looks like this:

```
╭─────────────────────────────────────────────────────────────────────╮
│  Session: refactor-utils-2024-01-15                                 │
│  Agent:   claude-3-5-sonnet  │  Duration: 1m 29s  │  Events: 29    │
╰─────────────────────────────────────────────────────────────────────╯

14:32:01  USER
          Refactor src/utils.py — it has grown too large. Split into
          focused modules, add type hints, and make sure nothing breaks.

14:32:01  ASSISTANT                                          28 tok out
          I'll start by reading the current utils.py to understand its
          contents and identify logical groupings.

14:32:01  ▶ tool_call  read_file
          │  path: src/utils.py
14:32:01  ✓ tool_result  read_file                              13 ms
          │  347 lines of mixed utilities

14:32:03  ASSISTANT                                          94 tok out
          The file has four clear domains: string helpers (lines 1–89),
          file I/O utilities (90–178), date/time parsing (179–251), and
          retry/backoff logic (252–347). I'll split these into
          src/string_utils.py, src/file_utils.py, src/date_utils.py,
          and src/retry.py, with a thin backward-compat re-export shim.

14:32:03  ▶ tool_call  write_file
          │  path: src/string_utils.py  (2,841 bytes)
14:32:03  ✓ tool_result  write_file                            163 ms
          │  ok
          📄 ARTIFACT  src/string_utils.py  (2,841 bytes)
             String utility functions with full type annotations

14:32:03  ▶ tool_call  write_file
          │  path: src/file_utils.py  (3,104 bytes)
14:32:03  ✓ tool_result  write_file                            140 ms
          │  ok
          📄 ARTIFACT  src/file_utils.py  (3,104 bytes)
             File I/O utilities with typed return values

14:32:03  ▶ tool_call  write_file
          │  path: src/date_utils.py  (2,197 bytes)
14:32:03  ✓ tool_result  write_file                            137 ms
          │  ok
          📄 ARTIFACT  src/date_utils.py  (2,197 bytes)
             Date/time parsing and formatting utilities

14:32:03  ▶ tool_call  write_file
          │  path: src/retry.py  (1,988 bytes)
14:32:03  ✓ tool_result  write_file                            146 ms
          │  ok
          📄 ARTIFACT  src/retry.py  (1,988 bytes)
             Retry/backoff decorator and helpers

14:32:03  ▶ tool_call  write_file
          │  path: src/utils.py  (124 bytes)  [overwrite]
14:32:03  ✓ tool_result  write_file                            119 ms
          │  ok
          📄 ARTIFACT  src/utils.py  (124 bytes)
             Backward-compatible re-export shim

14:32:04  ASSISTANT                                          19 tok out
          All four modules written. Running tests to confirm nothing broke.

14:32:05  ▶ tool_call  run_command
          │  cmd: python -m pytest tests/ -q
14:32:16  ✗ tool_result  run_command                        11,439 ms
          │  exit_code: 1
          │  FAILED tests/test_date_utils.py::test_parse_iso_with_tz
          │  AssertionError: expected '+05:30', got '+0530'

14:32:18  ASSISTANT                                          48 tok out
          One failure in date_utils — timezone offset format mismatch.
          Original produced '+05:30'; my rewrite produces '+0530'. Fixing.

14:32:18  ▶ tool_call  edit_file
          │  path: src/date_utils.py
          │  fix format_tz_offset colon insertion
14:32:18  ✓ tool_result  edit_file                             123 ms
          │  ok

14:32:18  ▶ tool_call  run_command
          │  cmd: python -m pytest tests/ -q
14:32:28  ✓ tool_result  run_command                        10,637 ms
          │  exit_code: 0
          │  47 passed in 10.63s

14:32:30  ASSISTANT                                         112 tok out
          All 47 tests pass. Refactor complete:
          • src/utils.py (347 lines) → 4 focused modules + re-export shim
          • All functions have type hints
          • Backward compatibility preserved
          • 1 bug caught and fixed (timezone offset format)

╭─────────────────────────────────────────────────────────────────────╮
│  SESSION SUMMARY                                                    │
├─────────────────────────────────────────────────────────────────────┤
│  Duration:       1m 29s                                             │
│  Total events:   29  (9 tool calls, 9 tool results, 5 artifacts,   │
│                       5 messages, 1 error/failure)                 │
│  Token usage:    4,517 input  /  301 output                        │
│  Tool calls:     9  (8 succeeded, 1 failed → recovered)            │
│  Artifacts:      5 files written  (10,254 bytes total)             │
│  Tests run:      2  (first: 1 failure; second: 47 passed)          │
╰─────────────────────────────────────────────────────────────────────╯
```

---

## Artifacts Captured

The session record tracks all five files produced, linked back to the tool calls that created them:

| Artifact | Produced by | Size | Description |
|---|---|---|---|
| `src/string_utils.py` | call_02 (write_file) | 2,841 B | String helpers, type-annotated |
| `src/file_utils.py` | call_03 (write_file) | 3,104 B | File I/O utilities |
| `src/date_utils.py` | call_04 (write_file) | 2,197 B | Date/time parsing |
| `src/retry.py` | call_05 (write_file) | 1,988 B | Retry/backoff decorator |
| `src/utils.py` | call_06 (write_file) | 124 B | Backward-compat re-export shim |

Note that `src/date_utils.py` was subsequently modified by call_08 (edit_file) to fix the timezone format bug — the session record preserves both events, so you can see exactly what changed and why.

---

## What the Recording Enables

After the session is stored, you can:

1. **Audit** — replay the event stream to see exactly what the agent read, wrote, and ran. No guesswork about what it touched.

2. **Debug** — the test failure at seq 23 and the reasoning at seq 24 are both captured. If the fix had been wrong, you'd have a complete record to investigate.

3. **Diff sessions** — run the same task twice with different models or prompts, then diff the session records to see what changed: different tool call sequences, different reasoning, different artifacts.

4. **Share** — hand the JSON file to a colleague. They can render the timeline locally and see exactly what the agent did, without needing access to the original environment.

5. **Measure** — aggregate across sessions: how many tool calls does this agent typically take? Where does it get stuck? What's the token cost distribution?

---

## Session Record Format

The full session record is stored at `records/examples/example-session.json`. Its top-level structure:

```json
{
  "session_id": "refactor-utils-2024-01-15",
  "schema_version": "1.0.0",
  "agent_name": "claude-3-5-sonnet",
  "started_at": "2024-01-15T14:32:01.004Z",
  "finished_at": "2024-01-15T14:33:30.002Z",
  "duration_ms": 88998,
  "status": "completed",
  "metadata": {
    "model": "claude-3-5-sonnet-20241022",
    "task": "Refactor src/utils.py",
    "tags": ["refactor", "python", "type-hints"]
  },
  "summary": {
    "total_events": 29,
    "tool_calls": 9,
    "tool_failures": 1,
    "artifacts_produced": 5,
    "token_input_total": 4517,
    "token_output_total": 301
  },
  "events": [ ... ]
}
```

See `records/schema/session-schema.json` for the full JSON Schema.
