from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import arabic_reshaper
import io
import os
from networkx import draw
import numpy as np
from pathlib import Path

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

# def detect_cta(image:Image.Image) -> int | None:
#     """
#     this method will detect the vertical center of th CTA Button 
#     by looking for a horizontal uniform colored band in the bottom 50% of the image.
#     returns the y coordinate of the button center, or None if not found.

#     """
#     image_arr = np.array(image) # converting the image to numpy array for easier processing
#     height, width, _ = image_arr.shape # _ is the number of color channels (3 for RGB) - we dont need it
    
#     search_start = int(height * 0.50) # starting the serach from the middle of the image
#     search_region = image_arr[search_start:, :, :]

#     button_rows = []

#     for i, row in enumerate(search_region):
#         # now need to calculate the standard deviation of the colors in this row, if its low enough we can consider it as part of the button
#         std_r = np.std(row[:, 0]) # std of the red channel
#         std_g = np.std(row[:,1]) # std of the green channel
#         std_b = np.std(row[:, 2]) # std of the blue channel

#         avg_std = (std_r+std_g +std_b) /3
#         if avg_std < 18:
#             button_rows.append(search_start + i)
    
#     if not button_rows:
#         return None
#     print("---BUTTON ROWS---", button_rows)
#     # now need to find the largest continuous uniform rows which will represent the button
#     blocks = []
#     current_block = [button_rows[0]]

#     for i in range(1, len(button_rows)):
#         if button_rows[i] - button_rows[i-1] <= 3:
#             current_block.append(button_rows[i])
#         else:
#             blocks.append(current_block)
#             current_block = [button_rows[i]]
#     blocks.append(current_block)

#     largest_block = max(blocks, key=len)
#     print("---LARGEST BLOCK---", largest_block)

#     if len(largest_block) <20:
#         return None
    
#     return int(sum(largest_block) / len(largest_block)) # returning the average y coordinate of the button rows as the button center


def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)

    width, height = image.size
    cx = width / 2

    title_font = "Rubik-Bold.ttf"
    subtitle_font = "Rubik-Regular.ttf"

    # ── ZONE 1: TOP TEXT AREA (0% – 28%) ──────────────────────────────
    title_y = int(height * 0.10)
    draw_text(draw, content.get("title"), (cx, title_y), title_font, 70, (0, 0, 0))

    subtitle_y = int(height * 0.18)
    draw_text(draw, content.get("subtitle"), (cx, subtitle_y), subtitle_font, 40, (30, 30, 30))

    # ── ZONE 3: CTA BUTTON (72% – 80%) ────────────────────────────────
    cta_text = content.get("cta")
    if cta_text:
        # detected_y = detect_cta(image)
        # cta_y = detected_y if detected_y else int(height * 0.80)  # must match prompt's 78%
        # print(f"CTA button detected at y={detected_y}, using y={cta_y} for text placement.")
        cta_y = int(height * 0.78)
        draw_text(draw, cta_text, (cx, cta_y), title_font, 35, (255, 255, 255))

#     cta_text = content.get("cta")
#     font = load_font(title_font, 32)

# # Measure text
#     bbox = font.getbbox(cta_text)
#     text_w = bbox[2] - bbox[0]
#     text_h = bbox[3] - bbox[1]

#     # Padding (important for that "pill" look)
#     pad_x = 50
#     pad_y = 22

#     btn_w = text_w + pad_x * 2
#     btn_h = text_h + pad_y * 2

#     cta_y = int(height * 0.82)

#     # Button background (light pill like your image)
#     draw.rounded_rectangle(
#         [cx - btn_w // 2, cta_y - btn_h // 2,
#         cx + btn_w // 2, cta_y + btn_h // 2],
#         radius=btn_h // 2,
#         fill=(235, 230, 210)   # soft beige/white like reference
#     )

#     # Optional: subtle border (this makes it POP)
#     draw.rounded_rectangle(
#         [cx - btn_w // 2, cta_y - btn_h // 2,
#         cx + btn_w // 2, cta_y + btn_h // 2],
#         radius=btn_h // 2,
#         outline=(200, 200, 200),
#         width=2
#     )

# Text on top
    # draw_text(draw, cta_text, (cx, cta_y), title_font, 32, (60, 60, 60))

    # # Draw text
    # draw_text(draw, cta_text, (cx, cta_y), title_font, 35, (255, 255, 255))

    # cta_text = content.get("cta")
    # if cta_text:
    #     btn_w, btn_h = int(width * 0.55), 68
    #     cta_y = int(height * 0.80)
    #     draw.rounded_rectangle(
    #         [cx - btn_w // 2, cta_y - btn_h // 2,
    #          cx + btn_w // 2, cta_y + btn_h // 2],
    #         radius=34,
    #         fill=(180, 30, 30)  
    #     )
    #     draw_text(draw, cta_text, (cx, cta_y), title_font, 30, (255, 255, 255))

    # ── ZONE 4: FOOTER (82% – 97%) ────────────────────────────────────
    # draw_text(draw, content.get("brand_name"), (cx, int(height * 0.70)), title_font, 26, (0, 0, 0))
    # draw_text(draw, content.get("tagline"), (cx, int(height * 0.75)), subtitle_font, 21, (40, 40, 40))
    footer_top = cta_y - 100 if cta_text else int(height * 0.68)
    draw_text(draw, content.get("brand_name"), (cx, footer_top), title_font, 26, (0, 0, 0))
    draw_text(draw, content.get("tagline"), (cx, footer_top + 40), subtitle_font, 21, (40, 40, 40))

    contact_text = " | ".join(filter(None, [
        content.get("phone"),
        content.get("address"),
        content.get("website")
    ]))
    draw_text(draw, contact_text, (cx, int(height * 0.99)), subtitle_font, 19, (50, 50, 50), anchor="mb")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()

# def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
#     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     draw = ImageDraw.Draw(image)

#     width, height = image.size
#     cx = width / 2  # horizontal center

#     title_font = "Rubik-Bold.ttf"
#     subtitle_font = "Rubik-Regular.ttf"

#     # ── ZONE 1: TOP TEXT AREA (0% – 28%) ──────────────────────────────
#     # Title at ~12% from top
#     title_y = int(height * 0.12)
#     draw_text(draw, content.get("title"), (cx, title_y), title_font, 75, (0, 0, 0))

#     # Subtitle at ~21% from top
#     subtitle_y = int(height * 0.21)
#     draw_text(draw, content.get("subtitle"), (cx, subtitle_y), subtitle_font, 38, (30, 30, 30))

#     # ── ZONE 3: CTA BUTTON (74% – 82%) ────────────────────────────────
#     cta_text = content.get("cta")
#     if cta_text:
#         btn_w, btn_h = int(width * 0.42), 65
#         cta_y = int(height * 0.78)
#         draw.rounded_rectangle(
#             [cx - btn_w // 2, cta_y - btn_h // 2,
#              cx + btn_w // 2, cta_y + btn_h // 2],
#             radius=33,
#             fill=(20, 20, 20)
#         )
#         draw_text(draw, cta_text, (cx, cta_y), title_font, 28, (255, 255, 255))

#     # ── ZONE 4: FOOTER AREA (82% – 100%) ──────────────────────────────
#     # Brand name at ~84%
#     draw_text(draw, content.get("brand_name"), (cx, int(height * 0.84)), title_font, 28, (0, 0, 0))

#     # Tagline at ~89%
#     draw_text(draw, content.get("tagline"), (cx, int(height * 0.89)), subtitle_font, 22, (40, 40, 40))

#     # Contact info at ~94%
#     contact_text = " | ".join(filter(None, [
#         content.get("phone"),
#         content.get("address"),
#         content.get("website")
#     ]))
#     draw_text(draw, contact_text, (cx, int(height * 0.94)), subtitle_font, 18, (50, 50, 50))

#     buffer = io.BytesIO()
#     image.save(buffer, format="PNG")
#     buffer.seek(0)
#     return buffer.getvalue()















# from PIL import Image, ImageDraw, ImageFont
# from bidi.algorithm import get_display
# import arabic_reshaper
# import io
# import os
# from pathlib import Path

# # Always stable path (works in Celery, Docker, etc.)
# BASE_DIR = Path(__file__).resolve().parent.parent.parent  # resolves to Poster-AI/
# FONTS_DIR = BASE_DIR / "fonts"  

    

# def fix_hebrew_text(text: str) -> str:
#     """
#     Fix RTL languages (Arabic/Hebrew)
#     """
#     if not text:
#         return ""

#     reshaped_text = arabic_reshaper.reshape(text)
#     bidi_text = get_display(reshaped_text)

#     return bidi_text

# def load_font(font_name, font_size):
#     font_dir = Path(FONTS_DIR)
#     font_path = font_dir / font_name
    
#     print("FONT PATH:", font_path)
#     print("EXISTS:", font_path.exists())
#     print("IS FILE:", font_path.is_file())
#     if font_path.exists():
#         print("FILE SIZE:", font_path.stat().st_size)  # 0 bytes = corrupted/empty
    
#     try:
#         return ImageFont.truetype(str(font_path), font_size)
#     except Exception as e:
#         print("FONT LOAD FAILED:", e)
#         return ImageFont.load_default()


# def draw_text(
#         draw,
#         text,
#         position,
#         font_name,
#         font_size,
#         color=(0, 0, 0),
#         anchor="mm"
# ):
#     """
#     Draw text safely with proper font loading
#     """
#     if not text:
#         return

#     font = load_font(font_name, font_size)
#     fixed_text = fix_hebrew_text(text)

#     draw.text(position, fixed_text, font=font, fill=color, anchor=anchor)



# def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
#     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     draw = ImageDraw.Draw(image)

#     width, height = image.size

#     SAFE_MARGIN = 0.15
#     top_y = int(height * SAFE_MARGIN)
#     bottom_y = int(height * (1 - SAFE_MARGIN))

#     title_font = "Rubik-Bold.ttf"
#     subtitle_font = "Rubik-Regular.ttf"

#     # 1. TITLE — top zone, ensure it stays within top 25%
#     title_y = top_y + 50
#     draw_text(draw, content.get("title"), (width/2, title_y), title_font, 75, (0, 0, 0))

#     # 2. SUBTITLE — directly below title
#     subtitle_y = title_y + 90
#     draw_text(draw, content.get("subtitle"), (width/2, subtitle_y), subtitle_font, 38, (30, 30, 30))

#     # 3. BRAND NAME — above CTA
#     draw_text(draw, content.get("brand_name"), (width/2, bottom_y - 120), title_font, 32, (0, 0, 0))

#     # 4. TAGLINE — below brand
#     draw_text(draw, content.get("tagline"), (width/2, bottom_y - 80), subtitle_font, 24, (40, 40, 40))

#     # 5. CONTACT INFO — below tagline
#     contact_text = " | ".join(filter(None, [
#         content.get("phone"),
#         content.get("address"),
#         content.get("website")
#     ]))
#     draw_text(draw, contact_text, (width/2, bottom_y - 40), subtitle_font, 18, (50, 50, 50))

#     # 6. CTA BUTTON — draw background first, then text on top
#     cta_text = content.get("cta")
#     if cta_text:
#         btn_w, btn_h = 420, 65
#         cta_y = int(height * 0.80)
#         draw.rounded_rectangle(
#             [width/2 - btn_w//2, cta_y - btn_h//2,
#              width/2 + btn_w//2, cta_y + btn_h//2],
#             radius=33,
#             fill=(0, 0, 0)
#         )
#         draw_text(draw, cta_text, (width/2, cta_y), title_font, 28, (255, 255, 255))

#     buffer = io.BytesIO()
#     image.save(buffer, format="PNG")
#     buffer.seek(0)
#     return buffer.getvalue()


# # def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
# #     """
# #     Takes raw image bytes → returns new image bytes with text overlay
# #     """

# #     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
# #     draw = ImageDraw.Draw(image)

# #     width, height = image.size

# #     SAFE_MARGIN = 0.15
# #     top_y = int(height * SAFE_MARGIN)
# #     bottom_y = int(height * (1 - SAFE_MARGIN))

# #     # Fonts (ONLY NAMES NOW, NOT FULL PATHS)
# #     title_font = "Rubik-Bold.ttf"
# #     subtitle_font = "Rubik-Regular.ttf"

# #     # Draw text
# #     draw_text(draw, content.get("title"), (width / 2, top_y + 40), title_font, 80)
# #     draw_text(draw, content.get("subtitle"), (width / 2, top_y + 130), subtitle_font, 40)
# #     draw_text(draw, content.get("cta"), (width / 2, int(height * 0.78)), title_font, 45, (255, 255, 255))
# #     draw_text(draw, content.get("brand_name"), (width / 2, bottom_y - 80), subtitle_font, 30)
# #     draw_text(draw, content.get("tagline"), (width / 2, bottom_y - 40), subtitle_font, 25)

# #     contact_text = " | ".join(filter(None, [
# #         content.get("phone"),
# #         content.get("address"),
# #         content.get("website")
# #     ]))

# #     draw_text(draw, contact_text, (width / 2, bottom_y), subtitle_font, 20)

# #     # Save to bytes
# #     buffer = io.BytesIO()
# #     image.save(buffer, format="PNG")
# #     buffer.seek(0)

# #     return buffer.getvalue()