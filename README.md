# 📧 Akta Epsteina - Wyszukiwarka Maili

Aplikacja webowa do wyszukiwania i przeglądania maili z automatycznym tłumaczeniem na żądanie.

## 📋 Funkcjonalności

- 🔍 **Wyszukiwanie w mailach** - wyszukiwanie po słowach kluczowych w treści maili
- 🌐 **Tłumaczenie zapytań** - automatyczne tłumaczenie polskich zapytań na angielski
- 📧 **Metadane maili** - wyświetlanie daty, nadawcy, odbiorcy i tematu
- 🇵🇱 **Tłumaczenie na żądanie** - tłumaczenie maili na polski po kliknięciu przycisku
- ✅ **Podwójna walidacja** - sprawdzanie poprawności tłumaczenia przed wyświetleniem
- 💾 **Cache tłumaczeń** - zapisywanie przetłumaczonych tekstów dla lepszej wydajności

## 🚀 Instalacja

### 1. Zainstaluj wymagane pakiety

```bash
pip install -r requirements.txt
```

### 2. (Opcjonalnie) Ustaw token Hugging Face

Aplikacja używa tokena Hugging Face do ładowania modeli tłumaczeniowych. Token nie jest wymagany dla publicznych modeli, ale pomaga w rate limiting i dostępie do większej liczby zasobów.

**Opcja A: Użyj zmiennej środowiskowej (ZALECANE)**

Windows PowerShell:
```powershell
$env:HF_TOKEN="twój_token_tutaj"
```

Windows CMD:
```cmd
set HF_TOKEN=twój_token_tutaj
```

Linux/Mac:
```bash
export HF_TOKEN="twój_token_tutaj"
```

**Opcja B: Token jest już w kodzie (fallback)**

Jeśli nie ustawisz zmiennej środowiskowej, aplikacja użyje tokena zapisanego w kodzie (sprawdź `translation_utils.py`).

**Jak uzyskać token:**
1. Zaloguj się na https://huggingface.co/
2. Przejdź do Settings > Access Tokens
3. Utwórz nowy token z uprawnieniami "Read"
4. Skopiuj token (zaczyna się od `hf_`)
5. Ustaw jako zmienną środowiskową lub zostaw w kodzie

## 💻 Uruchomienie lokalne

```bash
streamlit run app.py
```

Aplikacja otworzy się automatycznie w przeglądarce na `http://localhost:8501`

## 🌐 Publikacja w sieci (Streamlit Cloud)

Aplikacja jest gotowa do publikacji na Streamlit Community Cloud:

1. Przejdź na https://share.streamlit.io/
2. Zaloguj się przez GitHub
3. Kliknij "New app"
4. Wybierz repozytorium: `towmasjan/epstein-email-search`
5. Branch: `main`, Main file: `app.py`
6. Kliknij "Deploy!"

Szczegółowe instrukcje: [QUICK_DEPLOY.md](QUICK_DEPLOY.md) lub [DEPLOY.md](DEPLOY.md)

## 📚 Jak używać

### Wyszukiwanie maili

1. Wpisz słowo kluczowe w polu wyszukiwania (możesz pisać po polsku - zostanie przetłumaczone)
2. Wybierz opcje wyszukiwania:
   - "Szukaj w treści" - wyszukiwanie w treści maili
   - "Rozróżniaj wielkość liter" - wyszukiwanie z uwzględnieniem wielkości liter
3. Kliknij przycisk "🔍 Szukaj"
4. Przejrzyj wyniki - każdy mail pokazuje metadane (data, nadawca, odbiorca)

### Tłumaczenie maili

1. Otwórz mail klikając na expander
2. Kliknij przycisk "🔄 Przetłumacz na polski"
3. Poczekaj na zakończenie tłumaczenia
4. Tłumaczenie zostanie wyświetlone poniżej oryginału

## 🛠️ Technologie

- **Streamlit** - framework webowy do aplikacji danych
- **🤗 Datasets** - biblioteka do pracy ze zbiorami danych Hugging Face
- **🤗 Transformers** - modele tłumaczeniowe (Helsinki-NLP/opus-mt-en-pl)
- **deep-translator** - fallback tłumaczenia (Google Translator)
- **Pandas** - analiza i manipulacja danych

## 📦 Wymagane pakiety

Zobacz `requirements.txt` aby zobaczyć pełną listę zależności.

Główne zależności:
- streamlit >= 1.28.0
- datasets >= 2.14.0
- pandas >= 2.0.0
- transformers >= 4.30.0
- deep-translator >= 1.11.0
- huggingface-hub >= 0.17.0

## ⚠️ Uwagi

- Dataset jest ładowany automatycznie przy starcie aplikacji
- Tłumaczenie może zająć kilka sekund dla długich maili
- Wyniki wyszukiwania są ograniczone do pierwszych 100 maili
- Tłumaczenia są cache'owane w session_state dla lepszej wydajności

## 🔒 Bezpieczeństwo

⚠️ **WAŻNE:** Przed publikacją projektu na GitHub:
- Usuń token Hugging Face z kodu lub użyj zmiennych środowiskowych
- Jeśli już opublikowałeś z tokenem, wygeneruj nowy token na https://huggingface.co/settings/tokens

## 📄 Licencja

Aplikacja używa zbiorów danych z Hugging Face Hub, które mogą mieć różne licencje. Sprawdź licencję konkretnego zbioru danych przed użyciem komercyjnym.

## 🤝 Wkład

Możesz rozszerzyć aplikację o:
- Dodatkowe języki tłumaczenia
- Zaawansowane filtrowanie
- Eksport wyników
- Statystyki wyszukiwania
