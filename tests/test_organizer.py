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

def test_unique_filename_when_multiple_duplicates(tmp_path: Path):
    """Multiple duplicates should continue incrementing."""
    organizer = FileOrganizer(tmp_path)

    pdf_folder = tmp_path / "PDF"
    pdf_folder.mkdir()

    (pdf_folder / "invoice.pdf").write_text("1")
    (pdf_folder / "invoice (1).pdf").write_text("2")
    (pdf_folder / "invoice (2).pdf").write_text("3")

    destination = organizer.get_unique_destination(
        pdf_folder / "invoice.pdf"
    )

    assert destination.name == "invoice (3).pdf"


def test_organize_files(tmp_path: Path):
    """Files should be moved into their correct categories."""
    pdf_file = tmp_path / "invoice.pdf"
    image_file = tmp_path / "photo.jpg"
    text_file = tmp_path / "notes.txt"

    pdf_file.write_text("invoice")
    image_file.write_text("image")
    text_file.write_text("notes")

    organizer = FileOrganizer(tmp_path)

    report = organizer.organize()

    assert report["scanned"] == 3
    assert report["moved"] == 3

    assert (tmp_path / "PDF" / "invoice.pdf").exists()
    assert (tmp_path / "Images" / "photo.jpg").exists()
    assert (tmp_path / "Documents" / "notes.txt").exists()