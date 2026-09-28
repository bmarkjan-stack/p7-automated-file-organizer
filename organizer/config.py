"""
Configuration loading and saving for the Automated File Organizer.

Settings are stored as a plain JSON file so users can hand-edit them, or
edit them through the GUI's "Edit Categories..." dialog. When no config
file exists yet, sensible defaults are used and nothing is written to
disk until the user explicitly saves.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Stored under the user's home directory (not next to the .exe) so it
# survives reinstalls/updates and works even if the app folder is
# read-only (e.g. Program Files).
DEFAULT_CONFIG_DIR = Path.home() / ".file_organizer"
DEFAULT_CONFIG_PATH = DEFAULT_CONFIG_DIR / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    # Additional/override categories, merged on top of the built-ins.
    # Example: {"Code": [".py", ".js", ".ts", ".json"]}
    "categories": {},
    # Extensions (".tmp") or glob patterns ("~$*") to always skip.
    "exclude": [],
    # How files are grouped: "extension" | "date" | "size"
    "strategy": "extension",
    # If true, skip moving a file whose content already exists in the
    # destination folder (true duplicate), instead of just renaming it.
    "hash_duplicates": False,
    # Seconds between passes while in watch mode.
    "watch_interval": 10,
}


def get_default_config_path() -> Path:
    """Return the default location of the user's config.json."""
    return DEFAULT_CONFIG_PATH


def load_config(path: Path | None = None) -> dict[str, Any]:
    """
    Load configuration, filling in any missing keys with defaults.

    A missing config file is not an error - the defaults are returned as-is.
    A present-but-invalid config file raises ValueError so the caller can
    surface a clear message instead of silently ignoring the user's setup.
    """
    path = Path(path) if path else DEFAULT_CONFIG_PATH

    config = json.loads(json.dumps(DEFAULT_CONFIG))  # deep copy of defaults

    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as file:
                user_config = json.load(file)
        except (json.JSONDecodeError, OSError) as error:
            raise ValueError(f"Invalid config file at {path}: {error}") from error

        if not isinstance(user_config, dict):
            raise ValueError(f"Config file at {path} must contain a JSON object.")

        config.update(user_config)

    return config


def save_config(config: dict[str, Any], path: Path | None = None) -> Path:
    """Write configuration to disk, creating parent folders as needed."""
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=2)
        file.write("\n")

    return path