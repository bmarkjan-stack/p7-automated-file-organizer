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

    def create_category_folder(self, category: str) -> Path:
        category_folder = self.directory / category
        category_folder.mkdir(parents=True, exist_ok=True)

        return category_folder