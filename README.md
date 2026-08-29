# Automated File Organizer

A Python command-line utility that automatically organizes files into categorized folders based on their file extensions.

This project demonstrates practical Python skills including file handling, `pathlib`, functions, classes, exception handling, logging, automation, testing, and command-line programming.

## Features

* Scan a directory for files
* Detect file extensions automatically
* Categorize files by type
* Create category folders automatically
* Move files into the appropriate folders
* Handle duplicate filenames
* Generate an activity log
* Display an organizing report
* Support command-line arguments
* Provide a dry-run mode
* Include automated tests
* Handle common file-system errors

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

## Supported Categories

| Category      | Example Extensions                      |
| ------------- | --------------------------------------- |
| PDF           | `.pdf`                                  |
| Images        | `.jpg`, `.png`, `.gif`, `.webp`, `.svg` |
| Videos        | `.mp4`, `.mkv`, `.avi`, `.mov`          |
| Documents     | `.doc`, `.docx`, `.txt`, `.rtf`         |
| Spreadsheets  | `.xls`, `.xlsx`, `.csv`                 |
| Presentations | `.ppt`, `.pptx`                         |
| ZIP           | `.zip`, `.rar`, `.7z`, `.tar`, `.gz`    |
| Audio         | `.mp3`, `.wav`, `.flac`, `.aac`         |
| Other         | Unknown or unsupported extensions       |

## Project Structure

```text
automated-file-organizer/
│
├── organizer/
│   ├── __init__.py
│   ├── categories.py
│   ├── organizer.py
│   └── reporter.py
│
├── tests/
│   ├── __init__.py
│   └── test_organizer.py
│
├── .gitignore
├── LICENSE
├── README.md
├── main.py
└── requirements.txt
```

## Requirements

* Python 3.10 or newer
* Git
* VS Code or another code editor

No external Python packages are required for the main application because it uses Python's standard library.

## Installation

Clone the repository:

```bash
git clone https://github.com/bmarkjan-stack/p7-automated-file-organizer.git
```

Move into the project directory:

```bash
cd automated-file-organizer
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

## Usage

The basic command is:

```bash
python main.py <directory>
```

For example:

```bash
python main.py Downloads
```

You can also provide an absolute path:

```bash
python main.py "C:\Users\YourName\Downloads"
```

## Dry Run

The application includes a dry-run mode that lets you preview the changes without moving any files.

```bash
python main.py Downloads --dry-run
```

Example output:

```text
DRY RUN - No files will be moved.

invoice.pdf                         -> PDF/
vacation.jpg                        -> Images/
movie.mp4                           -> Videos/
project.zip                         -> ZIP/
resume.docx                         -> Documents/
```

This is useful when you want to verify the categorization before making changes.

## Custom Log Directory

By default, logs are stored in:

```text
logs/organizer.log
```

You can specify a different log directory:

```bash
python main.py Downloads --log-dir reports
```

## Duplicate Files

The organizer does not overwrite existing files.

For example, if the destination already contains:

```text
invoice.pdf
```

and another `invoice.pdf` is moved into the folder, it becomes:

```text
invoice (1).pdf
```

If another duplicate exists:

```text
invoice (2).pdf
```

The program continues incrementing the filename until it finds an available name.

## Reports and Logging

After organizing the files, the application displays a summary:

```text
==================================================
FILE ORGANIZER REPORT
==================================================
Files scanned : 5
Files moved   : 5
Duplicates    : 1
Skipped       : 0
Errors        : 0
==================================================
```

The application also records file operations in:

```text
logs/organizer.log
```

Example:

```text
2026-08-28 13:00:12 - INFO - Moved: Downloads/invoice.pdf -> Downloads/PDF/invoice.pdf
2026-08-28 13:00:12 - INFO - Moved: Downloads/photo.jpg -> Downloads/Images/photo.jpg
```

## Running Tests

Install `pytest` if you want to run the automated test suite:

```bash
pip install pytest
```

Then run:

```bash
pytest
```

The tests cover:

* File extension categorization
* Unknown extensions
* Duplicate filename handling
* Multiple duplicate files
* File organization
* Report statistics

## Error Handling

The application handles common file-system errors including:

* Missing directories
* Invalid directory paths
* Permission errors
* File movement errors
* Existing destination files

Instead of crashing unexpectedly, the application records errors and continues where possible.

## What This Project Demonstrates

### Python

The project demonstrates:

* Variables and data structures
* Functions
* Classes
* Modules
* Packages
* Imports
* Exception handling
* Type hints

### File Handling

The application uses:

* `pathlib.Path`
* `Path.iterdir()`
* `Path.is_file()`
* `Path.mkdir()`
* File extensions
* File paths
* `shutil.move()`

### Automation

The program can automatically:

1. Scan a directory
2. Detect file types
3. Create folders
4. Move files
5. Resolve duplicate filenames
6. Generate a report
7. Record operations in a log

### CLI Programming

The application uses Python's `argparse` module to support command-line arguments.

Example:

```bash
python main.py Downloads --dry-run
```

## Future Improvements

Possible future improvements include:

* Recursive directory scanning
* Configurable file categories
* Configuration through a JSON file
* Undo functionality
* Scheduled automatic organization
* GUI interface
* Watch a directory for new files
* Organize files by date
* Export reports as CSV
* Add colored terminal output
* Add a confirmation prompt before moving files

## License

This project is licensed under the MIT License.

## Author

Created as a portfolio project demonstrating practical Python automation and file-handling skills.
