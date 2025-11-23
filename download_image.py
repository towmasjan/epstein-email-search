"""Skrypt pomocniczy do pobrania i zoptymalizowania obrazu header.jpg."""
import io
import os

import requests
from PIL import Image


def download_and_optimize_image(url, output_path="images/header.jpg", max_width=1600, quality=85):
    """
    Pobiera obraz z URL, optymalizuje go i zapisuje jako header.jpg.

    Args:
        url: URL obrazu do pobrania
        output_path: Ścieżka do zapisania obrazu
        max_width: Maksymalna szerokość obrazu (px)
        quality: Jakość JPG (1-100)
    """
    try:
        # Pobierz obraz
        print(f"📥 Pobieranie obrazu z {url}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Otwórz obraz
        img = Image.open(io.BytesIO(response.content))

        # Konwertuj na RGB jeśli potrzeba (dla JPG)
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
            img = background

        # Zmniejsz rozmiar jeśli za duży
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"📐 Zmniejszono rozmiar do {max_width}x{new_height}px")

        # Utwórz folder jeśli nie istnieje
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Zapisz zoptymalizowany obraz
        img.save(output_path, "JPEG", quality=quality, optimize=True)
        file_size = os.path.getsize(output_path) / 1024  # KB
        print(f"✅ Obraz zapisany: {output_path}")
        print(f"📊 Rozmiar pliku: {file_size:.1f} KB")
        print(f"📐 Wymiary: {img.width}x{img.height}px")

        return True
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Pobieranie i optymalizacja obrazu header.jpg")
    print("=" * 50)

    # Jeśli masz URL obrazu, wklej go tutaj:
    image_url = input("Wklej URL obrazu (lub naciśnij Enter aby pominąć): ").strip()

    if image_url:
        download_and_optimize_image(image_url)
    else:
        print("\n💡 Instrukcje:")
        print("1. Zapisz obraz jako 'header.jpg' w folderze 'images/'")
        print("2. Lub użyj tego skryptu z URL obrazu")
        print("3. Zalecany rozmiar: < 500KB, szerokość 1200-1600px")
