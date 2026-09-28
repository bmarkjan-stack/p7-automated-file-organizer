"""
Reporting and logging functionality for the file organizer.
"""

import logging
from pathlib import Path
from typing import Iterable

def setup_logger(log_directory: Path) -> logging.Logger:
    log_directory.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("file_organizer")

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    log_file = log_directory / "organizer.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def print_report(report: dict) -> None:
    print("\n" + "=" * 50)
    print("FILE ORGANIZER REPORT")
    print("=" * 50)

    print(f"Files scanned      : {report['scanned']}")
    print(f"Files moved        : {report['moved']}")
    print(f"Renamed duplicates : {report['duplicates']}")

    if "duplicate_content_skipped" in report:
        print(f"Duplicate content  : {report['duplicate_content_skipped']}")

    if "excluded" in report:
        print(f"Excluded           : {report['excluded']}")

    print(f"Skipped            : {report['skipped']}")
    print(f"Errors             : {report['errors']}")

    print("=" * 50)

def print_plan(plan: Iterable[tuple[Path, str]], base_directory: Path) -> None:
    """Print a dry-run preview of (file, destination category) pairs."""
    plan = list(plan)

    if not plan:
        print("No files to organize.")
        return

    for file_path, category in plan:
        try:
            display_name = file_path.relative_to(base_directory)
        except ValueError:
            display_name = file_path

        print(f"{str(display_name):<40} -> {category}/")

    print(f"\n{len(plan)} file(s) would be organized.")