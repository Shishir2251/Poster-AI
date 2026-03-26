from PIL import Image, ImageDraw, ImageFont
import os
import uuid


def load_font(font_path, size):
    """Try to load a TrueType font, fall back to PIL default if not found."""
    if font_path and os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    try:
        # Try loading a common system font on Windows
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        pass
    # Final fallback: PIL built-in bitmap font (no size control, always works)
    return ImageFont.load_default()


def render_poster(image_path, headline, content, font_path=None):

    base = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(base)

    headline_font = load_font(font_path, 60)
    content_font = load_font(font_path, 35)

    draw.text((50, 80), headline, fill="white", font=headline_font)
    draw.text((50, 200), content, fill="white", font=content_font)

    os.makedirs("generated", exist_ok=True)
    output_path = f"generated/{uuid.uuid4()}.png"
    base.save(output_path)

    return output_path