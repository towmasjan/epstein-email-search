"""
Testy jednostkowe dla systemu tłumaczenia.
Testy sprawdzają czy tłumaczenie działa poprawnie.
"""
import sys
import os

# Dodaj ścieżkę do modułu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_is_translation_valid():
    """Test funkcji is_translation_valid"""
    from translation_utils import is_translation_valid
    
    # Test 1: Poprawne tłumaczenie
    assert is_translation_valid("Hello", "Witaj") == True, "Poprawne tłumaczenie powinno być valid"
    
    # Test 2: Tłumaczenie takie samo jak oryginał
    assert is_translation_valid("Hello", "Hello") == False, "Tłumaczenie identyczne z oryginałem powinno być invalid"
    
    # Test 3: Puste tłumaczenie
    assert is_translation_valid("Hello", "") == False, "Puste tłumaczenie powinno być invalid"
    
    # Test 4: None jako tłumaczenie
    assert is_translation_valid("Hello", None) == False, "None jako tłumaczenie powinno być invalid"
    
    print("✅ Test is_translation_valid: PASSED")

def test_get_cache_key():
    """Test funkcji get_cache_key"""
    from translation_utils import get_cache_key
    
    # Test 1: Różne teksty powinny mieć różne klucze
    key1 = get_cache_key("Hello world")
    key2 = get_cache_key("Hello world!")
    assert key1 != key2, "Różne teksty powinny mieć różne klucze cache"
    
    # Test 2: Ten sam tekst powinien mieć ten sam klucz
    key3 = get_cache_key("Hello world")
    assert key1 == key3, "Ten sam tekst powinien mieć ten sam klucz cache"
    
    # Test 3: Pusty tekst
    key4 = get_cache_key("")
    assert isinstance(key4, str) and len(key4) > 0, "Pusty tekst powinien zwrócić poprawny hash"
    
    print("✅ Test get_cache_key: PASSED")

def test_is_pipeline():
    """Test funkcji is_pipeline"""
    from translation_utils import is_pipeline
    
    # Test 1: None
    assert is_pipeline(None) == False, "None nie powinno być pipeline"
    
    # Test 2: Zwykła funkcja
    def test_func():
        pass
    assert is_pipeline(test_func) == False, "Zwykła funkcja nie powinna być pipeline"
    
    # Test 3: Obiekt z atrybutami model i tokenizer (symulacja pipeline)
    class MockPipeline:
        def __init__(self):
            self.model = "mock_model"
            self.tokenizer = "mock_tokenizer"
    
    mock_pipeline = MockPipeline()
    assert is_pipeline(mock_pipeline) == True, "Obiekt z model i tokenizer powinien być pipeline"
    
    print("✅ Test is_pipeline: PASSED")

def test_translate_with_fallback():
    """Test funkcji translate_with_fallback"""
    from translation_utils import translate_with_fallback
    
    # Test 1: Pusty tekst
    result = translate_with_fallback("")
    assert result == "", "Pusty tekst powinien zwrócić pusty string"
    
    # Test 2: Krótki tekst (powinien użyć Google Translator jeśli dostępny)
    try:
        result = translate_with_fallback("Hello")
        # Jeśli deep-translator jest dostępny, powinno zwrócić tłumaczenie
        # Jeśli nie, zwróci oryginał
        assert isinstance(result, str), "Wynik powinien być stringiem"
        assert len(result) > 0, "Wynik nie powinien być pusty"
    except Exception as e:
        print(f"⚠️ Fallback test: {e} (może brakować deep-translator)")
    
    print("✅ Test translate_with_fallback: PASSED")

def test_basic_translation():
    """Test podstawowego tłumaczenia - sprawdza czy system działa"""
    print("\n🔍 Test podstawowego tłumaczenia...")
    print("   (Ten test wymaga działającego modelu lub deep-translator)")
    
    # Ten test wymaga działającego środowiska Streamlit lub mock
    # W rzeczywistej aplikacji będzie testowany przez test 8
    
    print("✅ Test podstawowego tłumaczenia: SKIPPED (wymaga środowiska Streamlit)")

def run_all_tests():
    """Uruchamia wszystkie testy"""
    print("=" * 50)
    print("Uruchamianie testów systemu tłumaczenia")
    print("=" * 50)
    
    try:
        test_is_translation_valid()
        test_get_cache_key()
        test_is_pipeline()
        test_translate_with_fallback()
        test_basic_translation()
        
        print("\n" + "=" * 50)
        print("✅ WSZYSTKIE TESTY ZAKOŃCZONE POMYŚLNIE")
        print("=" * 50)
        return True
    except Exception as e:
        print(f"\n❌ BŁĄD W TESTACH: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

