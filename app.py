import streamlit as st
from datasets import load_dataset
import pandas as pd
from translation_utils import (
    translate_text, 
    get_cache_key, 
    extract_email_metadata,
    translate_query_to_english,
    double_validate_translation,
    translate_with_fallback
)
import re

st.set_page_config(
    page_title="Akta Epsteina - Wyszukiwarka Maili",
    page_icon="📧",
    layout="wide"
)

st.title("📧 Akta Epsteina - Wyszukiwarka Maili")
st.markdown("**Wyszukiwanie i przeglądanie maili po angielsku**")

# Auto-load dataset
DATASET_NAME = "tensonaut/EPSTEIN_FILES_20K"
SPLIT_NAME = "train"

if 'dataset' not in st.session_state:
    with st.spinner("🔄 Ładowanie zbioru danych..."):
        try:
            dataset = load_dataset(DATASET_NAME, split=SPLIT_NAME)
            st.session_state['dataset'] = dataset
            st.success("✅ Zbiór danych załadowany!")
        except Exception as e:
            st.error(f"❌ Błąd podczas ładowania: {str(e)}")
            st.stop()

# Main content - Wyszukiwarka
st.header("🔍 Wyszukiwanie w mailach")

if 'dataset' in st.session_state:
    dataset = st.session_state['dataset']
    try:
        df = dataset.to_pandas()
        if 'text' not in df.columns or 'filename' not in df.columns:
            st.error("❌ Błąd: Brak wymaganych kolumn w zbiorze danych")
            st.stop()
    except Exception as e:
        st.error(f"❌ Błąd podczas konwersji do pandas: {e}")
        st.stop()
    
    # Wyszukiwarka
    search_query = st.text_input(
        "🔎 Szukaj w mailach", 
        placeholder="np. 'Epstein', 'Clinton', 'court', 'travel'...",
        help="Wpisz słowo kluczowe, nazwisko lub frazę (możesz pisać po polsku - zostanie przetłumaczone)"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        search_in_text = st.checkbox("Szukaj w treści", value=True)
    with col2:
        case_sensitive = st.checkbox("Rozróżniaj wielkość liter", value=False)
    
    # Przycisk zawsze widoczny
    search_button_clicked = st.button("🔍 Szukaj", type="primary", key="search_button")
    
    # Wykonaj wyszukiwanie tylko jeśli przycisk został kliknięty I jest zapytanie
    if search_button_clicked:
        if not search_query or not search_query.strip():
            st.warning("⚠️ Wpisz zapytanie wyszukiwania")
        else:
            with st.spinner("🔍 Przeszukiwanie maili..."):
                try:
                    # Tłumaczenie zapytania z polskiego na angielski
                    original_query = search_query.strip()
                    translated_query = translate_query_to_english(original_query)
                    
                    # Wyświetl informację o tłumaczeniu jeśli się różni
                    if translated_query != original_query:
                        st.info(f"🔤 Zapytanie przetłumaczone: '{original_query}' → '{translated_query}'")
                        search_query_final = translated_query
                    else:
                        search_query_final = original_query
                    
                    # Wyszukiwanie
                    if search_in_text:
                        text_mask = df['text'].astype(str).str.contains(
                            search_query_final, 
                            case=case_sensitive, 
                            na=False, 
                            regex=False
                        )
                        filtered_df = df[text_mask].copy()
                    else:
                        filtered_df = pd.DataFrame()
                    
                    if len(filtered_df) > 0:
                        st.success(f"✅ Znaleziono {len(filtered_df)} maili")
                        
                        # KROK 1: Zapisz stan wyszukiwania w session_state
                        st.session_state['search_results'] = filtered_df.head(100).copy()  # Ograniczenie do 100 wyników
                        st.session_state['last_search_query'] = search_query_final
                        st.session_state['last_case_sensitive'] = case_sensitive
                        st.session_state['last_search_in_text'] = search_in_text
                        st.session_state['last_original_query'] = original_query
                        
                        # Wyświetl wyniki
                        for idx, row in filtered_df.head(100).iterrows():
                            try:
                                row_text = str(row.get('text', ''))
                                row_filename = str(row.get('filename', 'N/A'))
                                
                                if not row_text or row_text == 'nan':
                                    continue
                                
                                # Wyciągnij metadane
                                metadata = extract_email_metadata(row_text)
                                
                                # Zbuduj nagłówek z metadanymi
                                metadata_parts = []
                                if metadata['from'] != 'N/A':
                                    metadata_parts.append(f"Od: {metadata['from']}")
                                if metadata['to'] != 'N/A':
                                    metadata_parts.append(f"Do: {metadata['to']}")
                                if metadata['date'] != 'N/A':
                                    metadata_parts.append(f"Data: {metadata['date']}")
                                
                                metadata_str = " | ".join(metadata_parts) if metadata_parts else ""
                                
                                occurrences = row_text.lower().count(search_query_final.lower())
                                
                                # Nagłówek expandera z metadanymi
                                expander_title = f"📧 {row_filename}"
                                if metadata_str:
                                    expander_title += f" | {metadata_str}"
                                expander_title += f" ({occurrences} wystąpień)"
                                
                                with st.expander(expander_title, expanded=False):
                                    # Wyświetl metadane jeśli są dostępne
                                    if metadata['subject'] != 'N/A':
                                        st.caption(f"📌 Temat: {metadata['subject']}")
                                    
                                    # Wyświetl oryginalny tekst (zawsze po angielsku)
                                    st.markdown("**🇬🇧 Oryginał (angielski):**")
                                    
                                    # Podświetl wyszukiwane słowo
                                    if search_query_final.lower() in row_text.lower():
                                        pattern = re.compile(re.escape(search_query_final), re.IGNORECASE if not case_sensitive else 0)
                                        # Wyświetl pełny tekst (lub pierwsze 5000 znaków dla długich maili)
                                        display_text = row_text[:5000] if len(row_text) > 5000 else row_text
                                        highlighted = pattern.sub(lambda m: f"**{m.group()}**", display_text)
                                        st.markdown(highlighted + ("..." if len(row_text) > 5000 else ""))
                                    else:
                                        display_text = row_text[:5000] if len(row_text) > 5000 else row_text
                                        st.text(display_text + ("..." if len(row_text) > 5000 else ""))
                                    
                                    st.caption(f"📊 Długość: {len(row_text):,} znaków")
                                    
                                    # Przycisk do tłumaczenia na żądanie
                                    translation_key = f"trans_{idx}_{get_cache_key(row_text)}"
                                    translate_button_key = f"translate_btn_{idx}"
                                    
                                    # Sprawdź czy tłumaczenie już istnieje w cache
                                    if translation_key in st.session_state:
                                        st.divider()
                                        st.markdown("**🇵🇱 Tłumaczenie (polski):**")
                                        translated_text = st.session_state[translation_key]
                                        
                                        # Podświetl wyszukiwane słowo w tłumaczeniu
                                        if search_query_final.lower() in translated_text.lower():
                                            pattern = re.compile(re.escape(search_query_final), re.IGNORECASE if not case_sensitive else 0)
                                            display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                            highlighted_trans = pattern.sub(lambda m: f"**{m.group()}**", display_trans)
                                            st.markdown(highlighted_trans + ("..." if len(translated_text) > 5000 else ""))
                                        else:
                                            display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                            st.text(display_trans + ("..." if len(translated_text) > 5000 else ""))
                                    else:
                                        # Przycisk do tłumaczenia
                                        if st.button("🔄 Przetłumacz na polski", key=translate_button_key):
                                            with st.spinner("🔄 Tłumaczenie na polski..."):
                                                try:
                                                    # Tłumacz pełny tekst (lub fragment dla długich maili)
                                                    text_to_translate = row_text[:5000] if len(row_text) > 5000 else row_text
                                                    translated = translate_text(text_to_translate, None)
                                                    
                                                    # Podwójna walidacja
                                                    is_valid, reason = double_validate_translation(text_to_translate, translated)
                                                    
                                                    if is_valid:
                                                        st.session_state[translation_key] = translated
                                                        st.success("✅ Tłumaczenie zakończone pomyślnie!")
                                                        # KROK 3: Wyświetl tłumaczenie bezpośrednio zamiast st.rerun()
                                                        st.divider()
                                                        st.markdown("**🇵🇱 Tłumaczenie (polski):**")
                                                        translated_text = st.session_state[translation_key]
                                                        
                                                        # Podświetl wyszukiwane słowo w tłumaczeniu
                                                        if search_query_final.lower() in translated_text.lower():
                                                            pattern = re.compile(re.escape(search_query_final), re.IGNORECASE if not case_sensitive else 0)
                                                            display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                                            highlighted_trans = pattern.sub(lambda m: f"**{m.group()}**", display_trans)
                                                            st.markdown(highlighted_trans + ("..." if len(translated_text) > 5000 else ""))
                                                        else:
                                                            display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                                            st.text(display_trans + ("..." if len(translated_text) > 5000 else ""))
                                                    else:
                                                        # Spróbuj fallback
                                                        st.warning(f"⚠️ Tłumaczenie nie przeszło walidacji: {reason}")
                                                        st.info("🔄 Próbuję alternatywnej metody tłumaczenia...")
                                                        fallback_translated = translate_with_fallback(text_to_translate)
                                                        
                                                        # Walidacja fallback
                                                        is_valid_fallback, reason_fallback = double_validate_translation(text_to_translate, fallback_translated)
                                                        
                                                        if is_valid_fallback:
                                                            st.session_state[translation_key] = fallback_translated
                                                            st.success("✅ Tłumaczenie zakończone pomyślnie (metoda alternatywna)!")
                                                            # KROK 3: Wyświetl tłumaczenie bezpośrednio zamiast st.rerun()
                                                            st.divider()
                                                            st.markdown("**🇵🇱 Tłumaczenie (polski):**")
                                                            translated_text = st.session_state[translation_key]
                                                            
                                                            # Podświetl wyszukiwane słowo w tłumaczeniu
                                                            if search_query_final.lower() in translated_text.lower():
                                                                pattern = re.compile(re.escape(search_query_final), re.IGNORECASE if not case_sensitive else 0)
                                                                display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                                                highlighted_trans = pattern.sub(lambda m: f"**{m.group()}**", display_trans)
                                                                st.markdown(highlighted_trans + ("..." if len(translated_text) > 5000 else ""))
                                                            else:
                                                                display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                                                st.text(display_trans + ("..." if len(translated_text) > 5000 else ""))
                                                        else:
                                                            st.error(f"❌ Nie udało się przetłumaczyć: {reason_fallback}")
                                                            st.info("💡 Wyświetlany jest oryginalny tekst po angielsku")
                                                except Exception as e:
                                                    st.error(f"❌ Błąd podczas tłumaczenia: {e}")
                            except Exception as e:
                                st.warning(f"⚠️ Błąd podczas przetwarzania maila: {e}")
                                continue
                    else:
                        st.info("❌ Nie znaleziono maili pasujących do zapytania")
                        # Wyczyść stare wyniki jeśli nie znaleziono
                        if 'search_results' in st.session_state:
                            del st.session_state['search_results']
                except Exception as e:
                    st.error(f"❌ Błąd podczas wyszukiwania: {e}")
                    st.exception(e)
    
    # KROK 2: Wyświetl wyniki z session_state jeśli są dostępne (po rerun lub gdy nie było nowego wyszukiwania)
    if 'search_results' in st.session_state and len(st.session_state['search_results']) > 0 and not search_button_clicked:
        filtered_df = st.session_state['search_results']
        search_query_final = st.session_state.get('last_search_query', '')
        case_sensitive = st.session_state.get('last_case_sensitive', False)
        
        if len(filtered_df) > 0:
            st.success(f"✅ Znaleziono {len(filtered_df)} maili")
            
            # Wyświetl wyniki (identyczna logika jak w głównej pętli)
            for idx, row in filtered_df.iterrows():
                try:
                    row_text = str(row.get('text', ''))
                    row_filename = str(row.get('filename', 'N/A'))
                    
                    if not row_text or row_text == 'nan':
                        continue
                    
                    # Wyciągnij metadane
                    metadata = extract_email_metadata(row_text)
                    
                    # Zbuduj nagłówek z metadanymi
                    metadata_parts = []
                    if metadata['from'] != 'N/A':
                        metadata_parts.append(f"Od: {metadata['from']}")
                    if metadata['to'] != 'N/A':
                        metadata_parts.append(f"Do: {metadata['to']}")
                    if metadata['date'] != 'N/A':
                        metadata_parts.append(f"Data: {metadata['date']}")
                    
                    metadata_str = " | ".join(metadata_parts) if metadata_parts else ""
                    
                    occurrences = row_text.lower().count(search_query_final.lower())
                    
                    # Nagłówek expandera z metadanymi
                    expander_title = f"📧 {row_filename}"
                    if metadata_str:
                        expander_title += f" | {metadata_str}"
                    expander_title += f" ({occurrences} wystąpień)"
                    
                    with st.expander(expander_title, expanded=False):
                        # Wyświetl metadane jeśli są dostępne
                        if metadata['subject'] != 'N/A':
                            st.caption(f"📌 Temat: {metadata['subject']}")
                        
                        # Wyświetl oryginalny tekst (zawsze po angielsku)
                        st.markdown("**🇬🇧 Oryginał (angielski):**")
                        
                        # Podświetl wyszukiwane słowo
                        if search_query_final.lower() in row_text.lower():
                            pattern = re.compile(re.escape(search_query_final), re.IGNORECASE if not case_sensitive else 0)
                            display_text = row_text[:5000] if len(row_text) > 5000 else row_text
                            highlighted = pattern.sub(lambda m: f"**{m.group()}**", display_text)
                            st.markdown(highlighted + ("..." if len(row_text) > 5000 else ""))
                        else:
                            display_text = row_text[:5000] if len(row_text) > 5000 else row_text
                            st.text(display_text + ("..." if len(row_text) > 5000 else ""))
                        
                        st.caption(f"📊 Długość: {len(row_text):,} znaków")
                        
                        # Przycisk do tłumaczenia na żądanie
                        translation_key = f"trans_{idx}_{get_cache_key(row_text)}"
                        translate_button_key = f"translate_btn_{idx}"
                        
                        # Sprawdź czy tłumaczenie już istnieje w cache
                        if translation_key in st.session_state:
                            st.divider()
                            st.markdown("**🇵🇱 Tłumaczenie (polski):**")
                            translated_text = st.session_state[translation_key]
                            
                            # Podświetl wyszukiwane słowo w tłumaczeniu
                            if search_query_final.lower() in translated_text.lower():
                                pattern = re.compile(re.escape(search_query_final), re.IGNORECASE if not case_sensitive else 0)
                                display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                highlighted_trans = pattern.sub(lambda m: f"**{m.group()}**", display_trans)
                                st.markdown(highlighted_trans + ("..." if len(translated_text) > 5000 else ""))
                            else:
                                display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                st.text(display_trans + ("..." if len(translated_text) > 5000 else ""))
                        else:
                            # Przycisk do tłumaczenia
                            if st.button("🔄 Przetłumacz na polski", key=translate_button_key):
                                with st.spinner("🔄 Tłumaczenie na polski..."):
                                    try:
                                        text_to_translate = row_text[:5000] if len(row_text) > 5000 else row_text
                                        translated = translate_text(text_to_translate, None)
                                        
                                        is_valid, reason = double_validate_translation(text_to_translate, translated)
                                        
                                        if is_valid:
                                            st.session_state[translation_key] = translated
                                            st.success("✅ Tłumaczenie zakończone pomyślnie!")
                                            # Wyświetl tłumaczenie bezpośrednio
                                            st.divider()
                                            st.markdown("**🇵🇱 Tłumaczenie (polski):**")
                                            translated_text = st.session_state[translation_key]
                                            
                                            if search_query_final.lower() in translated_text.lower():
                                                pattern = re.compile(re.escape(search_query_final), re.IGNORECASE if not case_sensitive else 0)
                                                display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                                highlighted_trans = pattern.sub(lambda m: f"**{m.group()}**", display_trans)
                                                st.markdown(highlighted_trans + ("..." if len(translated_text) > 5000 else ""))
                                            else:
                                                display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                                st.text(display_trans + ("..." if len(translated_text) > 5000 else ""))
                                        else:
                                            st.warning(f"⚠️ Tłumaczenie nie przeszło walidacji: {reason}")
                                            st.info("🔄 Próbuję alternatywnej metody tłumaczenia...")
                                            fallback_translated = translate_with_fallback(text_to_translate)
                                            
                                            is_valid_fallback, reason_fallback = double_validate_translation(text_to_translate, fallback_translated)
                                            
                                            if is_valid_fallback:
                                                st.session_state[translation_key] = fallback_translated
                                                st.success("✅ Tłumaczenie zakończone pomyślnie (metoda alternatywna)!")
                                                st.divider()
                                                st.markdown("**🇵🇱 Tłumaczenie (polski):**")
                                                translated_text = st.session_state[translation_key]
                                                
                                                if search_query_final.lower() in translated_text.lower():
                                                    pattern = re.compile(re.escape(search_query_final), re.IGNORECASE if not case_sensitive else 0)
                                                    display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                                    highlighted_trans = pattern.sub(lambda m: f"**{m.group()}**", display_trans)
                                                    st.markdown(highlighted_trans + ("..." if len(translated_text) > 5000 else ""))
                                                else:
                                                    display_trans = translated_text[:5000] if len(translated_text) > 5000 else translated_text
                                                    st.text(display_trans + ("..." if len(translated_text) > 5000 else ""))
                                            else:
                                                st.error(f"❌ Nie udało się przetłumaczyć: {reason_fallback}")
                                                st.info("💡 Wyświetlany jest oryginalny tekst po angielsku")
                                    except Exception as e:
                                        st.error(f"❌ Błąd podczas tłumaczenia: {e}")
                except Exception as e:
                    st.warning(f"⚠️ Błąd podczas przetwarzania maila: {e}")
                    continue
    
    # Informacja o zbiorze
    st.divider()
    st.caption(f"📋 Zbiór danych: {DATASET_NAME} | Liczba dokumentów: {len(df):,}")

else:
    st.warning("⚠️ Zbiór danych nie został załadowany. Odśwież stronę.")

# Footer
st.divider()
st.caption("📧 Akta Epsteina - Wyszukiwarka Maili | Zbudowane z ❤️ używając Streamlit i Hugging Face 🤗")
