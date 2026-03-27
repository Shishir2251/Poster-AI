import os
import uuid
import base64
import random
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)


# -----------------------------------------
# Get Image Size Based on Aspect Ratio
# -----------------------------------------
def get_image_size(output_format: str):

    if output_format == "1:1":
        return "1024x1024"

    if output_format == "9:16":
        return "1024x1792"

    if output_format == "16:9":
        return "1792x1024"

    # default fallback
    return "1024x1024"


# -----------------------------------------
# Poster Generator
# -----------------------------------------
async def generate_poster(prompt: str, output_format: str = "1:1"):

    # ensure variation randomness
    creative_seed = random.randint(1000, 999999)

    final_prompt = f"""
{prompt}

IMPORTANT DESIGN RULES:
- Keep all text inside safe margins
- Maintain 10% padding from edges
- Ensure title, subtitle and CTA are fully visible
- Do not cut text near borders

Creative seed: {creative_seed}
"""

    size = get_image_size(output_format)

    try:

        result = client.images.generate(
            model="gpt-image-1",
            prompt=final_prompt,
            size=size
        )

        image_base64 = result.data[0].b64_json

        image_bytes = base64.b64decode(image_base64)

        filename = f"poster_{uuid.uuid4()}.png"

        file_path = os.path.join(GENERATED_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        # return only filename (important)
        return filename

    except Exception as e:
        print("Image generation error:", e)
        raise