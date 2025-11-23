"""
Podstawowe testy dla aplikacji Streamlit.

Uruchom: pytest tests/ -v
"""
import sys
from pathlib import Path

import pytest

# Dodaj ścieżkę do modułów
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test czy wszystkie importy działają."""
    try:
        # Test podstawowego importu modułu
        import translation_utils  # noqa: F401

        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_classify_content_type():
    """Test klasyfikacji zawartości."""
    from translation_utils import classify_content_type

    # Test maila
    email_text = "From: test@example.com\nTo: user@example.com\nSubject: Test"
    content_type, label = classify_content_type(email_text)
    assert content_type == "email"
    assert "Mail" in label or "mail" in label.lower()

    # Test JSON/metadanych
    json_text = '{"key": "value", "component": "test"}'
    content_type, label = classify_content_type(json_text)
    assert content_type in ["metadata", "json"]

    # Test pustego tekstu
    content_type, label = classify_content_type("")
    assert content_type == "other"


def test_extract_email_metadata():
    """Test ekstrakcji metadanych z maila."""
    from translation_utils import extract_email_metadata

    text = """From: sender@example.com
To: receiver@example.com
Subject: Test Email
Date: Mon, 1 Jan 2024 12:00:00 +0000

Body text here."""

    metadata = extract_email_metadata(text)
    assert metadata["from"] != "N/A"
    assert metadata["to"] != "N/A"
    assert metadata["subject"] != "N/A"
    assert metadata["date"] != "N/A"


def test_get_cache_key():
    """Test generowania klucza cache."""
    from translation_utils import get_cache_key

    key1 = get_cache_key("test text")
    key2 = get_cache_key("test text")
    key3 = get_cache_key("different text")

    # Ten sam tekst = ten sam klucz
    assert key1 == key2

    # Różny tekst = różny klucz
    assert key1 != key3

    # Klucz nie jest pusty
    assert len(key1) > 0


def test_syntax_check():
    """Test składni plików Python."""
    import py_compile
    from pathlib import Path

    files_to_check = [Path(__file__).parent.parent / "app.py", Path(__file__).parent.parent / "translation_utils.py"]

    for file_path in files_to_check:
        if file_path.exists():
            try:
                py_compile.compile(str(file_path), doraise=True)
            except py_compile.PyCompileError as e:
                pytest.fail(f"Syntax error in {file_path}: {e}")
