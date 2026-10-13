# Automated File Organizer

A Python app that sorts the files in a folder into categories. It sorts by file type, modified date, or size, and offers both a Tkinter desktop window and a command-line interface. It also builds into a standalone Windows `.exe` that runs by double-click, with no Python install required.

![Live demo of the File Organizer GUI](live-demo/file-organizer-live-demo.gif)

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [The GUI](#the-gui)
- [Command-Line Usage](#command-line-usage)
- [How Files Are Sorted](#how-files-are-sorted)
- [Configuration](#configuration)
- [Logs and Reports](#logs-and-reports)
- [Building the Windows App](#building-the-windows-app)
- [Releasing](#releasing)
- [Running the Tests](#running-the-tests)
- [Project Structure](#project-structure)
- [Error Handling](#error-handling)
- [Future Improvements](#future-improvements)
- [License](#license)
- [Author](#author)

---

## Features

- Sort files by **extension**, **modified date** (`Year/Month`), or **size** (small, medium, large)
- Create category folders and move files into them automatically
- Never overwrite a file: name clashes become `invoice (1).pdf`, `invoice (2).pdf`, and so on
- Optionally detect **duplicate content** with `--hash-duplicates`, so identical files are left alone instead of being renamed
- Skip files by extension or glob pattern, such as in-progress downloads (`.crdownload`, `~$*`)
- Scan subfolders with `--recursive`
- **Dry run** to preview every move before anything changes
- **Undo** the most recent run
- **Watch mode** that re-organizes a folder on an interval
- Custom categories and defaults in a JSON config file
- A desktop GUI that runs work in the background, so the window never freezes
- An activity log and a summary report after each run
- Packaged as a single Windows `.exe`, with the build automated by GitHub Actions on version tags

---

## Quick Start

**Just want to organize a folder by double-clicking?** Download `FileOrganizer.exe` from the repository's **Releases** page and run it. No Python needed.

**Running from source:**

```bash
python main.py                 # open the GUI
python main.py Downloads       # organize Downloads/ from the command line
```

---

## Installation

Requires **Python 3.10 or newer**. The app uses only the standard library, so there are no packages to install to run it.

```bash
git clone https://github.com/bmarkjan-stack/p7-automated-file-organizer.git
cd p7-automated-file-organizer
```

Optionally, create a virtual environment:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**Tkinter** (for the GUI) ships with the python.org installers on Windows and macOS. On Linux, install your distribution's package, for example `sudo apt install python3-tk`.

---

## The GUI

Running the app with no arguments opens the window. Double-clicking the packaged `.exe` does the same.

- **Folder:** the directory to organize, with a Browse button
- **Options:** include subfolders, skip duplicate content, sort strategy (extension, date, or size), and a comma-separated exclude list
- **Preview (Dry Run):** shows what would happen without moving anything
- **Organize:** moves the files, after a confirmation prompt
- **Undo Last:** reverses the most recent organize run
- **Edit Categories...:** opens the config file to edit custom categories, exclude patterns, and defaults, and saves the result
- **Start / Stop Watching:** re-organizes the folder on an interval in the background

Everything the app logs also goes to `logs/organizer.log`.

---

## Command-Line Usage

```bash
python main.py <directory> [options]
```

| Flag | Description |
| --- | --- |
| `directory` | Folder to organize. Omit it to open the GUI. |
| `--dry-run` | Preview only. Moves nothing. |
| `--recursive` | Also include files in subfolders. |
| `--strategy {extension,date,size}` | How to group files. Default: from the config file, or `extension`. |
| `--exclude PATTERN` | Skip an extension (`.tmp`) or glob (`~$*`). Repeatable. |
| `--hash-duplicates` | Skip files whose content already exists in the destination folder. |
| `--config PATH` | Use a different config file. |
| `--log-dir DIR` | Where the log and undo history are stored. Default: `logs`. |
| `--undo` | Reverse the most recent organize run, then exit. |
| `--watch` | Keep re-organizing the folder until stopped with Ctrl+C. |
| `--interval SECONDS` | Seconds between passes in `--watch` mode. Default: from the config file, or `10`. |
| `--gui` | Open the GUI even when other flags are given. |
| `--version` | Print the app version. |

Command-line flags always override the config file for that run.

---

## How Files Are Sorted

### Example

Before:

```text
Downloads/
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

After:

```text
Downloads/
├── PDF/
│   └── invoice.pdf
├── Images/
│   └── vacation.jpg
├── Videos/
│   └── movie.mp4
├── ZIP/
│   └── project.zip
└── Documents/
    ├── resume.docx
    └── notes.txt
```

The `test_files/` folder in this repository contains these six sample files, so you can try the app safely:

```bash
python main.py test_files --dry-run
```

### Built-in categories

| Category | Extensions |
| --- | --- |
| PDF | `.pdf` |
| Images | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.svg`, `.tiff`, `.ico` |
| Videos | `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`, `.m4v` |
| Documents | `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.pages` |
| Spreadsheets | `.xls`, `.xlsx`, `.csv`, `.ods` |
| Presentations | `.ppt`, `.pptx`, `.odp` |
| ZIP | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2` |
| Audio | `.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.m4a`, `.wma` |
| Other | Anything without a matching extension |

Add your own categories or move extensions between them in the config file (see [Configuration](#configuration)).

### Sorting strategies

```bash
python main.py Downloads                    # extension (default) -> PDF/, Images/, ...
python main.py Downloads --strategy date    # -> 2026/09 - September/
python main.py Downloads --strategy size    # -> Small (Under 1MB)/, Medium (1-100MB)/, Large (Over 100MB)/
```

The `date` strategy uses each file's modified date.

### Recursive mode

By default only the top level of the folder is scanned. With `--recursive`, files in subfolders are pulled up and sorted into the same top-level category folders. Category folders and the log directory are skipped on later scans, so running the app again doesn't reshuffle files that are already sorted.

```bash
python main.py Downloads --recursive
```

### Excluding files

Skip files that are still downloading, lock files, and similar:

```bash
python main.py Downloads --exclude .tmp --exclude "~$*" --exclude .crdownload
```

### Duplicates

- **Same name:** the organizer never overwrites. If `invoice.pdf` already exists in the destination, the new file becomes `invoice (1).pdf`, then `invoice (2).pdf`, and so on.
- **Same content (opt-in):** with `--hash-duplicates`, each file's MD5 hash is compared against files already in the destination folder. An exact copy is left where it is and counted separately in the report, instead of creating a renamed copy.

```bash
python main.py Downloads --hash-duplicates
```

### Dry run

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

---

## Undo

Each real (non-dry-run) organize pass records every move. To reverse the most recent pass:

```bash
python main.py --undo
```

or click **Undo Last** in the GUI. Each file goes back to where it started. If a file has been moved or deleted since, or something new now sits in its original spot, that one file is left alone and reported, so nothing is overwritten.

Only the most recent session can be undone.

---

## Watch Mode

Keep a folder tidy by re-organizing it on an interval:

```bash
python main.py Downloads --watch --interval 30
```

Press `Ctrl+C` to stop. In the GUI, click **Start Watching**; it keeps running in the background while you use the window. Each pass is a full organize run, so this uses a simple polling loop with no extra dependencies.

---

## Configuration

Settings live in a JSON file. The default location is:

- Windows: `C:\Users\<you>\.file_organizer\config.json`
- macOS / Linux: `~/.file_organizer/config.json`

Edit it by hand, point to another file with `--config`, or use **Edit Categories...** in the GUI. `config.example.json` in this repository is a starting point:

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

| Key | Purpose |
| --- | --- |
| `categories` | Add a new category, or add extensions to an existing one. A custom mapping overrides the built-in one for the same extension. In the example, `.jpg` and `.png` move out of `Images/` into `Screenshots/`. |
| `exclude` | Extensions or glob patterns to skip by default. A command-line `--exclude` replaces this list for that run. |
| `strategy` | Default sort strategy. |
| `hash_duplicates` | Default for duplicate-content detection. |
| `watch_interval` | Default seconds between passes in watch mode. |

Command-line flags and GUI fields take precedence over the config file for a given run.

---

## Logs and Reports

After each run, a summary is printed:

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

Each move is also written to `logs/organizer.log`:

```text
2026-08-28 13:00:12 - INFO - Moved: Downloads/invoice.pdf -> Downloads/PDF/invoice.pdf
2026-08-28 13:00:12 - INFO - Moved: Downloads/photo.jpg -> Downloads/Images/photo.jpg
```

The undo history is kept in `logs/move_history.json`. To store both somewhere else, use `--log-dir`:

```bash
python main.py Downloads --log-dir reports
```

---

## Building the Windows App

Build a double-clickable `.exe` that doesn't need Python installed.

1. On Windows, install Python 3.10 or newer and add it to your `PATH`.
2. From the project root, run:

   ```bat
   build_scripts\build_exe.bat
   ```

   This installs PyInstaller (listed in `requirements-dev.txt`) and builds `dist\FileOrganizer.exe` from `build_scripts\organizer.spec`, using the icon in `assets\icon.ico`.

3. Run `dist\FileOrganizer.exe`. It opens the GUI, and it still accepts all the command-line flags.

> PyInstaller builds for the OS it runs on, so a `.exe` must be built on Windows (or in a Windows VM). `build_scripts/build_exe.sh` builds a native app on macOS or Linux, but it does not produce a `.exe`.

---

## Releasing

`FileOrganizer.exe` is a build artifact and isn't committed to the repository. A GitHub Actions workflow builds it whenever a version tag is pushed:

```bash
git tag -a vX.Y.Z -m "vX.Y.Z"
git push origin vX.Y.Z
```

The workflow in `.github/workflows/release.yml`:

1. Builds `FileOrganizer.exe` on a Windows runner.
2. Signs it with Authenticode, using a code-signing certificate stored in GitHub repository secrets. The temporary certificate file is deleted from the runner afterward.
3. Verifies the signature.
4. Attaches the signed `.exe` to a new GitHub Release for that tag.

Users can download it from the **Releases** page with no Python or Git required.

Keep the version in `organizer/version.py` and the entry in `CHANGELOG.md` in sync with the tag.

---

## Running the Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The suite (32 tests) covers:

- Categorizing by extension, including custom and overridden categories
- Renaming duplicate filenames and skipping duplicate content
- Recursive and non-recursive scanning, including that rescans don't touch already-sorted files
- Exclude patterns (extensions and globs)
- Date and size strategies
- Loading and saving the config, and validating it
- Undo: restoring files, handling conflicts safely, and reversing only the most recent session
- Report statistics

---

## Project Structure

```text
p7-automated-file-organizer/
├── organizer/
│   ├── categories.py     # extension -> category mapping and custom-category merging
│   ├── organizer.py      # scan, categorize, and move logic
│   ├── config.py         # JSON config load and save
│   ├── undo.py           # move-history recording and undo
│   ├── watcher.py        # polling-based watch loop
│   ├── gui.py            # Tkinter GUI
│   ├── reporter.py       # logging, plan printing, and reports
│   └── version.py        # single source of truth for the version number
├── tests/                # pytest suite
├── test_files/           # sample files for trying the app
├── build_scripts/
│   ├── organizer.spec    # PyInstaller spec
│   ├── build_exe.bat     # Windows build -> dist/FileOrganizer.exe
│   └── build_exe.sh      # macOS / Linux build
├── .github/workflows/
│   └── release.yml       # builds, signs, and publishes the .exe on version tags
├── assets/
│   └── icon.ico
├── live-demo/            # demo recording used in this README
├── config.example.json
├── CHANGELOG.md
├── LICENSE
├── main.py               # entry point: GUI or CLI
├── requirements.txt
└── requirements-dev.txt
```

---

## Error Handling

The app handles common file-system problems without crashing:

- Missing or invalid directories are reported with a clear message.
- Permission errors and failed moves are logged and counted in the report, and the run continues with the remaining files.
- Destination conflicts are renamed or skipped, never overwritten.
- A malformed config file is reported as an error instead of crashing the app.

---

## Future Improvements

- Scheduled organizing through the OS task scheduler, instead of the in-app watch loop
- Auto-update checks
- Exporting reports as CSV
- Colored or rich terminal output
- A system tray icon for watch mode (for example, with `pystray`)
- Packaged builds for macOS (`.app`) and Linux (AppImage)
- A proper installer (for example, Inno Setup) with a Start Menu entry and an uninstaller

---

## What This Project Demonstrates

- **Python:** functions, classes, modules and packages, type hints, exception handling, and threading
- **File handling:** `pathlib`, `shutil.move()`, directory walking, and content hashing with `hashlib`
- **Automation:** scanning, classifying, moving, deduplicating, logging, undoing, and watching folders on an interval
- **GUI:** Tkinter and `ttk`, with background work kept off the UI thread
- **CLI:** `argparse` with a full set of flags
- **Packaging and release:** PyInstaller, a custom icon, and a GitHub Actions pipeline that builds, signs, and publishes on version tags

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Author

Created as a portfolio project demonstrating practical Python automation, GUI, and packaging skills.

- GitHub: https://github.com/bmarkjan-stack
- Repository: https://github.com/bmarkjan-stack/p7-automated-file-organizer