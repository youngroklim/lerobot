from __future__ import annotations

import os
import subprocess
import threading
from pathlib import Path
from time import monotonic
from typing import Callable, Iterable, List, Optional

from core.models import ExecutionRequest
from core.planner import CommandPlanner
from core.session import SessionManager


OutputHandler = Callable[[str], None]
ExitHandler = Callable[[int, float], None]


class LeRobotRunner:
    """Run LeRobot CLI commands in a background thread while streaming logs."""

    def __init__(self, planner: Optional[CommandPlanner] = None, session_manager: Optional[SessionManager] = None) -> None:
        self.planner = planner or CommandPlanner()
        self.session_manager = session_manager or SessionManager()
        self._process: Optional[subprocess.Popen[str]] = None
        self._thread: Optional[threading.Thread] = None

    def start(
        self,
        request: ExecutionRequest,
        on_stdout: Optional[OutputHandler] = None,
        on_stderr: Optional[OutputHandler] = None,
        on_exit: Optional[ExitHandler] = None,
    ) -> None:
        if self._thread and self._thread.is_alive():
            raise RuntimeError("A LeRobot process is already running")

        session = self.session_manager.create_session(request)
        args = self.planner.build_args(request.command_config)
        env = {**os.environ, **request.environment}
        start_time = monotonic()

        def _run() -> None:
            try:
                with subprocess.Popen(
                    args,
                    cwd=request.working_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True,
                ) as proc:
                    self._process = proc
                    self._stream_output(proc.stdout, on_stdout, session.stdout_path)
                    self._stream_output(proc.stderr, on_stderr, session.stderr_path)
                    proc.wait()
                    duration = monotonic() - start_time
                    if on_exit:
                        on_exit(proc.returncode, duration)
            finally:
                self._process = None

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._process is None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait()

    def _stream_output(
        self,
        pipe: Optional[Iterable[str]],
        callback: Optional[OutputHandler],
        log_path: Path,
    ) -> None:
        if pipe is None:
            return
        buffer: List[str] = []
        for chunk in pipe:
            buffer.append(chunk)
            if callback:
                callback(chunk)
        if buffer:
            log_path.write_text("".join(buffer), encoding="utf-8")
