# Plan naprawy błędu paginacji - session_state modification error

## 🔍 Analiza błędu

### Problem:
```
StreamlitAPIException: st.session_state.results_page cannot be modified after the widget with key results_page is instantiated.
```

### Lokalizacja błędu:
- **Linia 237:** `st.session_state[page_key] = page`
- **Linia 509:** `st.session_state[page_key] = page` (duplikacja)

### Przyczyna:

1. **Widget z kluczem automatycznie synchronizuje session_state**
   - Gdy tworzymy `st.number_input(key=page_key)`, Streamlit automatycznie synchronizuje wartość widgetu z `st.session_state[page_key]`
   - Nie możemy ręcznie modyfikować `st.session_state[page_key]` w tym samym przebiegu, w którym widget został utworzony

2. **Próba ręcznej modyfikacji po utworzeniu widgetu**
   - W linii 229-236 tworzymy widget: `st.number_input(..., key=page_key)`
   - W linii 237 próbujemy ustawić: `st.session_state[page_key] = page`
   - To powoduje błąd, ponieważ wartość jest już zarządzana przez widget

3. **Duplikacja problemu**
   - Ten sam błąd występuje w dwóch miejscach (linie 237 i 509)
   - Oba miejsca używają tej samej logiki

---

## 📋 Plan naprawy

### KROK 1: Usunąć ręczne ustawianie session_state po utworzeniu widgetu

**Lokalizacja:** `app.py` linie 237, 509

**Problem:**
```python
page = st.number_input(
    "Strona", 
    min_value=1, 
    max_value=total_pages, 
    value=st.session_state.get(page_key, 1),
    key=page_key,
    help=f"Wyświetlanie {RESULTS_PER_PAGE} wyników na stronę"
)
st.session_state[page_key] = page  # ❌ BŁĄD - nie można modyfikować
```

**Rozwiązanie:**
```python
page = st.number_input(
    "Strona", 
    min_value=1, 
    max_value=total_pages, 
    value=st.session_state.get(page_key, 1),
    key=page_key,
    help=f"Wyświetlanie {RESULTS_PER_PAGE} wyników na stronę"
)
# ✅ USUNĄĆ - wartość jest już automatycznie w session_state przez widget
```

**Działania:**
- Usunąć linię `st.session_state[page_key] = page` z linii 237
- Usunąć linię `st.session_state[page_key] = page` z linii 509

---

### KROK 2: Użyć wartości z widgetu bezpośrednio

**Lokalizacja:** `app.py` linie 243-246, 515-518

**Problem:**
- W niektórych miejscach używamy `st.session_state.get('results_page', 1)` zamiast zmiennej `page`
- To może powodować niespójności

**Rozwiązanie:**
- Używać zmiennej `page` bezpośrednio z widgetu
- Jeśli `page` nie jest dostępne (np. gdy `total_pages == 1`), użyć wartości domyślnej `1`

**Kod przed:**
```python
if total_pages > 1:
    page = st.number_input(...)
    st.session_state[page_key] = page  # ❌

# Później:
if total_pages > 1:
    start_idx = (page - 1) * RESULTS_PER_PAGE  # ✅ OK - używa zmiennej page
else:
    # ...
```

**Kod po:**
```python
if total_pages > 1:
    page = st.number_input(...)
    # ✅ Usunięto: st.session_state[page_key] = page

# Później:
if total_pages > 1:
    start_idx = (page - 1) * RESULTS_PER_PAGE  # ✅ Używa zmiennej page
else:
    page = 1  # Domyślna wartość
    results_to_show = filtered_df_limited
```

---

### KROK 3: Poprawić inicjalizację session_state

**Lokalizacja:** `app.py` linie 222-225, 494-497

**Problem:**
- Inicjalizujemy `st.session_state[page_key] = 1` przed utworzeniem widgetu
- To jest OK, ale możemy to uprościć

**Rozwiązanie:**
- Inicjalizacja jest poprawna - widget użyje wartości z `session_state` jeśli istnieje
- Możemy zostawić jak jest, ale upewnić się, że nie modyfikujemy po utworzeniu widgetu

**Kod:**
```python
page_key = 'results_page'
if page_key not in st.session_state:
    st.session_state[page_key] = 1  # ✅ OK - inicjalizacja przed widgetem

page = st.number_input(
    ...,
    value=st.session_state.get(page_key, 1),  # ✅ OK - używa wartości z session_state
    key=page_key,
    ...
)
# ❌ NIE MOŻEMY: st.session_state[page_key] = page
```

---

### KROK 4: Sprawdzić użycie w innych miejscach

**Lokalizacja:** `app.py` linia 516

**Problem:**
- W linii 516 używamy `st.session_state.get('results_page', 1)` zamiast zmiennej `page`
- To może być problem, jeśli `page` nie jest zdefiniowane w tym kontekście

**Rozwiązanie:**
- Upewnić się, że zmienna `page` jest dostępna w tym miejscu
- Jeśli nie, użyć `st.session_state.get('results_page', 1)` (to jest OK, bo nie modyfikujemy)

**Kod:**
```python
# W bloku gdzie jest widget:
if total_pages > 1:
    page = st.number_input(...)  # page jest zdefiniowane
    # ...
    start_idx = (page - 1) * RESULTS_PER_PAGE  # ✅ Używa page

# W innym bloku (gdzie widget może nie być):
if total_pages > 1:
    page = st.session_state.get('results_page', 1)  # ✅ OK - tylko odczyt
    start_idx = (page - 1) * RESULTS_PER_PAGE
```

---

## ✅ Lista kontrolna

Po implementacji sprawdzić:
- [ ] Usunięto `st.session_state[page_key] = page` z linii 237
- [ ] Usunięto `st.session_state[page_key] = page` z linii 509
- [ ] Zmienna `page` jest używana bezpośrednio z widgetu
- [ ] Inicjalizacja `session_state` przed widgetem jest poprawna
- [ ] Aplikacja działa bez błędów
- [ ] Paginacja działa poprawnie

---

## 🎯 Kolejność wykonania

1. **KROK 1** - Usunąć ręczne ustawianie session_state (linie 237, 509)
2. **KROK 2** - Upewnić się, że używamy zmiennej `page` bezpośrednio
3. **KROK 3** - Sprawdzić inicjalizację (już OK)
4. **KROK 4** - Sprawdzić użycie w innych miejscach
5. **Walidacja** - Przetestować paginację

---

## ⚠️ Uwagi

1. **Widget automatycznie synchronizuje session_state**
   - Gdy widget ma `key`, jego wartość jest automatycznie w `session_state[key]`
   - Nie musimy ręcznie ustawiać wartości

2. **Możemy tylko odczytywać, nie modyfikować**
   - `value = st.session_state.get(key, default)` - ✅ OK (odczyt)
   - `st.session_state[key] = value` - ❌ BŁĄD (modyfikacja po utworzeniu widgetu)

3. **Inicjalizacja przed widgetem jest OK**
   - Możemy ustawić `st.session_state[key] = value` PRZED utworzeniem widgetu
   - Widget użyje tej wartości jako wartości początkowej

---

## 📊 Oczekiwane rezultaty

Po implementacji:
- ✅ Błąd `cannot be modified after widget is instantiated` zniknie
- ✅ Paginacja będzie działać poprawnie
- ✅ Wartość strony będzie synchronizowana automatycznie przez widget
- ✅ Aplikacja będzie działać bez błędów

