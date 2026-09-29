"""
Entry point for the Automated File Organizer.

Run with no arguments (e.g. by double-clicking the packaged .exe) to open
the graphical interface. Run with a directory and/or flags for the
original command-line behavior, now extended with recursion, custom
strategies, exclusions, duplicate-content detection, undo, and a watch
mode.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

from organizer.categories import merge_categories
from organizer.config import get_default_config_path, load_config
from organizer.organizer import FileOrganizer
from organizer.reporter import print_plan, print_report, setup_logger
from organizer.undo import get_history_path, undo_last_session
from organizer.version import __version__


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automatically organize files by type, date, or size."
    )

    parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        help="Directory containing the files to organize.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would happen without moving files.",
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Also include files inside subfolders.",
    )

    parser.add_argument(
        "--strategy",
        choices=["extension", "date", "size"],
        default=None,
        help="How to group files (default: from config.json, or 'extension').",
    )

    parser.add_argument(
        "--exclude",
        action="append",
        default=None,
        help="Extension (e.g. .tmp) or glob pattern (e.g. '~$*') to skip. Repeatable.",
    )

    parser.add_argument(
        "--hash-duplicates",
        dest="hash_duplicates",
        action="store_true",
        default=None,
        help="Skip files whose content already exists in the destination folder.",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"Path to config.json (default: {get_default_config_path()}).",
    )

    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("logs"),
        help="Directory where the log file and undo history will be stored.",
    )

    parser.add_argument(
        "--undo",
        action="store_true",
        help="Reverse the most recent organize run and exit.",
    )

    parser.add_argument(
        "--watch",
        action="store_true",
        help="Keep watching the directory and re-organize it on an interval.",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Seconds between passes in --watch mode (default: from config.json, or 10).",
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Force launching the graphical interface.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Automated File Organizer {__version__}",
    )

    return parser.parse_args()


def run_dry_run(organizer: FileOrganizer) -> None:
    print("\nDRY RUN - No files will be moved.\n")
    plan = organizer.plan_moves()
    print_plan(plan, organizer.directory)


def run_undo(log_dir: Path) -> None:
    logger = setup_logger(log_dir)
    result = undo_last_session(get_history_path(log_dir), logger=logger)

    if "error" in result:
        print(result["error"])
        return

    print(f"Undo complete - restored {result['restored']} file(s).")

    if result["missing"]:
        print(f"  {result['missing']} file(s) could not be found where expected.")
    if result["conflicts"]:
        print(f"  {result['conflicts']} file(s) skipped: original location now occupied.")
    if result["errors"]:
        print(f"  {result['errors']} error(s) occurred - see the log for details.")


def main() -> None:
    # Double-clicking a packaged .exe launches with no arguments - open the GUI.
    if len(sys.argv) == 1:
        from organizer.gui import run_gui
        run_gui()
        return

    args = parse_arguments()

    if args.gui:
        from organizer.gui import run_gui
        run_gui()
        return

    try:
        config = load_config(args.config)
    except ValueError as error:
        print(f"Error: {error}")
        return

    if args.undo:
        run_undo(args.log_dir)
        return

    if args.directory is None:
        print("Error: a directory is required (or run with no arguments to open the GUI).")
        return

    directory = args.directory

    if not directory.exists():
        print(f"Error: Directory does not exist: {directory}")
        return

    if not directory.is_dir():
        print(f"Error: Not a directory: {directory}")
        return

    categories = merge_categories(config.get("categories"))
    strategy = args.strategy or config.get("strategy", "extension")
    exclude = args.exclude if args.exclude is not None else config.get("exclude", [])
    hash_duplicates = (
        args.hash_duplicates if args.hash_duplicates is not None
        else config.get("hash_duplicates", False)
    )
    interval = args.interval or config.get("watch_interval", 10)

    if args.dry_run:
        organizer = FileOrganizer(
            directory=directory,
            recursive=args.recursive,
            strategy=strategy,
            categories=categories,
            exclude=exclude,
            hash_duplicates=hash_duplicates,
            log_dir=args.log_dir,
        )
        run_dry_run(organizer)
        return

    logger = setup_logger(args.log_dir)

    def build_organizer() -> FileOrganizer:
        return FileOrganizer(
            directory=directory,
            logger=logger,
            recursive=args.recursive,
            strategy=strategy,
            categories=categories,
            exclude=exclude,
            hash_duplicates=hash_duplicates,
            log_dir=args.log_dir,
        )

    if args.watch:
        from organizer.watcher import watch_folder

        print(f"Watching {directory} every {interval}s. Press Ctrl+C to stop.\n")

        try:
            watch_folder(build_organizer, interval=interval, on_run=print_report)
        except KeyboardInterrupt:
            print("\nStopped watching.")

        return

    try:
        organizer = build_organizer()
        report = organizer.organize()

        print_report(report)

        print(f"\nLog file: {args.log_dir / 'organizer.log'}")

    except (FileNotFoundError, NotADirectoryError) as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()