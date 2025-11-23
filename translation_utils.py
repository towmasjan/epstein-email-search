"""
Modu┼é do t┼éumaczenia tekstu z angielskiego na polski u┼╝ywaj─ůc modelu Hugging Face.
Zawiera r├│wnie┼╝ funkcje pomocnicze do ekstrakcji metadanych z maili.
"""
import streamlit as st
from transformers import pipeline  # type: ignore
import re
import os
import hashlib
from typing import Dict, Optional

# Token Hugging Face
# PRIORYTET: 1. Zmienna ┼Ťrodowiskowa HF_TOKEN lub HUGGINGFACE_TOKEN
#           2. Token poni┼╝ej (fallback)
# 
# Jak uzyska─ç token:
# 1. Zaloguj si─Ö na https://huggingface.co/
# 2. Przejd┼║ do Settings > Access Tokens
# 3. Utw├│rz nowy token z uprawnieniami "Read"
# 4. Skopiuj token i ustaw jako zmienn─ů ┼Ťrodowiskow─ů:
#    Windows PowerShell: $env:HF_TOKEN="tw├│j_token"
#    Linux/Mac: export HF_TOKEN="tw├│j_token"
#    Lub dodaj do pliku .env
HF_TOKEN = None  # Token musi być ustawiony jako zmienna środowiskowa

# Funkcje pomocnicze
def is_pipeline(translator):
    """
    Sprawdza czy translator jest pipeline z transformers.
    Pipeline ma atrybuty 'model' i 'tokenizer'.
    """
    if translator is None:
        return False
    return hasattr(translator, 'model') and hasattr(translator, 'tokenizer')

def is_translation_valid(original, translated):
    """
    Sprawdza czy t┼éumaczenie jest poprawne i r├│┼╝ni si─Ö od orygina┼éu.
    
    Args:
        original: Oryginalny tekst
        translated: Przet┼éumaczony tekst
    
    Returns:
        True je┼Ťli t┼éumaczenie jest poprawne, False w przeciwnym razie
    """
    if not translated or not isinstance(translated, str):
        return False
    
    if not translated.strip():
        return False
    
    # Sprawd┼║ czy t┼éumaczenie r├│┼╝ni si─Ö od orygina┼éu
    if translated.strip().lower() == original.strip().lower():
        return False
    
    # Sprawd┼║ czy nie zawiera dziwnych znak├│w (znaki kontrolne)
    if len(translated) > 0:
        # Sprawd┼║ pierwsze 50 znak├│w - je┼Ťli wszystkie s─ů znakami kontrolnymi, to problem
        control_chars = [c for c in translated[:50] if ord(c) > 127 and ord(c) < 160]
        if len(control_chars) == len(translated[:50]) and len(translated[:50]) > 0:
            return False
    
    return True

def get_cache_key(text):
    """
    Generuje unikalny klucz cache dla tekstu u┼╝ywaj─ůc hash MD5.
    
    Args:
        text: Tekst do zahashowania
    
    Returns:
        Hex string hash MD5
    """
    if not text:
        return hashlib.md5(b"").hexdigest()
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# Cache dla modelu - ┼éadujemy raz
@st.cache_resource
def load_translator():
    """┼üaduje model t┼éumaczeniowy - cache'owany przez Streamlit"""
    # U┼╝yj tokena z zmiennej ┼Ťrodowiskowej lub fallback z kodu
    # Token nie jest wymagany dla publicznych modeli, ale pomaga w rate limiting
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or HF_TOKEN
    
    # Informacja o tokenie (ukryta dla u┼╝ytkownika)
    # if hf_token and hf_token != "":
    #     token_source = "zmiennej ┼Ťrodowiskowej" if os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") else "kodu"
    #     st.info(f"­čöĹ U┼╝ywam tokena Hugging Face z {token_source}")
    
    # Lista modeli do wypr├│bowania
    model_options = [
        "Helsinki-NLP/opus-mt-en-pl",
        "facebook/mbart-large-50-many-to-many-mmt",  # Alternatywny model
    ]
    
    for model_name in model_options:
        try:
            # Opcja 1: U┼╝yj MarianMTModel dla modeli Helsinki-NLP
            if "Helsinki-NLP" in model_name:
                try:
                    from transformers import MarianMTModel, MarianTokenizer  # type: ignore
                    
                    # st.info(f"­čöä ┼üadowanie modelu {model_name}...")  # Ukryte dla u┼╝ytkownika
                    tokenizer = MarianTokenizer.from_pretrained(
                        model_name,
                        token=hf_token
                    )
                    model = MarianMTModel.from_pretrained(
                        model_name,
                        token=hf_token
                    )
                    
                    def translate_func(text, max_length=512):
                        try:
                            # Upewnij si─Ö, ┼╝e tekst jest stringiem
                            if not isinstance(text, str):
                                text = str(text)
                            
                            # Oczy┼Ť─ç tekst z problematycznych znak├│w
                            text = text.strip()
                            if not text:
                                return [{"translation_text": ""}]
                            
                            # Tokenizuj tekst
                            inputs = tokenizer(
                                text, 
                                return_tensors="pt", 
                                padding=True, 
                                truncation=True, 
                                max_length=max_length
                            )
                            
                            # Generuj t┼éumaczenie
                            outputs = model.generate(
                                **inputs, 
                                max_length=max_length, 
                                num_beams=4,
                                early_stopping=True
                            )
                            
                            # Dekoduj wynik
                            translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
                            
                            # Upewnij si─Ö, ┼╝e wynik jest poprawnym stringiem
                            if not isinstance(translated, str):
                                translated = str(translated)
                            
                            translated = translated.strip()
                            
                            # Sprawd┼║ czy t┼éumaczenie jest poprawne u┼╝ywaj─ůc funkcji walidacyjnej
                            if not is_translation_valid(text, translated):
                                # T┼éumaczenie nie jest poprawne - zwr├│─ç orygina┼é (fallback zostanie u┼╝yty w translate_text)
                                # st.warning("ÔÜá´ŞĆ Model zwr├│ci┼é nieprawid┼éowe t┼éumaczenie - u┼╝yj─Ö fallback")  # Ukryte
                                return [{"translation_text": text}]
                            
                            return [{"translation_text": translated}]
                        except Exception as e:
                            # W przypadku b┼é─Ödu zwr├│─ç orygina┼é
                            return [{"translation_text": text}]
                    
                    # st.success(f"Ôťů Model {model_name} za┼éadowany pomy┼Ťlnie!")  # Ukryte
                    return translate_func
                except Exception as e1:
                    # st.warning(f"ÔÜá´ŞĆ Nie uda┼éo si─Ö za┼éadowa─ç {model_name} metod─ů MarianMT: {str(e1)[:200]}")  # Ukryte
                    # Spr├│buj pipeline
                    try:
                        translator = pipeline(
                            "translation",
                            model=model_name,
                            device=-1,
                            token=hf_token
                        )
                        # st.success(f"Ôťů Model {model_name} za┼éadowany przez pipeline!")  # Ukryte
                        return translator
                    except Exception as e2:
                        # st.warning(f"ÔÜá´ŞĆ Pipeline r├│wnie┼╝ nie zadzia┼éa┼é: {str(e2)[:200]}")  # Ukryte
                        continue
            else:
                # Dla innych modeli u┼╝yj standardowego pipeline
                try:
                    translator = pipeline(
                        "translation",
                        model=model_name,
                        device=-1,
                        token=hf_token,
                        use_auth_token=True
                    )
                    # st.success(f"Ôťů Model {model_name} za┼éadowany pomy┼Ťlnie!")  # Ukryte
                    return translator
                except Exception as e:
                    # st.warning(f"ÔÜá´ŞĆ Nie uda┼éo si─Ö za┼éadowa─ç {model_name}: {str(e)[:200]}")  # Ukryte
                    continue
        except Exception as e:
            # st.warning(f"ÔÜá´ŞĆ B┼é─ůd przy pr├│bie za┼éadowania {model_name}: {str(e)[:200]}")  # Ukryte
            continue
    
    # Je┼Ťli ┼╝aden model nie zadzia┼éa┼é - ukryte dla u┼╝ytkownika
    # st.error("ÔŁî Nie uda┼éo si─Ö za┼éadowa─ç ┼╝adnego modelu t┼éumaczeniowego")
    # st.info("­čĺí Wskaz├│wki:")
    # st.info("1. Sprawd┼║ po┼é─ůczenie z internetem")
    # st.info("2. Sprawd┼║ czy token jest poprawny")
    # st.info("3. Spr├│buj zaktualizowa─ç transformers: pip install --upgrade transformers")
    return None

def split_text_into_chunks(text, max_length=500):
    """Dzieli tekst na mniejsze fragmenty dla modelu t┼éumaczeniowego"""
    # Dzielimy na zdania
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]

def translate_text(text, translator=None):
    """
    T┼éumaczy tekst z angielskiego na polski.
    U┼╝ywa cache w session state, aby nie t┼éumaczy─ç tego samego tekstu dwa razy.
    """
    if not text or not text.strip():
        return text
    
    # Inicjalizuj cache t┼éumacze┼ä je┼Ťli nie istnieje
    if 'translation_cache' not in st.session_state:
        st.session_state['translation_cache'] = {}
    
    # Sprawd┼║ cache
    cache_key = get_cache_key(text)  # U┼╝ywamy hash MD5 dla unikalnych kluczy
    if cache_key in st.session_state['translation_cache']:
        return st.session_state['translation_cache'][cache_key]
    
    # Je┼Ťli nie ma w cache, t┼éumacz
    try:
        if translator is None:
            # Sprawd┼║ czy translator jest ju┼╝ w session_state
            if 'translator' not in st.session_state:
                st.session_state['translator'] = load_translator()
            translator = st.session_state['translator']
        
        if translator is None:
            # Spr├│buj u┼╝y─ç alternatywnej biblioteki
            return translate_with_fallback(text)
        
        # Dla d┼éugich tekst├│w dzielimy na fragmenty
        if len(text) > 500:
            chunks = split_text_into_chunks(text, max_length=500)
            translated_chunks = []
            
            for chunk in chunks:
                if chunk.strip():
                    try:
                        # Sprawd┼║ czy translator jest funkcj─ů czy pipeline
                        if is_pipeline(translator):
                            # To jest pipeline
                            result = translator(chunk, max_length=512)
                        else:
                            # To jest nasza funkcja translate_func
                            result = translator(chunk, max_length=512)
                        
                        # Obs┼éuga r├│┼╝nych format├│w odpowiedzi
                        translated_text_chunk = None
                        if isinstance(result, list) and len(result) > 0:
                            if isinstance(result[0], dict) and 'translation_text' in result[0]:
                                translated_text_chunk = result[0]['translation_text']
                            elif isinstance(result[0], str):
                                translated_text_chunk = result[0]
                        elif isinstance(result, dict) and 'translation_text' in result:
                            translated_text_chunk = result['translation_text']
                        elif isinstance(result, str):
                            translated_text_chunk = result
                        
                        # Sprawd┼║ czy t┼éumaczenie jest poprawne u┼╝ywaj─ůc funkcji walidacyjnej
                        if is_translation_valid(chunk, translated_text_chunk):
                            translated_chunks.append(translated_text_chunk)
                        else:
                            # Je┼Ťli t┼éumaczenie nie jest poprawne, u┼╝yj fallback
                            fallback_trans = translate_with_fallback(chunk)
                            translated_chunks.append(fallback_trans if fallback_trans != chunk else chunk)
                    except Exception as e:
                        # st.warning(f"B┼é─ůd t┼éumaczenia fragmentu: {e}")  # Ukryte
                        # U┼╝yj fallback zamiast orygina┼éu
                        fallback_trans = translate_with_fallback(chunk)
                        translated_chunks.append(fallback_trans if fallback_trans != chunk else chunk)
            
            translated_text = " ".join(translated_chunks)
        else:
            # Dla kr├│tszych tekst├│w t┼éumaczymy ca┼éo┼Ť─ç
            try:
                # Sprawd┼║ czy translator jest funkcj─ů czy pipeline
                if is_pipeline(translator):
                    # To jest pipeline
                    result = translator(text, max_length=512)
                else:
                    # To jest nasza funkcja translate_func
                    result = translator(text, max_length=512)
                
                # Obs┼éuga r├│┼╝nych format├│w odpowiedzi
                translated_text = None
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'translation_text' in result[0]:
                        translated_text = result[0]['translation_text']
                    elif isinstance(result[0], str):
                        translated_text = result[0]
                elif isinstance(result, dict) and 'translation_text' in result:
                    translated_text = result['translation_text']
                elif isinstance(result, str):
                    translated_text = result
                
                # Sprawd┼║ czy t┼éumaczenie jest poprawne u┼╝ywaj─ůc funkcji walidacyjnej
                if not is_translation_valid(text, translated_text):
                    # Je┼Ťli t┼éumaczenie nie jest poprawne, u┼╝yj fallback
                    translated_text = translate_with_fallback(text)
            except Exception as e:
                # st.warning(f"B┼é─ůd t┼éumaczenia: {e}")  # Ukryte
                # U┼╝yj fallback zamiast orygina┼éu
                translated_text = translate_with_fallback(text)
        
        # Zapisz w cache
        st.session_state['translation_cache'][cache_key] = translated_text
        
        return translated_text
        
    except Exception as e:
        # st.warning(f"B┼é─ůd podczas t┼éumaczenia: {e}")  # Ukryte
        # Spr├│buj fallback
        return translate_with_fallback(text)

def translate_with_fallback(text):
    """Alternatywna metoda t┼éumaczenia u┼╝ywaj─ůca deep-translator jako fallback"""
    if not text or not text.strip():
        return text
    
    # Sprawd┼║ cache dla fallback
    cache_key = f"fallback_{get_cache_key(text)}"
    if 'translation_cache' in st.session_state and cache_key in st.session_state['translation_cache']:
        return st.session_state['translation_cache'][cache_key]
    
    try:
        # Spr├│buj u┼╝y─ç deep-translator
        from deep_translator import GoogleTranslator  # type: ignore
        
        # Dla d┼éugich tekst├│w dzielimy na fragmenty
        if len(text) > 5000:
            chunks = split_text_into_chunks(text, max_length=4500)
            translated_chunks = []
            translator = GoogleTranslator(source='en', target='pl')
            
            for chunk in chunks:
                if chunk.strip():
                    try:
                        translated_chunk = translator.translate(chunk)
                        if translated_chunk and translated_chunk != chunk:
                            translated_chunks.append(translated_chunk)
                        else:
                            translated_chunks.append(chunk)
                    except Exception as e:
                        translated_chunks.append(chunk)
            
            translated = " ".join(translated_chunks)
        else:
            translator = GoogleTranslator(source='en', target='pl')
            translated = translator.translate(text)
        
        if translated and translated != text and translated.strip():
            # Zapisz w cache
            if 'translation_cache' not in st.session_state:
                st.session_state['translation_cache'] = {}
            st.session_state['translation_cache'][cache_key] = translated
            return translated
    except ImportError:
        # st.info("­čĺí Zainstaluj deep-translator: pip install deep-translator")  # Ukryte
        pass
    except Exception as e:
        # st.warning(f"ÔÜá´ŞĆ B┼é─ůd t┼éumaczenia fallback (Google Translator): {str(e)}")  # Ukryte
        # st.info("­čĺí T┼éumaczenie nie jest dost─Öpne - wy┼Ťwietlany jest orygina┼é")  # Ukryte
        pass
    
    # Je┼Ťli wszystko zawiedzie, zwr├│─ç orygina┼é
    return text

def extract_email_metadata(text: str) -> Dict[str, str]:
    """
    Wyci─ůga metadane z tekstu maila (data, nadawca, odbiorca, temat).
    
    Args:
        text: Tekst maila
    
    Returns:
        S┼éownik z metadanymi: {'date': ..., 'from': ..., 'to': ..., 'subject': ...}
    """
    metadata = {
        'date': 'N/A',
        'from': 'N/A',
        'to': 'N/A',
        'subject': 'N/A'
    }
    
    if not text:
        return metadata
    
    # Wzorce regex dla r├│┼╝nych format├│w nag┼é├│wk├│w email
    # Date: r├│┼╝ne formaty
    date_patterns = [
        r'Date:\s*(.+?)(?:\n|$)',
        r'Sent:\s*(.+?)(?:\n|$)',
        r'Date\s*:\s*(.+?)(?:\n|$)',
        r'On\s+(.+?)\s+wrote:'
    ]
    
    # From: nadawca
    from_patterns = [
        r'From:\s*(.+?)(?:\n|$)',
        r'Sender:\s*(.+?)(?:\n|$)',
        r'From\s*:\s*(.+?)(?:\n|$)'
    ]
    
    # To: odbiorca
    to_patterns = [
        r'To:\s*(.+?)(?:\n|$)',
        r'Recipient:\s*(.+?)(?:\n|$)',
        r'To\s*:\s*(.+?)(?:\n|$)'
    ]
    
    # Subject: temat
    subject_patterns = [
        r'Subject:\s*(.+?)(?:\n|$)',
        r'Subject\s*:\s*(.+?)(?:\n|$)',
        r'Re:\s*(.+?)(?:\n|$)'
    ]
    
    # Szukaj w pierwszych 2000 znakach (nag┼é├│wki s─ů na pocz─ůtku)
    header_text = text[:2000] if len(text) > 2000 else text
    
    # Wyci─ůgnij dat─Ö
    for pattern in date_patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            metadata['date'] = match.group(1).strip()
            break
    
    # Wyci─ůgnij nadawc─Ö
    for pattern in from_patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            metadata['from'] = match.group(1).strip()
            break
    
    # Wyci─ůgnij odbiorc─Ö
    for pattern in to_patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            metadata['to'] = match.group(1).strip()
            break
    
    # Wyci─ůgnij temat
    for pattern in subject_patterns:
        match = re.search(pattern, header_text, re.IGNORECASE | re.MULTILINE)
        if match:
            metadata['subject'] = match.group(1).strip()
            break
    
    # Oczy┼Ť─ç metadane (usu┼ä znaki specjalne, skr├│─ç je┼Ťli za d┼éugie)
    for key in metadata:
        if metadata[key] != 'N/A':
            # Usu┼ä znaki nowej linii i nadmiarowe spacje
            metadata[key] = re.sub(r'\s+', ' ', metadata[key]).strip()
            # Skr├│─ç je┼Ťli za d┼éugie (max 100 znak├│w)
            if len(metadata[key]) > 100:
                metadata[key] = metadata[key][:97] + '...'
    
    return metadata

def classify_content_type(text: str) -> tuple[str, str]:
    """
    Klasyfikuje typ zawartości tekstu.
    
    Args:
        text: Tekst do klasyfikacji
    
    Returns:
        Tuple (typ, etykieta) gdzie:
        - typ: 'email', 'metadata', 'json', 'other'
        - etykieta: Opisowa nazwa typu
    """
    if not text or len(text.strip()) < 10:
        return ('other', 'Pusty tekst')
    
    text_lower = text.lower()
    text_stripped = text.strip()
    
    # Sprawdź czy to JSON
    if text_stripped.startswith('{') or text_stripped.startswith('['):
        # Sprawdź czy to wygląda jak JSON (ma klucze i wartości)
        if ('"' in text or "'" in text) and (':' in text or ',' in text):
            return ('metadata', '📋 Metadane/JSON')
    
    # Sprawdź czy to wygląda jak mail
    has_email_headers = (
        bool(re.search(r'From:\s*', text, re.IGNORECASE)) or
        bool(re.search(r'To:\s*', text, re.IGNORECASE)) or
        bool(re.search(r'Subject:\s*', text, re.IGNORECASE)) or
        bool(re.search(r'Date:\s*', text, re.IGNORECASE))
    )
    
    # Sprawdź czy zawiera typowe elementy maila
    has_email_content = (
        bool(re.search(r'@', text)) or  # Adres email
        bool(re.search(r'Dear\s+', text, re.IGNORECASE)) or  # "Dear..."
        bool(re.search(r'Best regards', text, re.IGNORECASE)) or
        bool(re.search(r'Sincerely', text, re.IGNORECASE))
    )
    
    if has_email_headers or (has_email_content and len(text) > 100):
        return ('email', '📧 Mail')
    
    # Sprawdź czy to metadane (strukturalne dane)
    if any(keyword in text_lower for keyword in ['component', 'identifier', 'style', 'layout', 'metadata']):
        if '{' in text or '[' in text:
            return ('metadata', '📋 Metadane')
    
    # Sprawdź czy to może być konfiguracja/XML
    if text_stripped.startswith('<') and '>' in text:
        return ('metadata', '📋 Konfiguracja/XML')
    
    # Domyślnie - inny typ
    return ('other', '📄 Inny dokument')

def translate_query_to_english(query: str) -> str:
    """
    T┼éumaczy zapytanie wyszukiwania z polskiego na angielski.
    U┼╝ywa Google Translator jako fallback (model HF nie ma pl->en).
    
    Args:
        query: Zapytanie wyszukiwania (mo┼╝e by─ç po polsku lub angielsku)
    
    Returns:
        Przet┼éumaczone zapytanie (lub orygina┼é je┼Ťli ju┼╝ po angielsku)
    """
    if not query or not query.strip():
        return query
    
    # Prosta heurystyka: je┼Ťli zapytanie zawiera g┼é├│wnie polskie znaki, przet┼éumacz
    polish_chars = re.compile(r'[─ů─ç─Ö┼é┼ä├│┼Ť┼║┼╝─ä─ć─ś┼ü┼â├ô┼Ü┼╣┼╗]')
    has_polish = bool(polish_chars.search(query))
    
    if not has_polish:
        # Prawdopodobnie ju┼╝ po angielsku
        return query
    
    # Spr├│buj przet┼éumaczy─ç u┼╝ywaj─ůc Google Translator
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='pl', target='en')
        translated = translator.translate(query)
        
        # Sprawd┼║ czy t┼éumaczenie jest sensowne
        if translated and translated.strip() and translated != query:
            return translated
    except Exception:
        # Je┼Ťli t┼éumaczenie nie dzia┼éa, zwr├│─ç orygina┼é
        pass
    
    return query

def double_validate_translation(original: str, translated: str) -> tuple[bool, Optional[str]]:
    """
    Podw├│jna walidacja t┼éumaczenia - sprawdza czy t┼éumaczenie jest poprawne.
    
    Args:
        original: Oryginalny tekst
        translated: Przet┼éumaczony tekst
    
    Returns:
        Tuple (is_valid, reason) - czy t┼éumaczenie jest poprawne i pow├│d odrzucenia (je┼Ťli nie)
    """
    # Walidacja 1: Podstawowa walidacja
    if not is_translation_valid(original, translated):
        return False, "T┼éumaczenie nie przesz┼éo podstawowej walidacji"
    
    # Walidacja 2: Sprawdzenie d┼éugo┼Ťci
    original_len = len(original.strip())
    translated_len = len(translated.strip())
    
    # T┼éumaczenie nie powinno by─ç zbyt kr├│tkie (mniej ni┼╝ 30% orygina┼éu)
    if translated_len < original_len * 0.3:
        return False, "T┼éumaczenie jest zbyt kr├│tkie"
    
    # T┼éumaczenie nie powinno by─ç zbyt d┼éugie (wi─Öcej ni┼╝ 300% orygina┼éu)
    if translated_len > original_len * 3:
        return False, "T┼éumaczenie jest zbyt d┼éugie"
    
    # Walidacja 3: Sprawdzenie czy nie zawiera zbyt wielu "dziwnych" znak├│w
    # (ju┼╝ sprawdzane w is_translation_valid, ale dodatkowo sprawdzamy procent)
    valid_chars = re.compile(r'[a-zA-Z0-9─ů─ç─Ö┼é┼ä├│┼Ť┼║┼╝─ä─ć─ś┼ü┼â├ô┼Ü┼╣┼╗.,!?;:\s\-\'\"()]+')
    cleaned = "".join(valid_chars.findall(translated))
    if len(translated) > 0 and (len(cleaned) / len(translated)) < 0.8:
        return False, "T┼éumaczenie zawiera zbyt wiele nieprawid┼éowych znak├│w"
    
    # Wszystkie walidacje przesz┼éy
    return True, None

