from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from core.models import ExecutionRequest, Session


class SessionManager:
    """Create and persist session metadata and log files."""

    def __init__(self, base_dir: Path = Path("logs")) -> None:
        self.base_dir = base_dir

    def create_session(self, request: ExecutionRequest) -> Session:
        request.validate()
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        root = self.base_dir / timestamp
        root.mkdir(parents=True, exist_ok=True)
        session = Session(root=root, started_at=datetime.utcnow())
        self._write_metadata(session, request)
        return session

    def _write_metadata(self, session: Session, request: ExecutionRequest) -> None:
        payload = {
            "command": request.command_config.command,
            "config": str(request.command_config.config_path) if request.command_config.config_path else None,
            "extra_args": request.command_config.extra_args,
            "working_dir": str(request.working_dir),
            "environment": request.environment,
            "started_at": session.started_at.isoformat(),
        }
        session.metadata_path.write_text(json.dumps(payload, indent=2))

    def append_output(self, session: Session, stdout: Optional[str] = None, stderr: Optional[str] = None) -> None:
        if stdout:
            session.stdout_path.write_text(stdout, encoding="utf-8")
        if stderr:
            session.stderr_path.write_text(stderr, encoding="utf-8")
