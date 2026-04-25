"""
File-based persistence for agent session records.

Sessions are stored as pretty-printed JSON files under a configurable
root directory.  The directory layout is::

    <root>/
        sessions/
            <session-id>.json
            <session-id>.json
            ...

Usage::

    from src.storage import SessionStorage
    from src.recorder import SessionRecorder

    recorder = SessionRecorder("my-session", "my-agent")
    recorder.start()
    # ... record events ...
    session = recorder.finish()

    storage = SessionStorage("records/")
    storage.save(session)

    # Later:
    session = storage.load("my-session")
"""

from __future__ import annotations

import json
from pathlib import Path

from src.schema import AgentSession


class SessionStorage:
    """
    Reads and writes AgentSession records as JSON files.

    Parameters
    ----------
    root:
        Root directory for storage.  A ``sessions/`` subdirectory is
        created automatically.
    indent:
        JSON indentation level for human-readable output.  Set to None
        for compact output.
    """

    SESSIONS_SUBDIR = "sessions"

    def __init__(self, root: str | Path, indent: int = 2) -> None:
        self.root = Path(root)
        self.sessions_dir = self.root / self.SESSIONS_SUBDIR
        self.indent = indent

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(self, session: AgentSession) -> Path:
        """
        Persist *session* to disk.

        Returns the path of the written file.
        Raises FileExistsError if a session with this ID already exists.
        """
        self._ensure_dirs()
        path = self._path_for(session.session_id)
        if path.exists():
            raise FileExistsError(
                f"Session '{session.session_id}' already exists at {path}. "
                "Use save_overwrite() to replace it."
            )
        self._write(path, session)
        return path

    def save_overwrite(self, session: AgentSession) -> Path:
        """Persist *session* to disk, overwriting any existing file."""
        self._ensure_dirs()
        path = self._path_for(session.session_id)
        self._write(path, session)
        return path

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def load(self, session_id: str) -> AgentSession:
        """
        Load a session record by ID.

        Raises FileNotFoundError if no session with this ID exists.
        """
        path = self._path_for(session_id)
        if not path.exists():
            raise FileNotFoundError(
                f"No session record found for '{session_id}' at {path}"
            )
        return self._read(path)

    def load_from_path(self, path: str | Path) -> AgentSession:
        """Load a session record from an explicit file path."""
        return self._read(Path(path))

    def list_sessions(self) -> list[str]:
        """
        Return session IDs for all stored sessions, sorted by filename
        (which is typically chronological if IDs include a date).
        """
        if not self.sessions_dir.exists():
            return []
        return sorted(
            p.stem for p in self.sessions_dir.glob("*.json")
        )

    def exists(self, session_id: str) -> bool:
        """Return True if a session with this ID is stored on disk."""
        return self._path_for(session_id).exists()

    def delete(self, session_id: str) -> None:
        """
        Delete a stored session.

        Raises FileNotFoundError if the session does not exist.
        """
        path = self._path_for(session_id)
        if not path.exists():
            raise FileNotFoundError(f"No session record found for '{session_id}'")
        path.unlink()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _path_for(self, session_id: str) -> Path:
        # Sanitise: replace path separators to prevent directory traversal.
        safe_id = session_id.replace("/", "_").replace("\\", "_")
        return self.sessions_dir / f"{safe_id}.json"

    def _ensure_dirs(self) -> None:
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _write(self, path: Path, session: AgentSession) -> None:
        data = session.model_dump(mode="json")
        path.write_text(json.dumps(data, indent=self.indent, default=str), encoding="utf-8")

    @staticmethod
    def _read(path: Path) -> AgentSession:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return AgentSession.model_validate(raw)
