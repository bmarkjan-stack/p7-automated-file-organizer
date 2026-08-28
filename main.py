"""
Command-line interface for the Automated File Organizer.
"""

import argparse
from pathlib import Path

from organizer.organizer import FileOrganizer
from organizer.reporter import print_report, setup_logger


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automatically organize files by type."
    )

    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing the files to organize.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without moving files.",
    )

    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("logs"),
        help="Directory where the log file will be stored.",
    )

    return parser.parse_args()


def dry_run(directory: Path) -> None:
    from organizer.categories import get_category

    print("\nDRY RUN - No files will be moved.\n")

    try:
        for item in directory.iterdir():
            if item.is_file():
                category = get_category(item.suffix)

                print(
                    f"{item.name:<35} -> {category}/"
                )

    except PermissionError:
        print(f"Permission denied: {directory}")


def main() -> None:
    args = parse_arguments()

    directory = args.directory

    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        return

    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}")
        return

    if args.dry_run:
        dry_run(directory)
        return

    logger = setup_logger(args.log_dir)

    organizer = FileOrganizer(
        directory=directory,
        logger=logger,
    )

    try:
        report = organizer.organize()

        print_report(report)

        print(f"\nLog file: {args.log_dir / 'organizer.log'}")

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()