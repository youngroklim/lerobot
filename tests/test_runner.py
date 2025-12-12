from __future__ import annotations

import types
from pathlib import Path
from typing import List, Optional

import adapters.lerobot_runner as runner_module
from adapters.lerobot_runner import LeRobotRunner
from core.models import CommandConfig, ExecutionRequest


class DummyProcess:
    def __init__(self) -> None:
        self.stdout = ["out1\n", "out2\n"]
        self.stderr = ["err1\n"]
        self.returncode = 0

    def wait(self, timeout: Optional[int] = None) -> int:  # noqa: ARG002
        return self.returncode

    def __enter__(self) -> "DummyProcess":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001, D401
        return None


class DummyPopen:
    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN001, D401
        self.process = DummyProcess()
        self.args = args
        self.kwargs = kwargs

    def __enter__(self) -> DummyProcess:
        return self.process

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001, D401
        return None



def test_runner_streams_output(monkeypatch, tmp_path: Path) -> None:
    working_dir = tmp_path / "work"
    working_dir.mkdir()
    command_config = CommandConfig(command="lerobot-teleoperate")
    request = ExecutionRequest(command_config=command_config, working_dir=working_dir)

    popen_calls: List[tuple] = []

    def fake_popen(*args, **kwargs):  # noqa: ANN001
        popen_calls.append((args, kwargs))
        return DummyPopen(*args, **kwargs)

    monkeypatch.setattr(runner_module.subprocess, "Popen", fake_popen)

    collected_stdout: List[str] = []
    collected_stderr: List[str] = []
    exit_payload: List[tuple] = []

    runner = LeRobotRunner()
    runner.start(
        request,
        on_stdout=collected_stdout.append,
        on_stderr=collected_stderr.append,
        on_exit=lambda code, duration: exit_payload.append((code, duration)),
    )

    # Wait for thread to finish
    runner._thread.join(timeout=2)

    assert collected_stdout == ["out1\n", "out2\n"]
    assert collected_stderr == ["err1\n"]
    assert exit_payload and exit_payload[0][0] == 0

    # Ensure subprocess was called with list args and working directory
    assert popen_calls
    args, kwargs = popen_calls[0]
    assert isinstance(args[0], list)
    assert kwargs["cwd"] == working_dir
