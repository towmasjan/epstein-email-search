# Folder na obrazy

## Jak dodać grafikę na stronę główną:

1. Umieść plik obrazu w tym folderze jako `header.jpg`
2. Zalecane formaty:
   - **JPG/JPEG** - najlepsza kompresja (zalecane)
   - **PNG** - jeśli potrzebujesz przezroczystości
   - **WebP** - najlepsza kompresja, ale mniejsza kompatybilność

3. Zalecany rozmiar:
   - Szerokość: 1200-1600px
   - Wysokość: 300-600px (w zależności od proporcji)
   - Rozmiar pliku: < 500KB (najlepiej < 200KB)

4. Optymalizacja obrazu:
   - Użyj narzędzi online jak TinyPNG, Squoosh, lub ImageOptim
   - Dla JPG: jakość 70-85% jest zazwyczaj wystarczająca
   - Dla PNG: użyj optymalizacji bezstratnej

## Uwaga:
- Streamlit automatycznie optymalizuje obrazy przy wyświetlaniu
- Obraz będzie responsywny (dopasuje się do szerokości ekranu)
- Jeśli plik nie istnieje, aplikacja po prostu go pominie
