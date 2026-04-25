"""
Timeline renderer for agent-run-recorder.

Renders an AgentSession as a readable, colour-coded terminal timeline
using the Rich library.

Usage::

    from src.storage import SessionStorage
    from src.timeline import TimelineRenderer

    session = SessionStorage("records/").load("my-session")
    TimelineRenderer().render(session)

Or to get a string instead of printing::

    output = TimelineRenderer(output_format="text").render_to_string(session)
"""

from __future__ import annotations

from typing import Literal

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.schema import (
    AgentSession,
    ArtifactPayload,
    ErrorPayload,
    EventType,
    MessagePayload,
    SessionEvent,
    ToolCallPayload,
    ToolResultPayload,
)


class TimelineRenderer:
    """
    Renders an AgentSession as a human-readable timeline.

    Parameters
    ----------
    output_format:
        "rich"  — full colour/styled Rich output (default)
        "text"  — plain text, no ANSI codes
    show_full_content:
        If True, tool results and message content are printed in full.
        If False (default), long content is truncated at max_content_chars.
    max_content_chars:
        Maximum characters of content to show per event when truncating.
    """

    def __init__(
        self,
        output_format: Literal["rich", "text"] = "rich",
        show_full_content: bool = False,
        max_content_chars: int = 200,
    ) -> None:
        self.output_format = output_format
        self.show_full_content = show_full_content
        self.max_content_chars = max_content_chars
        self._console = Console(
            highlight=False,
            markup=True,
            no_color=(output_format == "text"),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, session: AgentSession) -> None:
        """Print the session timeline to stdout."""
        self._render_header(session)
        for event in session.events:
            self._render_event(event)
        self._render_footer(session)

    def render_to_string(self, session: AgentSession) -> str:
        """Return the rendered timeline as a string."""
        with self._console.capture() as capture:
            self.render(session)
        return capture.get()

    # ------------------------------------------------------------------
    # Header / footer
    # ------------------------------------------------------------------

    def _render_header(self, session: AgentSession) -> None:
        duration = self._format_duration(session.duration_ms)
        event_count = len(session.events)
        header = (
            f"[bold]Session:[/bold] {session.session_id}\n"
            f"[bold]Agent:[/bold]   {session.agent_name}  "
            f"│  [bold]Duration:[/bold] {duration}  "
            f"│  [bold]Events:[/bold] {event_count}"
        )
        self._console.print(Panel(header, expand=False, border_style="blue"))

    def _render_footer(self, session: AgentSession) -> None:
        if session.summary is None:
            return

        s = session.summary
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold")
        table.add_column()

        table.add_row("Duration:", self._format_duration(session.duration_ms))
        table.add_row(
            "Total events:",
            (
                f"{s.total_events}  "
                f"({s.tool_calls} tool calls, {s.artifacts_produced} artifacts, "
                f"{s.tool_failures} failures)"
            ),
        )
        table.add_row(
            "Tokens:",
            f"{s.token_input_total:,} input  /  {s.token_output_total:,} output",
        )

        self._console.print(Panel(table, title="SESSION SUMMARY", border_style="green", expand=False))

    # ------------------------------------------------------------------
    # Per-event rendering
    # ------------------------------------------------------------------

    def _render_event(self, event: SessionEvent) -> None:
        ts = event.ts.strftime("%H:%M:%S")

        if event.type == EventType.message:
            self._render_message(ts, event)
        elif event.type == EventType.tool_call:
            self._render_tool_call(ts, event)
        elif event.type == EventType.tool_result:
            self._render_tool_result(ts, event)
        elif event.type == EventType.artifact:
            self._render_artifact(ts, event)
        elif event.type == EventType.error:
            self._render_error(ts, event)

    def _render_message(self, ts: str, event: SessionEvent) -> None:
        assert isinstance(event.payload, MessagePayload)
        p = event.payload

        role_label = p.role.upper()
        role_style = {
            "user": "cyan bold",
            "assistant": "green bold",
            "system": "yellow bold",
        }.get(p.role, "white bold")

        token_info = ""
        if p.token_counts is not None:
            token_info = f"[dim]{p.token_counts.output} tok out[/dim]"

        content = self._truncate(p.content)
        self._console.print(
            f"[dim]{ts}[/dim]  [{role_style}]{role_label}[/{role_style]}  {token_info}\n"
            f"          {content}\n"
        )

    def _render_tool_call(self, ts: str, event: SessionEvent) -> None:
        assert isinstance(event.payload, ToolCallPayload)
        p = event.payload

        args_preview = "  ".join(f"[dim]{k}:[/dim] {self._truncate(str(v), 60)}" for k, v in p.args.items())
        self._console.print(
            f"[dim]{ts}[/dim]  [bold yellow]▶ tool_call[/bold yellow]  [bold]{p.tool}[/bold]\n"
            f"          │  {args_preview}"
        )

    def _render_tool_result(self, ts: str, event: SessionEvent) -> None:
        assert isinstance(event.payload, ToolResultPayload)
        p = event.payload

        if p.error or (p.exit_code is not None and p.exit_code != 0):
            icon = "[bold red]✗ tool_result[/bold red]"
        else:
            icon = "[bold green]✓ tool_result[/bold green]"

        result_preview = self._truncate(str(p.result)) if p.result is not None else ""
        exit_info = f"  exit_code: {p.exit_code}" if p.exit_code is not None else ""
        error_info = f"\n          │  [red]{p.error}[/red]" if p.error else ""

        self._console.print(
            f"[dim]{ts}[/dim]  {icon}  [bold]{p.tool}[/bold]  [dim]{p.duration_ms:,} ms[/dim]\n"
            f"          │  {result_preview}{exit_info}{error_info}"
        )

    def _render_artifact(self, ts: str, event: SessionEvent) -> None:
        assert isinstance(event.payload, ArtifactPayload)
        p = event.payload

        size = f"  ({p.size_bytes:,} bytes)" if p.size_bytes is not None else ""
        desc = f"\n             [dim]{p.description}[/dim]" if p.description else ""
        path_or_id = p.path or p.artifact_id

        self._console.print(
            f"          [bold magenta]📄 ARTIFACT[/bold magenta]  {path_or_id}{size}{desc}\n"
        )

    def _render_error(self, ts: str, event: SessionEvent) -> None:
        assert isinstance(event.payload, ErrorPayload)
        p = event.payload

        recoverable_tag = "[dim](recoverable)[/dim]" if p.recoverable else "[bold red](fatal)[/bold red]"
        self._console.print(
            f"[dim]{ts}[/dim]  [bold red]⚠ ERROR[/bold red]  {recoverable_tag}\n"
            f"          │  [red]{p.message}[/red]\n"
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _truncate(self, text: str, limit: int | None = None) -> str:
        if self.show_full_content:
            return text
        limit = limit or self.max_content_chars
        if len(text) > limit:
            return text[:limit] + "[dim]…[/dim]"
        return text

    @staticmethod
    def _format_duration(duration_ms: int | None) -> str:
        if duration_ms is None:
            return "—"
        seconds = duration_ms // 1000
        if seconds < 60:
            return f"{seconds}s"
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes}m {seconds}s"
