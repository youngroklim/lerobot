# LeRobot GUI Runner

This repository hosts a GUI application that safely orchestrates LeRobot CLI commands such as `lerobot-record`, `lerobot-calibrate`, `lerobot-teleoperate`, and `lerobot-find-port`. The app keeps command execution observable and user-friendly while isolating subprocess work from UI code.

## Architecture boundaries

- `ui/` contains GUI-only code and must not spawn subprocesses directly.
- `core/` handles command planning, validation, and session modeling.
- `adapters/` is responsible for subprocess execution and OS or device interaction.
- `configs/` stores templates and defaults used by the CLI.
- `logs/` collects runtime output and should stay gitignored.

All LeRobot invocations should use subprocesses with argument lists (no shell strings), explicit working directories, captured stdout/stderr, and detailed logging of the command, environment, exit code, and duration. Each run should create a timestamped session directory. The UI thread must remain responsive with streamed logs and a stop/cancel action that attempts graceful termination before a forced kill.

### Current implementation

- `core.models` defines `CommandConfig`, `ExecutionRequest`, and session metadata.
- `core.planner` builds safe argument lists for supported LeRobot commands.
- `core.session` creates per-run session directories and writes metadata/log files.
- `adapters.lerobot_runner` executes CLI calls in a background thread with streamed output and stop/kill handling.
- `ui.app` provides a minimal Tkinter interface to pick a command, supply CLI arguments directly, set a working directory, and observe logs.

## Python and dependency rules

- Python **3.10** is the supported version.
- Use a local virtual environment at `.venv/`; never rely on system or global Python installs.
- Activate the venv before working:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows (PowerShell): `.\.venv\Scripts\Activate.ps1`
- Manage dependencies with pip only (via `requirements.txt` or `pyproject.toml`), avoiding conda or mixed toolchains.

### Local setup

Use only venv-based workflows and pip. A minimal bootstrap on macOS/Linux looks like:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python --version  # should report 3.10.x from .venv
pip install --upgrade pip
pip install -r requirements.txt  # or `pip install .` when a package is provided
```

On Windows (PowerShell), replace the activation command with `.\.venv\Scripts\Activate.ps1`. Avoid conda/mamba entirely, and do not mix multiple dependency managers.

## Running the GUI

With the virtual environment active and dependencies installed:

```bash
python -m ui.app
```

The window allows choosing a LeRobot command (including `lerobot-find-port`), entering CLI arguments directly instead of a config file, setting a working directory, and streaming stdout/stderr for the run. Use **Stop** to request termination; the runner sends a terminate signal first and escalates to kill on timeout.

## Environment validation

Before running the GUI or committing changes, verify the environment with:

```bash
python --version
python -c "import sys; print(sys.executable)"
lerobot --help
python -c "import lerobot"
```

The printed Python executable should live inside `.venv`. Fix the setup if it does not.

## Testing

Core logic should be testable without launching LeRobot. Add unit tests for argument construction, input/config validation, session directory creation, and subprocess lifecycle handling (mocked). Run the suite with:

```bash
python -m pytest
```

## Development notes

- Keep changes focused by avoiding unrelated updates in a single branch.
- Document which LeRobot commands are affected by each change and how to reproduce behavior locally.
- Preserve the CLI-first approach; future Python API integrations should be hidden behind adapters with CLI fallbacks.
- Pushes to remote repositories are performed manually; automated push steps are intentionally omitted.
