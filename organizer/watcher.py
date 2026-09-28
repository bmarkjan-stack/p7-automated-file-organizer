"""
Simple polling-based folder watcher.

Rather than depending on an external package (e.g. watchdog) just for
this, a plain interval-based poll keeps the app dependency-free and easy
to package into a single .exe. It re-runs a full organize pass every
`interval` seconds until asked to stop.
"""

from __future__ import annotations

import threading
import time
from typing import Callable, Optional


def watch_folder(
    build_organizer: Callable[[], "FileOrganizer"],  # noqa: F821 - avoid circular import
    interval: int = 10,
    on_run: Optional[Callable[[dict], None]] = None,
    stop_event: Optional[threading.Event] = None,
) -> None:
    """
    Repeatedly organize a folder every `interval` seconds until stopped.

    Args:
        build_organizer: Zero-argument callable returning a fresh
            FileOrganizer instance (a fresh instance is used each pass so
            per-run counters/report stay accurate).
        interval: Seconds to wait between passes.
        on_run: Optional callback invoked with the report dict after each pass.
        stop_event: Optional threading.Event; the loop exits once it is set.
            When omitted, the loop runs until interrupted (e.g. Ctrl+C).
    """
    while stop_event is None or not stop_event.is_set():
        organizer = build_organizer()
        report = organizer.organize()

        if on_run:
            on_run(report)

        for _ in range(max(interval, 1)):
            if stop_event is not None and stop_event.is_set():
                return
            time.sleep(1)