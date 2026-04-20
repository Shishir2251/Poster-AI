from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
import arabic_reshaper
import io
import json
import re
import base64
from pathlib import Path
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FONTS_DIR = BASE_DIR / "fonts"

client = OpenAI()


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


# def draw_text(draw, text, position, font_name, font_size, color=(0, 0, 0), anchor="mm"):
#     if not text:
#         return
#     font = load_font(font_name, font_size)
#     fixed_text = fix_hebrew_text(text)
#     draw.text(position, fixed_text, font=font, fill=color, anchor=anchor)

def draw_text(draw, text, position, font_name, font_size, color=(0, 0, 0), anchor="mm", max_width=None):
    if not text:
        return
    font = load_font(font_name, font_size)
    fixed_text = fix_hebrew_text(text)
    
    if max_width:
        # Word wrap logic
        words = fixed_text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = " ".join(current_line)
            bbox = font.getbbox(test_line)
            line_width = bbox[2] - bbox[0]
            
            if line_width > max_width:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(test_line)
                    current_line = []
        
        if current_line:
            lines.append(" ".join(current_line))
        
        # Draw each line
        x, y = position
        line_height = font_size + 8
        total_height = line_height * len(lines)
        y_start = y - total_height // 2  # center vertically
        
        for i, line in enumerate(lines):
            draw.text((x, y_start + i * line_height), line, font=font, fill=color, anchor="mm")
    else:
        draw.text(position, fixed_text, font=font, fill=color, anchor=anchor)


def get_text_placement(image_bytes: bytes, content: dict, width: int, height: int) -> dict:
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    layout = content.get("layout", "center")

    prompt = f"""
You are a senior typographer and poster designer.

This is a poster background image of size {width}x{height} pixels.
The subject is {layout} aligned in this poster. Adjust text placement accordingly.

Analyze the image carefully:
- Where is the empty/clean space?
- What are the dominant background colors in each zone?
- Where does light vs dark background exist?
- Is the subject left, right, or center aligned?

I need to place these text elements:
- Title: "{content.get('title')}"
- Subtitle: "{content.get('subtitle')}"
- Brand name: "{content.get('brand_name')}"
- Tagline: "{content.get('tagline')}"
- CTA button: "{content.get('cta')}"
- Additional info: "{content.get('additional_info')}"
- Contact info: "{content.get('phone')} | {content.get('address')} | {content.get('website')}"

PLACEMENT RULES:
1. Place text ONLY on clean, empty areas of the image
2. NEVER place text over the main subject/product
3. If subject is LEFT aligned — place title/subtitle on the RIGHT side
4. If subject is RIGHT aligned — place title/subtitle on the LEFT side
5. If subject is CENTER — place title at top, other info at bottom
6. Title and subtitle go in the top 25% of the canvas
7. Brand, tagline, CTA, contact go in the bottom 32% of the canvas
8. All elements must be horizontally centered unless subject blocks center

TYPOGRAPHY RULES (MAKE IT DYNAMIC AND EXCITING):
1. Title must be the LARGEST element — font size between 65-90
2. Additional info (discount/promo) should be BOLD and use a highly
   contrasting vibrant color — never the same as title color
3. Brand name should feel premium — different size from title
4. CTA button bg_color must be a strong accent color that pops
5. No two adjacent elements should have the same color
6. Create visual hierarchy through SIZE contrast — vary sizes dramatically
7. If there is promotional info like discount — make it stand out with
   a bright color like red, orange, or gold
8. Subtitle should be noticeably smaller than title
9. Think like an award-winning typographer — make it exciting and dynamic, not bland and static

COLOR RULES (CRITICAL):
1. Analyze the actual background color behind where each text will be placed
2. If background is DARK — use light/white text color
3. If background is LIGHT — use dark/black text color
4. If background is COLORFUL — use white with high contrast
5. CTA button background color must strongly contrast with surrounding area
6. CTA text color must contrast with CTA button background
7. Choose colors that are vibrant and attention-grabbing, not bland

CRITICAL OVERLAP RULE:
- Brand name, tagline, additional info, CTA and contact must ONLY be 
  placed in the bottom 32% of the canvas (y_pct >= 0.68)
- NEVER place these elements over the main product/subject
- If subject is left aligned, bottom elements go on the RIGHT bottom area
- If subject is right aligned, bottom elements go on the LEFT bottom area

Return ONLY valid JSON, no markdown, no explanation:
{{
    "title": {{
        "x_pct": 0.5,
        "y_pct": 0.10,
        "font_size": 70,
        "color": [0, 0, 0],
        "anchor": "mm"
    }},
    "subtitle": {{
        "x_pct": 0.5,
        "y_pct": 0.19,
        "font_size": 38,
        "color": [30, 30, 30],
        "anchor": "mm"
    }},
    "brand_name": {{
        "x_pct": 0.5,
        "y_pct": 0.75,
        "font_size": 28,
        "color": [0, 0, 0],
        "anchor": "mm"
    }},
    "tagline": {{
        "x_pct": 0.5,
        "y_pct": 0.81,
        "font_size": 22,
        "color": [40, 40, 40],
        "anchor": "mm"
    }},
    "additional_info": {{
        "x_pct": 0.5,
        "y_pct": 0.72,
        "font_size": 24,
        "color": [255, 50, 50],
        "bg_color": [220, 30, 30],
        "anchor": "mm"
    }},
    "cta": {{
        "x_pct": 0.5,
        "y_pct": 0.88,
        "font_size": 28,
        "color": [255, 255, 255],
        "bg_color": [200, 50, 50],
        "anchor": "mm"
    }},
    "contact": {{
    "x_pct": 0.5,
    "y_pct": 0.95,
    "font_size": 16,   # keep small
    "color": [50, 50, 50],
    "anchor": "mm"     # center anchor keeps it within bounds
}}
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=600
        )

        raw = response.choices[0].message.content
        cleaned = re.sub(r"```json|```", "", raw).strip()
        placement = json.loads(cleaned)
        print("Dynamic placement received:", placement)
        return placement

    except Exception as e:
        print(f"Vision placement failed: {e}, using fallback")
        return {
            "title":           {"x_pct": 0.5, "y_pct": 0.10, "font_size": 70, "color": [0, 0, 0], "anchor": "mm"},
            "subtitle":        {"x_pct": 0.5, "y_pct": 0.19, "font_size": 38, "color": [30, 30, 30], "anchor": "mm"},
            "brand_name":      {"x_pct": 0.5, "y_pct": 0.75, "font_size": 28, "color": [0, 0, 0], "anchor": "mm"},
            "tagline":         {"x_pct": 0.5, "y_pct": 0.81, "font_size": 22, "color": [40, 40, 40], "anchor": "mm"},
            "additional_info": {"x_pct": 0.5, "y_pct": 0.72, "font_size": 24, "color": [255, 50, 50], "anchor": "mm"},
            "cta":             {"x_pct": 0.5, "y_pct": 0.88, "font_size": 28, "color": [255, 255, 255], "bg_color": [200, 50, 50], "anchor": "mm"},
            "contact":         {"x_pct": 0.5, "y_pct": 0.95, "font_size": 18, "color": [50, 50, 50], "anchor": "mm"}
        }


def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size

    # Get dynamic placement from GPT-4.1 Vision
    placement = get_text_placement(image_bytes, content, width, height)

    draw = ImageDraw.Draw(image)
    cx = width / 2
    title_font = "Rubik-Bold.ttf"
    subtitle_font = "Rubik-Regular.ttf"

    #defining max width based on layout
    layout = content.get("layout", "center")
    if layout in ["left", "right"]:
        text_max_width = int(width * 0.42)
    else:
        text_max_width = int(width *0.85)
    

    # def get_pos(key):
    #     p = placement.get(key, {})
    #     x = int(width * p.get("x_pct", 0.5))
    #     y = int(height * p.get("y_pct", 0.5))
    #     return x, y

    def get_pos(key):
        p = placement.get(key, {})
        x_pct = p.get("x_pct", 0.5)
        y_pct = p.get("y_pct", 0.5)
        
        # Clamp x position to keep text inside canvas
        # For right-aligned layouts, don't let x go beyond 80%
        # For left-aligned layouts, don't let x go below 20%
        if layout == "right":
            x_pct = min(x_pct, 0.75)
        elif layout == "left":
            x_pct = max(x_pct, 0.25)
        
        x = int(width * x_pct)
        y = int(height * y_pct)
        return x, y

    def get_color(key):
        return tuple(placement.get(key, {}).get("color", [0, 0, 0]))

    def get_size(key, default):
        return placement.get(key, {}).get("font_size", default)

    def get_anchor(key):
        return placement.get(key, {}).get("anchor", "mm")

   
    # ── Title ─────────────────────────────────────────────────────────
    draw_text(draw, content.get("title"),
              get_pos("title"), title_font,
              get_size("title", 70), get_color("title"),
              get_anchor("title"), max_width=text_max_width)

    # ── Subtitle ──────────────────────────────────────────────────────
    draw_text(draw, content.get("subtitle"),
              get_pos("subtitle"), subtitle_font,
              get_size("subtitle", 38), get_color("subtitle"),
              get_anchor("subtitle"), max_width=text_max_width)
    
    # ── Additional Info ───────────────────────────────────────────────
    # if content.get("additional_info"):
    #     draw_text(draw, content.get("additional_info"),
    #             get_pos("additional_info"), title_font,
    #             get_size("additional_info", 24), get_color("additional_info"),
    #             get_anchor("additional_info"), max_width=text_max_width)

    # ── Additional Info with badge background ─────────────────────────
    if content.get("additional_info"):
        info_p = placement.get("additional_info", {})
        info_x, info_y = get_pos("additional_info")
        info_font_size = get_size("additional_info", 28)
        info_color = get_color("additional_info")
        
        # Draw badge background behind promo text
        font = load_font(title_font, info_font_size)
        fixed_info = fix_hebrew_text(content.get("additional_info"))
        bbox = font.getbbox(fixed_info)
        text_w = bbox[2] - bbox[0]
        pad_x, pad_y = 30, 15
        
        draw.rounded_rectangle(
            [info_x - text_w//2 - pad_x, info_y - info_font_size//2 - pad_y,
            info_x + text_w//2 + pad_x, info_y + info_font_size//2 + pad_y],
            radius=8,
            fill=tuple(info_p.get("bg_color", [220, 30, 30]))  # red badge
        )
        draw_text(draw, content.get("additional_info"),
                (info_x, info_y), title_font,
                info_font_size, (255, 255, 255),  # white text on badge
                get_anchor("additional_info"), max_width=text_max_width)

    # ── Brand name ────────────────────────────────────────────────────
    draw_text(draw, content.get("brand_name"),
              get_pos("brand_name"), title_font,
              get_size("brand_name", 28), get_color("brand_name"),
              get_anchor("brand_name"), max_width=text_max_width)

    # ── Tagline ───────────────────────────────────────────────────────
    draw_text(draw, content.get("tagline"),
              get_pos("tagline"), subtitle_font,
              get_size("tagline", 22), get_color("tagline"),
              get_anchor("tagline"), max_width=text_max_width)


    # ── CTA Button ────────────────────────────────────────────────────
    cta_text = content.get("cta")
    if cta_text:
        cta_p = placement.get("cta", {})
        cta_x, cta_y = get_pos("cta")
        bg_color = tuple(cta_p.get("bg_color", [200, 50, 50]))
        btn_w = int(width * 0.35)
        btn_h = 62
        draw.rounded_rectangle(
            [cta_x - btn_w // 2, cta_y - btn_h // 2,
             cta_x + btn_w // 2, cta_y + btn_h // 2],
            radius=31,
            fill=bg_color
        )
        draw_text(draw, cta_text, (cta_x, cta_y), title_font,
                  get_size("cta", 28), get_color("cta"), get_anchor("cta"))

    # ── Contact Info ──────────────────────────────────────────────────
    contact_text = " | ".join(filter(None, [
        content.get("phone"),
        content.get("address"),
        content.get("website")
    ]))
    if contact_text:
        draw_text(draw, contact_text,
                  get_pos("contact"), subtitle_font,
                  get_size("contact", 18), get_color("contact"), get_anchor("contact"))

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()







#--------------------------------------------------------------
# from PIL import Image, ImageDraw, ImageFont
# from bidi.algorithm import get_display
# import arabic_reshaper
# import io
# import os
# from networkx import draw
# import numpy as np
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent.parent
# FONTS_DIR = BASE_DIR / "fonts"


# def fix_hebrew_text(text: str) -> str:
#     if not text:
#         return ""
#     reshaped_text = arabic_reshaper.reshape(text)
#     bidi_text = get_display(reshaped_text)
#     return bidi_text


# def load_font(font_name, font_size):
#     font_path = FONTS_DIR / font_name
#     try:
#         return ImageFont.truetype(str(font_path), font_size)
#     except Exception as e:
#         print("FONT LOAD FAILED:", e)
#         return ImageFont.load_default()


# def draw_text(draw, text, position, font_name, font_size, color=(0, 0, 0), anchor="mm"):
#     if not text:
#         return
#     font = load_font(font_name, font_size)
#     fixed_text = fix_hebrew_text(text)
#     draw.text(position, fixed_text, font=font, fill=color, anchor=anchor)


# def render_poster_text(image_bytes:bytes, content:dict) -> bytes:

#     image= Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     draw = ImageDraw.Draw(image)
#     width, height = image.size
#     cx = width / 2

#     title_font = "Rubik-Bold.ttf"
#     subtitle_font = "Rubik-Regular.ttf"

#     # -------------zone 1: top text area (0% - 28%)----------------------
#     draw_text(draw, content.get("title"), (cx, int(height * 0.10)), title_font, 70, (0,0,0))
#     draw_text(draw, content.get("subtitle"), (cx, int(height * 0.19)), subtitle_font,38, (30,30,30))

#     # -------------- Zone 2: brand name and tagline (68% - 82%)----------------------
#     #brand + tagline with readable background
#     brand_y = int(height *0.72)
#     tagline_y = int(height * 0.78)

#     overlay = Image.new("RGBA", image.size, (0,0,0,0))
#     overlay_draw = ImageDraw.Draw(overlay)
#     overlay_draw.rectangle(
#         [0, brand_y - 25, width, tagline_y + 30], fill=(255,255,255,120)
#     )
#     image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGBA")
#     draw = ImageDraw.Draw(image)

#     draw_text(draw, content.get("brand_name"), (cx, brand_y), title_font, 35, (10, 10, 10))
#     draw_text(draw, content.get("tagline"), (cx, tagline_y), subtitle_font, 30, (30,30, 30))


#     #------zone 4: CTA button -------------------------
#     cta_text = content.get("cta")
#     if cta_text:
#         btn_w = int(width * 0.35)
#         btn_h = 62
#         cta_y = int(height * 0.86)
#         draw.rounded_rectangle(
#             [cx - btn_w // 2, cta_y - btn_h // 2,
#              cx + btn_w // 2, cta_y + btn_h // 2],
#             radius=31,
#             fill=(200, 50, 50)
#         )
#         draw_text(draw, cta_text, (cx, cta_y), title_font, 28, (255, 255, 255))
    
#     #--- zone 5: Contact info (94% - 99%)----------------------
#     contact_text = " | ".join(filter(None, [
#         content.get("phone"),
#         content.get("address"),
#         content.get("website")
#     ]))
#     draw_text(draw, contact_text, (cx, int(height * 0.94)), subtitle_font, 20, (20, 20, 20))

#     buffer = io.BytesIO()
#     image.save(buffer, format="PNG")
#     buffer.seek(0)
#     return buffer.getvalue()
















# #-------------------------------------------------

# # def render_poster_text(image_bytes: bytes, content: dict) -> bytes:
# #     image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
# #     draw = ImageDraw.Draw(image)

# #     width, height = image.size
# #     cx = width / 2

# #     title_font = "Rubik-Bold.ttf"
# #     subtitle_font = "Rubik-Regular.ttf"

# #     # ── ZONE 1: TOP TEXT AREA (0% – 28%) ──────────────────────────────
# #     title_y = int(height * 0.10)
# #     draw_text(draw, content.get("title"), (cx, title_y), title_font, 70, (0, 0, 0))

# #     subtitle_y = int(height * 0.18)
# #     draw_text(draw, content.get("subtitle"), (cx, subtitle_y), subtitle_font, 40, (30, 30, 30))

# #     # ── ZONE 3: CTA BUTTON (72% – 80%) ────────────────────────────────
# #     cta_text = content.get("cta")
# #     if cta_text:
# #         # detected_y = detect_cta(image)
# #         # cta_y = detected_y if detected_y else int(height * 0.80)  # must match prompt's 78%
# #         # print(f"CTA button detected at y={detected_y}, using y={cta_y} for text placement.")
# #         cta_y = int(height * 0.78)
# #         draw_text(draw, cta_text, (cx, cta_y), title_font, 40, (255, 255, 255))

# # #     cta_text = content.get("cta")
# # #     font = load_font(title_font, 32)

# # # # Measure text
# # #     bbox = font.getbbox(cta_text)
# # #     text_w = bbox[2] - bbox[0]
# # #     text_h = bbox[3] - bbox[1]

# # #     # Padding (important for that "pill" look)
# # #     pad_x = 50
# # #     pad_y = 22

# # #     btn_w = text_w + pad_x * 2
# # #     btn_h = text_h + pad_y * 2

# # #     cta_y = int(height * 0.82)

# # #     # Button background (light pill like your image)
# # #     draw.rounded_rectangle(
# # #         [cx - btn_w // 2, cta_y - btn_h // 2,
# # #         cx + btn_w // 2, cta_y + btn_h // 2],
# # #         radius=btn_h // 2,
# # #         fill=(235, 230, 210)   # soft beige/white like reference
# # #     )

# # #     # Optional: subtle border (this makes it POP)
# # #     draw.rounded_rectangle(
# # #         [cx - btn_w // 2, cta_y - btn_h // 2,
# # #         cx + btn_w // 2, cta_y + btn_h // 2],
# # #         radius=btn_h // 2,
# # #         outline=(200, 200, 200),
# # #         width=2
# # #     )

# # # Text on top
# #     # draw_text(draw, cta_text, (cx, cta_y), title_font, 32, (60, 60, 60))

# #     # # Draw text
# #     # draw_text(draw, cta_text, (cx, cta_y), title_font, 35, (255, 255, 255))

# #     # cta_text = content.get("cta")
# #     # if cta_text:
# #     #     btn_w, btn_h = int(width * 0.55), 68
# #     #     cta_y = int(height * 0.80)
# #     #     draw.rounded_rectangle(
# #     #         [cx - btn_w // 2, cta_y - btn_h // 2,
# #     #          cx + btn_w // 2, cta_y + btn_h // 2],
# #     #         radius=34,
# #     #         fill=(180, 30, 30)  
# #     #     )
# #     #     draw_text(draw, cta_text, (cx, cta_y), title_font, 30, (255, 255, 255))

# #     # ── ZONE 4: FOOTER (82% – 97%) ────────────────────────────────────
# #     # draw_text(draw, content.get("brand_name"), (cx, int(height * 0.70)), title_font, 26, (0, 0, 0))
# #     # draw_text(draw, content.get("tagline"), (cx, int(height * 0.75)), subtitle_font, 21, (40, 40, 40))
# #     footer_top = cta_y - 100 if cta_text else int(height * 0.68)
# #     draw_text(draw, content.get("brand_name"), (cx, footer_top), title_font, 35, (0, 0, 0))
# #     draw_text(draw, content.get("tagline"), (cx, footer_top + 40), subtitle_font, 30, (40, 40, 40))

# #     contact_text = " | ".join(filter(None, [
# #         content.get("phone"),
# #         content.get("address"),
# #         content.get("website")
# #     ]))
# #     draw_text(draw, contact_text, (cx, int(height * 0.99)), subtitle_font, 28, (50, 50, 50), anchor="mb")

# #     buffer = io.BytesIO()
# #     image.save(buffer, format="PNG")
# #     buffer.seek(0)
# #     return buffer.getvalue()

