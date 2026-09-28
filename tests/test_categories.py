"""
Tests for custom category merging.
"""

from organizer.categories import FILE_CATEGORIES, get_category, merge_categories


def test_merge_adds_new_category():
    """A brand-new custom category should be usable alongside the built-ins."""
    categories = merge_categories({"Code": [".py", ".js"]})

    assert get_category(".py", categories) == "Code"
    assert get_category(".js", categories) == "Code"
    assert get_category(".pdf", categories) == "PDF"


def test_merge_extends_existing_category():
    """Adding extensions to a built-in category name should extend it."""
    categories = merge_categories({"Documents": [".md"]})

    assert get_category(".md", categories) == "Documents"
    assert get_category(".txt", categories) == "Documents"


def test_merge_override_wins_over_builtin():
    """If a custom category claims a built-in's extension, custom wins."""
    categories = merge_categories({"Screenshots": [".jpg"]})

    assert get_category(".jpg", categories) == "Screenshots"
    assert get_category(".png", categories) == "Images"


def test_merge_normalizes_extension_without_dot():
    """Extensions given without a leading dot should still work."""
    categories = merge_categories({"Code": ["py"]})

    assert get_category(".py", categories) == "Code"


def test_merge_none_returns_defaults():
    """Passing no custom categories should return the built-in set untouched."""
    categories = merge_categories(None)

    assert categories == {name: set(exts) for name, exts in FILE_CATEGORIES.items()}


def test_get_category_default_param():
    """get_category with no categories argument uses the built-ins."""
    assert get_category(".gif") == "Images"