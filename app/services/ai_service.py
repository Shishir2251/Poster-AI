from openai import OpenAI
import cloudinary.uploader
import os
import base64
import random
from dotenv import load_dotenv
from app.services.html_designer import generate_poster_html

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
        output_format=output_format,
        tokens={},
    )

    # Step 3 — Playwright renders to PNG
    print("[Step 3] Playwright rendering...")
    final_png = render_html_to_png(html, width=width, height=height)

    # Step 4 — Cloudinary
    print("[Step 4] Uploading...")
    result = cloudinary.uploader.upload(final_png, folder="posters")
    url = result.get("secure_url")
    print(f"[Done] {url}")
    return url


# claude only version of ai_service, without nano banana background generation step. Claude will generate the full poster as HTML with CSS background, and then we render it to PNG and upload to Cloudinary.
# """
# ai_service.py  —  Claude-only pipeline:
#   1. Claude → complete HTML poster (CSS background, no image needed)
#   2. Playwright → PNG screenshot
#   3. Cloudinary → upload & return URL
# """

# import os
# import random
# from dotenv import load_dotenv
# import cloudinary.uploader

# from app.services.html_designer import generate_poster_html
# from app.services.html_renderer import render_html_to_png

# load_dotenv()

# GENERATED_DIR = "generated"
# os.makedirs(GENERATED_DIR, exist_ok=True)

# CANVAS_SIZES = {
#     "1:1":  (1024, 1024),
#     "4:5":  (1024, 1280),
#     "9:16": (1024, 1792),
#     "16:9": (1792, 1024),
# }

# GOLDEN_RATIO = 1.618

# LAYOUT_ARCHETYPES = [
#     "centered_hero", "top_heavy", "bottom_heavy", "asymmetric_left",
#     "asymmetric_right", "split_panel", "diagonal_flow", "minimalist_float",
#     "bold_typographic", "editorial_magazine", "dramatic_fullbleed",
#     "geometric_grid", "luxury_centered", "street_poster", "vintage_stamp",
# ]

# CATEGORY_ARCHETYPE_WEIGHTS = {
#     "food":    ["centered_hero", "bottom_heavy", "dramatic_fullbleed", "editorial_magazine"],
#     "tech":    ["minimalist_float", "geometric_grid", "asymmetric_left", "bold_typographic"],
#     "fashion": ["editorial_magazine", "diagonal_flow", "luxury_centered", "asymmetric_right"],
#     "beauty":  ["luxury_centered", "minimalist_float", "centered_hero", "vintage_stamp"],
#     "default": LAYOUT_ARCHETYPES,
# }

# COLOR_MOODS = {
#     "energetic": {"accent": "#FF4500", "highlight": "#FFD700"},
#     "luxury":    {"accent": "#C9A84C", "highlight": "#FFFFFF"},
#     "fresh":     {"accent": "#27AE60", "highlight": "#E8F5E9"},
#     "bold":      {"accent": "#E74C3C", "highlight": "#FFF176"},
#     "calm":      {"accent": "#2980B9", "highlight": "#EAF4FB"},
# }


# def get_design_tokens(content: dict, width: int, height: int) -> dict:
#     category = content.get("category", "default").lower()
#     pool = CATEGORY_ARCHETYPE_WEIGHTS.get(category, CATEGORY_ARCHETYPE_WEIGHTS["default"])
#     archetype = random.choice(pool)
#     mood_key = random.choice(list(COLOR_MOODS.keys()))
#     base_size = int(width / 14)
#     return {
#         "archetype": archetype,
#         "color_mood": COLOR_MOODS[mood_key],
#         "typography_scale": {
#             "title":    base_size,
#             "subtitle": int(base_size / GOLDEN_RATIO),
#             "tagline":  int(base_size / GOLDEN_RATIO ** 2),
#             "body":     int(base_size / GOLDEN_RATIO ** 3),
#         },
#         "safe_margin_x": int(width * 0.05),
#         "safe_margin_y": int(height * 0.05),
#         "thirds_x": [width // 3, (width * 2) // 3],
#         "thirds_y": [height // 3, (height * 2) // 3],
#     }


# def generate_poster(prompt: str, content: dict, output_format="1:1", image_path=None):
#     width, height = CANVAS_SIZES.get(output_format, (1024, 1024))

#     tokens = get_design_tokens(content, width, height)
#     print(f"[Design] Archetype: {tokens['archetype']} | Mood: {tokens['color_mood']}")

#     # Step 1 — Claude generates full HTML poster (CSS background only)
#     print("[Step 1] Claude generating HTML poster...")
#     html = generate_poster_html(
#         background_bytes=None,  # no image — Claude uses CSS
#         content=content,
#         output_format=output_format,
#         tokens=tokens,
#     )

#     # Step 2 — Playwright renders HTML to PNG
#     print("[Step 2] Playwright rendering HTML to PNG...")
#     final_png = render_html_to_png(html, width=width, height=height)

#     # Step 3 — Upload to Cloudinary
#     print("[Step 3] Uploading to Cloudinary...")
#     result = cloudinary.uploader.upload(final_png, folder="posters")
#     url = result.get("secure_url")
#     print(f"[Done] {url}")
#     return url



def regenerate_poster(prompt, output_format, image_url=None):
    img_size = get_image_size(output_format)

    try:
        final_prompt = prompt

        # STEP 1 — If original poster exists, describe it first
        if image_url:
            vision_response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            },
                            {
                                "type": "text",
                                "text": """Describe this marketing poster in detail:
- Layout and composition
- Background style and colors
- All text content, fonts, sizes, colors
- Position of every element
- CTA button style
- Overall visual mood"""
                            }
                        ]
                    }
                ],
                max_tokens=800
            )

            poster_description = vision_response.choices[0].message.content

            # STEP 2 — Inject description into prompt
            final_prompt = f"""
{prompt}

=====================
ORIGINAL POSTER VISUAL REFERENCE
=====================
{poster_description}

CRITICAL:
- Preserve everything above UNLESS explicitly overridden in USER REQUESTED CHANGES
- Only change what has a new value — keep everything else identical
"""

        # STEP 3 — Generate
        response = client.images.generate(
            model="gpt-image-1",
            prompt=final_prompt,
            size=img_size
        )

        image_bytes = base64.b64decode(response.data[0].b64_json)
        upload_result = cloudinary.uploader.upload(image_bytes, folder="re_generated_posters")
        return upload_result["secure_url"]

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

        response = client.chat.completions.create(
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