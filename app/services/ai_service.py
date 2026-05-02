"""
ai_service.py  —  Full pipeline:
  1. Nano Banana  → background image (no text)
  2. Claude Vision → complete HTML poster
  3. Playwright   → PNG screenshot
  4. Cloudinary   → upload & return URL
"""

import os
import base64
import random
from dotenv import load_dotenv
from google import genai
from google.genai import types
import cloudinary.uploader

from app.services.remove_bg import remove_bg_api
from app.services.html_designer import generate_poster_html
from app.services.html_renderer import render_html_to_png

load_dotenv()

GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ── Canvas sizes ───────────────────────────────────────────────────────────────
CANVAS_SIZES = {
    "1:1":  (1024, 1024),
    "4:5":  (1024, 1280),
    "9:16": (1024, 1792),
    "16:9": (1792, 1024),
}

ASPECT_RATIOS = {
    "1:1": "1:1",
    "4:5": "4:5",
    "9:16": "9:16",
    "16:9": "16:9",
}

# ── Design system tokens ───────────────────────────────────────────────────────
GOLDEN_RATIO = 1.618

LAYOUT_ARCHETYPES = [
    "centered_hero", "top_heavy", "bottom_heavy", "asymmetric_left",
    "asymmetric_right", "split_panel", "diagonal_flow", "minimalist_float",
    "bold_typographic", "editorial_magazine", "dramatic_fullbleed",
    "geometric_grid", "luxury_centered", "street_poster", "vintage_stamp",
]

CATEGORY_ARCHETYPE_WEIGHTS = {
    "food":    ["centered_hero", "bottom_heavy", "dramatic_fullbleed", "editorial_magazine"],
    "tech":    ["minimalist_float", "geometric_grid", "asymmetric_left", "bold_typographic"],
    "fashion": ["editorial_magazine", "diagonal_flow", "luxury_centered", "asymmetric_right"],
    "beauty":  ["luxury_centered", "minimalist_float", "centered_hero", "vintage_stamp"],
    "default": LAYOUT_ARCHETYPES,
}

COLOR_MOODS = {
    "energetic": {"accent": "#FF4500", "highlight": "#FFD700"},
    "luxury":    {"accent": "#C9A84C", "highlight": "#FFFFFF"},
    "fresh":     {"accent": "#27AE60", "highlight": "#E8F5E9"},
    "bold":      {"accent": "#E74C3C", "highlight": "#FFF176"},
    "calm":      {"accent": "#2980B9", "highlight": "#EAF4FB"},
}


def get_design_tokens(content: dict, width: int, height: int) -> dict:
    category = content.get("category", "default").lower()
    pool = CATEGORY_ARCHETYPE_WEIGHTS.get(category, CATEGORY_ARCHETYPE_WEIGHTS["default"])
    archetype = random.choice(pool)
    mood_key = random.choice(list(COLOR_MOODS.keys()))

    base_size = int(width / 14)
    return {
        "archetype": archetype,
        "color_mood": COLOR_MOODS[mood_key],
        "typography_scale": {
            "title":    base_size,
            "subtitle": int(base_size / GOLDEN_RATIO),
            "tagline":  int(base_size / GOLDEN_RATIO ** 2),
            "body":     int(base_size / GOLDEN_RATIO ** 3),
        },
        "safe_margin_x": int(width * 0.05),
        "safe_margin_y": int(height * 0.05),
        "thirds_x": [width // 3, (width * 2) // 3],
        "thirds_y": [height // 3, (height * 2) // 3],
    }


# ── Step 1: Generate background with Nano Banana ───────────────────────────────
def generate_background(prompt: str, output_format: str, image_path=None) -> bytes:
    aspect_ratio = ASPECT_RATIOS.get(output_format, "1:1")

    if image_path and os.path.exists(image_path):
        image_path = remove_bg_api(image_path)
        with open(image_path, "rb") as f:
            img_bytes = f.read()

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                prompt,
            ],
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            ),
        )
    else:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=aspect_ratio),
            ),
        )

    for part in response.candidates[0].content.parts:
        if getattr(part, "thought", False):
            continue
        if getattr(part, "inline_data", None):
            return part.inline_data.data

    raise ValueError("Nano Banana returned no image")


# ── Main entry point called by Celery task ─────────────────────────────────────
def generate_poster(prompt: str, content: dict, output_format="1:1", image_path=None):
    width, height = CANVAS_SIZES.get(output_format, (1024, 1024))

    # Design tokens for uniqueness
    tokens = get_design_tokens(content, width, height)
    print(f"[Design] Archetype: {tokens['archetype']} | Mood: {tokens['color_mood']}")

    # Step 1 — background image from Nano Banana (NO text in prompt)
    print("[Step 1] Generating background with Nano Banana...")
    background_bytes = generate_background(prompt, output_format, image_path)

    # Step 2 — Claude Vision generates complete HTML poster
    print("[Step 2] Claude designing HTML poster...")
    html = generate_poster_html(
        background_bytes=background_bytes,
        content=content,
        output_format=output_format,
        tokens=tokens,
    )

    # Step 3 — Playwright renders HTML to PNG
    print("[Step 3] Playwright rendering HTML to PNG...")
    final_png = render_html_to_png(html, width=width, height=height)

    # Step 4 — Upload to Cloudinary
    print("[Step 4] Uploading to Cloudinary...")
    result = cloudinary.uploader.upload(final_png, folder="posters")
    url = result.get("secure_url")
    print(f"[Done] {url}")
    return url





#------------updated ai service with gemini, claude and playwright html renderer----------------
# import os
# import base64
# import re
# # from openai import OpenAI
# from dotenv import load_dotenv
# import json
# from app.services.remove_bg import remove_bg_api
# import cloudinary.uploader
# import base64
# from PIL import Image
# import io
# from io import BytesIO
# import cloudinary.uploader
# from .text_renderer import render_poster_text
# from google import genai
# from google.genai import types
# load_dotenv()
# # client = OpenAI()

# GENERATED_DIR = "generated"
# os.makedirs(GENERATED_DIR, exist_ok=True)


# def get_image_size(output_format: str):

#     size_map = {
#         "1:1": "1024x1024",
#         "4:5": "1024x1536",
#         "9:16": "1024x1536",
#         "16:9": "1536x1024"
#     }

#     return size_map.get(output_format, "1024x1024")

# # Configure Gemini
# # genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# def generate_poster_nano_banana(prompt, content, output_format="1:1", image_path=None):
#     try:
#         # 1. Build Dynamic Text Instructions
#         text_instructions = f"""- Main Title: "{content.get('title', '')}" (Bold, prominent artistic style)
# - Subtitle: "{content.get('subtitle', '')}" (Clearly below the title)
# - Brand: "{content.get('brand_name', '')}" (As a professional logo mark)"""

#         if content.get('cta'):
#             text_instructions += f'\n- Call to Action: "{content["cta"]}" (Inside a stylized button/badge)'
#         if content.get('website'):
#             text_instructions += f'\n- Website: "{content["website"]}" (Small, clean text at bottom)'
#         if content.get('phone'):
#             text_instructions += f'\n- Phone: "{content["phone"]}" (Discreetly at bottom)'

#         # 2. Enhanced Prompt
#         enhanced_prompt = f"""
# {prompt}

# TYPOGRAPHY & CONTENT INSTRUCTIONS (CRITICAL):
# Render the following Hebrew/English text blocks exactly as written.
# Maintain Right-to-Left (RTL) flow for all Hebrew script.

# {text_instructions}

# The text should not just sit on top; it should be part of the image,
# interacting with the shadows, lighting, and 3D depth of the scene.
# """

#         # 3. Generation Logic
#         if image_path and os.path.exists(image_path):
#             image_path = remove_bg_api(image_path)
#             with open(image_path, "rb") as f:
#                 img_bytes = f.read()

#             response = client.models.generate_content(
#                 model='gemini-3.1-flash-image-preview',
#                 contents=[
#                     types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
#                     enhanced_prompt
#                 ],
#                 config=types.GenerateContentConfig(
#                     response_modalities=["TEXT", "IMAGE"]
#                 )
#             )
#         else:
#             response = client.models.generate_content(
#                 model='gemini-2.5-flash-image',
#                 contents=enhanced_prompt,
#                 config=types.GenerateContentConfig(
#                     response_modalities=["TEXT", "IMAGE"]
#                 )
#             )

#         # 4. Extract image bytes from response
#         final_image_bytes = None
#         for part in response.candidates[0].content.parts:
#             if hasattr(part, 'thought') and part.thought:
#                 continue  # skip thinking images
#             if hasattr(part, 'inline_data') and part.inline_data:
#                 final_image_bytes = part.inline_data.data
#                 break

#         if not final_image_bytes:
#             raise ValueError("No image returned from Nano Banana")

#         # 5. Upload to Cloudinary
#         upload_result = cloudinary.uploader.upload(
#             final_image_bytes,
#             folder="posters"
#         )

#         return upload_result.get("secure_url")

#     except Exception as e:
#         print(f"Nano Banana Generation Error: {e}")
#         raise







#------------------------------------------
# def generate_poster_nano_banana(prompt, content, output_format="1:1", image_path=None):
#     # Nano Banana 2 (Gemini 3 Flash Image) model selection
#     model = client.models("gemini-3-flash-image")

#     try:
#         # 1. Prepare the Enhanced Prompt
#         # We merge your content (Hebrew text) directly into the visual prompt
#         enhanced_prompt = f"""
#         {prompt}
        
#         TYPOGRAPHY & CONTENT INSTRUCTIONS (CRITICAL):
#         Render the following Hebrew text blocks exactly as written. 
#         Maintain Right-to-Left (RTL) flow for all Hebrew script.
        
#         - Main Title: "{content['title']}" (Render in a bold, prominent artistic style)
#         - Subtitle: "{content['subtitle']}" (Render clearly below the title)
#         - Brand: "{content['brand_name']}" (Integrate as a professional logo mark)
#         - Call to Action: "{content['cta']}" (Render inside a stylized button or badge)
#         - Website: "{content['website']}" (Small, clean text at the bottom)
        
#         The text should not just sit on top; it should be part of the image, 
#         interacting with the shadows, lighting, and 3D depth of the scene.
#         """

#         # 2. Handle Image Input (Edit vs Generate)
#         if image_path and os.path.exists(image_path):
#             user_img = Image.open(image_path)
#             # Use 'image_edit' capability
#             result = model.edit_image(
#                 prompt=enhanced_prompt,
#                 base_image=user_img,
#                 number_of_images=1,
#                 aspect_ratio=output_format # Nano Banana supports ratios like "1:1", "16:9", "4:5"
#             )
#         else:
#             # Use 'generate_image' capability
#             result = model.generate_images(
#                 prompt=enhanced_prompt,
#                 number_of_images=1,
#                 aspect_ratio=output_format
#             )

#         # 3. Process Result
#         generated_image = result.images[0]
        
#         # Convert PIL to Bytes for Cloudinary
#         img_byte_arr = io.BytesIO()
#         generated_image.save(img_byte_arr, format='PNG')
#         img_byte_arr = img_byte_arr.getvalue()

#         # 4. Upload to Cloudinary
#         upload_result = cloudinary.uploader.upload(
#             img_byte_arr,
#             folder="posters"
#         )
        
#         return upload_result.get("secure_url")

#     except Exception as e:
#         print(f"Nano Banana Generation Error: {e}")
#         raise


# def generate_poster(prompt,content, output_format="1:1", image_path=None):

#     size = get_image_size(output_format)

#     try:

#         if image_path and os.path.exists(image_path):

#             # image_path = remove_background(image_path)
#             image_path = remove_bg_api(image_path) # using remove.bg API for for faster background removal

#             with open(image_path, "rb") as img:

#                 result = client.images.edit(
#                     model="gpt-image-1",
#                     prompt=prompt,
#                     size=size,
#                     image=img
#                 )

      
#         else:

#             result = client.images.generate(
#                 model="gpt-image-1",
#                 prompt=prompt,
#                 size=size
#             )
#             print("--Total tokens for poster generation--",result.usage.total_tokens)

#         image_base64 = result.data[0].b64_json
#         image_bytes = base64.b64decode(image_base64)

#         final_image_bytes = render_poster_text(
#             image_bytes=image_bytes,
#             content=content
#         )

#         result = cloudinary.uploader.upload(
#             final_image_bytes,
#             folder = "posters"
#         )
#         image_url = result.get("secure_url")

#         return image_url

#     except Exception as e:
#         print("Image generation error:", e)
#         raise



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



# def regenerate_poster(prompt, output_format, image_url=None):

#     img_size = get_image_size(output_format)

#     try:

#         # STEP 1 — load image (from URL)
#         image_file = None

#         if image_url:

#             try:
#                 response = requests.get(image_url, timeout=(3, 10))
#                 response.raise_for_status()

#                 image_file = BytesIO(response.content)
#                 image_file.name = "image.png"

#             except Exception as e:
#                 print("Image download failed:", e)
#                 raise

#         # STEP 2 — OpenAI generation
#         if image_file:

#             response = client.images.edit(
#                 model="gpt-image-1",
#                 prompt=prompt,
#                 size=img_size,
#                 image=image_file
#             )

#         else:

#             response = client.images.generate(
#                 model="gpt-image-1",
#                 prompt=prompt,
#                 size=img_size
#             )

#         # STEP 3 — decode result
#         image_base64 = response.data[0].b64_json
#         result_image_bytes = base64.b64decode(image_base64)

#         # STEP 4 — upload to Cloudinary
#         upload_result = cloudinary.uploader.upload(
#             result_image_bytes,
#             folder="re_generated_posters"
#         )

#         return upload_result["secure_url"]

#     except Exception as e:
#         print("Image regeneration failed:", e)
#         raise




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