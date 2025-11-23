# Instrukcja publikacji projektu na GitHub

## Krok 1: Zainstaluj Git (jeśli nie masz)

1. Pobierz Git z: https://git-scm.com/download/win
2. Zainstaluj używając domyślnych ustawień
3. Uruchom ponownie terminal/PowerShell

## Krok 2: Zainicjalizuj repozytorium Git

Otwórz terminal w folderze projektu i wykonaj:

```bash
git init
```

## Krok 3: Dodaj wszystkie pliki

```bash
git add .
```

## Krok 4: Utwórz pierwszy commit

```bash
git commit -m "Initial commit: Wyszukiwarka Maili Epsteina z tłumaczeniem"
```

## Krok 5: Utwórz repozytorium na GitHub

1. Zaloguj się na https://github.com
2. Kliknij przycisk "+" w prawym górnym rogu
3. Wybierz "New repository"
4. Wpisz nazwę repozytorium (np. `epstein-email-search`)
5. Wybierz "Public" lub "Private"
6. **NIE zaznaczaj** "Initialize this repository with a README"
7. Kliknij "Create repository"

## Krok 6: Połącz lokalne repozytorium z GitHub

GitHub pokaże Ci instrukcje. Wykonaj:

```bash
git remote add origin https://github.com/TWOJA_NAZWA_UZYTKOWNIKA/epstein-email-search.git
git branch -M main
git push -u origin main
```

**Uwaga:** Zamień `TWOJA_NAZWA_UZYTKOWNIKA` na swoją nazwę użytkownika GitHub.

## Krok 7: Jeśli potrzebujesz uwierzytelnienia

Jeśli Git poprosi o hasło, możesz użyć:
- **Personal Access Token** zamiast hasła (zalecane)
- Utwórz token na: https://github.com/settings/tokens
- Wybierz "Generate new token (classic)"
- Zaznacz uprawnienia: `repo` (pełny dostęp do repozytoriów)
- Skopiuj token i użyj go jako hasła

## Alternatywa: Użyj GitHub Desktop

Jeśli wolisz graficzny interfejs:

1. Pobierz GitHub Desktop: https://desktop.github.com/
2. Zaloguj się do swojego konta GitHub
3. Wybierz "File" > "Add Local Repository"
4. Wybierz folder projektu
5. Kliknij "Publish repository"

## Pliki które zostaną opublikowane

- `app.py` - główna aplikacja Streamlit
- `translation_utils.py` - moduł tłumaczenia
- `requirements.txt` - zależności Python
- `README.md` - dokumentacja
- `.gitignore` - pliki do ignorowania
- `test_translation.py` - testy jednostkowe

## Pliki które NIE zostaną opublikowane (zgodnie z .gitignore)

- `__pycache__/` - pliki cache Python
- `.streamlit/` - konfiguracja Streamlit
- Pliki środowiska wirtualnego
- Pliki IDE

## Ważne uwagi bezpieczeństwa

⚠️ **UWAGA:** Plik `translation_utils.py` zawiera token Hugging Face w kodzie. 

**Zalecane działania:**
1. Przed publikacją usuń token z kodu lub użyj zmiennych środowiskowych
2. Jeśli już opublikowałeś z tokenem, natychmiast wygeneruj nowy token na https://huggingface.co/settings/tokens
3. Użyj zmiennych środowiskowych dla tokenów w przyszłości

## Po publikacji

Po opublikowaniu projektu możesz:
- Udostępnić link do repozytorium
- Skonfigurować Streamlit Cloud do automatycznego wdrożenia
- Dodać więcej dokumentacji
- Utworzyć issues i pull requests

