from deep_translator import GoogleTranslator


def translate_text(language, text):
    try:
        return GoogleTranslator(source='auto', target=language).translate(text)
    except Exception:
        return text
