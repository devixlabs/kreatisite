"""Tests for the __init__ module."""

from kreatisite import __version__


def test_version_exists() -> None:
    """Test that version is defined."""
    assert __version__ is not None


def test_version_format() -> None:
    """Test that version follows semantic versioning format."""
    assert isinstance(__version__, str)
    assert len(__version__.split(".")) >= 2  # At least major.minor
