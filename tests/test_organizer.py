"""
Tests for the Automated File Organizer.
"""

from pathlib import Path

from organizer.categories import get_category
from organizer.organizer import FileOrganizer


def test_pdf_category():
    """PDF files should be categorized as PDF."""
    assert get_category(".pdf") == "PDF"


def test_image_category():
    """Image files should be categorized as Images."""
    assert get_category(".jpg") == "Images"


def test_video_category():
    """Video files should be categorized as Videos."""
    assert get_category(".mp4") == "Videos"


def test_unknown_category():
    """Unknown extensions should be categorized as Other."""
    assert get_category(".xyz") == "Other"


def test_duplicate_filename(tmp_path: Path):
    """Duplicate filenames should receive a unique name."""
    organizer = FileOrganizer(tmp_path)

    pdf_folder = tmp_path / "PDF"
    pdf_folder.mkdir()

    existing_file = pdf_folder / "invoice.pdf"
    existing_file.write_text("existing")

    destination = organizer.get_unique_destination(
        existing_file
    )

    assert destination.name == "invoice (1).pdf"