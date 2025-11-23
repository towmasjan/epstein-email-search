"""Pobiera i optymalizuje obraz header.jpg."""
import io
import os

import requests
from PIL import Image

url = "https://ichef.bbci.co.uk/news/1024/cpsprodpb/3760/live/19eacef0-6477-11f0-8a1d-ab1c0c4a7e9f.jpg.webp"
output_path = "images/header.jpg"
max_width = 1600
quality = 85

try:
    print("📥 Pobieranie obrazu...")
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    print("🖼️ Przetwarzanie obrazu...")
    img = Image.open(io.BytesIO(response.content))
    print(f"   Oryginalny rozmiar: {img.width}x{img.height}px")

    # Konwertuj na RGB jeśli potrzeba
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Zmniejsz jeśli za duży
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        print(f"   Zmniejszono do: {img.width}x{img.height}px")

    # Utwórz folder
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Zapisz zoptymalizowany
    img.save(output_path, "JPEG", quality=quality, optimize=True)
    file_size = os.path.getsize(output_path) / 1024

    print(f"✅ Zapisano: {output_path}")
    print(f"📊 Rozmiar: {file_size:.1f} KB")
    print(f"📐 Wymiary: {img.width}x{img.height}px")

except Exception as e:
    print(f"❌ Błąd: {e}")
    import traceback

    traceback.print_exc()
