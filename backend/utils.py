from deep_translator import GoogleTranslator


def translate_text(text, language='no'):
    try:
        return GoogleTranslator(source='auto', target=language).translate(text)
    except Exception:
        return text
