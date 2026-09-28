"""
File extension categories used by the organizer.
"""

FILE_CATEGORIES = {
    "PDF": {
        ".pdf",
    },
    "Images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".webp",
        ".svg",
        ".tiff",
        ".ico",
    },
    "Videos": {
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".m4v",
    },
    "Documents": {
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".pages",
    },
    "Spreadsheets": {
        ".xls",
        ".xlsx",
        ".csv",
        ".ods",
    },
    "Presentations": {
        ".ppt",
        ".pptx",
        ".odp",
    },
    "ZIP": {
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
        ".bz2",
    },
    "Audio": {
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".ogg",
        ".m4a",
        ".wma",
    },
}


def _normalize_extension(extension: str) -> str:
    extension = extension.strip().lower()

    if extension and not extension.startswith("."):
        extension = f".{extension}"

    return extension


def merge_categories(custom: dict | None) -> dict:
    """
    Merge user-defined categories (usually loaded from config.json) on top
    of the built-in defaults.

    A custom category with the same name as a built-in one extends it.
    If a custom category claims an extension that already belongs to a
    built-in (or another custom) category, the custom mapping wins - the
    extension is moved over rather than duplicated.

    Args:
        custom: Mapping of category name -> iterable of extensions, or None.

    Returns:
        A new dict of category name -> set of extensions.
    """
    merged = {name: set(extensions) for name, extensions in FILE_CATEGORIES.items()}

    if not custom:
        return merged

    for category, extensions in custom.items():
        normalized = {_normalize_extension(ext) for ext in extensions if ext}

        for existing_extensions in merged.values():
            existing_extensions -= normalized

        merged.setdefault(category, set())
        merged[category] |= normalized

    # Drop any category left empty because all of its extensions were
    # reassigned to a custom category above.
    return {name: extensions for name, extensions in merged.items() if extensions}


def get_category(extension: str, categories: dict | None = None) -> str:
    """
    Return the category for a file extension.

    Args:
        extension: File extension such as '.pdf' or '.jpg'.
        categories: Optional custom category mapping (see merge_categories).
            Defaults to the built-in FILE_CATEGORIES.

    Returns:
        The matching category or 'Other'.
    """
    extension = extension.lower()
    categories = categories if categories is not None else FILE_CATEGORIES

    for category, extensions in categories.items():
        if extension in extensions:
            return category

    return "Other"