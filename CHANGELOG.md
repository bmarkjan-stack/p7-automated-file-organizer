# Changelog

## 2.0.0

**New**
- Tkinter GUI - launches automatically when the app is run with no arguments (i.e. when the packaged `.exe` is double-clicked). Folder picker, dry-run preview, organize, undo, category editor, and a watch-mode toggle, all in one window.
- JSON config file (`~/.file_organizer/config.json`) for custom categories, exclude patterns, a default strategy, and duplicate-content detection - editable by hand or from the GUI's "Edit Categories..." dialog. See `config.example.json`.
- `--undo` / "Undo Last" - reverses the most recent organize run using a recorded move history (`logs/move_history.json`), moving every file back to where it started.
- `--recursive` - also organizes files inside subfolders, flattening them into the top-level category folders.
- `--strategy {extension,date,size}` - organize by file type (default, unchanged), by modified date (`Year/Month`), or by file size bucket.
- `--hash-duplicates` - skip moving a file whose content already exists in the destination folder (true duplicate), instead of just renaming it. Separate from the existing filename-collision handling, which is unchanged.
- `--exclude PATTERN` (repeatable) - skip files by extension (`.tmp`) or glob pattern (`~$*`).
- `--watch` / "Start Watching" - re-organizes the folder on an interval (default 10s, configurable) until stopped.
- `--config PATH` - use an alternate config file.
- `--version`.
- PyInstaller build script (`build_scripts/`) for producing a Windows `.exe`, plus an app icon (`assets/icon.ico`).
- GitHub Actions workflow (`.github/workflows/release.yml`) that builds `FileOrganizer.exe` on a Windows runner and publishes it to GitHub Releases whenever a `v*` tag is pushed.

**Changed**
- `main.py` now opens the GUI when run with no arguments; all prior CLI usage (`python main.py <directory> [--dry-run] [--log-dir ...]`) still works exactly as before.
- The report printed after a run now also shows duplicate-content-skipped and excluded counts.

**Compatibility**
- No breaking changes to the existing CLI or `FileOrganizer`/`get_category` APIs - all original tests still pass unmodified.

## 1.0.0
- Initial release: CLI file organizer with extension-based categorization, duplicate filename handling, dry-run mode, and logging.