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


def get_category(extension: str) -> str:
    """
    Return the category for a file extension.

    Args:
        extension: File extension such as '.pdf' or '.jpg'.

    Returns:
        The matching category or 'Other'.
    """
    extension = extension.lower()

    for category, extensions in FILE_CATEGORIES.items():
        if extension in extensions:
            return category

    return "Other"