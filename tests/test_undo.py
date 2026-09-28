"""
Tests for the undo (reverse last organize session) functionality.
"""

from pathlib import Path

from organizer.organizer import FileOrganizer
from organizer.undo import get_history_path, undo_last_session


def test_undo_restores_moved_files(tmp_path: Path):
    """After organizing, undo should put every file back where it was."""
    (tmp_path / "invoice.pdf").write_text("a")
    (tmp_path / "photo.jpg").write_text("b")

    log_dir = tmp_path / "logs"
    organizer = FileOrganizer(tmp_path, log_dir=log_dir)
    organizer.organize()

    assert not (tmp_path / "invoice.pdf").exists()

    result = undo_last_session(get_history_path(log_dir))

    assert result["restored"] == 2
    assert result["missing"] == 0
    assert result["conflicts"] == 0
    assert (tmp_path / "invoice.pdf").exists()
    assert (tmp_path / "photo.jpg").exists()


def test_undo_with_nothing_to_undo(tmp_path: Path):
    """Undoing with no history file should return a clear error, not crash."""
    result = undo_last_session(get_history_path(tmp_path / "logs"))

    assert "error" in result


def test_undo_reports_conflict_without_overwriting(tmp_path: Path):
    """If something now occupies the original spot, undo must not overwrite it."""
    (tmp_path / "notes.txt").write_text("original")

    log_dir = tmp_path / "logs"
    organizer = FileOrganizer(tmp_path, log_dir=log_dir)
    organizer.organize()

    # Something new was created where the original file used to be.
    (tmp_path / "notes.txt").write_text("a new, unrelated file")

    result = undo_last_session(get_history_path(log_dir))

    assert result["conflicts"] == 1
    assert result["restored"] == 0
    assert (tmp_path / "notes.txt").read_text() == "a new, unrelated file"


def test_undo_only_reverses_most_recent_session(tmp_path: Path):
    """Only the last session should be undone, not earlier ones."""
    log_dir = tmp_path / "logs"

    (tmp_path / "a.pdf").write_text("1")
    FileOrganizer(tmp_path, log_dir=log_dir).organize()

    (tmp_path / "b.pdf").write_text("2")
    FileOrganizer(tmp_path, log_dir=log_dir).organize()

    result = undo_last_session(get_history_path(log_dir))

    assert result["restored"] == 1
    assert (tmp_path / "b.pdf").exists()
    assert not (tmp_path / "a.pdf").exists()
    assert (tmp_path / "PDF" / "a.pdf").exists()
