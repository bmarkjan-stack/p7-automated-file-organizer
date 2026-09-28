"""
Core file organizing functionality.
"""

from __future__ import annotations

import fnmatch
import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path

from . import undo
from .categories import FILE_CATEGORIES, get_category

VALID_STRATEGIES = ("extension", "date", "size")


class FileOrganizer:
    """
    Organizes files into folders based on their extension, modified date,
    or size, with optional recursion, exclusion rules, and duplicate
    content detection. Every real run is recorded so it can be undone.
    """

    def __init__(
        self,
        directory: str | Path,
        logger=None,
        recursive: bool = False,
        strategy: str = "extension",
        categories: dict | None = None,
        exclude: list[str] | None = None,
        hash_duplicates: bool = False,
        log_dir: str | Path | None = None,
        history_path: str | Path | None = None,
    ):
        if strategy not in VALID_STRATEGIES:
            raise ValueError(
                f"Unknown strategy '{strategy}'. Expected one of: {', '.join(VALID_STRATEGIES)}"
            )

        self.directory = Path(directory)
        self.logger = logger
        self.recursive = recursive
        self.strategy = strategy
        self.categories = categories
        self.exclude = exclude or []
        self.hash_duplicates = hash_duplicates
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.history_path = Path(history_path) if history_path else undo.get_history_path(self.log_dir)

        self.report = {
            "scanned": 0,
            "moved": 0,
            "duplicates": 0,
            "duplicate_content_skipped": 0,
            "excluded": 0,
            "skipped": 0,
            "errors": 0,
        }

        self._hash_cache: dict[Path, dict[str, Path]] = {}
        self._session_moves: list[dict] = []

    # -- validation & scanning -------------------------------------------------

    def validate_directory(self) -> None:
        if not self.directory.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {self.directory}"
            )

        if not self.directory.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {self.directory}"
            )

    def _skip_folder_names(self) -> set[str]:
        """
        Folder names to not descend into during a recursive scan: the
        organizer's own category folders (built-in + custom), so a
        second run doesn't re-scan files it already sorted.
        """
        categories = self.categories if self.categories is not None else FILE_CATEGORIES
        return set(categories.keys()) | {"Other"}

    def scan_directory(self) -> list[Path]:
        files: list[Path] = []

        try:
            if self.recursive:
                skip_names = self._skip_folder_names()
                skip_log_dir = self.log_dir.resolve() if self.log_dir else None

                for root, dirs, filenames in os.walk(self.directory):
                    root_path = Path(root)
                    dirs[:] = [
                        name for name in dirs
                        if name not in skip_names
                        and not name.startswith(".")
                        and (root_path / name).resolve() != skip_log_dir
                    ]

                    for name in filenames:
                        files.append(root_path / name)
            else:
                for item in self.directory.iterdir():
                    if item.is_file():
                        files.append(item)
        except PermissionError as error:
            self.report["errors"] += 1

            if self.logger:
                self.logger.error(
                    "Permission denied while scanning %s: %s",
                    self.directory,
                    error,
                )

        self.report["scanned"] = len(files)

        return files

    # -- exclusion & categorization ---------------------------------------------

    def _is_excluded(self, file_path: Path) -> bool:
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()

        for pattern in self.exclude:
            pattern = pattern.strip().lower()

            if not pattern:
                continue

            if pattern.startswith(".") and "*" not in pattern and "?" not in pattern:
                if suffix == pattern:
                    return True
            elif fnmatch.fnmatch(name, pattern):
                return True

        return False

    def _category_for_file(self, file_path: Path) -> str:
        if self.strategy == "date":
            try:
                modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            except OSError:
                return "Unknown Date"
            return f"{modified.year}/{modified.strftime('%m - %B')}"

        if self.strategy == "size":
            try:
                size = file_path.stat().st_size
            except OSError:
                return "Unknown Size"

            if size < 1_000_000:
                return "Small (Under 1MB)"
            if size < 100_000_000:
                return "Medium (1-100MB)"
            return "Large (Over 100MB)"

        return get_category(file_path.suffix, self.categories)

    def plan_moves(self) -> list[tuple[Path, str]]:
        """
        Scan and categorize files without touching the filesystem. Used for
        dry-run previews and to check "is there anything to do" before a
        real run. Populates report['scanned'] and report['excluded'].
        """
        self.validate_directory()

        files = self.scan_directory()
        plan = []

        for file_path in files:
            if self._is_excluded(file_path):
                self.report["excluded"] += 1

                if self.logger:
                    self.logger.info("Excluded: %s", file_path)

                continue

            plan.append((file_path, self._category_for_file(file_path)))

        return plan

    # -- moving files -------------------------------------------------------

    def create_category_folder(self, category: str) -> Path:
        category_folder = self.directory / category
        category_folder.mkdir(parents=True, exist_ok=True)

        return category_folder

    def get_unique_destination(self, destination: Path) -> Path:
        if not destination.exists():
            return destination

        counter = 1

        while True:
            new_name = (
                f"{destination.stem} ({counter})"
                f"{destination.suffix}"
            )

            new_destination = destination.with_name(new_name)

            if not new_destination.exists():
                return new_destination

            counter += 1

    @staticmethod
    def _file_hash(file_path: Path, chunk_size: int = 65536) -> str:
        hasher = hashlib.md5()

        with open(file_path, "rb") as file:
            for chunk in iter(lambda: file.read(chunk_size), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    def _hashes_in_folder(self, folder: Path) -> dict[str, Path]:
        """Lazily hash existing files directly inside a folder, once per run."""
        if folder not in self._hash_cache:
            hashes: dict[str, Path] = {}

            if folder.exists():
                for existing in folder.iterdir():
                    if existing.is_file():
                        try:
                            hashes[self._file_hash(existing)] = existing
                        except OSError:
                            continue

            self._hash_cache[folder] = hashes

        return self._hash_cache[folder]

    def move_file(self, file_path: Path) -> bool:
        try:
            category = self._category_for_file(file_path)
            destination_folder = self.create_category_folder(category)
            destination = destination_folder / file_path.name

            if self.hash_duplicates:
                try:
                    file_hash = self._file_hash(file_path)
                except OSError:
                    file_hash = None

                if file_hash is not None:
                    existing_hashes = self._hashes_in_folder(destination_folder)
                    match = existing_hashes.get(file_hash)

                    if match is not None and match != file_path:
                        self.report["duplicate_content_skipped"] += 1

                        if self.logger:
                            self.logger.info(
                                "Duplicate content skipped: %s (matches %s)",
                                file_path,
                                match,
                            )

                        return False
            else:
                file_hash = None

            if destination.exists():
                self.report["duplicates"] += 1

                destination = self.get_unique_destination(destination)

                if self.logger:
                    self.logger.info(
                        "Duplicate detected: %s -> %s",
                        file_path.name,
                        destination.name,
                    )

            shutil.move(str(file_path), str(destination))

            self.report["moved"] += 1
            self._session_moves.append({"src": str(file_path), "dest": str(destination)})

            if self.hash_duplicates and file_hash is not None:
                self._hashes_in_folder(destination_folder)[file_hash] = destination

            if self.logger:
                self.logger.info(
                    "Moved: %s -> %s",
                    file_path,
                    destination,
                )

            return True

        except PermissionError as error:
            self.report["errors"] += 1

            if self.logger:
                self.logger.error(
                    "Permission denied: %s - %s",
                    file_path,
                    error,
                )

            return False

        except OSError as error:
            self.report["errors"] += 1

            if self.logger:
                self.logger.error(
                    "Could not move %s: %s",
                    file_path,
                    error,
                )

            return False

    def organize(self) -> dict:
        plan = self.plan_moves()
        self._session_moves = []

        for file_path, _category in plan:
            self.move_file(file_path)

        if self._session_moves:
            undo.record_session(
                self.history_path,
                self.directory,
                self._session_moves,
                datetime.now().isoformat(timespec="seconds"),
            )

        return self.report