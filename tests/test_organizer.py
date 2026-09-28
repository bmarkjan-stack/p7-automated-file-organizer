"""
Tests for the Automated File Organizer.
"""

from pathlib import Path

import pytest

from organizer.categories import get_category, merge_categories
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


def test_recursive_organizes_subfolders(tmp_path: Path):
    """With recursive=True, files in subfolders should be pulled up and sorted."""
    (tmp_path / "sub").mkdir()
    (tmp_path / "top.pdf").write_text("a")
    (tmp_path / "sub" / "nested.jpg").write_text("b")

    organizer = FileOrganizer(tmp_path, recursive=True)
    report = organizer.organize()

    assert report["moved"] == 2
    assert (tmp_path / "PDF" / "top.pdf").exists()
    assert (tmp_path / "Images" / "nested.jpg").exists()


def test_recursive_does_not_rescan_category_folders(tmp_path: Path):
    """A second recursive run shouldn't re-move already-organized files."""
    (tmp_path / "a.pdf").write_text("a")
    FileOrganizer(tmp_path, recursive=True).organize()

    second_report = FileOrganizer(tmp_path, recursive=True).organize()

    assert second_report["moved"] == 0


def test_non_recursive_ignores_subfolders(tmp_path: Path):
    """Without recursive, only top-level files should be scanned."""
    (tmp_path / "sub").mkdir()
    (tmp_path / "top.pdf").write_text("a")
    (tmp_path / "sub" / "nested.jpg").write_text("b")

    organizer = FileOrganizer(tmp_path)
    report = organizer.organize()

    assert report["scanned"] == 1
    assert report["moved"] == 1
    assert (tmp_path / "sub" / "nested.jpg").exists()


def test_exclude_extension(tmp_path: Path):
    """Files matching an excluded extension should be left in place."""
    (tmp_path / "keep.pdf").write_text("a")
    (tmp_path / "skip.tmp").write_text("b")

    organizer = FileOrganizer(tmp_path, exclude=[".tmp"])
    report = organizer.organize()

    assert report["moved"] == 1
    assert report["excluded"] == 1
    assert (tmp_path / "skip.tmp").exists()
    assert (tmp_path / "PDF" / "keep.pdf").exists()


def test_exclude_glob_pattern(tmp_path: Path):
    """Glob-style exclude patterns should also be respected."""
    (tmp_path / "~$lock.docx").write_text("a")
    (tmp_path / "report.docx").write_text("b")

    organizer = FileOrganizer(tmp_path, exclude=["~$*"])
    report = organizer.organize()

    assert report["excluded"] == 1
    assert (tmp_path / "~$lock.docx").exists()
    assert (tmp_path / "Documents" / "report.docx").exists()


def test_date_strategy_groups_by_year_and_month(tmp_path: Path):
    """The date strategy should file items under Year/Month folders."""
    (tmp_path / "a.txt").write_text("x")

    organizer = FileOrganizer(tmp_path, strategy="date")
    organizer.organize()

    matches = list(tmp_path.glob("*/*/a.txt"))
    assert len(matches) == 1


def test_size_strategy_buckets_small_files(tmp_path: Path):
    """The size strategy should put small files in the 'Small' bucket."""
    (tmp_path / "tiny.bin").write_bytes(b"0" * 10)

    organizer = FileOrganizer(tmp_path, strategy="size")
    organizer.organize()

    assert (tmp_path / "Small (Under 1MB)" / "tiny.bin").exists()


def test_invalid_strategy_raises():
    """An unknown strategy name should fail fast with a clear error."""
    with pytest.raises(ValueError):
        FileOrganizer(Path("."), strategy="alphabetical")


def test_hash_duplicates_skips_identical_content(tmp_path: Path):
    """With hash_duplicates=True, a byte-identical file should be skipped, not renamed."""
    (tmp_path / "a.txt").write_text("same content")
    (tmp_path / "b.txt").write_text("same content")

    organizer = FileOrganizer(tmp_path, hash_duplicates=True)
    report = organizer.organize()

    assert report["moved"] == 1
    assert report["duplicate_content_skipped"] == 1
    assert len(list((tmp_path / "Documents").iterdir())) == 1


def test_hash_duplicates_still_moves_different_content(tmp_path: Path):
    """Files with the same name-collision risk but different content aren't skipped."""
    (tmp_path / "a.txt").write_text("content one")
    (tmp_path / "b.txt").write_text("content two")

    organizer = FileOrganizer(tmp_path, hash_duplicates=True)
    report = organizer.organize()

    assert report["moved"] == 2
    assert report["duplicate_content_skipped"] == 0


def test_custom_categories_are_used(tmp_path: Path):
    """Custom categories passed in should override the built-in mapping."""
    (tmp_path / "script.py").write_text("print('hi')")

    categories = merge_categories({"Code": [".py"]})
    organizer = FileOrganizer(tmp_path, categories=categories)
    organizer.organize()

    assert (tmp_path / "Code" / "script.py").exists()