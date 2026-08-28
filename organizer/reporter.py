"""
Reporting and logging functionality for the file organizer.
"""

import logging
from pathlib import Path


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

    print(f"Files scanned : {report['scanned']}")
    print(f"Files moved   : {report['moved']}")
    print(f"Duplicates    : {report['duplicates']}")
    print(f"Skipped       : {report['skipped']}")
    print(f"Errors        : {report['errors']}")

    print("=" * 50)