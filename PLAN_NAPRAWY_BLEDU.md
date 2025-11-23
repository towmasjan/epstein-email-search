# Plan naprawy błędu - Przycisk "Przetłumacz na polski"

## Problem

Gdy użytkownik klika przycisk "🔄 Przetłumacz na polski", aplikacja wraca do strony głównej (resetuje się).

## Analiza przyczyny

### Główna przyczyna:
1. **`st.rerun()` powoduje pełne przeładowanie aplikacji**
   - Po `st.rerun()` cały kod jest wykonywany od nowa
   - Wszystkie zmienne są resetowane (z wyjątkiem `st.session_state`)
   - `search_button_clicked` staje się `False` (przycisk nie został ponownie kliknięty)
   - Aplikacja wraca do stanu początkowego (bez wyników wyszukiwania)

2. **Brak zapisania stanu wyszukiwania w session_state**
   - Wyniki wyszukiwania nie są zapisywane w `st.session_state`
   - Po `st.rerun()` wyniki znikają
   - Użytkownik musi ponownie kliknąć "Szukaj"

3. **Logika wyświetlania wyników zależy od `search_button_clicked`**
   - Wyniki są wyświetlane tylko gdy `search_button_clicked == True`
   - Po `st.rerun()` ta zmienna jest `False`

## Plan naprawy

### KROK 1: Zapisać stan wyszukiwania w session_state
**Cel:** Zachować wyniki wyszukiwania po `st.rerun()`

**Działania:**
- Utworzyć klucz `search_results` w `st.session_state`
- Zapisać `filtered_df` w `st.session_state['search_results']` po wyszukiwaniu
- Zapisać `search_query_final` w `st.session_state['last_search_query']`
- Zapisać `case_sensitive` i `search_in_text` w session_state

**Lokalizacja:** `app.py` linie 94-95 (po wyszukiwaniu)

**Kod:**
```python
# Po wyszukiwaniu
st.session_state['search_results'] = filtered_df
st.session_state['last_search_query'] = search_query_final
st.session_state['last_case_sensitive'] = case_sensitive
st.session_state['last_search_in_text'] = search_in_text
```

### KROK 2: Wyświetlać wyniki z session_state jeśli są dostępne
**Cel:** Pokazywać wyniki nawet po `st.rerun()`

**Działania:**
- Sprawdzić czy `'search_results'` istnieje w `st.session_state`
- Jeśli tak, użyć tych wyników zamiast `filtered_df`
- Wyświetlić wyniki używając zapisanych wartości

**Lokalizacja:** `app.py` linie 97-207 (wyświetlanie wyników)

**Kod:**
```python
# Sprawdź czy są zapisane wyniki
if 'search_results' in st.session_state and len(st.session_state['search_results']) > 0:
    filtered_df = st.session_state['search_results']
    search_query_final = st.session_state.get('last_search_query', search_query)
    # Wyświetl wyniki...
```

### KROK 3: Usunąć `st.rerun()` i użyć bezpośredniego wyświetlania
**Cel:** Uniknąć przeładowania strony

**Działania:**
- Usunąć wszystkie wywołania `st.rerun()`
- Po zapisaniu tłumaczenia w `st.session_state`, sprawdzić czy klucz istnieje
- Jeśli tak, wyświetlić tłumaczenie bezpośrednio (bez przeładowania)
- Użyć `st.empty()` lub warunkowego wyświetlania

**Lokalizacja:** `app.py` linie 186, 199

**Kod:**
```python
# Zamiast st.rerun():
if is_valid:
    st.session_state[translation_key] = translated
    st.success("✅ Tłumaczenie zakończone pomyślnie!")
    # Usunąć st.rerun() - tłumaczenie zostanie wyświetlone w następnej iteracji
    # lub użyć st.experimental_rerun() jeśli konieczne
```

### KROK 4: Alternatywne rozwiązanie - użyć `st.experimental_rerun()` z zachowaniem stanu
**Cel:** Jeśli `st.rerun()` jest konieczne, zachować stan

**Działania:**
- Użyć `st.experimental_rerun()` zamiast `st.rerun()` (jeśli dostępne)
- LUB zapisać flagę w session_state przed `st.rerun()`
- Po przeładowaniu sprawdzić flagę i automatycznie wyświetlić wyniki

**Lokalizacja:** `app.py` linie 186, 199

**Kod:**
```python
# Przed st.rerun():
st.session_state['show_results'] = True
st.rerun()

# Na początku wyświetlania wyników:
if st.session_state.get('show_results', False):
    # Wyświetl wyniki automatycznie
```

### KROK 5: Najlepsze rozwiązanie - bezpośrednie wyświetlanie bez rerun
**Cel:** Uniknąć przeładowania całkowicie

**Działania:**
- Po kliknięciu przycisku, zapisać tłumaczenie w `st.session_state`
- Użyć `st.empty()` do dynamicznego wyświetlania
- LUB sprawdzić czy tłumaczenie istnieje i wyświetlić je natychmiast
- Usunąć wszystkie `st.rerun()`

**Lokalizacja:** `app.py` linie 171-204

**Kod:**
```python
# Po zapisaniu tłumaczenia:
if is_valid:
    st.session_state[translation_key] = translated
    st.success("✅ Tłumaczenie zakończone pomyślnie!")
    # Sprawdź ponownie czy tłumaczenie istnieje i wyświetl
    if translation_key in st.session_state:
        st.divider()
        st.markdown("**🇵🇱 Tłumaczenie (polski):**")
        # Wyświetl tłumaczenie...
```

## Rekomendowane rozwiązanie

**Najlepsze podejście:** KROK 1 + KROK 2 + KROK 5

1. Zapisać stan wyszukiwania w `session_state`
2. Wyświetlać wyniki z `session_state` jeśli są dostępne
3. Usunąć `st.rerun()` i użyć bezpośredniego wyświetlania tłumaczenia

## Walidacja rozwiązania

Po implementacji sprawdzić:
- [ ] Czy wyniki wyszukiwania pozostają widoczne po kliknięciu "Przetłumacz"
- [ ] Czy tłumaczenie jest wyświetlane bez przeładowania strony
- [ ] Czy aplikacja nie wraca do strony głównej
- [ ] Czy wszystkie funkcje działają poprawnie
- [ ] Czy nie ma błędów w konsoli

## Potencjalne problemy

### Problem 1: Konflikt kluczy w session_state
**Rozwiązanie:** Użyć unikalnych kluczy z prefiksami

### Problem 2: Wydajność przy wielu wynikach
**Rozwiązanie:** Ograniczyć liczbę zapisanych wyników (np. pierwsze 100)

### Problem 3: Stary stan wyszukiwania
**Rozwiązanie:** Czyścić `search_results` gdy użytkownik wykonuje nowe wyszukiwanie

## Kolejność wykonania

1. **KROK 1** - Zapisać stan wyszukiwania
2. **KROK 2** - Wyświetlać wyniki z session_state
3. **KROK 5** - Usunąć st.rerun() i użyć bezpośredniego wyświetlania
4. **Walidacja** - Przetestować wszystkie scenariusze

