"""
Tests for configuration loading and saving.
"""

from pathlib import Path

import pytest

from organizer.config import DEFAULT_CONFIG, load_config, save_config


def test_load_missing_config_returns_defaults(tmp_path: Path):
    """Loading a config that doesn't exist yet should return the defaults."""
    config = load_config(tmp_path / "does_not_exist.json")

    assert config["strategy"] == DEFAULT_CONFIG["strategy"]
    assert config["categories"] == {}
    assert config["exclude"] == []


def test_save_then_load_round_trip(tmp_path: Path):
    """Saved settings should come back unchanged."""
    path = tmp_path / "config.json"

    save_config(
        {
            "categories": {"Code": [".py"]},
            "exclude": [".tmp"],
            "strategy": "date",
            "hash_duplicates": True,
            "watch_interval": 30,
        },
        path,
    )

    loaded = load_config(path)

    assert loaded["categories"] == {"Code": [".py"]}
    assert loaded["exclude"] == [".tmp"]
    assert loaded["strategy"] == "date"
    assert loaded["hash_duplicates"] is True
    assert loaded["watch_interval"] == 30


def test_partial_config_fills_in_missing_defaults(tmp_path: Path):
    """A config file that only sets some keys should still have all keys."""
    path = tmp_path / "config.json"
    path.write_text('{"strategy": "size"}', encoding="utf-8")

    loaded = load_config(path)

    assert loaded["strategy"] == "size"
    assert loaded["watch_interval"] == DEFAULT_CONFIG["watch_interval"]


def test_invalid_json_raises_value_error(tmp_path: Path):
    """A malformed config file should raise a clear error, not crash silently."""
    path = tmp_path / "config.json"
    path.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(path)