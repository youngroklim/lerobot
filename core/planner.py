from __future__ import annotations

from typing import List

from core.models import CommandConfig


class CommandPlanner:
    """Build sanitized argument lists for LeRobot CLI commands."""

    def __init__(self, python_executable: str = "python") -> None:
        self.python_executable = python_executable

    def build_args(self, config: CommandConfig) -> List[str]:
        """Create an argument list that can be safely passed to subprocess."""

        config.validate()
        args: List[str] = [config.command]
        if config.config_path is not None:
            args.extend(["--config", str(config.config_path)])
        args.extend(config.extra_args)
        return args
