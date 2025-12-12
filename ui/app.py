from __future__ import annotations

import queue
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from adapters.lerobot_runner import LeRobotRunner
from core.models import CommandConfig, ExecutionRequest, SUPPORTED_COMMANDS


class Application(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("LeRobot GUI Runner")
        self.geometry("640x480")

        self.runner = LeRobotRunner()
        self.log_queue: "queue.Queue[str]" = queue.Queue()

        self._build_form()
        self._build_log_area()
        self.after(50, self._poll_logs)

    def _build_form(self) -> None:
        frame = ttk.Frame(self)
        frame.pack(padx=12, pady=12, fill=tk.X)

        ttk.Label(frame, text="Command").grid(row=0, column=0, sticky=tk.W)
        self.command_var = tk.StringVar(value=SUPPORTED_COMMANDS[0])
        ttk.Combobox(frame, textvariable=self.command_var, values=SUPPORTED_COMMANDS, state="readonly").grid(
            row=0, column=1, sticky=tk.EW
        )

        ttk.Label(frame, text="Config path").grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        self.config_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.config_var).grid(row=1, column=1, sticky=tk.EW, pady=(8, 0))

        ttk.Label(frame, text="Working dir").grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        self.working_dir_var = tk.StringVar(value=str(Path.cwd()))
        ttk.Entry(frame, textvariable=self.working_dir_var).grid(row=2, column=1, sticky=tk.EW, pady=(8, 0))

        frame.columnconfigure(1, weight=1)

        buttons = ttk.Frame(frame)
        buttons.grid(row=3, column=0, columnspan=2, sticky=tk.E, pady=(12, 0))
        ttk.Button(buttons, text="Start", command=self.start).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons, text="Stop", command=self.stop).pack(side=tk.LEFT)

    def _build_log_area(self) -> None:
        self.log_text = tk.Text(self, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        self.log_text.configure(state=tk.DISABLED)

    def start(self) -> None:
        try:
            config_path = Path(self.config_var.get()) if self.config_var.get() else None
            working_dir = Path(self.working_dir_var.get())
            command_config = CommandConfig(command=self.command_var.get(), config_path=config_path)
            request = ExecutionRequest(command_config=command_config, working_dir=working_dir)
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.delete("1.0", tk.END)
            self.log_text.configure(state=tk.DISABLED)
            self.runner.start(request, on_stdout=self._enqueue_log, on_stderr=self._enqueue_log, on_exit=self._on_exit)
        except Exception as exc:  # noqa: BLE001 - surface errors to the user without crashing
            self._append_log(f"Error: {exc}\n")

    def stop(self) -> None:
        self.runner.stop()

    def _enqueue_log(self, text: str) -> None:
        self.log_queue.put(text)

    def _append_log(self, text: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)

    def _poll_logs(self) -> None:
        try:
            while True:
                text = self.log_queue.get_nowait()
                self._append_log(text)
        except queue.Empty:
            pass
        self.after(50, self._poll_logs)

    def _on_exit(self, code: int, duration: float) -> None:
        self._append_log(f"\nProcess exited with code {code} after {duration:.2f}s\n")


def main() -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
