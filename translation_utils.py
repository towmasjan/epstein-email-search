"""
Prosty moduł do tłumaczenia tekstu z angielskiego na polski.

Używa tylko deep-translator (Google Translator) - prosty i niezawodny.
"""

import hashlib
import re
from typing import Dict, Optional

import streamlit as st


def get_cache_key(text: str) -> str:
    """
    Generuje unikalny klucz cache dla tekstu używając hash MD5.

    Args:
        text: Tekst do zahashowania

    Returns:
        Hex string hash MD5
    """
    if not text:
        return hashlib.md5(b"").hexdigest()
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def split_text_into_chunks(text: str, max_length: int = 4500) -> list[str]:
    """Dzieli tekst na mniejsze fragmenty dla tłumaczenia."""
    if len(text) <= max_length:
        return [text]

    # Dzielimy na zdania
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]


def translate_text(text: str, translator=None) -> str:
    """
    Tłumaczy tekst z angielskiego na polski używając Google Translator.

    Używa cache w session state, aby nie tłumaczyć tego samego tekstu dwa razy.

    Args:
        text: Tekst do przetłumaczenia
        translator: Ignorowany (zachowany dla kompatybilności)

    Returns:
        Przetłumaczony tekst lub oryginał w przypadku błędu
    """
    if not text or not text.strip():
        return text

    # Inicjalizuj cache tłumaczeń jeśli nie istnieje
    if "translation_cache" not in st.session_state:
        st.session_state["translation_cache"] = {}

    # Sprawdź cache
    cache_key = get_cache_key(text)
    if cache_key in st.session_state["translation_cache"]:
        return st.session_state["translation_cache"][cache_key]

    # Spróbuj przetłumaczyć
    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source="en", target="pl")

        # Dla długich tekstów dzielimy na fragmenty
        if len(text) > 4500:
            chunks = split_text_into_chunks(text, max_length=4500)
            translated_chunks = []

            for chunk in chunks:
                if chunk.strip():
                    try:
                        translated_chunk = translator.translate(chunk)
                        if translated_chunk and translated_chunk.strip():
                            translated_chunks.append(translated_chunk)
                        else:
                            translated_chunks.append(chunk)
                    except Exception:
                        # W przypadku błędu użyj oryginału
                        translated_chunks.append(chunk)

            translated = " ".join(translated_chunks)
        else:
            # Krótki tekst - tłumacz całość
            translated = translator.translate(text)

        # Sprawdź czy tłumaczenie jest sensowne
        if translated and translated.strip() and translated != text:
            # Zapisz w cache
            st.session_state["translation_cache"][cache_key] = translated
            return translated

    except ImportError:
        # deep-translator nie jest zainstalowany
        pass
    except Exception:
        # W przypadku błędu zwróć oryginał
        pass

    # Jeśli wszystko zawiedzie, zwróć oryginał
    return text


def translate_with_fallback(text: str) -> str:
    """
    Alternatywna metoda tłumaczenia (alias dla translate_text).

    Zachowana dla kompatybilności z istniejącym kodem.
    """
    return translate_text(text)


def translate_query_to_english(query: str) -> str:
    """
    Tłumaczy zapytanie wyszukiwania z polskiego na angielski.

    Args:
        query: Zapytanie wyszukiwania (może być po polsku lub angielsku)

    Returns:
        Przetłumaczone zapytanie (lub oryginał jeśli już po angielsku)
    """
    if not query or not query.strip():
        return query

    # Prosta heurystyka: jeśli zapytanie zawiera głównie polskie znaki, przetłumacz
    polish_chars = re.compile(r"[ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]")
    has_polish = bool(polish_chars.search(query))

    if not has_polish:
        # Prawdopodobnie już po angielsku
        return query

    # Spróbuj przetłumaczyć używając Google Translator
    try:
        from deep_translator import GoogleTranslator

        translator = GoogleTranslator(source="pl", target="en")
        translated = translator.translate(query)

        # Sprawdź czy tłumaczenie jest sensowne
        if translated and translated.strip() and translated != query:
            return translated
    except Exception:
        # Jeśli tłumaczenie nie działa, zwróć oryginał
        pass

    return query


def extract_email_metadata(text: str) -> Dict[str, str]:
    """
    Wyciąga metadane z tekstu maila (data, nadawca, odbiorca, temat).

    Args:
        text: Tekst maila

    Returns:
        Słownik z metadanymi: {'date': ..., 'from': ..., 'to': ..., 'subject': ...}
    """
    metadata = {"date": "N/A", "from": "N/A", "to": "N/A", "subject": "N/A"}

    if not text:
        return metadata

    # Wzorce regex dla różnych formatów nagłówków email
    date_patterns = [
        r"Date:\s*(.+?)(?:\n|$)",
        r"Sent:\s*(.+?)(?:\n|$)",
        r"Date\s*:\s*(.+?)(?:\n|$)",
        r"On\s+(.+?)\s+wrote:",
    ]

    from_patterns = [r"From:\s*(.+?)(?:\n|$)", r"Sender:\s*(.+?)(?:\n|$)", r"From\s*:\s*(.+?)(?:\n|$)"]
    to_patterns = [r"To:\s*(.+?)(?:\n|$)", r"Recipient:\s*(.+?)(?:\n|$)", r"To\s*:\s*(.+?)(?:\n|$)"]
    subject_patterns = [r"Subject:\s*(.+?)(?:\n|$)", r"Subject\s*:\s*(.+?)(?:\n|$)", r"Re:\s*(.+?)(?:\n|$)"]

    # Szukaj w pierwszych 2000 znakach (nagłówki są na początku)
    header_text = text[:2000] if len(text) > 2000 else text

    # Wyciągnij datę
    for pattern in date_patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            metadata["date"] = match.group(1).strip()
            break

    # Wyciągnij nadawcę
    for pattern in from_patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            metadata["from"] = match.group(1).strip()
            break

    # Wyciągnij odbiorcę
    for pattern in to_patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            metadata["to"] = match.group(1).strip()
            break

    # Wyciągnij temat
    for pattern in subject_patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            metadata["subject"] = match.group(1).strip()
            break

    # Oczyść metadane (usuń znaki specjalne, skróć jeśli za długie)
    for key in metadata:
        if metadata[key] != "N/A":
            metadata[key] = re.sub(r"\s+", " ", metadata[key]).strip()
            if len(metadata[key]) > 100:
                metadata[key] = metadata[key][:97] + "..."

    return metadata


def classify_content_type(text: str) -> tuple[str, str]:
    """
    Klasyfikuje typ zawartości tekstu.

    Args:
        text: Tekst do klasyfikacji

    Returns:
        Tuple (typ, etykieta) gdzie:
        - typ: 'email', 'metadata', 'json', 'other'
        - etykieta: Opisowa nazwa typu
    """
    if not text or len(text.strip()) < 10:
        return ("other", "Pusty tekst")

    text_lower = text.lower()
    text_stripped = text.strip()

    # Sprawdź czy to JSON
    if text_stripped.startswith("{") or text_stripped.startswith("["):
        if ('"' in text or "'" in text) and (":" in text or "," in text):
            return ("metadata", "📋 Metadane/JSON")

    # Sprawdź czy to wygląda jak mail
    has_email_headers = (
        bool(re.search(r"From:\s*", text, re.IGNORECASE))
        or bool(re.search(r"To:\s*", text, re.IGNORECASE))
        or bool(re.search(r"Subject:\s*", text, re.IGNORECASE))
        or bool(re.search(r"Date:\s*", text, re.IGNORECASE))
    )

    has_email_content = (
        bool(re.search(r"@", text))
        or bool(re.search(r"Dear\s+", text, re.IGNORECASE))
        or bool(re.search(r"Best regards", text, re.IGNORECASE))
        or bool(re.search(r"Sincerely", text, re.IGNORECASE))
    )

    if has_email_headers or (has_email_content and len(text) > 100):
        return ("email", "📧 Mail")

    # Sprawdź czy to metadane
    if any(keyword in text_lower for keyword in ["component", "identifier", "style", "layout", "metadata"]):
        if "{" in text or "[" in text:
            return ("metadata", "📋 Metadane")

    # Sprawdź czy to może być konfiguracja/XML
    if text_stripped.startswith("<") and ">" in text:
        return ("metadata", "📋 Konfiguracja/XML")

    return ("other", "📄 Inny dokument")


def double_validate_translation(original: str, translated: str) -> tuple[bool, Optional[str]]:
    """
    Prosta walidacja tłumaczenia.

    Args:
        original: Oryginalny tekst
        translated: Przetłumaczony tekst

    Returns:
        Tuple (is_valid, reason) - czy tłumaczenie jest poprawne i powód odrzucenia (jeśli nie)
    """
    if not translated or not isinstance(translated, str):
        return False, "Tłumaczenie nie jest stringiem"

    if not translated.strip():
        return False, "Tłumaczenie jest puste"

    # Sprawdź czy tłumaczenie różni się od oryginału
    if translated.strip().lower() == original.strip().lower():
        return False, "Tłumaczenie jest identyczne z oryginałem"

    # Sprawdź długość (nie powinno być zbyt krótkie)
    if len(translated.strip()) < len(original.strip()) * 0.3:
        return False, "Tłumaczenie jest zbyt krótkie"

    # Wszystkie walidacje przeszły
    return True, None
