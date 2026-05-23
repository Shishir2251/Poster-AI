import os
import base64
from openai import OpenAI
import anthropic
import re
import cloudinary.uploader
from app.services.html_renderer import render_html_to_png

openai_client = OpenAI()
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)


def generate_logo_background(prompt: str, image_path=None) -> bytes:
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img:
            result = openai_client.images.edit(
                model="gpt-image-1",
                prompt=prompt,
                image=img,
                size="1024x1024",
            )
    else:
        result = openai_client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
        )
    return base64.b64decode(result.data[0].b64_json)


def generate_logo_html(logo_bytes: bytes, data: dict) -> str:
    brand_name = data.get("brand_name", "")
    tagline = data.get("tagline", "")
    language = data.get("language", "English")
    color_palette = data.get("color_palette", "")
    logo_style = data.get("logo_style", "modern minimal")
    industry = data.get("industry", "")

    # Resize for Claude vision
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(logo_bytes))
    img.thumbnail((512, 512))
    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=75)
    logo_b64_small = base64.standard_b64encode(buf.getvalue()).decode()
    logo_b64_full = base64.standard_b64encode(logo_bytes).decode()

    prompt = f"""
You are an elite logo designer. Create a complete HTML logo card.

CANVAS: 1024x1024px

══════════════════════════════
LOGO IMAGE (CRITICAL)
══════════════════════════════
A professionally generated logo image is provided.
Embed it as the root div background using this EXACT placeholder:
  background-image: url('__BG_BASE64_PLACEHOLDER__');
  background-size: cover;
  background-position: center;

DO NOT replace it with CSS. DO NOT use <img> tags.

══════════════════════════════
BRAND CONTENT (render EXACTLY as given — do NOT translate)
══════════════════════════════
Brand Name : {brand_name}
Tagline    : {tagline}
Industry   : {industry}

══════════════════════════════
DESIGN
══════════════════════════════
Language     : {language}
Style        : {logo_style}
Color Palette: {color_palette}

- If Hebrew/Arabic → direction:rtl; unicode-bidi:bidi-override on every text element
- If English → direction:ltr
- Load premium Hebrew Google Font: Frank Ruhl Libre or Suez One for Hebrew, Playfair Display for English
- Brand name: large, bold, prominent — minimum 64px
- Tagline: smaller, elegant — minimum 32px
- Place brand name and tagline at the bottom 25% of canvas
- Text must be legible over the logo image
- Add text shadow for contrast
- Add a subtle semi-transparent dark overlay (rgba(0,0,0,0.3)) behind text area for legibility

══════════════════════════════
OUTPUT (CRITICAL)
══════════════════════════════
- Return ONLY raw HTML, no markdown fences
- Start with <!DOCTYPE html>
- html, body: margin:0; padding:0; overflow:hidden; width:1024px; height:1024px
- ONE root div: 1024px x 1024px, overflow:hidden
- Root div MUST contain: background-image:url('__BG_BASE64_PLACEHOLDER__')
- All children: position:absolute
- Nothing overflows outside 1024x1024px
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
                        "media_type": "image/png",
                        "data": logo_b64_small,
                    },
                },
                {"type": "text", "text": prompt},
            ],
        }],
    )

    raw = response.content[0].text.strip()
    raw = re.sub(r"^```html\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"^```\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```\s*$", "", raw)
    raw = raw.strip()

    # Inject full-res background
    bg_data_uri = f"data:image/png;base64,{logo_b64_full}"

    if "__BG_BASE64_PLACEHOLDER__" in raw:
        raw = raw.replace("__BG_BASE64_PLACEHOLDER__", bg_data_uri)
    elif "background-image" in raw:
        raw = re.sub(
            r'background-image\s*:\s*url\([^)]*\)',
            f'background-image:url("{bg_data_uri}")',
            raw
        )
    else:
        if bg_data_uri not in raw:
            raw = raw.replace(
                "<body",
                f'<body style="background-image:url(\'{bg_data_uri}\');background-size:cover;background-position:center;"',
                1
            )

    return raw


def generate_logo(data, image_path=None):
    brand_name = data.get("brand_name", "")
    tagline = data.get("tagline", "")
    vision = data.get("vision", "")
    industry = data.get("industry", "")
    logo_style = data.get("logo_style", "modern minimal")
    color_palette = data.get("color_palette", "")
    language = data.get("language", "Hebrew")

    # Step 1 — GPT generates logo visual
    background_prompt = f"""
Design a professional vector-style logo graphic. NO TEXT.

Brand: {brand_name}
Industry: {industry}
Vision: {vision}
Style: {logo_style}
Colors: {color_palette}

- Flat vector aesthetic
- Minimal clean shapes
- No photo realism
- Absolutely NO text, NO words, NO letters, NO numbers anywhere — not even decorative scripts or watermarks
- Centered icon/mark composition
- Suitable as a logo symbol — must be truly unique, avoid clichéd combinations
- Think deeply about the brand vision and industry to create something unexpected and memorable
"""

    print("[Logo Step 1] GPT generating logo visual...")
    logo_bytes = generate_logo_background(background_prompt, image_path)

    # Step 2 — Claude generates HTML with brand name + tagline
    print("[Logo Step 2] Claude designing HTML logo card...")
    html = generate_logo_html(logo_bytes, data)

    # Step 3 — Playwright renders to PNG
    print("[Logo Step 3] Playwright rendering...")
    final_png = render_html_to_png(html, width=1024, height=1024)

    # Step 4 — Upload to Cloudinary
    print("[Logo Step 4] Uploading...")
    upload_result = cloudinary.uploader.upload(final_png, folder="logos")
    url = upload_result.get("secure_url")
    print(f"[Logo Done] {url}")

    return [url]