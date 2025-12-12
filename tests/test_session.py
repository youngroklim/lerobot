from pathlib import Path

from core.models import CommandConfig, ExecutionRequest
from core.session import SessionManager


def test_create_session_writes_metadata(tmp_path: Path) -> None:
    working_dir = tmp_path / "work"
    working_dir.mkdir()
    manager = SessionManager(base_dir=tmp_path / "logs")
    command_config = CommandConfig(command="lerobot-calibrate")
    request = ExecutionRequest(command_config=command_config, working_dir=working_dir)

    session = manager.create_session(request)

    assert session.root.exists()
    metadata = session.metadata_path.read_text()
    assert "lerobot-calibrate" in metadata
    assert str(working_dir) in metadata
