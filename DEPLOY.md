# 🚀 Publikacja aplikacji na Streamlit Community Cloud

## Wymagania

- ✅ Repozytorium na GitHub (już masz: https://github.com/towmasjan/epstein-email-search)
- ✅ Plik `app.py` jako główny plik aplikacji
- ✅ Plik `requirements.txt` z zależnościami
- ✅ Plik `.streamlit/config.toml` dla konfiguracji (utworzony)

## Krok 1: Przygotowanie repozytorium

1. Upewnij się, że wszystkie pliki są w repozytorium:
   ```bash
   git add .
   git commit -m "Add Streamlit config and prepare for deployment"
   git push
   ```

## Krok 2: Publikacja na Streamlit Cloud

1. **Zaloguj się na Streamlit Cloud:**
   - Przejdź na https://share.streamlit.io/
   - Zaloguj się używając konta GitHub

2. **Utwórz nową aplikację:**
   - Kliknij "New app"
   - Wybierz repozytorium: `towmasjan/epstein-email-search`
   - Wybierz branch: `main`
   - Wpisz ścieżkę do pliku: `app.py`
   - Kliknij "Deploy!"

3. **Skonfiguruj zmienne środowiskowe (opcjonalnie):**
   - W ustawieniach aplikacji (Settings)
   - Dodaj zmienną środowiskową:
     - **Key:** `HF_TOKEN`
     - **Value:** Twój token Hugging Face (opcjonalnie, ale zalecane)

## Krok 3: Oczekiwanie na wdrożenie

- Streamlit Cloud automatycznie zainstaluje zależności z `requirements.txt`
- Pierwsze wdrożenie może zająć 5-10 minut
- Możesz obserwować postęp w logach

## Krok 4: Dostęp do aplikacji

- Po wdrożeniu otrzymasz link do aplikacji: `https://epstein-email-search.streamlit.app`
- Link będzie również dostępny w repozytorium GitHub

## ⚠️ Ważne uwagi

### Zmienne środowiskowe

Aplikacja używa tokena Hugging Face do ładowania modeli tłumaczeniowych. Możesz:

1. **Ustawić token w Streamlit Cloud (ZALECANE):**
   - Settings → Secrets → Add new secret
   - Key: `HF_TOKEN`
   - Value: Twój token Hugging Face

2. **Lub użyć bez tokena:**
   - Aplikacja będzie działać, ale może być wolniejsza
   - Niektóre modele mogą nie być dostępne

### Rozmiar modeli

- Modele tłumaczeniowe są duże (kilka GB)
- Pierwsze ładowanie może zająć kilka minut
- Streamlit Cloud cache'uje modele między sesjami

### Limity Streamlit Community Cloud

- **Darmowy plan:**
  - Aplikacje są publiczne
  - Limit czasu działania aplikacji
  - Ograniczenia zasobów CPU/RAM

## 🔧 Rozwiązywanie problemów

### Aplikacja nie uruchamia się

1. Sprawdź logi w Streamlit Cloud
2. Upewnij się, że `requirements.txt` zawiera wszystkie zależności
3. Sprawdź czy `app.py` jest w głównym katalogu

### Błędy importu

- Upewnij się, że wszystkie pliki Python są w repozytorium
- Sprawdź czy ścieżki importów są poprawne

### Problemy z tokenem Hugging Face

- Sprawdź czy token jest poprawnie ustawiony w Secrets
- Upewnij się, że token ma uprawnienia "Read"

## 📝 Alternatywne platformy

Jeśli Streamlit Cloud nie spełnia Twoich potrzeb, możesz użyć:

1. **Heroku** - https://www.heroku.com/
2. **Railway** - https://railway.app/
3. **Render** - https://render.com/
4. **AWS/GCP/Azure** - dla większych aplikacji

## 🎉 Gotowe!

Po wdrożeniu Twoja aplikacja będzie dostępna publicznie w internecie!
