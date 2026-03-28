import os
import uuid
import base64
from openai import OpenAI

client = OpenAI()

GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)


async def generate_logo(data, image_path=None):

    brand_name = data.get("brand_name")
    tagline = data.get("tagline", "")
    vision = data.get("vision", "")
    industry = data.get("industry", "")
    logo_style = data.get("logo_style", "")
    color_palette = data.get("color_palette", "")

    prompt = f"""
Design a professional vector logo.

Brand Name: {brand_name}
Tagline: {tagline}

Brand Vision:
{vision}

Industry:
{industry}

Logo Style:
{logo_style}

Color Palette:
{color_palette}

Requirements:
- flat vector logo
- minimal shapes
- no photo style
- no complex gradients
- clean lines
- suitable for SVG conversion
- centered composition
"""

    try:

        # If reference image uploaded
        if image_path and os.path.exists(image_path):

            with open(image_path, "rb") as img:

                result = client.images.edit(
                    model="gpt-image-1",
                    prompt=prompt,
                    image=img,
                    size="1024x1024",
                    n=1
                )

        else:

            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024",
                n=1
            )

        logos = []

        for img in result.data:

            image_bytes = base64.b64decode(img.b64_json)

            filename = f"logo_{uuid.uuid4().hex}.png"

            path = os.path.join(GENERATED_DIR, filename)

            with open(path, "wb") as f:
                f.write(image_bytes)

            logos.append(f"/generated/{filename}")

        return logos

    except Exception as e:
        print("Logo generation error:", e)
        raise
