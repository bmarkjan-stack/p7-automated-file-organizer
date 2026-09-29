# Automated File Organizer

A Python utility that automatically organizes files into categorized folders - by type, date, or size - with both a point-and-click GUI and a scriptable command-line interface. Packages into a standalone Windows `.exe` that anyone can double-click, no Python install required.

This project demonstrates practical Python skills including file handling, `pathlib`, classes, exception handling, logging, a GUI (Tkinter), JSON configuration, automated testing, command-line programming, and app packaging/distribution.

## Features

* Scan a directory (optionally including subfolders) for files
* Categorize files by extension, modified date, or size
* Create category folders automatically and move files into them
* Handle duplicate filenames, and optionally detect true duplicate *content*
* Skip files by extension or glob pattern (e.g. in-progress downloads)
* Undo the most recent run
* Watch a folder and auto-organize it on an interval
* Custom categories and settings via a JSON config file
* A desktop GUI, and a full CLI for scripting/automation
* Generate an activity log and an organizing report
* Dry-run mode to preview changes safely
* Package into a standalone Windows `.exe` (and installer)
* Automated test suite

## Quick start

**Just want to double-click and organize a folder?** Skip to [Building the Windows app](#building-the-windows-app), build `FileOrganizer.exe` once, then just run it - no terminal needed after that.

**Using Python directly?**

```bash
python main.py                 # opens the GUI
python main.py Downloads       # organizes Downloads/ from the command line
```

## The GUI

Running the app with no arguments (which is exactly what happens when you double-click the packaged `.exe`) opens a window with:

* **Folder** - the directory to organize, with a Browse button
* **Options** - include subfolders, skip duplicate content, sort-by strategy (extension/date/size), and a comma-separated exclude list
* **Preview (Dry Run)** - shows what would happen without moving anything
* **Organize** - moves the files, after a confirmation dialog
* **Undo Last** - reverses the most recent organize run
* **Edit Categories...** - opens the JSON config for editing custom categories, exclude patterns, and defaults, and saves it back
* **Start/Stop Watching** - keeps re-organizing the folder on an interval in the background

All actions run in a background thread so the window never freezes, and everything logged also lands in `logs/organizer.log`.

## Example

Before running the program:

```text
Downloads/
│
├── invoice.pdf
├── vacation.jpg
├── movie.mp4
├── project.zip
├── resume.docx
└── notes.txt
```

Run:

```bash
python main.py Downloads
```

The program organizes the files:

```text
Downloads/
│
├── PDF/
│   └── invoice.pdf
│
├── Images/
│   └── vacation.jpg
│
├── Videos/
│   └── movie.mp4
│
├── ZIP/
│   └── project.zip
│
├── Documents/
│   ├── resume.docx
│   └── notes.txt
```

## Supported categories (built-in)

| Category      | Example Extensions                      |
| ------------- | ---------------------------------------- |
| PDF           | `.pdf`                                   |
| Images        | `.jpg`, `.png`, `.gif`, `.webp`, `.svg`  |
| Videos        | `.mp4`, `.mkv`, `.avi`, `.mov`           |
| Documents     | `.doc`, `.docx`, `.txt`, `.rtf`          |
| Spreadsheets  | `.xls`, `.xlsx`, `.csv`                  |
| Presentations | `.ppt`, `.pptx`                          |
| ZIP           | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`     |
| Audio         | `.mp3`, `.wav`, `.flac`, `.aac`          |
| Other         | Unknown or unsupported extensions        |

Add your own or override these via the config file - see [Configuration](#configuration).

## Project Structure

```text
p7-automated-file-organizer/
│
├── organizer/
│   ├── __init__.py
│   ├── categories.py     # extension -> category mapping, custom-category merging
│   ├── organizer.py      # core scan/categorize/move logic
│   ├── config.py         # JSON config load/save
│   ├── undo.py           # move-history recording and undo
│   ├── watcher.py        # polling-based folder watch loop
│   ├── gui.py            # Tkinter GUI
│   ├── reporter.py       # logging + printed report/plan
│   └── version.py
│
├── build_scripts/
│   ├── organizer.spec    # PyInstaller spec
│   ├── build_exe.bat     # Windows build script -> dist/FileOrganizer.exe
│   └── build_exe.sh      # macOS/Linux build script
│
├── installer/
│   └── setup.iss         # Inno Setup script -> Windows installer
│
├── assets/
│   └── icon.ico           # app icon
│
├── tests/
│   ├── __init__.py
│   ├── test_organizer.py
│   ├── test_categories.py
│   ├── test_config.py
│   └── test_undo.py
│
├── config.example.json
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── README.md
├── main.py
├── requirements.txt
└── requirements-dev.txt
```

## Requirements

* Python 3.10 or newer
* Tkinter (included with the standard python.org installer on Windows/macOS; on Linux, install your distro's `python3-tk` package if it's not already present)

No external Python packages are required to **run** the app - it uses only the standard library. `requirements-dev.txt` lists what's needed to run the tests or build the `.exe`.

## Installation (running from source)

Clone the repository:

```bash
git clone https://github.com/bmarkjan-stack/p7-automated-file-organizer.git
cd p7-automated-file-organizer
```

Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Usage

**GUI:**

```bash
python main.py
```

**CLI, basic:**

```bash
python main.py <directory>
python main.py Downloads
python main.py "C:\Users\YourName\Downloads"
```

**All CLI options:**

```text
usage: main.py [-h] [--dry-run] [--recursive] [--strategy {extension,date,size}]
                [--exclude EXCLUDE] [--hash-duplicates] [--config CONFIG]
                [--log-dir LOG_DIR] [--undo] [--watch] [--interval INTERVAL]
                [--gui] [--version]
                [directory]
```

| Flag | Description |
| --- | --- |
| `directory` | Folder to organize (omit entirely to open the GUI) |
| `--dry-run` | Preview only, moves nothing |
| `--recursive` | Also include files in subfolders |
| `--strategy {extension,date,size}` | How to group files (default: from config, or `extension`) |
| `--exclude PATTERN` | Extension (`.tmp`) or glob pattern (`~$*`) to skip; repeatable |
| `--hash-duplicates` | Skip files whose content already exists in the destination folder |
| `--config PATH` | Use an alternate config.json |
| `--log-dir DIR` | Where the log file and undo history are stored (default: `logs`) |
| `--undo` | Reverse the most recent organize run and exit |
| `--watch` | Keep re-organizing the folder on an interval until stopped (Ctrl+C) |
| `--interval SECONDS` | Interval for `--watch` (default: from config, or `10`) |
| `--gui` | Force-launch the GUI even with other flags present |
| `--version` | Print the app version |

## Dry Run

Preview changes without moving anything:

```bash
python main.py Downloads --dry-run
```

```text
DRY RUN - No files will be moved.

invoice.pdf                              -> PDF/
vacation.jpg                             -> Images/
movie.mp4                                -> Videos/
project.zip                              -> ZIP/
resume.docx                              -> Documents/

5 file(s) would be organized.
```

## Recursive mode

By default only the top level of the given folder is scanned. With `--recursive`, files in subfolders are pulled up and sorted into the same top-level category folders - handy for cleaning out a Downloads folder full of nested subfolders. Category folders (and the log directory) are automatically skipped on rescans, so running it again is safe and won't re-shuffle already-sorted files.

```bash
python main.py Downloads --recursive
```

## Organizing by date or size

```bash
python main.py Downloads --strategy date   # -> Downloads/2026/09 - September/...
python main.py Downloads --strategy size   # -> Downloads/Small (Under 1MB)/...
```

## Excluding files

Skip specific extensions or filename patterns - useful for partially-downloaded files, lock files, etc.:

```bash
python main.py Downloads --exclude .tmp --exclude "~$*" --exclude .crdownload
```

## Duplicate handling

**Filename collisions** (unchanged from before): the organizer never overwrites an existing file. If the destination already has `invoice.pdf` and another `invoice.pdf` arrives, it becomes `invoice (1).pdf`, then `invoice (2).pdf`, and so on.

**Duplicate content** (new, opt-in): with `--hash-duplicates`, files are also compared by content hash. If an incoming file's content exactly matches a file already in the destination folder, it's left where it is and counted separately in the report - instead of creating a redundant renamed copy.

```bash
python main.py Downloads --hash-duplicates
```

## Undo

Every real (non-dry-run) organize pass records exactly what it moved. Reverse the most recent run:

```bash
python main.py --undo --log-dir logs
```

or click **Undo Last** in the GUI. Files are moved back to their original locations; if a file has since been moved/deleted, or something new now occupies its original spot, that one file is safely left alone and reported rather than risking an overwrite.

## Watch mode

Keep a folder tidy automatically by re-organizing it on an interval:

```bash
python main.py Downloads --watch --interval 30
```

Press `Ctrl+C` to stop (CLI), or toggle **Start/Stop Watching** in the GUI, which runs it in the background while you keep using the window.

## Configuration

Settings are stored as JSON, by default at:

* Windows: `C:\Users\<you>\.file_organizer\config.json`
* macOS/Linux: `~/.file_organizer/config.json`

Edit it directly, use `--config path/to/config.json` to point at a different file, or use **Edit Categories...** in the GUI. See `config.example.json` for a starting point:

```json
{
  "categories": {
    "Code": [".py", ".js", ".ts", ".json", ".html", ".css"],
    "Screenshots": [".jpg", ".png"]
  },
  "exclude": [".tmp", "~$*", ".crdownload", ".part"],
  "strategy": "extension",
  "hash_duplicates": false,
  "watch_interval": 10
}
```

* `categories` - add a new category, or list extensions under an existing category name to extend it. If an extension is claimed by a custom category, that takes priority over the built-in mapping (e.g. `"Screenshots": [".jpg"]` moves `.jpg` out of `Images` and into `Screenshots`).
* `exclude` - extensions or glob patterns skipped by default (overridden per-run by `--exclude`/the GUI's exclude field, if set).
* `strategy` - default sorting strategy, overridden per-run by `--strategy`.
* `hash_duplicates` - default for content-based duplicate detection.
* `watch_interval` - default seconds between passes in watch mode.

Command-line flags and GUI fields always take precedence over the config file for a given run.

## Custom Log Directory

By default, logs (and the undo history) are stored in:

```text
logs/organizer.log
logs/move_history.json
```

Specify a different location:

```bash
python main.py Downloads --log-dir reports
```

## Reports and Logging

After organizing, the application displays a summary:

```text
==================================================
FILE ORGANIZER REPORT
==================================================
Files scanned      : 6
Files moved        : 5
Renamed duplicates : 1
Duplicate content  : 0
Excluded           : 0
Skipped            : 0
Errors             : 0
==================================================
```

and records each move in `logs/organizer.log`:

```text
2026-08-28 13:00:12 - INFO - Moved: Downloads/invoice.pdf -> Downloads/PDF/invoice.pdf
2026-08-28 13:00:12 - INFO - Moved: Downloads/photo.jpg -> Downloads/Images/photo.jpg
```

## Building the Windows app

Turn this into a double-clickable `.exe` that doesn't require Python to be installed:

1. On a Windows machine, install Python 3.10+ and make sure it's on your `PATH`.
2. From the project root, run:

   ```bat
   build_scripts\build_exe.bat
   ```

   This installs PyInstaller (see `requirements-dev.txt`) and builds `dist\FileOrganizer.exe` using `build_scripts\organizer.spec` and the icon in `assets\icon.ico`.
3. Double-click `dist\FileOrganizer.exe` to launch the GUI. It also still works from a terminal with all the CLI flags above.

> PyInstaller builds for whatever OS it runs on - to get a `.exe`, the build step itself needs to run on Windows (or a Windows VM). `build_scripts/build_exe.sh` is included for building a native macOS/Linux app the same way, but it will not produce a `.exe`.

### Optional: a proper installer

For a nicer install experience (Start Menu entry, optional desktop shortcut, uninstaller) instead of handing someone a bare `.exe`:

1. Build `dist\FileOrganizer.exe` as above.
2. Install [Inno Setup](https://jrsoftware.org/isinfo.php).
3. Open `installer\setup.iss` in Inno Setup and click **Compile** (or run it via the Inno Setup command line).
4. This produces `installer\Output\FileOrganizerSetup.exe` - share that single file.

Keep the version number in `installer/setup.iss`, `organizer/version.py`, and `CHANGELOG.md` in sync when you cut a new release.

## Running Tests

Install the dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Then run:

```bash
pytest
```

The tests cover:

* File extension categorization, including custom/overridden categories
* Duplicate filename handling (renaming) and duplicate content handling (skipping)
* Recursive vs. non-recursive scanning, including that rescans don't touch already-sorted files
* Exclude patterns (extensions and globs)
* Date and size sorting strategies
* Config load/save round-tripping and validation
* Undo: restoring files, handling conflicts safely, only reversing the most recent session
* Report statistics

## Error Handling

The application handles common file-system errors including:

* Missing or invalid directories
* Permission errors
* File movement errors
* Existing destination files
* Invalid/malformed config files (reported clearly rather than crashing)

Instead of crashing unexpectedly, the application records errors and continues where possible.

## What This Project Demonstrates

### Python

* Variables and data structures, functions, classes, modules, packages, imports
* Exception handling and type hints
* Threading (background work in the GUI, the watch-mode loop)

### File Handling

* `pathlib.Path`, `Path.iterdir()` / `os.walk()`, `Path.is_file()`, `Path.mkdir()`
* File extensions, file paths, `shutil.move()`
* Content hashing with `hashlib`

### Automation

The program can automatically:

1. Scan a directory (optionally recursively, optionally on a repeating interval)
2. Detect file types, dates, or sizes
3. Create folders and move files, skipping excludes and true duplicates
4. Resolve duplicate filenames
5. Record every move so it can be undone
6. Generate a report and a log

### GUI Programming

Tkinter, `ttk` themed widgets, background threads kept off the UI thread via `root.after`, modal dialogs for confirmation and config editing.

### CLI Programming

`argparse` for command-line arguments:

```bash
python main.py Downloads --recursive --strategy date --dry-run
```

### Packaging & Distribution

PyInstaller for a single-file `.exe`, a custom app icon, and an Inno Setup script for a proper Windows installer.

## Future Improvements

* Scheduled organizing via the OS task scheduler (vs. the in-app watch loop)
* Auto-update checks
* Export reports as CSV
* Colored/rich terminal output
* System tray icon for watch mode (e.g. via `pystray`)
* Cross-platform packaged builds (macOS `.app`, Linux AppImage)

## License

This project is licensed under the MIT License.

## Author

Created as a portfolio project demonstrating practical Python automation, GUI, and packaging skills.