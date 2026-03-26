from langdetect import detect

def detect_language(text: str):

    try:
        lang = detect(text)
    except:
        lang = "en"

    return lang