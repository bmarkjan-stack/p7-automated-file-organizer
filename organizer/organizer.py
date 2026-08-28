"""
Core file organizing functionality.
"""

import shutil
from pathlib import Path

from .categories import get_category


class FileOrganizer:
    """
    Organizes files into folders based on their extensions.
    """
    def __init__(self, directory: str | Path, logger=None):
        self.directory = Path(directory)
        self.logger = logger

        self.report = {
            "scanned": 0,
            "moved": 0,
            "duplicates": 0,
            "skipped": 0,
            "errors": 0,
        }

    def validate_directory(self) -> None:
        if not self.directory.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {self.directory}"
            )

        if not self.directory.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {self.directory}"
            )


    def scan_directory(self) -> list[Path]:
        files = []

        try:
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

    def move_file(self, file_path: Path) -> bool:
        try:
            category = get_category(file_path.suffix)

            destination_folder = self.create_category_folder(category)
            destination = destination_folder / file_path.name

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
        self.validate_directory()

        files = self.scan_directory()

        for file_path in files:
            self.move_file(file_path)

        return self.report