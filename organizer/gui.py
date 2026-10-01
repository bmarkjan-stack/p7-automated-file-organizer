"""
Tkinter GUI for the Automated File Organizer.

Tkinter ships with the Python standard library, so this adds zero extra
dependencies and packages cleanly into a single .exe. This module is what
runs when main.py is launched with no command-line arguments (i.e. when
someone double-clicks the packaged app).
"""

from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from .categories import merge_categories
from .config import DEFAULT_CONFIG, get_default_config_path, load_config, save_config
from .organizer import FileOrganizer
from .reporter import setup_logger
from .undo import get_history_path, undo_last_session
from .version import __version__
from .watcher import watch_folder

LOG_DIR = Path("logs")


class OrganizerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"Automated File Organizer v{__version__}")
        self.root.geometry("680x560")
        self.root.minsize(600, 480)

        try:
            self.config_data = load_config()
        except ValueError as error:
            messagebox.showerror("Config error", str(error))
            self.config_data = dict(DEFAULT_CONFIG)

        self.watch_stop_event: threading.Event | None = None
        self.watch_thread: threading.Thread | None = None

        self._build_widgets()
        self._log(f"Ready. Config file: {get_default_config_path()}")

    # -- UI construction ---------------------------------------------------

    def _build_widgets(self) -> None:
        pad = {"padx": 8, "pady": 6}

        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(fill="x", **pad)

        ttk.Label(folder_frame, text="Folder:").pack(side="left")
        self.folder_var = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_var).pack(
            side="left", fill="x", expand=True, padx=6
        )
        ttk.Button(folder_frame, text="Browse...", command=self._browse).pack(side="left")

        options_frame = ttk.LabelFrame(self.root, text="Options")
        options_frame.pack(fill="x", **pad)
        options_frame.columnconfigure(2, weight=1)

        self.recursive_var = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame, text="Include subfolders", variable=self.recursive_var
        ).grid(row=0, column=0, sticky="w", padx=8, pady=4)

        self.hash_var = tk.BooleanVar(value=bool(self.config_data.get("hash_duplicates", False)))
        ttk.Checkbutton(
            options_frame, text="Skip duplicate file content", variable=self.hash_var
        ).grid(row=0, column=1, columnspan=2, sticky="w", padx=8, pady=4)

        ttk.Label(options_frame, text="Sort by:").grid(row=1, column=0, sticky="w", padx=8)
        self.strategy_var = tk.StringVar(value=self.config_data.get("strategy", "extension"))
        ttk.Combobox(
            options_frame,
            textvariable=self.strategy_var,
            values=["extension", "date", "size"],
            state="readonly",
            width=12,
        ).grid(row=1, column=1, sticky="w", padx=8, pady=4)

        ttk.Label(options_frame, text="Exclude (comma-separated):").grid(
            row=2, column=0, sticky="w", padx=8, pady=4
        )
        self.exclude_var = tk.StringVar(value=", ".join(self.config_data.get("exclude", [])))
        ttk.Entry(options_frame, textvariable=self.exclude_var).grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=8, pady=4
        )

        actions_frame = ttk.Frame(self.root)
        actions_frame.pack(fill="x", **pad)

        ttk.Button(actions_frame, text="Preview (Dry Run)", command=self._preview).pack(
            side="left", padx=4
        )
        ttk.Button(actions_frame, text="Organize", command=self._organize).pack(side="left", padx=4)
        ttk.Button(actions_frame, text="Undo Last", command=self._undo).pack(side="left", padx=4)
        ttk.Button(
            actions_frame, text="Edit Categories...", command=self._edit_categories
        ).pack(side="left", padx=4)

        self.watch_button = ttk.Button(
            actions_frame, text="Start Watching", command=self._toggle_watch
        )
        self.watch_button.pack(side="left", padx=4)

        output_frame = ttk.LabelFrame(self.root, text="Output")
        output_frame.pack(fill="both", expand=True, **pad)

        self.output = scrolledtext.ScrolledText(output_frame, wrap="word", height=18, state="disabled")
        self.output.pack(fill="both", expand=True)

        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(self.root, textvariable=self.status_var, anchor="w").pack(
            fill="x", padx=8, pady=(0, 6)
        )

    # -- small helpers -------------------------------------------------------

    def _browse(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def _log(self, message: str) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", message + "\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def _get_directory(self) -> Path | None:
        folder = self.folder_var.get().strip()

        if not folder:
            messagebox.showwarning("No folder selected", "Choose a folder first.")
            return None

        path = Path(folder)

        if not path.is_dir():
            messagebox.showerror("Invalid folder", f"Not a valid directory:\n{path}")
            return None

        return path

    def _exclude_list(self) -> list[str]:
        return [item.strip() for item in self.exclude_var.get().split(",") if item.strip()]

    def _build_organizer(self, directory: Path, logger=None) -> FileOrganizer:
        categories = merge_categories(self.config_data.get("categories"))

        return FileOrganizer(
            directory=directory,
            logger=logger,
            recursive=self.recursive_var.get(),
            strategy=self.strategy_var.get(),
            categories=categories,
            exclude=self._exclude_list(),
            hash_duplicates=self.hash_var.get(),
            log_dir=LOG_DIR,
        )

    def _run_in_background(self, target, on_done=None) -> None:
        def worker():
            try:
                result = target()
                error = None
            except Exception as exc:  # noqa: BLE001 - surface any failure to the user
                result = None
                error = exc

            def finish():
                if error is not None:
                    messagebox.showerror("Something went wrong", str(error))
                    self.status_var.set("Error - see message.")
                elif on_done:
                    on_done(result)

            self.root.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    # -- actions --------------------------------------------------------------

    def _preview(self) -> None:
        directory = self._get_directory()
        if directory is None:
            return

        self.status_var.set("Scanning...")

        def task():
            organizer = self._build_organizer(directory)
            return organizer.plan_moves(), organizer.report

        def done(result):
            plan, report = result
            self._log(f"\n--- Preview of {directory} ---")

            if not plan:
                self._log("No files to organize.")
            else:
                for file_path, category in plan:
                    try:
                        name = file_path.relative_to(directory)
                    except ValueError:
                        name = file_path
                    self._log(f"  {name}  ->  {category}/")

            self._log(f"({len(plan)} file(s) would be organized, {report.get('excluded', 0)} excluded)")
            self.status_var.set("Preview complete.")

        self._run_in_background(task, done)

    def _organize(self) -> None:
        directory = self._get_directory()
        if directory is None:
            return

        preview_organizer = self._build_organizer(directory)
        plan = preview_organizer.plan_moves()

        if not plan:
            messagebox.showinfo("Nothing to do", "No files matched - nothing will be moved.")
            return

        confirmed = messagebox.askyesno(
            "Confirm organize",
            f"This will move {len(plan)} file(s) inside:\n{directory}\n\n"
            "Files are grouped into folders based on the options above. "
            "This can be reversed afterward with 'Undo Last'. Continue?",
        )
        if not confirmed:
            return

        self.status_var.set("Organizing...")

        def task():
            logger = setup_logger(LOG_DIR)
            organizer = self._build_organizer(directory, logger=logger)
            return organizer.organize()

        def done(report):
            self._log(f"\n--- Organized {directory} ---")
            for key, value in report.items():
                self._log(f"  {key}: {value}")
            self.status_var.set("Done.")

        self._run_in_background(task, done)

    def _undo(self) -> None:
        confirmed = messagebox.askyesno(
            "Undo last organize",
            "This will move files back to where they were before the most "
            "recent organize run. Continue?",
        )
        if not confirmed:
            return

        self.status_var.set("Undoing...")

        def task():
            logger = setup_logger(LOG_DIR)
            return undo_last_session(get_history_path(LOG_DIR), logger=logger)

        def done(result):
            if "error" in result:
                self._log(f"\n{result['error']}")
            else:
                self._log(
                    "\n--- Undo complete ---\n"
                    f"  restored: {result['restored']}\n"
                    f"  missing: {result['missing']}\n"
                    f"  conflicts: {result['conflicts']}\n"
                    f"  errors: {result['errors']}"
                )
            self.status_var.set("Undo complete.")

        self._run_in_background(task, done)

    def _edit_categories(self) -> None:
        editor = tk.Toplevel(self.root)
        editor.title("Edit configuration")
        editor.geometry("520x460")
        editor.minsize(420, 320)
        editor.transient(self.root)

        ttk.Label(
            editor,
            text="Edit and save your config.json. 'categories' adds or overrides "
            "extension groups, e.g. \"Code\": [\".py\", \".js\"].",
            wraplength=490,
            justify="left",
        ).pack(side="top", fill="x", padx=8, pady=(8, 0))

        # Reserve the button row's space at the bottom FIRST. Packing order
        # matters here: an expanding ScrolledText packed before this would
        # claim its full natural size (its default is a roomy 80x24
        # characters) before this row ever gets a share of the window,
        # squeezing the buttons down to zero visible height.
        button_row = ttk.Frame(editor)
        button_row.pack(side="bottom", fill="x", padx=8, pady=8)
        ttk.Button(button_row, text="Save", command=lambda: save()).pack(side="right", padx=4)
        ttk.Button(button_row, text="Cancel", command=editor.destroy).pack(side="right")

        text = scrolledtext.ScrolledText(editor, wrap="word", width=56, height=16)
        text.pack(side="top", fill="both", expand=True, padx=8, pady=(8, 0))
        text.insert("1.0", json.dumps(self.config_data, indent=2))

        def save():
            try:
                updated = json.loads(text.get("1.0", "end"))
            except json.JSONDecodeError as error:
                messagebox.showerror("Invalid JSON", str(error))
                return

            if not isinstance(updated, dict):
                messagebox.showerror("Invalid config", "The config must be a JSON object.")
                return

            save_config(updated)
            self.config_data = load_config()
            self.strategy_var.set(self.config_data.get("strategy", "extension"))
            self.exclude_var.set(", ".join(self.config_data.get("exclude", [])))
            self.hash_var.set(bool(self.config_data.get("hash_duplicates", False)))
            self._log(f"Config saved to {get_default_config_path()}")
            editor.destroy()

        editor.lift()
        editor.focus_force()

    def _toggle_watch(self) -> None:
        if self.watch_thread and self.watch_thread.is_alive():
            self.watch_stop_event.set()
            self.watch_button.configure(text="Start Watching")
            self.status_var.set("Watching stopped.")
            self._log("\nStopped watching.")
            return

        directory = self._get_directory()
        if directory is None:
            return

        interval = int(self.config_data.get("watch_interval", 10))
        self.watch_stop_event = threading.Event()

        def on_run(report):
            self.root.after(0, lambda: self._log(f"[watch] pass complete: {report}"))

        def build():
            logger = setup_logger(LOG_DIR)
            return self._build_organizer(directory, logger=logger)

        def worker():
            watch_folder(build, interval=interval, on_run=on_run, stop_event=self.watch_stop_event)

        self.watch_thread = threading.Thread(target=worker, daemon=True)
        self.watch_thread.start()
        self.watch_button.configure(text="Stop Watching")
        self._log(f"\nWatching {directory} every {interval}s...")
        self.status_var.set("Watching...")


def run_gui() -> None:
    root = tk.Tk()
    OrganizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
