"""
Undo support for the Automated File Organizer.

Every real (non-dry-run) organize pass records the exact source and
destination of each file it moves as a "session" in a small JSON history
file, next to the text log. Undoing pops the most recent session and
moves each file back to where it started.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

HISTORY_FILENAME = "move_history.json"


def get_history_path(log_dir: Path) -> Path:
    """Return the path to the move-history file for a given log directory."""
    return Path(log_dir) / HISTORY_FILENAME


def load_sessions(history_path: Path) -> list[dict]:
    """Load recorded organize sessions, oldest first. Missing/bad file -> []."""
    history_path = Path(history_path)

    if not history_path.exists():
        return []

    try:
        with open(history_path, "r", encoding="utf-8") as file:
            sessions = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    return sessions if isinstance(sessions, list) else []


def save_sessions(history_path: Path, sessions: list[dict]) -> None:
    """Persist the session list, creating the log directory if needed."""
    history_path = Path(history_path)
    history_path.parent.mkdir(parents=True, exist_ok=True)

    with open(history_path, "w", encoding="utf-8") as file:
        json.dump(sessions, file, indent=2)
        file.write("\n")


def record_session(history_path: Path, directory: Path, moves: list[dict], timestamp: str) -> None:
    """Append a completed organize session to the history file."""
    sessions = load_sessions(history_path)
    sessions.append(
        {
            "timestamp": timestamp,
            "directory": str(directory),
            "moves": moves,
        }
    )
    save_sessions(history_path, sessions)


def undo_last_session(history_path: Path, logger=None) -> dict:
    """
    Reverse the most recently recorded organize session, moving every file
    it touched back to its original location.

    Returns a small result dict:
        {"restored": int, "missing": int, "conflicts": int, "errors": int}
    or, if there was nothing to undo:
        {"error": "..."}

    A file is "missing" if it's no longer where the organizer left it
    (the user likely moved/renamed/deleted it since). A "conflict" means
    something now occupies the file's original spot, so restoring would
    overwrite it - that file is left in place rather than risking data
    loss, and the session is still cleared for the files that could be
    restored.
    """
    history_path = Path(history_path)
    sessions = load_sessions(history_path)

    if not sessions:
        return {"error": "No previous organize session found to undo."}

    session = sessions.pop()
    result = {"restored": 0, "missing": 0, "conflicts": 0, "errors": 0}

    for move in reversed(session.get("moves", [])):
        current_location = Path(move["dest"])
        original_location = Path(move["src"])

        if not current_location.exists():
            result["missing"] += 1
            if logger:
                logger.warning("Undo: file no longer at %s", current_location)
            continue

        if original_location.exists():
            result["conflicts"] += 1
            if logger:
                logger.warning(
                    "Undo: cannot restore %s, original location %s is occupied",
                    current_location,
                    original_location,
                )
            continue

        try:
            original_location.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current_location), str(original_location))
            result["restored"] += 1

            if logger:
                logger.info("Undo: restored %s -> %s", current_location, original_location)
        except OSError as error:
            result["errors"] += 1

            if logger:
                logger.error("Undo: failed to restore %s: %s", current_location, error)

    save_sessions(history_path, sessions)

    return result