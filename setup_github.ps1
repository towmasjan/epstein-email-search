# Skrypt do przygotowania projektu do publikacji na GitHub
# Uruchom: .\setup_github.ps1

Write-Host "Przygotowywanie projektu do publikacji na GitHub..." -ForegroundColor Green

# Sprawdz czy git jest zainstalowany
try {
    $gitVersion = git --version
    Write-Host "Git jest zainstalowany: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Git nie jest zainstalowany!" -ForegroundColor Red
    Write-Host "Pobierz Git z: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Po instalacji uruchom ponownie ten skrypt" -ForegroundColor Yellow
    exit 1
}

# Sprawdz czy repozytorium juz istnieje
if (Test-Path .git) {
    Write-Host "Repozytorium Git juz istnieje w tym folderze" -ForegroundColor Yellow
    $continue = Read-Host "Czy chcesz kontynuowac? (t/n)"
    if ($continue -ne "t") {
        exit 0
    }
} else {
    # Inicjalizuj repozytorium
    Write-Host "Inicjalizowanie repozytorium Git..." -ForegroundColor Cyan
    git init
    Write-Host "Repozytorium zainicjalizowane" -ForegroundColor Green
}

# Dodaj wszystkie pliki
Write-Host "Dodawanie plikow do repozytorium..." -ForegroundColor Cyan
git add .

# Sprawdz czy sa zmiany do commitowania
$status = git status --porcelain
if ($status) {
    Write-Host "Tworzenie commita..." -ForegroundColor Cyan
    git commit -m "Initial commit: Wyszukiwarka Maili Epsteina z tlumaczeniem"
    Write-Host "Commit utworzony" -ForegroundColor Green
} else {
    Write-Host "Brak zmian do commitowania" -ForegroundColor Yellow
}

# Sprawdz czy istnieje remote
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "Znaleziono remote: $remote" -ForegroundColor Green
    Write-Host "Aby opublikowac, uruchom: git push -u origin main" -ForegroundColor Yellow
} else {
    Write-Host "Instrukcje dalszych krokow:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Utworz nowe repozytorium na GitHub:" -ForegroundColor White
    Write-Host "   - Zaloguj sie na https://github.com" -ForegroundColor White
    Write-Host "   - Kliknij '+' > 'New repository'" -ForegroundColor White
    Write-Host "   - Wpisz nazwe (np. 'epstein-email-search')" -ForegroundColor White
    Write-Host "   - NIE zaznaczaj 'Initialize with README'" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Polacz lokalne repozytorium z GitHub:" -ForegroundColor White
    Write-Host "   git remote add origin https://github.com/TWOJA_NAZWA_UZYTKOWNIKA/NAZWA_REPO.git" -ForegroundColor Yellow
    Write-Host "   git branch -M main" -ForegroundColor Yellow
    Write-Host "   git push -u origin main" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "UWAGA: Przed publikacja usun token Hugging Face z translation_utils.py!" -ForegroundColor Red
    Write-Host "   Lub uzyj zmiennych srodowiskowych (zobacz README.md)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Gotowe! Projekt jest gotowy do publikacji." -ForegroundColor Green
