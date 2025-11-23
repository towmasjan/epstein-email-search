# Plan zmian aplikacji - Wyszukiwarka Maili Epsteina

## Analiza wymagań użytkownika

### Obecny stan:
- Aplikacja automatycznie tłumaczy wszystkie maile
- Tłumaczenie jest wyświetlane od razu w wynikach wyszukiwania
- Brak informacji o datach, nadawcy, odbiorcy
- Tłumaczenie działa na całym tekście maila

### Nowe wymagania:
1. **Usunąć automatyczne tłumaczenie** - aplikacja operuje tylko po angielsku
2. **Tłumaczyć tylko słowo z wyszukiwania** - przetłumaczyć zapytanie użytkownika
3. **Pokazywać oryginalny mail** - zawsze wyświetlać angielski tekst
4. **Tłumaczenie na żądanie** - tylko gdy użytkownik otworzy konkretny e-mail
5. **Podwójna walidacja** - sprawdzić tłumaczenie dwukrotnie przed wyświetleniem
6. **Metadane maili** - dodać daty, nadawcę, odbiorcę (krótki opis kontekstu)

## Plan implementacji

### KROK 1: Analiza struktury danych
**Cel:** Sprawdzić jakie kolumny są dostępne w zbiorze danych

**Działania:**
- Sprawdzić strukturę datasetu `tensonaut/EPSTEIN_FILES_20K`
- Zidentyfikować dostępne kolumny (text, filename, date, from, to, subject, etc.)
- Określić które kolumny można wyekstrahować z tekstu maila jeśli nie ma ich w datasetcie
- Utworzyć funkcję do parsowania metadanych z tekstu maila

**Walidacja:**
- Sprawdzić czy kolumny `text` i `filename` istnieją
- Sprawdzić czy można wyekstrahować datę, nadawcę, odbiorcę z tekstu
- Przetestować parsowanie na przykładowych mailach

### KROK 2: Usunięcie automatycznego tłumaczenia
**Cel:** Usunąć wszystkie automatyczne tłumaczenia z listy wyników

**Działania:**
- Usunąć checkbox "Automatyczne tłumaczenie" z sidebaru
- Usunąć checkbox "Pokaż oryginał obok tłumaczenia" z sidebaru
- Usunąć logikę tłumaczenia z pętli wyświetlania wyników (linie 110-155 w app.py)
- Zostawić tylko wyświetlanie oryginalnego tekstu po angielsku
- Usunąć import `translate_text` i `get_cache_key` jeśli nie będą używane w głównej pętli

**Walidacja:**
- Sprawdzić czy aplikacja wyświetla tylko angielski tekst
- Sprawdzić czy nie ma błędów związanych z usuniętymi funkcjami
- Sprawdzić czy wydajność się poprawiła (brak tłumaczeń)

### KROK 3: Tłumaczenie słowa z wyszukiwania
**Cel:** Przetłumaczyć zapytanie użytkownika z polskiego na angielski

**Działania:**
- Utworzyć funkcję `translate_search_query(query)` w `translation_utils.py`
- Funkcja tłumaczy zapytanie z polskiego na angielski (jeśli jest po polsku)
- Jeśli zapytanie jest już po angielsku, zwraca bez zmian
- Użyć tej funkcji przed wyszukiwaniem w bazie
- Wyświetlić zarówno oryginalne zapytanie jak i przetłumaczone (jeśli się różni)

**Walidacja:**
- Przetestować tłumaczenie polskich słów na angielskie
- Sprawdzić czy wyszukiwanie działa z przetłumaczonym zapytaniem
- Sprawdzić czy wyświetlanie zapytania działa poprawnie

### KROK 4: Wyświetlanie metadanych maili
**Cel:** Dodać informacje o dacie, nadawcy, odbiorcy w wynikach wyszukiwania

**Działania:**
- Utworzyć funkcję `extract_email_metadata(text)` do parsowania metadanych
- Funkcja wyciąga:
  - Datę (Date:, Sent:, etc.)
  - Nadawcę (From:, Sender:)
  - Odbiorcę (To:, Cc:, Bcc:)
  - Temat (Subject:)
- Wyświetlić te informacje w nagłówku każdego maila w wynikach
- Format: `📧 Od: [nadawca] | Do: [odbiorca] | Data: [data] | [filename]`

**Walidacja:**
- Sprawdzić czy metadane są poprawnie wyekstrahowane
- Sprawdzić czy wyświetlanie działa dla różnych formatów maili
- Sprawdzić obsługę przypadków gdy metadane nie są dostępne

### KROK 5: Tłumaczenie na żądanie (gdy użytkownik otworzy mail)
**Cel:** Tłumaczyć mail tylko gdy użytkownik kliknie i otworzy expander

**Działania:**
- W expanderze każdego maila dodać przycisk "Przetłumacz na polski"
- Przycisk uruchamia tłumaczenie tylko dla tego konkretnego maila
- Użyć podwójnej walidacji tłumaczenia:
  - Pierwsza walidacja: `is_translation_valid(original, translated)`
  - Druga walidacja: sprawdzenie czy tłumaczenie różni się od oryginału i nie zawiera błędów
- Wyświetlić tłumaczenie obok oryginału (lub w osobnym expanderze)
- Cache'ować tłumaczenie w session_state

**Walidacja:**
- Sprawdzić czy tłumaczenie uruchamia się tylko po kliknięciu przycisku
- Sprawdzić czy podwójna walidacja działa poprawnie
- Sprawdzić czy cache działa
- Sprawdzić czy wydajność jest dobra

### KROK 6: Podwójna walidacja tłumaczenia
**Cel:** Upewnić się że tłumaczenie jest poprawne przed wyświetleniem

**Działania:**
- Utworzyć funkcję `double_validate_translation(original, translated)` w `translation_utils.py`
- Funkcja wykonuje:
  1. Walidację 1: `is_translation_valid(original, translated)` - sprawdza czy różni się od oryginału
  2. Walidację 2: Sprawdza czy tłumaczenie nie zawiera błędów kodowania, czy ma sensowną długość, czy nie jest zbyt krótkie/długie
- Jeśli walidacja nie przejdzie, użyć fallback (Google Translator)
- Jeśli fallback też nie przejdzie, wyświetlić oryginał z komunikatem

**Walidacja:**
- Przetestować na różnych tekstach
- Sprawdzić czy błędne tłumaczenia są odrzucane
- Sprawdzić czy fallback działa

### KROK 7: Czyszczenie i porządkowanie kodu
**Cel:** Usunąć niepotrzebne części kodu i uporządkować

**Działania:**
- Usunąć nieużywane importy
- Usunąć nieużywane funkcje z `translation_utils.py` (jeśli są)
- Uporządkować strukturę plików
- Dodać komentarze do nowych funkcji
- Zaktualizować README.md z nowymi funkcjami

**Walidacja:**
- Sprawdzić czy nie ma błędów składniowych
- Sprawdzić czy wszystkie funkcje są używane
- Sprawdzić czy kod jest czytelny

## Analiza potencjalnych błędów

### Błąd 1: Brak kolumn z metadanymi w datasetcie
**Problem:** Dataset może nie mieć kolumn `date`, `from`, `to`
**Rozwiązanie:** Wyekstrahować metadane z tekstu maila używając regex

### Błąd 2: Tłumaczenie zapytania może zwrócić złe słowo
**Problem:** Tłumaczenie polskiego słowa może nie pasować do kontekstu
**Rozwiązanie:** Wyświetlić zarówno oryginalne jak i przetłumaczone zapytanie, pozwolić użytkownikowi wybrać

### Błąd 3: Parsowanie metadanych może nie działać dla wszystkich formatów
**Problem:** Maile mogą mieć różne formaty nagłówków
**Rozwiązanie:** Obsłużyć różne formaty (Date:, Sent:, From:, To:, etc.)

### Błąd 4: Podwójna walidacja może odrzucić poprawne tłumaczenia
**Problem:** Zbyt restrykcyjna walidacja
**Rozwiązanie:** Użyć elastycznych kryteriów, logować powody odrzucenia

### Błąd 5: Wydajność przy tłumaczeniu długich maili
**Problem:** Tłumaczenie długich maili może być wolne
**Rozwiązanie:** Dzielić na fragmenty, pokazywać progress bar

## Kolejność wykonania

1. **KROK 1** - Analiza struktury danych
2. **KROK 2** - Usunięcie automatycznego tłumaczenia
3. **KROK 3** - Tłumaczenie słowa z wyszukiwania
4. **KROK 4** - Wyświetlanie metadanych
5. **KROK 5** - Tłumaczenie na żądanie
6. **KROK 6** - Podwójna walidacja
7. **KROK 7** - Czyszczenie kodu

## WALIDACJA PLANU

### ✅ Walidacja 1: Kompletność wymagań
- [x] Wszystkie wymagania użytkownika są uwzględnione w planie
- [x] Każdy krok ma jasno określony cel i działania
- [x] Kolejność wykonania jest logiczna

### ✅ Walidacja 2: Realność implementacji
- [x] Wszystkie funkcje są możliwe do zaimplementowania
- [x] Używamy istniejących bibliotek (transformers, deep-translator)
- [x] Nie wymagamy nowych zewnętrznych zależności

### ✅ Walidacja 3: Zgodność z architekturą
- [x] Zmiany nie naruszają podstawowej struktury aplikacji
- [x] Możemy użyć istniejących funkcji z translation_utils.py
- [x] Struktura plików pozostaje czytelna

## ANALIZA BŁĘDÓW - SZCZEGÓŁOWA

### Błąd 1: Brak kolumn z metadanymi w datasetcie
**Problem:** Dataset może nie mieć kolumn `date`, `from`, `to`, `subject`
**Prawdopodobieństwo:** WYSOKIE - większość datasetów ma tylko `text` i `filename`
**Wpływ:** ŚREDNI - możemy wyekstrahować z tekstu
**Rozwiązanie:**
- Utworzyć funkcję `extract_email_metadata(text)` używającą regex
- Obsłużyć różne formaty nagłówków email (RFC 5322)
- Obsłużyć przypadki gdy metadane nie są dostępne (zwrócić "N/A")

**Kod rozwiązania:**
```python
def extract_email_metadata(text):
    """Wyciąga metadane z tekstu maila"""
    metadata = {
        'date': 'N/A',
        'from': 'N/A',
        'to': 'N/A',
        'subject': 'N/A'
    }

    # Wzorce regex dla różnych formatów
    date_patterns = [
        r'Date:\s*(.+?)(?:\n|$)',
        r'Sent:\s*(.+?)(?:\n|$)',
        r'Date\s*:\s*(.+?)(?:\n|$)'
    ]
    # ... podobnie dla from, to, subject
    return metadata
```

### Błąd 2: Tłumaczenie zapytania może zwrócić złe słowo
**Problem:** Tłumaczenie polskiego słowa może nie pasować do kontekstu (np. "sąd" -> "court" vs "judgment")
**Prawdopodobieństwo:** ŚREDNIE - zależy od kontekstu
**Wpływ:** NISKIE - użytkownik może użyć angielskiego zapytania
**Rozwiązanie:**
- Wyświetlić zarówno oryginalne jak i przetłumaczone zapytanie
- Pozwolić użytkownikowi wybrać które użyć
- Dodać checkbox "Użyj przetłumaczonego zapytania"

### Błąd 3: Parsowanie metadanych może nie działać dla wszystkich formatów
**Problem:** Maile mogą mieć różne formaty nagłówków (RFC 5322, MIME, etc.)
**Prawdopodobieństwo:** WYSOKIE - różne źródła danych
**Wpływ:** ŚREDNI - metadane są opcjonalne
**Rozwiązanie:**
- Obsłużyć najczęstsze formaty (Date:, From:, To:, Subject:)
- Obsłużyć wieloliniowe nagłówki (kontynuacja z spacją/tabem)
- Obsłużyć kodowanie znaków (UTF-8, ISO-8859-1)
- Zwrócić "N/A" jeśli nie można wyekstrahować

### Błąd 4: Podwójna walidacja może odrzucić poprawne tłumaczenia
**Problem:** Zbyt restrykcyjna walidacja może odrzucić poprawne tłumaczenia
**Prawdopodobieństwo:** ŚREDNIE - zależy od kryteriów
**Wpływ:** ŚREDNI - użytkownik może zobaczyć oryginał zamiast tłumaczenia
**Rozwiązanie:**
- Użyć elastycznych kryteriów walidacji
- Logować powody odrzucenia (w trybie debug)
- Pozwolić użytkownikowi wymusić wyświetlenie tłumaczenia (przycisk "Pokaż mimo wszystko")

### Błąd 5: Wydajność przy tłumaczeniu długich maili
**Problem:** Tłumaczenie długich maili może być wolne (kilka sekund)
**Prawdopodobieństwo:** WYSOKIE - długie maile są częste
**Wpływ:** ŚREDNI - użytkownik musi czekać
**Rozwiązanie:**
- Dzielić na fragmenty (już mamy `split_text_into_chunks`)
- Pokazywać progress bar podczas tłumaczenia
- Cache'ować wyniki (już mamy cache)
- Ograniczyć długość tłumaczonego tekstu (np. pierwsze 5000 znaków)

### Błąd 6: Session state może się przepełnić
**Problem:** Cache tłumaczeń w session_state może zajmować dużo pamięci
**Prawdopodobieństwo:** NISKIE - Streamlit ma limity
**Wpływ:** NISKIE - aplikacja może zwolnić
**Rozwiązanie:**
- Ograniczyć rozmiar cache (np. max 50 tłumaczeń)
- Usunąć najstarsze wpisy gdy cache jest pełny
- Użyć `get_cache_key` dla unikalnych kluczy

### Błąd 7: Tłumaczenie zapytania może nie działać dla fraz
**Problem:** Tłumaczenie całej frazy może zwrócić złą kolejność słów
**Prawdopodobieństwo:** ŚREDNIE - zależy od modelu
**Wpływ:** NISKIE - użytkownik może użyć angielskiego
**Rozwiązanie:**
- Tłumaczyć słowo po słowie dla krótkich fraz
- Dla dłuższych fraz użyć pełnego tłumaczenia
- Wyświetlić oba warianty

## KOLEJNA WALIDACJA

### ✅ Walidacja 4: Analiza ryzyka
- [x] Wszystkie potencjalne błędy są zidentyfikowane
- [x] Każdy błąd ma rozwiązanie
- [x] Rozwiązania są realne do implementacji

### ✅ Walidacja 5: Zgodność z wymaganiami użytkownika
- [x] Plan spełnia wszystkie wymagania
- [x] Nie ma konfliktów między wymaganiami
- [x] Kolejność wykonania jest optymalna

### ✅ Walidacja 6: Gotowość do implementacji
- [x] Plan jest szczegółowy i kompletny
- [x] Wszystkie funkcje są opisane
- [x] Kod przykładowy jest dostępny
- [x] Możemy rozpocząć implementację

## Weryfikacja końcowa

Po zakończeniu wszystkich kroków:
- [ ] Aplikacja wyświetla tylko angielskie maile w wynikach
- [ ] Zapytanie jest tłumaczone z polskiego na angielski
- [ ] Metadane (data, nadawca, odbiorca) są wyświetlane
- [ ] Tłumaczenie uruchamia się tylko po kliknięciu przycisku
- [ ] Podwójna walidacja działa poprawnie
- [ ] Kod jest uporządkowany i czytelny
- [ ] Nie ma błędów składniowych
- [ ] Wydajność jest dobra
