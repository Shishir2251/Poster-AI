"""
html_designer.py
Uses Claude Vision to analyze the background image and generate
a complete, self-contained HTML poster with perfect Hebrew RTL text.
"""

import base64
import re
import anthropic
import os
from PIL import Image
import io
from dotenv import load_dotenv

load_dotenv()

claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

CANVAS_SIZES = {
    "1:1":  (1024, 1024),
    "4:5":  (1024, 1280),
    "9:16": (1024, 1792),
    "16:9": (1792, 1024),
}

HEBREW_FONTS = [
    "Heebo", "Rubik", "Assistant",
    "Frank Ruhl Libre", "Secular One", "Varela Round", "Suez One",
]


def generate_poster_html(
    background_bytes: bytes,
    content: dict,
    output_format: str = "1:1",
    tokens: dict = None,
) -> str:
    width, height = CANVAS_SIZES.get(output_format, (1024, 1024))

    # ── Small version for Claude vision (reduces tokens) ──────────────────────
    img = Image.open(io.BytesIO(background_bytes))
    img.thumbnail((512, 512))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    bg_b64_small = base64.standard_b64encode(buf.getvalue()).decode()

    # ── Full res for HTML embedding ────────────────────────────────────────────
    bg_b64_full = base64.standard_b64encode(background_bytes).decode()

    layout = content.get("layout", "center")
    archetype = (tokens or {}).get("archetype", "centered_hero")
    mood_accent = (tokens or {}).get("color_mood", {}).get("accent", "#E74C3C")

    prompt = f"""
You are an elite graphic designer and front-end developer specialising in
Hebrew RTL marketing posters.

I will give you a background image ({width}×{height}px) and brand content.
Your job: return a SINGLE, COMPLETE, self-contained HTML file that renders
a stunning marketing poster on top of this background.

══════════════════════════════════════════════
CANVAS & BACKGROUND  (CRITICAL)
══════════════════════════════════════════════
Width : {width}px  |  Height: {height}px

You MUST set the background image on the root div using this EXACT inline style:
  style="background-image:url('__BG_BASE64_PLACEHOLDER__');background-size:cover;background-position:center;"

Use the literal string __BG_BASE64_PLACEHOLDER__ — the system will replace it
with the actual base64 image data after you respond. Do NOT generate or invent
any base64 string yourself.

══════════════════════════════════════════════
BRAND CONTENT  (render EXACTLY — do not invent or change any word)
══════════════════════════════════════════════
Title          : {content.get("title", "")}
Subtitle       : {content.get("subtitle", "")}
Brand Name     : {content.get("brand_name", "")}
Tagline        : {content.get("tagline", "")}
CTA Button     : {content.get("cta", "")}
Additional     : {content.get("additional_info", "")}
Phone          : {content.get("phone", "")}
Address        : {content.get("address", "")}
Website        : {content.get("website", "")}
Primary Color  : {content.get("primary_color", "#1A1A1A")}
Secondary Color: {content.get("secondary_color", "#E74C3C")}

══════════════════════════════════════════════
DESIGN DIRECTION
══════════════════════════════════════════════
Layout archetype : {archetype}
Subject position : {layout} aligned in the image
Accent color     : {mood_accent}
Style            : {content.get("design_style_prompt", "modern minimalist luxury")}

Analyse the background image carefully:
- Where is the empty / clean space?
- What colors dominate each zone?
- Where is the product / hero element?
Place ALL text elements ONLY on clean empty areas — never over the product.

══════════════════════════════════════════════
TYPOGRAPHY RULES  (CRITICAL)
══════════════════════════════════════════════
1. Content language is: {content.get("language", "hebrew")}
   - If Hebrew or Arabic: use direction:rtl; unicode-bidi:bidi-override on EVERY text element
   - If English or other LTR: use direction:ltr
   - Render ALL text EXACTLY as provided — do not translate, do not change any word

2. Load Hebrew fonts from Google Fonts. Choose 1-2 from: {", ".join(HEBREW_FONTS)}
3. Title must be the largest element (golden-ratio scale).
4. Create dramatic visual hierarchy: title >> subtitle >> tagline >> body.
5. Add text-shadow or drop-shadow to ensure legibility over any background.
6. Letter-spacing, line-height, font-weight — vary them to create premium feel.
7. Never use placeholder or lorem ipsum text.

══════════════════════════════════════════════
LAYOUT ZONES  (STRICT)
══════════════════════════════════════════════
- TOP ZONE    (0–22% height)   : Title + Subtitle — place here
- HERO ZONE   (22%–65% height) : Product — NO text here
- BOTTOM ZONE (65%–100% height): Brand, Tagline, CTA, Contact — place here

If layout is "left"  → text goes on RIGHT side (x > 55%)
If layout is "right" → text goes on LEFT side  (x < 45%)
If layout is "center"→ text centered horizontally

══════════════════════════════════════════════
CTA BUTTON
══════════════════════════════════════════════
- Gradient background (primary → secondary color)
- box-shadow for depth
- border-radius: 40-50px
- min padding: 16px 40px
- Must be visually dominant

══════════════════════════════════════════════
BADGE  (only if additional_info is not empty)
══════════════════════════════════════════════
- Shape: circle, starburst, or rounded-rect, or use clip-path for unique shapes
- Vibrant contrasting color (red, gold, orange)
- Position at right:5% and at edge of hero zone (≈62% from top) — NEVER inside the product image frame
- Never overlap the product/hero image

BADGE TEXT RULE:
- Numbers and % symbols must stay LTR inside RTL context
- Wrap number+% in a span with direction:ltr; display:inline-block;
- Example: <span style="direction:ltr;display:inline-block;">30%</span>

══════════════════════════════════════════════
CONTACT INFO RULES  (CRITICAL)
══════════════════════════════════════════════
- URLs, phone numbers, and numeric addresses must NEVER be reversed
- Always wrap them with: style="direction:ltr;display:inline-block;unicode-bidi:plaintext;"
- Example URL: <span style="direction:ltr;display:inline-block;">www.google.com</span>
- Example phone: <span style="direction:ltr;display:inline-block;">054-1234567</span>
- Hebrew labels like "טלפון:" or "אתר:" stay RTL — only the value goes LTR
══════════════════════════════════════════════
DECORATIVE ELEMENTS
══════════════════════════════════════════════
Add 1-3 subtle CSS decorative elements (lines, shapes, overlays).
Never obscure text.

══════════════════════════════════════════════
OUTPUT FORMAT  (CRITICAL)
══════════════════════════════════════════════
Return ONLY raw HTML. No markdown fences. No explanation.
Requirements:
1. Start with <!DOCTYPE html>
2. Self-contained (Google Fonts CDN allowed)
3. html, body: margin:0; padding:0; overflow:hidden; width:{width}px; height:{height}px
4. Single root div: exactly {width}px × {height}px
5. Root div MUST have: style="background-image:url('__BG_BASE64_PLACEHOLDER__');background-size:cover;background-position:center;"
6. All elements use position:absolute
"""

    response = claude.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=8000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": bg_b64_small,
                    },
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        }],
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences
    raw = re.sub(r"^```html\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```\s*$", "", raw)
    raw = raw.strip()

    # ── Inject full-res background (guaranteed, regardless of what Claude did) ─
    bg_data_uri = f"data:image/png;base64,{bg_b64_full}"

    if "__BG_BASE64_PLACEHOLDER__" in raw:
        # Claude used the placeholder correctly
        raw = raw.replace("__BG_BASE64_PLACEHOLDER__", bg_data_uri)
    elif "background-image" in raw:
        # Claude set its own background — replace it with our real image
        raw = re.sub(
            r'background-image\s*:\s*url\([^)]*\)',
            f'background-image:url("{bg_data_uri}")',
            raw
        )
    else:
        # Claude didn't set any background — force inject into root div
        raw = re.sub(
            r'(<div[^>]*id=["\']?poster["\']?[^>]*)(style=["\'])',
            rf'\1style="background-image:url(\'{bg_data_uri}\');background-size:cover;background-position:center;',
            raw,
            count=1
        )
        # Fallback: inject into body if no poster div found
        if bg_data_uri not in raw:
            raw = raw.replace(
                "<body",
                f'<body style="background-image:url(\'{bg_data_uri}\');background-size:cover;background-position:center;"',
                1
            )

    return raw






#----------------------------------------- previous working version
# """
# html_designer.py
# Uses Claude Vision to analyze the background image and generate
# a complete, self-contained HTML poster with perfect Hebrew RTL text.
# """

# import base64
# import json
# import re
# import anthropic
# import os
# from dotenv import load_dotenv

# load_dotenv()

# claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# # ── Canvas size map ────────────────────────────────────────────────────────────
# CANVAS_SIZES = {
#     "1:1":  (1024, 1024),
#     "4:5":  (1024, 1280),
#     "9:16": (1024, 1792),
#     "16:9": (1792, 1024),
# }

# # ── Hebrew Google Fonts available ──────────────────────────────────────────────
# HEBREW_FONTS = [
#     "Heebo",
#     "Rubik",
#     "Assistant",
#     "Frank Ruhl Libre",
#     "Secular One",
#     "Varela Round",
#     "Suez One",
# ]


# def generate_poster_html(
#     background_bytes: bytes,
#     content: dict,
#     output_format: str = "1:1",
#     tokens: dict = None,
# ) -> str:
#     """
#     Sends the background image to Claude Vision.
#     Claude returns a complete self-contained HTML poster string.
#     """
#     width, height = CANVAS_SIZES.get(output_format, (1024, 1024))
#     # bg_b64 = base64.standard_b64encode(background_bytes).decode()
#      # Resize image before sending to Claude to reduce token count
#     from PIL import Image
#     import io
#     img = Image.open(io.BytesIO(background_bytes))
#     img.thumbnail((512, 512))  # downscale for Claude vision only
#     buf = io.BytesIO()
#     img.save(buf, format="JPEG", quality=75)  # JPEG = much smaller
#     small_bytes = buf.getvalue()
#     bg_b64_small = base64.standard_b64encode(small_bytes).decode()

#     # Full res base64 for actual HTML embedding
#     bg_b64_full = base64.standard_b64encode(background_bytes).decode()

#     layout = content.get("layout", "center")
#     archetype = (tokens or {}).get("archetype", "centered_hero")
#     mood_accent = (tokens or {}).get("color_mood", {}).get("accent", "#E74C3C")

#     prompt = f"""
# You are an elite graphic designer and front-end developer specialising in
# Hebrew RTL marketing posters.

# I will give you a background image ({width}×{height}px) and brand content.
# Your job: return a SINGLE, COMPLETE, self-contained HTML file that renders
# a stunning marketing poster on top of this background.

# ══════════════════════════════════════════════
# CANVAS & BACKGROUND
# ══════════════════════════════════════════════
# Width : {width}px  |  Height: {height}px
# The background image must be set as the CSS background of the root element.
# Embed it as a base64 data-URI so the file is fully self-contained:

# ══════════════════════════════════════════════
# BRAND CONTENT  (render EXACTLY — do not invent or change any word)
# ══════════════════════════════════════════════
# Title         : {content.get("title", "")}
# Subtitle      : {content.get("subtitle", "")}
# Brand Name    : {content.get("brand_name", "")}
# Tagline       : {content.get("tagline", "")}
# CTA Button    : {content.get("cta", "")}
# Additional    : {content.get("additional_info", "")}
# Phone         : {content.get("phone", "")}
# Address       : {content.get("address", "")}
# Website       : {content.get("website", "")}
# Primary Color : {content.get("primary_color", "#1A1A1A")}
# Secondary Color: {content.get("secondary_color", "#E74C3C")}

# ══════════════════════════════════════════════
# DESIGN DIRECTION
# ══════════════════════════════════════════════
# Layout archetype : {archetype}
# Subject position : {layout} aligned in the image
# Accent color     : {mood_accent}
# Style            : {content.get("design_style_prompt", "modern minimalist luxury")}

# Analyse the background image carefully:
# - Where is the empty / clean space?
# - What colors dominate each zone?
# - Where is the product / hero element?
# Place ALL text elements ONLY on clean empty areas — never over the product.

# ══════════════════════════════════════════════
# TYPOGRAPHY RULES  (CRITICAL)
# ══════════════════════════════════════════════
# 1. ALL text is Hebrew — use direction:rtl; unicode-bidi:bidi-override on every text element.
# 2. Load Hebrew fonts from Google Fonts. Choose 1-2 from: {", ".join(HEBREW_FONTS)}
# 3. Title must be the largest element (golden-ratio scale).
# 4. Create dramatic visual hierarchy: title >> subtitle >> tagline >> body.
# 5. Add text-shadow or drop-shadow to ensure legibility over any background.
# 6. Letter-spacing, line-height, font-weight — vary them to create premium feel.
# 7. Never use placeholder or lorem ipsum text.

# ══════════════════════════════════════════════
# LAYOUT ZONES  (STRICT)
# ══════════════════════════════════════════════
# - TOP ZONE    (0 – 22% height)  : Title + Subtitle  — place here
# - HERO ZONE   (22% – 65% height): Product image — NO text here
# - BOTTOM ZONE (65% – 100% height): Brand, Tagline, CTA, Contact — place here

# If layout is "left"  → text goes on RIGHT side (x > 55%)
# If layout is "right" → text goes on LEFT side  (x < 45%)
# If layout is "center"→ text centered horizontally

# ══════════════════════════════════════════════
# CTA BUTTON  (make it stunning)
# ══════════════════════════════════════════════
# - Use a gradient background (primary → secondary color)
# - Add box-shadow for depth
# - Border-radius: 40-50px (pill shape) OR use clip-path for unique shapes
# - Hover state not needed (static image)
# - Width: auto with generous padding (min 200px)
# - The button must pop — it is the most important interactive element

# ══════════════════════════════════════════════
# BADGE / PROMO  (only if additional_info is not empty)
# ══════════════════════════════════════════════
# If additional_info contains a discount or promo:
# - Render it as a badge: circle, starburst, or rounded-rect
# - Use a vibrant contrasting color (red, gold, orange)
# - Position it at the edge of the hero zone (≈65% from top)
# - Make it feel urgent and eye-catching

# ══════════════════════════════════════════════
# DECORATIVE ELEMENTS
# ══════════════════════════════════════════════
# Add 1-3 subtle decorative CSS elements to make it feel designed:
# - Thin accent lines, geometric shapes, gradient overlays
# - Match the brand colors and style preset
# - Never clash with or obscure text

# ══════════════════════════════════════════════
# OUTPUT FORMAT  (CRITICAL)
# ══════════════════════════════════════════════
# Return ONLY the raw HTML — no markdown fences, no explanation, no comments
# outside the HTML. The file must:
# 1. Start with <!DOCTYPE html>
# 2. Be 100% self-contained (no external files except Google Fonts CDN)
# 3. Have body/html with margin:0; padding:0; overflow:hidden
# 4. Have a single root div exactly {width}px × {height}px
# 5. Use position:absolute for all poster elements
# 6. Embed the background image as base64 (already provided above)
# """

#     response = claude.messages.create(
#         model="claude-sonnet-4-5",
#         max_tokens=8000,
#         messages=[{
#             "role": "user",
#             "content": [
#                 {
#                     "type": "image",
#                     "source": {
#                         "type": "base64",
#                         "media_type": "image/jpeg",
#                         "data": bg_b64_small,
#                     },
#                 },
#                 {
#                     "type": "text",
#                     "text": prompt,
#                 },
#             ],
#         }],
#     )

#     raw = response.content[0].text.strip()
#     raw = re.sub(r"^```html\s*", "", raw, flags=re.IGNORECASE)
#     raw = re.sub(r"```\s*$", "", raw)
    
#     # Replace placeholder with actual full-res base64
#     html = raw.replace("__BG_BASE64__", bg_b64_full)
    
#     return html.strip()