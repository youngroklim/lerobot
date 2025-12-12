from pathlib import Path

import pytest

from core.models import CommandConfig
from core.planner import CommandPlanner


def test_build_args_adds_config(tmp_path: Path) -> None:
    config_file = tmp_path / "config.yaml"
    config_file.write_text("sample: true")
    planner = CommandPlanner()
    config = CommandConfig(command="lerobot-record", config_path=config_file, extra_args=["--foo", "bar"])

    args = planner.build_args(config)

    assert args == ["lerobot-record", "--config", str(config_file), "--foo", "bar"]


def test_build_args_rejects_unknown_command() -> None:
    planner = CommandPlanner()
    config = CommandConfig(command="invalid-command")

    with pytest.raises(ValueError):
        planner.build_args(config)


def test_build_args_allow_find_port_without_config() -> None:
    planner = CommandPlanner()
    config = CommandConfig(command="lerobot-find-port", extra_args=["--list"])

    args = planner.build_args(config)

    assert args == ["lerobot-find-port", "--list"]
