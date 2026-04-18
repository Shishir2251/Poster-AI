from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import arabic_reshaper
import io
import os
from networkx import draw
import numpy as np
from pathlib import Path
from app.routers.pipeline_router import secondary_color

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FONTS_DIR = BASE_DIR / "fonts"


def fix_hebrew_text(text: str) -> str:
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


def load_font(font_name, font_size):
    font_path = FONTS_DIR / font_name
    try:
        return ImageFont.truetype(str(font_path), font_size)
    except Exception as e:
        print("FONT LOAD FAILED:", e)
        return ImageFont.load_default()


def draw_text(draw, text, position, font_name, font_size, color=(0, 0, 0), anchor="mm"):
    if not text:
        return
    font = load_font(font_name, font_size)
    fixed_text = fix_hebrew_text(text)
    draw.text(position, fixed_text, font=font, fill=color, anchor=anchor)


def render_poster_text(image_bytes:bytes, content:dict) -> bytes:

    image= Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)
    width, height = image.size
    cx = width / 2

    title_font = "Rubik-Bold.ttf"
    subtitle_font = "Rubik-Regular.ttf"

    # -------------zone 1: top text area (0% - 28%)----------------------
    draw_text(draw, content.get("title"), (cx, int(height * 0.10)), title_font, 70, (0,0,0))
    draw_text(draw, content.get("subtitle"), (cx, int(height * 0.19)), subtitle_font,38, (30,30,30))

    # -------------- Zone 2: brand name and tagline (68% - 82%)----------------------
    #brand + tagline with readable background
    brand_y = int(height *0.72)
    tagline_y = int(height * 0.78)

    overlay = Image.new("RGBA", image.size, (0,0,0,0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [0, brand_y - 25, width, tagline_y + 30], fill=(255,255,255,120)
    )
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGBA")
    draw = ImageDraw.Draw(image)

    draw_text(draw, content.get("brand_name"), (cx, brand_y), title_font, 35, (10, 10, 10))
    draw_text(draw, content.get("tagline"), (cx, tagline_y), subtitle_font, 30, (30,30, 30))


    #------zone 4: CTA button -------------------------
    cta_text = content.get("cta")
    if cta_text:
        btn_w = int(width * 0.35)
        btn_h = 62
        cta_y = int(height * 0.86)
        draw.rounded_rectangle(
            [cx - btn_w // 2, cta_y - btn_h // 2,
             cx + btn_w // 2, cta_y + btn_h // 2],
            radius=31,
            fill=(200, 50, 50)
        )
        draw_text(draw, cta_text, (cx, cta_y), title_font, 28, (255, 255, 255))
    
    #--- zone 5: Contact info (94% - 99%)----------------------
    contact_text = " | ".join(filter(None, [
        content.get("phone"),
        content.get("address"),
        content.get("website")
    ]))
    draw_text(draw, contact_text, (cx, int(height * 0.94)), subtitle_font, 20, (20, 20, 20))

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()
















#-------------------------------------------------

# def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
#     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     draw = ImageDraw.Draw(image)

#     width, height = image.size
#     cx = width / 2

#     title_font = "Rubik-Bold.ttf"
#     subtitle_font = "Rubik-Regular.ttf"

#     # ── ZONE 1: TOP TEXT AREA (0% – 28%) ──────────────────────────────
#     title_y = int(height * 0.10)
#     draw_text(draw, content.get("title"), (cx, title_y), title_font, 70, (0, 0, 0))

#     subtitle_y = int(height * 0.18)
#     draw_text(draw, content.get("subtitle"), (cx, subtitle_y), subtitle_font, 40, (30, 30, 30))

#     # ── ZONE 3: CTA BUTTON (72% – 80%) ────────────────────────────────
#     cta_text = content.get("cta")
#     if cta_text:
#         # detected_y = detect_cta(image)
#         # cta_y = detected_y if detected_y else int(height * 0.80)  # must match prompt's 78%
#         # print(f"CTA button detected at y={detected_y}, using y={cta_y} for text placement.")
#         cta_y = int(height * 0.78)
#         draw_text(draw, cta_text, (cx, cta_y), title_font, 40, (255, 255, 255))

# #     cta_text = content.get("cta")
# #     font = load_font(title_font, 32)

# # # Measure text
# #     bbox = font.getbbox(cta_text)
# #     text_w = bbox[2] - bbox[0]
# #     text_h = bbox[3] - bbox[1]

# #     # Padding (important for that "pill" look)
# #     pad_x = 50
# #     pad_y = 22

# #     btn_w = text_w + pad_x * 2
# #     btn_h = text_h + pad_y * 2

# #     cta_y = int(height * 0.82)

# #     # Button background (light pill like your image)
# #     draw.rounded_rectangle(
# #         [cx - btn_w // 2, cta_y - btn_h // 2,
# #         cx + btn_w // 2, cta_y + btn_h // 2],
# #         radius=btn_h // 2,
# #         fill=(235, 230, 210)   # soft beige/white like reference
# #     )

# #     # Optional: subtle border (this makes it POP)
# #     draw.rounded_rectangle(
# #         [cx - btn_w // 2, cta_y - btn_h // 2,
# #         cx + btn_w // 2, cta_y + btn_h // 2],
# #         radius=btn_h // 2,
# #         outline=(200, 200, 200),
# #         width=2
# #     )

# # Text on top
#     # draw_text(draw, cta_text, (cx, cta_y), title_font, 32, (60, 60, 60))

#     # # Draw text
#     # draw_text(draw, cta_text, (cx, cta_y), title_font, 35, (255, 255, 255))

#     # cta_text = content.get("cta")
#     # if cta_text:
#     #     btn_w, btn_h = int(width * 0.55), 68
#     #     cta_y = int(height * 0.80)
#     #     draw.rounded_rectangle(
#     #         [cx - btn_w // 2, cta_y - btn_h // 2,
#     #          cx + btn_w // 2, cta_y + btn_h // 2],
#     #         radius=34,
#     #         fill=(180, 30, 30)  
#     #     )
#     #     draw_text(draw, cta_text, (cx, cta_y), title_font, 30, (255, 255, 255))

#     # ── ZONE 4: FOOTER (82% – 97%) ────────────────────────────────────
#     # draw_text(draw, content.get("brand_name"), (cx, int(height * 0.70)), title_font, 26, (0, 0, 0))
#     # draw_text(draw, content.get("tagline"), (cx, int(height * 0.75)), subtitle_font, 21, (40, 40, 40))
#     footer_top = cta_y - 100 if cta_text else int(height * 0.68)
#     draw_text(draw, content.get("brand_name"), (cx, footer_top), title_font, 35, (0, 0, 0))
#     draw_text(draw, content.get("tagline"), (cx, footer_top + 40), subtitle_font, 30, (40, 40, 40))

#     contact_text = " | ".join(filter(None, [
#         content.get("phone"),
#         content.get("address"),
#         content.get("website")
#     ]))
#     draw_text(draw, contact_text, (cx, int(height * 0.99)), subtitle_font, 28, (50, 50, 50), anchor="mb")

#     buffer = io.BytesIO()
#     image.save(buffer, format="PNG")
#     buffer.seek(0)
#     return buffer.getvalue()

