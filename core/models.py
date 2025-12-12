from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


SUPPORTED_COMMANDS = (
    "lerobot-record",
    "lerobot-calibrate",
    "lerobot-teleoperate",
    "lerobot-find-port",
)


@dataclass
class CommandConfig:
    """Declarative description of a LeRobot invocation."""

    command: str
    config_path: Optional[Path] = None
    extra_args: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.command not in SUPPORTED_COMMANDS:
            raise ValueError(f"Unsupported command: {self.command}")
        if self.config_path is not None and not self.config_path.exists():
            raise FileNotFoundError(f"Config path does not exist: {self.config_path}")


@dataclass
class ExecutionRequest:
    """Execution request flowing from the UI into the adapters layer."""

    command_config: CommandConfig
    working_dir: Path
    environment: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        self.command_config.validate()
        if not self.working_dir.exists():
            raise FileNotFoundError(f"Working directory does not exist: {self.working_dir}")
        if not self.working_dir.is_dir():
            raise NotADirectoryError(f"Working directory must be a directory: {self.working_dir}")


@dataclass
class Session:
    """Metadata for a single CLI session."""

    root: Path
    started_at: datetime

    @property
    def stdout_path(self) -> Path:
        return self.root / "stdout.log"

    @property
    def stderr_path(self) -> Path:
        return self.root / "stderr.log"

    @property
    def metadata_path(self) -> Path:
        return self.root / "session.json"
