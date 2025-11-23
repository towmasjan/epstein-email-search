"""
Uproszczona wersja aplikacji do wyszukiwania maili Epsteina.

Stabilna, bez duplikacji kodu, z lepszym error handling.
"""
import re

import pandas as pd
import streamlit as st
from datasets import load_dataset

from translation_utils import (
    classify_content_type,
    double_validate_translation,
    extract_email_metadata,
    get_cache_key,
    translate_query_to_english,
    translate_text,
    translate_with_fallback,
)

# Konfiguracja strony
st.set_page_config(page_title="Akta Epsteina - Wyszukiwarka Maili", page_icon="📧", layout="wide")


# Funkcja pomocnicza do formatowania tekstu
def format_email_text(text, highlight_pattern=None, case_sensitive=False):
    """Formatuje tekst maila z podziałem na akapity i podświetleniem."""
    if not text or not text.strip():
        return ""

    # Podziel na akapity
    paragraphs = text.split("\n\n")
    if len(paragraphs) == 1:
        paragraphs = [p for p in text.split("\n") if p.strip()]

    formatted_paragraphs = []
    for para in paragraphs:
        if not para.strip():
            continue

        para = " ".join(para.split())

        # Podświetl jeśli jest wzorzec
        if highlight_pattern:
            try:
                pattern = re.compile(re.escape(highlight_pattern), re.IGNORECASE if not case_sensitive else 0)
                para = pattern.sub(
                    lambda m: f"<mark style='background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px; font-weight: bold;'>{m.group()}</mark>",
                    para,
                )
            except (re.error, Exception):
                pass

        formatted_paragraphs.append(
            f"<p style='margin-bottom: 1em; line-height: 1.6; text-align: left; word-wrap: break-word;'>{para}</p>"
        )

    return "\n".join(formatted_paragraphs)


# Funkcja do wyświetlania pojedynczego wyniku
def display_email_result(row, idx, search_query_final, case_sensitive, translation_key_prefix=""):
    """Wyświetla pojedynczy wynik maila."""
    try:
        row_text = str(row.get("text", ""))
        row_filename = str(row.get("filename", "N/A"))

        if not row_text or row_text == "nan":
            return

        # Klasyfikuj typ zawartości
        content_type, content_label = classify_content_type(row_text)

        # Wybierz ikonę
        type_badge = "📧" if content_type == "email" else ("📋" if content_type == "metadata" else "📄")

        # Wyciągnij metadane
        metadata = extract_email_metadata(row_text)

        # Zbuduj nagłówek
        metadata_parts = []
        if metadata["from"] != "N/A":
            metadata_parts.append(f"Od: {metadata['from']}")
        if metadata["to"] != "N/A":
            metadata_parts.append(f"Do: {metadata['to']}")
        if metadata["date"] != "N/A":
            metadata_parts.append(f"Data: {metadata['date']}")

        metadata_str = " | ".join(metadata_parts) if metadata_parts else ""
        occurrences = row_text.lower().count(search_query_final.lower())

        expander_title = f"{type_badge} {row_filename}"
        if content_type != "email":
            expander_title += f" [{content_label}]"
        if metadata_str:
            expander_title += f" | {metadata_str}"
        expander_title += f" ({occurrences} wystąpień)"

        with st.expander(expander_title, expanded=False):
            # Metadane
            if metadata["subject"] != "N/A" or any(
                v != "N/A" for v in [metadata["from"], metadata["to"], metadata["date"]]
            ):
                col1, col2 = st.columns(2)
                with col1:
                    if metadata["from"] != "N/A":
                        st.markdown(f"**📤 Od:** `{metadata['from'][:50]}{'...' if len(metadata['from']) > 50 else ''}`")
                    if metadata["to"] != "N/A":
                        st.markdown(f"**📥 Do:** `{metadata['to'][:50]}{'...' if len(metadata['to']) > 50 else ''}`")
                with col2:
                    if metadata["date"] != "N/A":
                        st.markdown(f"**📅 Data:** `{metadata['date']}`")
                    if metadata["subject"] != "N/A":
                        st.markdown(
                            f"**📌 Temat:** `{metadata['subject'][:50]}{'...' if len(metadata['subject']) > 50 else ''}`"
                        )
                st.divider()

            # Informacja o typie dla nie-maili
            if content_type != "email":
                st.info(f"ℹ️ **Typ zawartości:** {content_label}")
                st.divider()

            # Oryginalny tekst
            st.markdown("**🇬🇧 Oryginał (angielski):**")
            display_text = row_text[:5000] if len(row_text) > 5000 else row_text

            formatted_text = format_email_text(
                display_text,
                highlight_pattern=search_query_final if search_query_final.lower() in row_text.lower() else None,
                case_sensitive=case_sensitive,
            )

            st.markdown(
                f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #1f77b4; max-height: 500px; overflow-y: auto;'>{formatted_text}</div>",
                unsafe_allow_html=True,
            )

            if len(row_text) > 5000:
                st.caption("⚠️ Wyświetlono pierwsze 5000 znaków. Kliknij 'Przetłumacz' aby zobaczyć pełne tłumaczenie.")

            st.caption(f"📊 Długość: {len(row_text):,} znaków")

            # Tłumaczenie
            translation_key = f"trans_{translation_key_prefix}{idx}_{get_cache_key(row_text)}"
            translate_button_key = f"translate_btn_{translation_key_prefix}{idx}"

            if translation_key in st.session_state:
                # Wyświetl istniejące tłumaczenie
                st.divider()
                st.markdown("**🇵🇱 Tłumaczenie (polski):**")
                translated_text = st.session_state[translation_key]

                display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                formatted_trans = format_email_text(
                    display_trans,
                    highlight_pattern=search_query_final
                    if search_query_final.lower() in translated_text.lower()
                    else None,
                    case_sensitive=case_sensitive,
                )

                st.markdown(
                    f"<div style='background-color: #e8f5e9; padding: 15px; border-radius: 5px; border-left: 4px solid #4caf50; max-height: 500px; overflow-y: auto;'>{formatted_trans}</div>",
                    unsafe_allow_html=True,
                )

                if len(translated_text) > 5000:
                    st.caption("⚠️ Wyświetlono pierwsze 5000 znaków tłumaczenia.")
            else:
                # Przycisk do tłumaczenia
                if st.button("🔄 Przetłumacz na polski", key=translate_button_key):
                    _handle_translation(row_text, translation_key, search_query_final, case_sensitive)

    except Exception as e:
        st.warning(f"⚠️ Błąd podczas przetwarzania maila: {e}")


def _handle_translation(row_text, translation_key, search_query_final, case_sensitive):
    """Obsługuje proces tłumaczenia."""
    progress_container = st.empty()

    with progress_container.container():
        st.info("🔄 Tłumaczenie na polski... To może zająć kilka sekund.")
        progress_bar = st.progress(0)
        status_text = st.empty()

    try:
        # Ograniczenie długości
        text_to_translate = row_text[:3000] if len(row_text) > 3000 else row_text

        status_text.text("📝 Przygotowywanie tekstu...")
        progress_bar.progress(0.1)

        if len(text_to_translate) > 500:
            status_text.text("📄 Dzielenie tekstu na fragmenty...")
            progress_bar.progress(0.3)

        status_text.text("🌐 Tłumaczenie tekstu...")
        progress_bar.progress(0.5)
        translated = translate_text(text_to_translate, None)

        status_text.text("✅ Walidacja tłumaczenia...")
        progress_bar.progress(0.8)

        is_valid, reason = double_validate_translation(text_to_translate, translated)

        progress_bar.progress(1.0)
        progress_container.empty()

        if is_valid:
            st.session_state[translation_key] = translated
            st.success("✅ Tłumaczenie zakończone pomyślnie!")
            st.rerun()
        else:
            # Fallback
            progress_container.empty()
            st.warning(f"⚠️ Tłumaczenie nie przeszło walidacji: {reason}")

            with progress_container.container():
                st.info("🔄 Próbuję alternatywnej metody tłumaczenia...")
                fallback_progress = st.progress(0)
                fallback_status = st.empty()

            fallback_status.text("🌐 Tłumaczenie metodą alternatywną...")
            fallback_progress.progress(0.5)
            fallback_translated = translate_with_fallback(text_to_translate)
            fallback_progress.progress(1.0)
            progress_container.empty()

            is_valid_fallback, reason_fallback = double_validate_translation(text_to_translate, fallback_translated)

            if is_valid_fallback:
                st.session_state[translation_key] = fallback_translated
                st.success("✅ Tłumaczenie zakończone pomyślnie (metoda alternatywna)!")
                st.rerun()
            else:
                st.error(f"❌ Nie udało się przetłumaczyć: {reason_fallback}")
                st.info("💡 Wyświetlany jest oryginalny tekst po angielsku")

    except Exception as e:
        progress_container.empty()
        st.error(f"❌ Błąd podczas tłumaczenia: {e}")


# Nagłówek
st.title("📧 Akta Epsteina - Wyszukiwarka Maili")
st.markdown("**Wyszukiwanie i przeglądanie maili po angielsku**")

# Opis aplikacji
with st.expander("ℹ️ O aplikacji", expanded=False):
    st.markdown(
        """
    ### 📖 Opis

    Ta aplikacja służy do **wyszukiwania i przeglądania maili** pochodzących z publicznego repozytorium
    [Hugging Face](https://huggingface.co/datasets/tensonaut/EPSTEIN_FILES_20K).
    Aplikacja została stworzona wyłącznie w **celach badawczych i edukacyjnych**.

    ### 🔍 Jak działa program?

    1. **Wyszukiwanie**: Wpisz słowo kluczowe, nazwisko lub frazę w polu wyszukiwania.
       - Możesz pisać po **polsku** - aplikacja automatycznie przetłumaczy zapytanie na angielski
       - Możesz również pisać bezpośrednio po angielsku

    2. **Wyniki**: Aplikacja wyświetli wszystkie maile zawierające wyszukiwane słowo/frazę
       - Każdy wynik pokazuje metadane (nadawca, odbiorca, data, temat)
       - Wyszukiwane słowa są **podświetlone** w tekście

    3. **Tłumaczenie**: Każdy mail można przetłumaczyć na polski klikając przycisk **"🔄 Przetłumacz na polski"**
       - ⚠️ **Uwaga**: Tłumaczenie nie jest idealne, ponieważ korzysta z publicznego modelu tłumaczeniowego
         z repozytorium Hugging Face

    ### 👤 Autor

    **PT**

    ---

    *Aplikacja wykorzystuje biblioteki: Streamlit, Hugging Face Transformers, Pandas*
    """
    )

# Ładowanie datasetu
DATASET_NAME = "tensonaut/EPSTEIN_FILES_20K"
SPLIT_NAME = "train"

if "dataset" not in st.session_state:
    with st.spinner("🔄 Ładowanie zbioru danych..."):
        try:
            dataset = load_dataset(DATASET_NAME, split=SPLIT_NAME)
            st.session_state["dataset"] = dataset
            st.success("✅ Zbiór danych załadowany!")
        except Exception as e:
            st.error(f"❌ Błąd podczas ładowania: {str(e)}")
            st.stop()

# Główna zawartość
st.header("🔍 Wyszukiwanie w mailach")

if "dataset" in st.session_state:
    dataset = st.session_state["dataset"]

    # Cache DataFrame
    if "dataframe" not in st.session_state:
        with st.spinner("🔄 Konwersja danych do formatu pandas..."):
            try:
                df = dataset.to_pandas()
                st.session_state["dataframe"] = df
            except Exception as e:
                st.error(f"❌ Błąd podczas konwersji do pandas: {e}")
                st.stop()
    else:
        df = st.session_state["dataframe"]

    # Sprawdź kolumny
    if "text" not in df.columns or "filename" not in df.columns:
        st.error("❌ Błąd: Brak wymaganych kolumn w zbiorze danych")
        st.stop()

    # Wyszukiwarka
    search_query = st.text_input(
        "🔎 Szukaj w mailach",
        placeholder="np. 'Epstein', 'Clinton', 'court', 'travel'...",
        help="Wpisz słowo kluczowe, nazwisko lub frazę (możesz pisać po polsku - zostanie przetłumaczone)",
    )

    col1, col2 = st.columns(2)
    with col1:
        search_in_text = st.checkbox("Szukaj w treści", value=True)
    with col2:
        case_sensitive = st.checkbox("Rozróżniaj wielkość liter", value=False)

    search_button_clicked = st.button("🔍 Szukaj", type="primary", key="search_button")

    # Wyszukiwanie
    if search_button_clicked:
        if not search_query or not search_query.strip():
            st.warning("⚠️ Wpisz zapytanie wyszukiwania")
        else:
            with st.spinner("🔍 Przeszukiwanie maili..."):
                try:
                    # Tłumaczenie zapytania
                    original_query = search_query.strip()
                    translated_query = translate_query_to_english(original_query)

                    if translated_query != original_query:
                        st.info(f"🔤 Zapytanie przetłumaczone: '{original_query}' → '{translated_query}'")
                        search_query_final = translated_query
                    else:
                        search_query_final = original_query

                    # Wyszukiwanie
                    if search_in_text:
                        text_mask = (
                            df["text"]
                            .astype(str)
                            .str.contains(search_query_final, case=case_sensitive, na=False, regex=False)
                        )
                        filtered_df = df[text_mask].copy()
                    else:
                        filtered_df = pd.DataFrame()

                    if len(filtered_df) > 0:
                        # Ograniczenie i klasyfikacja
                        filtered_df_limited = filtered_df.head(100).copy()

                        # Klasyfikuj i sortuj
                        filtered_df_limited["content_type"] = filtered_df_limited["text"].apply(
                            lambda x: classify_content_type(str(x))[0] if pd.notna(x) else "other"
                        )
                        filtered_df_limited["content_label"] = filtered_df_limited["text"].apply(
                            lambda x: classify_content_type(str(x))[1] if pd.notna(x) else "Inny dokument"
                        )

                        type_order = {"email": 0, "metadata": 1, "json": 2, "other": 3}
                        filtered_df_limited["sort_order"] = filtered_df_limited["content_type"].map(type_order)
                        filtered_df_limited = filtered_df_limited.sort_values("sort_order").reset_index(drop=True)
                        filtered_df_limited = filtered_df_limited.drop(columns=["sort_order"])

                        # Zapisz w session_state
                        st.session_state["search_results"] = filtered_df_limited
                        st.session_state["last_search_query"] = search_query_final
                        st.session_state["last_case_sensitive"] = case_sensitive
                        st.session_state["last_search_in_text"] = search_in_text
                        st.session_state["last_original_query"] = original_query

                        st.success(f"✅ Znaleziono {len(filtered_df)} wyników")

                        # Statystyki
                        type_counts = filtered_df_limited["content_type"].value_counts()
                        stats_parts = []
                        if "email" in type_counts:
                            stats_parts.append(f"📧 Maile: {type_counts['email']}")
                        if "metadata" in type_counts:
                            stats_parts.append(f"📋 Metadane: {type_counts['metadata']}")
                        if "other" in type_counts:
                            stats_parts.append(f"📄 Inne: {type_counts['other']}")

                        if stats_parts:
                            st.caption(" | ".join(stats_parts))

                        # Paginacja
                        RESULTS_PER_PAGE = 10
                        total_results = len(filtered_df_limited)
                        total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

                        if total_pages > 1:
                            page_key = "results_page"
                            if page_key not in st.session_state:
                                st.session_state[page_key] = 1

                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                page = st.number_input(
                                    "Strona",
                                    min_value=1,
                                    max_value=total_pages,
                                    value=st.session_state.get(page_key, 1),
                                    key=page_key,
                                    help=f"Wyświetlanie {RESULTS_PER_PAGE} wyników na stronę",
                                )

                            st.caption(
                                f"📄 Strona {page} z {total_pages} ({RESULTS_PER_PAGE} wyników na stronę, łącznie {total_results} wyników)"
                            )
                            st.divider()

                            start_idx = (page - 1) * RESULTS_PER_PAGE
                            end_idx = min(start_idx + RESULTS_PER_PAGE, total_results)
                            results_to_show = filtered_df_limited.iloc[start_idx:end_idx]
                        else:
                            page = 1
                            results_to_show = filtered_df_limited

                        # Wyświetl wyniki
                        for idx, row in results_to_show.iterrows():
                            display_email_result(row, idx, search_query_final, case_sensitive)
                    else:
                        st.info("❌ Nie znaleziono maili pasujących do zapytania")
                        if "search_results" in st.session_state:
                            del st.session_state["search_results"]
                except Exception as e:
                    st.error(f"❌ Błąd podczas wyszukiwania: {e}")
                    st.exception(e)

    # Wyświetl zapisane wyniki jeśli są dostępne
    if (
        "search_results" in st.session_state
        and len(st.session_state["search_results"]) > 0
        and not search_button_clicked
    ):
        filtered_df = st.session_state["search_results"]
        search_query_final = st.session_state.get("last_search_query", "")
        case_sensitive = st.session_state.get("last_case_sensitive", False)

        if len(filtered_df) > 0:
            st.success(f"✅ Znaleziono {len(filtered_df)} wyników")

            # Paginacja
            RESULTS_PER_PAGE = 10
            total_results = len(filtered_df)
            total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

            if total_pages > 1:
                page_key = "results_page"
                if page_key not in st.session_state:
                    st.session_state[page_key] = 1

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    page = st.number_input(
                        "Strona",
                        min_value=1,
                        max_value=total_pages,
                        value=st.session_state.get(page_key, 1),
                        key=page_key,
                        help=f"Wyświetlanie {RESULTS_PER_PAGE} wyników na stronę",
                    )

                st.caption(
                    f"📄 Strona {page} z {total_pages} ({RESULTS_PER_PAGE} wyników na stronę, łącznie {total_results} wyników)"
                )
                st.divider()

                page = st.session_state.get("results_page", 1)
                start_idx = (page - 1) * RESULTS_PER_PAGE
                end_idx = min(start_idx + RESULTS_PER_PAGE, total_results)
                results_to_show = filtered_df.iloc[start_idx:end_idx]
            else:
                page = 1
                results_to_show = filtered_df

            # Wyświetl wyniki
            for idx, row in results_to_show.iterrows():
                display_email_result(row, idx, search_query_final, case_sensitive, translation_key_prefix="saved_")

    # Informacja o zbiorze
    st.divider()
    st.caption(f"📋 Zbiór danych: {DATASET_NAME} | Liczba dokumentów: {len(df):,}")

else:
    st.warning("⚠️ Zbiór danych nie został załadowany. Odśwież stronę.")

# Footer
st.divider()
st.caption("📧 Akta Epsteina - Wyszukiwarka Maili | Autor: **PT** | Zbudowane z ❤️ używając Streamlit i Hugging Face 🤗")
st.caption("⚠️ Aplikacja służy wyłącznie celom badawczym i edukacyjnym. Tłumaczenia mogą zawierać błędy.")
