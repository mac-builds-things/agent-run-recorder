#!/usr/bin/env bash
# At session end, remind agent to save session artifacts if any tool calls were made.
set -euo pipefail

input=$(cat)
# Check if there were any tool uses this session
tool_count=$(echo "$input" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    tools = d.get('tool_uses', [])
    print(len(tools))
except:
    print(0)
" 2>/dev/null || echo "0")

if [ "$tool_count" -gt "3" ]; then
  echo '{
    "followup_message": "This session made several tool calls. Consider recording it using the session recorder: python examples/record_session.py. Stored sessions can be replayed and shared using python examples/render_timeline.py."
  }'
  exit 0
fi

exit 0
