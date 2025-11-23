# Plan naprawy wydajności i formatowania aplikacji Streamlit

## 🔍 Analiza problemów

### Problem 1: Aplikacja się zacina przy tłumaczeniu
**Przyczyna:**
- `translate_text()` jest wywoływane synchronicznie w bloku `with st.spinner()`
- Model tłumaczeniowy może ładować się długo przy pierwszym użyciu (kilka sekund)
- Tłumaczenie długich tekstów (5000 znaków) może trwać 10-30 sekund
- Operacje blokują główny wątek Streamlit, co powoduje zamrożenie UI
- Brak progress bara - użytkownik nie widzi postępu

**Lokalizacja:** `app.py` linie 180-237, 331-381

### Problem 2: Słabe formatowanie tekstu
**Przyczyna:**
- Używa `st.text()` dla długich tekstów (nie formatuje, brak podziału na akapity)
- Tekst jest wyświetlany jako jeden długi blok bez formatowania
- Brak podziału na akapity (paragraphy)
- Brak lepszego layoutu (kolumny, karty)
- Brak kolorowania i wyróżnień
- Brak czytelnego formatowania dla długich maili

**Lokalizacja:** `app.py` linie 144-177, 296-328

### Problem 3: Wydajność - brak cache'owania DataFrame
**Przyczyna:**
- `dataset.to_pandas()` jest wywoływane przy każdym renderowaniu strony
- Konwersja dużego datasetu do pandas może trwać kilka sekund
- Brak cache'owania DataFrame w session_state

**Lokalizacja:** `app.py` linia 43

### Problem 4: Wydajność - iteracja przez wszystkie wyniki
**Przyczyna:**
- Pętla `for idx, row in filtered_df.head(100).iterrows()` może być wolna dla wielu wyników
- Każda iteracja wywołuje `extract_email_metadata()` i inne operacje
- Brak optymalizacji dla dużych wyników

**Lokalizacja:** `app.py` linie 108-240, 260-384

---

## 📋 Plan naprawy

### KROK 1: Naprawić zacięcie aplikacji - dodać progress bar i optymalizację tłumaczenia

**Cel:** Użytkownik widzi postęp i aplikacja nie zamraża się

**Działania:**
1. Dodać `st.progress()` dla długich operacji tłumaczenia
2. Dodać informację o postępie (np. "Tłumaczenie fragmentu 3/10...")
3. Ograniczyć długość tłumaczonego tekstu (np. pierwsze 3000 znaków zamiast 5000)
4. Dodać timeout dla tłumaczenia (max 30 sekund)
5. Użyć `st.empty()` do dynamicznego aktualizowania UI

**Lokalizacja:** `app.py` linie 180-237

**Kod:**
```python
if st.button("🔄 Przetłumacz na polski", key=translate_button_key):
    # Ograniczenie długości tekstu
    text_to_translate = row_text[:3000] if len(row_text) > 3000 else row_text

    # Utwórz kontenery dla progress i wyniku
    progress_container = st.empty()
    result_container = st.empty()

    with progress_container.container():
        st.info("🔄 Tłumaczenie na polski... To może zająć kilka sekund.")
        progress_bar = st.progress(0)
        status_text = st.empty()

    try:
        # Symulacja postępu (dla długich tekstów)
        if len(text_to_translate) > 500:
            status_text.text("📝 Dzielenie tekstu na fragmenty...")
            progress_bar.progress(0.2)

            status_text.text("🤖 Ładowanie modelu tłumaczeniowego...")
            progress_bar.progress(0.4)

        # Tłumaczenie
        translated = translate_text(text_to_translate, None)

        progress_bar.progress(0.8)
        status_text.text("✅ Walidacja tłumaczenia...")

        # Walidacja
        is_valid, reason = double_validate_translation(text_to_translate, translated)

        progress_bar.progress(1.0)
        progress_container.empty()  # Usuń progress bar

        if is_valid:
            st.session_state[translation_key] = translated
            # Wyświetl wynik...
```

---

### KROK 2: Poprawić formatowanie tekstu - użyć lepszych komponentów Streamlit

**Cel:** Tekst wygląda atrakcyjnie i jest czytelny

**Działania:**
1. Zastąpić `st.text()` przez `st.markdown()` z lepszym formatowaniem
2. Dodać podział na akapity (paragraphy)
3. Użyć `st.container()` lub `st.columns()` dla lepszego layoutu
4. Dodać kolorowanie i wyróżnienia
5. Użyć `st.code()` dla fragmentów kodu/struktury
6. Dodać czytelne formatowanie dla długich tekstów

**Lokalizacja:** `app.py` linie 144-177, 296-328

**Kod:**
```python
# Funkcja pomocnicza do formatowania tekstu
def format_email_text(text, highlight_pattern=None, case_sensitive=False):
    """
    Formatuje tekst maila z podziałem na akapity i podświetleniem.
    """
    # Podziel na akapity (podwójne znaki nowej linii)
    paragraphs = text.split('\n\n')

    formatted_paragraphs = []
    for para in paragraphs:
        if not para.strip():
            continue

        # Podświetl jeśli jest wzorzec
        if highlight_pattern and highlight_pattern.lower() in para.lower():
            pattern = re.compile(re.escape(highlight_pattern),
                               re.IGNORECASE if not case_sensitive else 0)
            para = pattern.sub(lambda m: f"<mark style='background-color: #ffeb3b; padding: 2px 4px;'>{m.group()}</mark>", para)

        # Formatuj jako akapit
        formatted_paragraphs.append(f"<p style='margin-bottom: 1em; line-height: 1.6;'>{para}</p>")

    return "\n".join(formatted_paragraphs)

# W kodzie:
st.markdown("**🇬🇧 Oryginał (angielski):**")
display_text = row_text[:5000] if len(row_text) > 5000 else row_text

# Użyj kontenera z lepszym formatowaniem
with st.container():
    if search_query_final.lower() in display_text.lower():
        formatted = format_email_text(display_text, search_query_final, case_sensitive)
        st.markdown(f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #1f77b4;'>{formatted}</div>",
                   unsafe_allow_html=True)
    else:
        formatted = format_email_text(display_text)
        st.markdown(f"<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px;'>{formatted}</div>",
                   unsafe_allow_html=True)

    if len(row_text) > 5000:
        st.caption("⚠️ Wyświetlono pierwsze 5000 znaków. Kliknij 'Przetłumacz' aby zobaczyć pełne tłumaczenie.")
```

---

### KROK 3: Cache'ować DataFrame w session_state

**Cel:** Uniknąć powtarzanej konwersji datasetu do pandas

**Działania:**
1. Sprawdzić czy DataFrame jest już w session_state
2. Jeśli nie, skonwertować i zapisać
3. Użyć zapisanego DataFrame zamiast konwersji przy każdym renderowaniu

**Lokalizacja:** `app.py` linie 40-49

**Kod:**
```python
if 'dataset' in st.session_state:
    dataset = st.session_state['dataset']

    # Cache DataFrame w session_state
    if 'dataframe' not in st.session_state:
        with st.spinner("🔄 Konwersja danych do formatu pandas..."):
            try:
                df = dataset.to_pandas()
                st.session_state['dataframe'] = df
            except Exception as e:
                st.error(f"❌ Błąd podczas konwersji do pandas: {e}")
                st.stop()
    else:
        df = st.session_state['dataframe']

    if 'text' not in df.columns or 'filename' not in df.columns:
        st.error("❌ Błąd: Brak wymaganych kolumn w zbiorze danych")
        st.stop()
```

---

### KROK 4: Optymalizować wyświetlanie wyników - użyć paginacji

**Cel:** Szybsze wyświetlanie wyników dla dużych zbiorów

**Działania:**
1. Dodać paginację (np. 10 wyników na stronę)
2. Użyć `st.number_input()` do wyboru strony
3. Wyświetlać tylko wyniki z aktualnej strony
4. Dodać informację o liczbie stron

**Lokalizacja:** `app.py` linie 97-240

**Kod:**
```python
if len(filtered_df) > 0:
    st.success(f"✅ Znaleziono {len(filtered_df)} maili")

    # Paginacja
    RESULTS_PER_PAGE = 10
    total_pages = (len(filtered_df) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    if total_pages > 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input("Strona", min_value=1, max_value=total_pages,
                                 value=1, key="results_page")
        st.caption(f"Strona {page} z {total_pages} ({RESULTS_PER_PAGE} wyników na stronę)")

    # Oblicz zakres wyników do wyświetlenia
    start_idx = (page - 1) * RESULTS_PER_PAGE
    end_idx = min(start_idx + RESULTS_PER_PAGE, len(filtered_df))

    # Wyświetl tylko wyniki z aktualnej strony
    for idx, row in filtered_df.iloc[start_idx:end_idx].iterrows():
        # ... reszta kodu ...
```

---

### KROK 5: Dodać asynchroniczne przetwarzanie tłumaczenia (opcjonalne)

**Cel:** Aplikacja nie zamraża się podczas tłumaczenia

**Działania:**
1. Użyć `threading` lub `multiprocessing` dla długich operacji
2. LUB użyć `st.rerun()` z flagą w session_state
3. LUB użyć `st.empty()` do dynamicznego aktualizowania

**Lokalizacja:** `app.py` linie 180-237

**Kod (uproszczony - bez threading):**
```python
# Użyj flagi w session_state zamiast bezpośredniego wywołania
if st.button("🔄 Przetłumacz na polski", key=translate_button_key):
    st.session_state[f'translate_requested_{idx}'] = True
    st.rerun()

# W głównej pętli:
if st.session_state.get(f'translate_requested_{idx}', False):
    st.session_state[f'translate_requested_{idx}'] = False
    # Wykonaj tłumaczenie...
```

---

### KROK 6: Poprawić wygląd expanderów i metadanych

**Cel:** Lepszy wygląd i czytelność

**Działania:**
1. Użyć lepszych ikon i formatowania dla metadanych
2. Dodać kolory i wyróżnienia
3. Użyć `st.columns()` dla lepszego layoutu metadanych
4. Dodać tooltips i pomoc

**Lokalizacja:** `app.py` linie 138-157

**Kod:**
```python
with st.expander(expander_title, expanded=False):
    # Metadane w kolumnach
    if metadata['subject'] != 'N/A' or any(v != 'N/A' for v in [metadata['from'], metadata['to'], metadata['date']]):
        col1, col2 = st.columns(2)
        with col1:
            if metadata['from'] != 'N/A':
                st.markdown(f"**📤 Od:** `{metadata['from']}`")
            if metadata['to'] != 'N/A':
                st.markdown(f"**📥 Do:** `{metadata['to']}`")
        with col2:
            if metadata['date'] != 'N/A':
                st.markdown(f"**📅 Data:** `{metadata['date']}`")
            if metadata['subject'] != 'N/A':
                st.markdown(f"**📌 Temat:** `{metadata['subject']}`")

        st.divider()

    # Reszta kodu...
```

---

## 🎯 Priorytety wykonania

### WYSOKI PRIORYTET (naprawić natychmiast):
1. **KROK 1** - Naprawić zacięcie aplikacji (progress bar, timeout)
2. **KROK 2** - Poprawić formatowanie tekstu
3. **KROK 3** - Cache'ować DataFrame

### ŚREDNI PRIORYTET (poprawić wydajność):
4. **KROK 4** - Dodać paginację wyników
5. **KROK 6** - Poprawić wygląd expanderów

### NISKI PRIORYTET (opcjonalne):
6. **KROK 5** - Asynchroniczne przetwarzanie (może być skomplikowane)

---

## 📝 Szczegółowy plan wykonania

### Faza 1: Naprawa zacięcia (KROK 1)
1. Dodać progress bar do tłumaczenia
2. Dodać status text z informacją o postępie
3. Ograniczyć długość tłumaczonego tekstu do 3000 znaków
4. Dodać timeout (30 sekund)
5. Przetestować na długich mailach

### Faza 2: Formatowanie tekstu (KROK 2)
1. Utworzyć funkcję `format_email_text()`
2. Zastąpić wszystkie `st.text()` przez `st.markdown()` z formatowaniem
3. Dodać podział na akapity
4. Dodać kolorowanie i wyróżnienia
5. Przetestować wygląd

### Faza 3: Cache DataFrame (KROK 3)
1. Dodać sprawdzenie `dataframe` w session_state
2. Cache'ować DataFrame po pierwszej konwersji
3. Użyć zapisanego DataFrame
4. Przetestować wydajność

### Faza 4: Paginacja (KROK 4)
1. Dodać zmienną `RESULTS_PER_PAGE = 10`
2. Dodać `st.number_input()` dla wyboru strony
3. Obliczyć zakres wyników do wyświetlenia
4. Wyświetlać tylko wyniki z aktualnej strony
5. Przetestować z dużą liczbą wyników

### Faza 5: Poprawa wyglądu (KROK 6)
1. Użyć `st.columns()` dla metadanych
2. Dodać lepsze ikony i formatowanie
3. Dodać kolory i wyróżnienia
4. Przetestować wygląd

---

## ✅ Lista kontrolna weryfikacji

Po implementacji sprawdzić:
- [ ] Aplikacja nie zamraża się przy tłumaczeniu
- [ ] Progress bar jest widoczny podczas tłumaczenia
- [ ] Tekst jest czytelnie sformatowany z akapitami
- [ ] DataFrame jest cache'owany (szybsze ładowanie)
- [ ] Paginacja działa poprawnie
- [ ] Metadane są czytelnie wyświetlone
- [ ] Aplikacja działa szybko na Streamlit Cloud
- [ ] Nie ma błędów w konsoli
- [ ] Wszystkie funkcje działają poprawnie

---

## 🔧 Narzędzia i biblioteki

- `st.progress()` - progress bar
- `st.empty()` - dynamiczne kontenery
- `st.container()` - grupowanie elementów
- `st.columns()` - layout kolumnowy
- `st.markdown()` z `unsafe_allow_html=True` - zaawansowane formatowanie
- HTML/CSS inline - kolorowanie i stylowanie

---

## ⚠️ Uwagi

1. **Bezpieczeństwo HTML:** Używając `unsafe_allow_html=True`, upewnij się, że tekst nie zawiera złośliwego kodu
2. **Wydajność:** Paginacja może wymagać zapisania stanu strony w session_state
3. **Timeout:** 30 sekund może być za długo - rozważyć 15-20 sekund
4. **Limit tekstu:** 3000 znaków może być za mało - rozważyć 4000-5000

---

## 📊 Oczekiwane rezultaty

Po implementacji:
- ✅ Aplikacja nie zamraża się przy tłumaczeniu
- ✅ Użytkownik widzi postęp tłumaczenia
- ✅ Tekst jest czytelnie sformatowany
- ✅ Aplikacja ładuje się szybciej (cache DataFrame)
- ✅ Wyniki są wyświetlane szybciej (paginacja)
- ✅ Lepszy wygląd i UX
