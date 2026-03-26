from app.services.language_service import detect_language
from app.services.ai_service import generate_ai_content
from app.engine.renderer import render_poster
from app.utils.hebrew_utils import process_hebrew


def generate_poster(image_path, headline, content, font_path, use_ai):

    language = detect_language(headline)

    if use_ai:
        content = generate_ai_content(headline, content, language)

    if language == "he":
        headline = process_hebrew(headline)
        content = process_hebrew(content)

    poster = render_poster(
        image_path,
        headline,
        content,
        font_path
    )

    return poster