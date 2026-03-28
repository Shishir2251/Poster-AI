import os
import uuid
import base64
import random
from openai import OpenAI
from dotenv import load_dotenv
from rembg import remove
from PIL import Image
import json

load_dotenv()

# Initialize OpenAI client
client = OpenAI()

GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)


# -----------------------------------------
# Get Image Size Based on Aspect Ratio
# -----------------------------------------
def get_image_size(output_format: str):

    size_map = {
        "1:1": "1024x1024",
        "4:5": "1024x1536",
        "9:16": "1024x1536",
        "16:9": "1536x1024"
    }

    return size_map.get(output_format, "1024x1024")

def remove_background(input_path):

    output_path = input_path.replace(".", "_no_bg.")

    try:
        # verify image
        with Image.open(input_path) as img:
            img.verify()

        with open(input_path, "rb") as i:
            input_bytes = i.read()

        output_bytes = remove(input_bytes)

        with open(output_path, "wb") as o:
            o.write(output_bytes)

        return output_path

    except Exception as e:
        print("Background removal failed:", e)
        return input_path


# -----------------------------------------
# Poster Generator
# -----------------------------------------
async def generate_poster(prompt, output_format="1:1", image_path=None):

    # ensure variation randomness
    creative_seed = random.randint(1000, 999999)

    final_prompt = f"""
{prompt}

IMPORTANT DESIGN RULES:
- Use the uploaded image as the MAIN SUBJECT
- Do NOT modify the product or object in the image
- Only design poster layout around the image

TEXT RULES:
- Title must be clearly visible
- Subtitle must be readable
- CTA button must be visible

LAYOUT RULES:
- Keep all text inside safe margins
- Maintain 10% padding from edges
- Ensure title, subtitle and CTA are fully visible
- Do not cut text near borders

Creative seed: {creative_seed}
"""

    size = get_image_size(output_format)

    try:

        # -----------------------------
        # If user uploaded an image
        # -----------------------------
        if image_path and os.path.exists(image_path):

            image_path = remove_background(image_path)

            with open(image_path, "rb") as img:

                result = client.images.edit(
                    model="gpt-image-1",
                    prompt=final_prompt,
                    size=size,
                    image=img
                )

        # -----------------------------
        # No image provided
        # -----------------------------
        else:

            result = client.images.generate(
                model="gpt-image-1",
                prompt=final_prompt,
                size=size
            )

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        filename = f"poster_{uuid.uuid4().hex}.png"
        file_path = os.path.join(GENERATED_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        return filename

    except Exception as e:
        print("Image generation error:", e)
        raise
# AI Poster Idea → Structured Fields
async def generate_poster_fields(user_idea: str):

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

        try:
            return json.loads(content)

        except json.JSONDecodeError:
            return {
                "error": "AI returned non JSON output",
                "raw_output": content
            }

    except Exception as e:
        print("AI field generation error:", e)
        raise