
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

# HEBREW_FONTS = [
#     "Heebo", "Rubik", "Assistant",
#     "Frank Ruhl Libre", "Secular One", "Varela Round", "Suez One",
# ]


def generate_poster_html(
    background_bytes: bytes,
    content: dict,
    output_format: str = "1:1"
) -> str:
    width, height = CANVAS_SIZES.get(output_format, (1024, 1024))

    # ── Small version for Claude vision (reduces tokens) ─────
    img = Image.open(io.BytesIO(background_bytes))
    img.thumbnail((512, 512))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    bg_b64_small = base64.standard_b64encode(buf.getvalue()).decode()

    # ── Full res for HTML embedding ─────────
    bg_b64_full = base64.standard_b64encode(background_bytes).decode()

    prompt = f"""
You are an elite graphic designer. Create a complete HTML marketing poster.

CANVAS: {width}x{height}px

══════════════════════════════
BACKGROUND (CRITICAL)
══════════════════════════════
A professionally generated background image is provided.
You MUST embed it as the root div background using this EXACT placeholder:
  background-image: url('__BG_BASE64_PLACEHOLDER__');
  background-size: cover;
  background-position: center;

DO NOT replace it with CSS gradients. DO NOT use <img> tags.
You MAY add CSS overlays (dark vignette, gradient) on top for depth.

══════════════════════════════
BRAND CONTENT (render EXACTLY as given)
══════════════════════════════
CRITICAL: Render every field EXACTLY as typed — do NOT translate, 
do NOT transliterate, do NOT change any word in any field.
If the user typed Hebrew → show Hebrew. If English → show English.

Title      : {content.get("title", "")}
Subtitle   : {content.get("subtitle", "")}
Brand Name : {content.get("brand_name", "")}
Tagline    : {content.get("tagline", "")}
CTA        : {content.get("cta", "")}
Additional : {content.get("additional_info", "")}
Phone      : {content.get("phone", "")}
Address    : {content.get("address", "")}
Website    : {content.get("website", "")}

══════════════════════════════
DESIGN
══════════════════════════════
Language   : {content.get("language", "hebrew")}
Analyse the background image to determine the best layout:
- Where is the empty space? Place text there.
- Where is the product/subject? Never place text over it.
- Choose layout freely based on what you see.
Style      : {content.get("design_style_prompt", "modern minimalist")}
Primary    : {content.get("primary_color", "#1A1A1A")}
Secondary  : {content.get("secondary_color", "#E74C3C")}

- Hebrew/Arabic → direction:rtl; unicode-bidi:bidi-override on EVERY text element
- English → direction:ltr
- URLs, phones, numbers → direction:ltr; display:inline-block
- Load Hebrew Google Font from this list: Heebo, Rubik, Assistant, Frank Ruhl Libre, Secular One, Varela Round, Suez One
- Pick 1-2 fonts that match the poster style — vary your choice each generation

FONT SIZE RULES (STRICT — canvas is {width}x{height}px static image):
- Title: minimum 72px, bold
- Subtitle: minimum 48px
- Brand name: minimum 40px
- Tagline: minimum 36px
- CTA button text: minimum 36px
- Badge text: minimum 28px
- Contact/address/website: minimum 22px
- No text element ever below 22px
- When in doubt go BIGGER — poster is viewed scaled down on mobile feeds

- Title top 25%, CTA + contact bottom 20%, rest in middle
- All elements position:absolute inside root div
- Numbers/% in badge → <span style="direction:ltr;display:inline-block;">30%</span>
- CTA: random shape, gradient, box-shadow, min 250px wide
- Badge (only if additional_info not empty): vibrant contrasting color, right:4% top:62%
  Choose a RANDOM unique shape each generation from: circle, starburst (css clip-path polygon), 
  shield, hexagon, ribbon, diamond, rounded-rect with rotation, speech bubble
  Use CSS clip-path or border-radius creatively — never the same shape twice
══════════════════════════════
OUTPUT (CRITICAL)
══════════════════════════════
- Return ONLY raw HTML, no markdown fences
- Start with <!DOCTYPE html>
- html, body: margin:0; padding:0; overflow:hidden; width:{width}px; height:{height}px
- ONE root div: {width}px x {height}px, overflow:hidden
- Root div MUST contain: background-image:url('__BG_BASE64_PLACEHOLDER__')
- All children: position:absolute
- Nothing overflows outside {width}x{height}px
- Google Fonts CDN allowed
"""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
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