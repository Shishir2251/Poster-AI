from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import arabic_reshaper
import io
import os
from pathlib import Path

# Always stable path (works in Celery, Docker, etc.)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # resolves to Poster-AI/
FONTS_DIR = BASE_DIR / "fonts"  

    

def fix_hebrew_text(text: str) -> str:
    """
    Fix RTL languages (Arabic/Hebrew)
    """
    if not text:
        return ""

    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)

    return bidi_text

def load_font(font_name, font_size):
    font_dir = Path(FONTS_DIR)
    font_path = font_dir / font_name
    
    print("FONT PATH:", font_path)
    print("EXISTS:", font_path.exists())
    print("IS FILE:", font_path.is_file())
    if font_path.exists():
        print("FILE SIZE:", font_path.stat().st_size)  # 0 bytes = corrupted/empty
    
    try:
        return ImageFont.truetype(str(font_path), font_size)
    except Exception as e:
        print("FONT LOAD FAILED:", e)
        return ImageFont.load_default()

# def load_font(font_name: str, font_size: int):
#     """
#     Safe font loader with fallback
#     """
#     font_path = FONTS_DIR / font_name

#     print("FONT PATH:", font_path)
#     print("EXISTS:", font_path.exists())

#     try:
#         return ImageFont.truetype(str(font_path), font_size)
#     except Exception as e:
#         print("FONT LOAD FAILED:", e)
#         return ImageFont.load_default()


def draw_text(
        draw,
        text,
        position,
        font_name,
        font_size,
        color=(0, 0, 0),
        anchor="mm"
):
    """
    Draw text safely with proper font loading
    """
    if not text:
        return

    font = load_font(font_name, font_size)
    fixed_text = fix_hebrew_text(text)

    draw.text(position, fixed_text, font=font, fill=color, anchor=anchor)



def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)

    width, height = image.size

    SAFE_MARGIN = 0.15
    top_y = int(height * SAFE_MARGIN)
    bottom_y = int(height * (1 - SAFE_MARGIN))

    title_font = "Rubik-Bold.ttf"
    subtitle_font = "Rubik-Regular.ttf"

    # 1. TITLE — top zone, ensure it stays within top 25%
    title_y = top_y + 50
    draw_text(draw, content.get("title"), (width/2, title_y), title_font, 75, (0, 0, 0))

    # 2. SUBTITLE — directly below title
    subtitle_y = title_y + 90
    draw_text(draw, content.get("subtitle"), (width/2, subtitle_y), subtitle_font, 38, (30, 30, 30))

    # 3. BRAND NAME — above CTA
    draw_text(draw, content.get("brand_name"), (width/2, bottom_y - 120), title_font, 32, (0, 0, 0))

    # 4. TAGLINE — below brand
    draw_text(draw, content.get("tagline"), (width/2, bottom_y - 80), subtitle_font, 24, (40, 40, 40))

    # 5. CONTACT INFO — below tagline
    contact_text = " | ".join(filter(None, [
        content.get("phone"),
        content.get("address"),
        content.get("website")
    ]))
    draw_text(draw, contact_text, (width/2, bottom_y - 40), subtitle_font, 18, (50, 50, 50))

    # 6. CTA BUTTON — draw background first, then text on top
    cta_text = content.get("cta")
    if cta_text:
        btn_w, btn_h = 420, 65
        cta_y = int(height * 0.80)
        draw.rounded_rectangle(
            [width/2 - btn_w//2, cta_y - btn_h//2,
             width/2 + btn_w//2, cta_y + btn_h//2],
            radius=33,
            fill=(0, 0, 0)
        )
        draw_text(draw, cta_text, (width/2, cta_y), title_font, 28, (255, 255, 255))

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


# def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
#     """
#     Takes raw image bytes → returns new image bytes with text overlay
#     """

#     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     draw = ImageDraw.Draw(image)

#     width, height = image.size

#     SAFE_MARGIN = 0.15
#     top_y = int(height * SAFE_MARGIN)
#     bottom_y = int(height * (1 - SAFE_MARGIN))

#     # Fonts (ONLY NAMES NOW, NOT FULL PATHS)
#     title_font = "Rubik-Bold.ttf"
#     subtitle_font = "Rubik-Regular.ttf"

#     # Draw text
#     draw_text(draw, content.get("title"), (width / 2, top_y + 40), title_font, 80)
#     draw_text(draw, content.get("subtitle"), (width / 2, top_y + 130), subtitle_font, 40)
#     draw_text(draw, content.get("cta"), (width / 2, int(height * 0.78)), title_font, 45, (255, 255, 255))
#     draw_text(draw, content.get("brand_name"), (width / 2, bottom_y - 80), subtitle_font, 30)
#     draw_text(draw, content.get("tagline"), (width / 2, bottom_y - 40), subtitle_font, 25)

#     contact_text = " | ".join(filter(None, [
#         content.get("phone"),
#         content.get("address"),
#         content.get("website")
#     ]))

#     draw_text(draw, contact_text, (width / 2, bottom_y), subtitle_font, 20)

#     # Save to bytes
#     buffer = io.BytesIO()
#     image.save(buffer, format="PNG")
#     buffer.seek(0)

#     return buffer.getvalue()