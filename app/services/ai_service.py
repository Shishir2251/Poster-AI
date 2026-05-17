from openai import OpenAI
import cloudinary.uploader
import os
import base64
import random
from dotenv import load_dotenv
from app.services.html_designer import generate_poster_html
import re
import json
import anthropic


load_dotenv()

from app.services.html_renderer import render_html_to_png
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CANVAS_SIZES = {
    "1:1":  (1024, 1024),
    "4:5":  (1024, 1280),
    "9:16": (1024, 1792),
    "16:9": (1792, 1024),
}

LAYOUT_ARCHETYPES = [
    "centered_hero", "asymmetric_left", "asymmetric_right",
    "split_panel", "bold_typographic", "editorial_magazine",
    "luxury_centered", "dramatic_fullbleed",
]

def get_design_tokens(content: dict) -> dict:
    # archetype = random.choice(LAYOUT_ARCHETYPES)
    # return {"archetype": archetype}
    return {}

def generate_background(prompt: str, output_format: str, image_path=None) -> bytes:
    size_map = {
        "1:1": "1024x1024",
        "4:5": "1024x1536",
        "9:16": "1024x1536",
        "16:9": "1536x1024"
    }
    size = size_map.get(output_format, "1024x1024")

    if image_path and os.path.exists(image_path):
        from app.services.remove_bg import remove_bg_api
        image_path = remove_bg_api(image_path)
        with open(image_path, "rb") as img:
            result = openai_client.images.edit(
                model="gpt-image-1",
                prompt=prompt,
                size=size,
                image=img
            )
    else:
        result = openai_client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size
        )

    return base64.b64decode(result.data[0].b64_json)


def generate_poster(prompt: str, content: dict, output_format="1:1", image_path=None):
    width, height = CANVAS_SIZES.get(output_format, (1024, 1024))

    # Step 1 — GPT-image-1 generates background (no text)
    print("[Step 1] GPT-image-1 generating background...")
    background_bytes = generate_background(prompt, output_format, image_path)

    # Step 2 — Claude generates HTML with background embedded
    print("[Step 2] Claude designing HTML poster...")
    html = generate_poster_html(
        background_bytes=background_bytes,
        content=content,
        output_format=output_format)

    # Step 3 — Playwright renders to PNG
    print("[Step 3] Playwright rendering...")
    final_png = render_html_to_png(html, width=width, height=height)

    # Step 4 — Cloudinary
    print("[Step 4] Uploading...")
    result = cloudinary.uploader.upload(final_png, folder="posters")
    url = result.get("secure_url")
    print(f"[Done] {url}")
    return url




def regenerate_poster(prompt: str, output_format: str, image_url: str = None, original_html: str = None):
    """
    Regenerate by modifying the existing HTML poster based on user instructions.
    Much faster and cheaper — no GPT image generation needed.
    """
    width, height = CANVAS_SIZES.get(output_format, (1024, 1024))

    try:
        # ── If we have the original HTML, modify it directly ──────────────────
        if original_html:
            modification_prompt = f"""
You are an elite graphic designer. You have an existing HTML marketing poster.
The user wants to make specific changes to it.

USER REQUESTED CHANGES:
{prompt}

RULES:
- Apply ONLY what the user asked to change
- Keep everything else exactly the same
- Preserve all Hebrew text exactly as is — do not translate or change
- Preserve the background image (the base64 url() value must stay untouched)
- Preserve all font sizes, positions, and layout unless user asked to change them
- Return ONLY the complete modified HTML — no explanation, no markdown fences

ORIGINAL HTML:
{original_html}
"""
            response = anthropic.Anthropic().messages.create(
                model="claude-sonnet-4-6",
                max_tokens=8000,
                messages=[{"role": "user", "content": modification_prompt}]
            )

            raw = response.content[0].text.strip()
            raw = re.sub(r"^```html\s*", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"```\s*$", "", raw)
            modified_html = raw.strip()

        # ── Fallback: if no HTML, use vision to describe then regenerate ──────
        elif image_url:
            import httpx

            # Download image for Claude vision
            img_bytes = httpx.get(image_url).content
            img_b64 = base64.b64encode(img_bytes).decode()

            vision_prompt = f"""
You are an elite graphic designer. Analyze this marketing poster and apply the following changes.

USER REQUESTED CHANGES:
{prompt}

Generate a complete new HTML poster that:
- Applies the requested changes
- Keeps everything else the same as the original
- Has perfect Hebrew RTL text
- Is {width}x{height}px
- Returns ONLY raw HTML, no markdown

CANVAS: {width}x{height}px
OUTPUT RULES:
- Start with <!DOCTYPE html>
- html, body: margin:0; padding:0; overflow:hidden; width:{width}px; height:{height}px
- ONE root div: {width}px x {height}px, overflow:hidden
- All children: position:absolute
- Google Fonts CDN allowed
"""
            response = anthropic.Anthropic().messages.create(
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
                                "data": img_b64,
                            }
                        },
                        {"type": "text", "text": vision_prompt}
                    ]
                }]
            )

            raw = response.content[0].text.strip()
            raw = re.sub(r"^```html\s*", "", raw, flags=re.IGNORECASE)
            raw = re.sub(r"```\s*$", "", raw)
            modified_html = raw.strip()

        else:
            raise ValueError("Either original_html or image_url must be provided")

        # ── Render and upload ─────────────────────────────────────────────────
        final_png = render_html_to_png(modified_html, width=width, height=height)
        upload_result = cloudinary.uploader.upload(final_png, folder="re_generated_posters")
        return {
            "url": upload_result["secure_url"],
            "html": modified_html  # return HTML so it can be stored for future edits
        }

    except Exception as e:
        print("Regeneration failed:", e)
        raise


def CleanData(text):
    # Step 1: Remove all literal backslashes
    cleaned = text.replace("\\", "")

    # Step 2: Remove backticks (` or ``` )
    cleaned = re.sub(r"`{1,3}", "", cleaned)

    # Step 3: Remove code language keywords (json, bash, python, etc.)
    cleaned = re.sub(r'\b(json|bash|python)\b', '', cleaned, flags=re.IGNORECASE)

    # Step 4: Remove newlines and extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    print(cleaned)
    # cleaned = ast.literal_eval(cleaned)
    return cleaned
    
# AI Poster Idea → Structured Fields
def generate_poster_fields(user_idea: str):

    prompt = f"""
        You are a professional poster designer.

        A user will describe a poster idea.

        Your task is to convert the idea into structured poster inputs.

        Return ONLY valid JSON with these fields:

        title
        subtitle
        description
        cta
        design_style
        color_theme
        layout_hint

        Rules:
        - title must be short and catchy
        - subtitle supports the title
        - description explains the offer/event
        - cta should be a short action phrase
        - design_style should describe the visual style
        - color_theme should be 2–3 colors
        - layout_hint should explain image/text placement

        User Idea:
        {user_idea}
        """

    try:

        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are an expert poster designer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content
        cleaned_content = CleanData(content)

        try:
            # return json.loads(cleaned_content)
            return cleaned_content

        except json.JSONDecodeError:
            return {
                "error": "AI returned non JSON output",
                "raw_output": cleaned_content
            }

    except Exception as e:
        print("AI field generation error:", e)
        raise