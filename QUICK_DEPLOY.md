# 🚀 Szybka publikacja na Streamlit Cloud

## Krok po kroku (5 minut)

### 1. Przejdź na Streamlit Cloud
👉 https://share.streamlit.io/

### 2. Zaloguj się przez GitHub
- Kliknij "Sign in with GitHub"
- Autoryzuj Streamlit Cloud

### 3. Utwórz nową aplikację
- Kliknij **"New app"**
- **Repository:** `towmasjan/epstein-email-search`
- **Branch:** `main`
- **Main file path:** `app.py`
- Kliknij **"Deploy!"**

### 4. (Opcjonalnie) Dodaj token Hugging Face
- W ustawieniach aplikacji kliknij **"Settings"**
- Przejdź do **"Secrets"**
- Dodaj:
  ```
  HF_TOKEN = "twój_token_tutaj"
  ```

### 5. Gotowe! 🎉
- Aplikacja będzie dostępna pod adresem: `https://epstein-email-search.streamlit.app`
- Pierwsze wdrożenie zajmie 5-10 minut

## ⚠️ Ważne
- Aplikacja jest publiczna (darmowy plan)
- Modele są duże - pierwsze ładowanie może zająć kilka minut
- Token Hugging Face jest opcjonalny, ale zalecany

