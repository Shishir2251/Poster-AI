import os
import base64
import re
# import random
from openai import OpenAI
from dotenv import load_dotenv
# from rembg import remove
# from PIL import Image
import json
# from rembg import new_session, remove
from app.services.remove_bg import remove_bg_api
import cloudinary.uploader
import requests
import base64
from io import BytesIO
import cloudinary.uploader

load_dotenv()


client = OpenAI()

GENERATED_DIR = "generated"
os.makedirs(GENERATED_DIR, exist_ok=True)


def get_image_size(output_format: str):

    size_map = {
        "1:1": "1024x1024",
        "4:5": "1024x1536",
        "9:16": "1024x1536",
        "16:9": "1536x1024"
    }

    return size_map.get(output_format, "1024x1024")



def generate_poster(prompt, output_format="1:1", image_path=None):

    size = get_image_size(output_format)

    try:

        if image_path and os.path.exists(image_path):

            # image_path = remove_background(image_path)
            image_path = remove_bg_api(image_path) # using remove.bg API for for faster background removal

            with open(image_path, "rb") as img:

                result = client.images.edit(
                    model="gpt-image-1",
                    prompt=prompt,
                    size=size,
                    image=img
                )

      
        else:

            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=size
            )
            print("--Total tokens for poster generation--",result.usage.total_tokens)

        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        result = cloudinary.uploader.upload(
            image_bytes,
            folder = "posters"
        )
        image_url = result.get("secure_url")


        return image_url

    except Exception as e:
        print("Image generation error:", e)
        raise




def regenerate_poster(prompt, output_format, image_url=None):

    img_size = get_image_size(output_format)

    try:

        # STEP 1 — load image (from URL)
        image_file = None

        if image_url:

            try:
                response = requests.get(image_url, timeout=(3, 10))
                response.raise_for_status()

                image_file = BytesIO(response.content)
                image_file.name = "image.png"

            except Exception as e:
                print("Image download failed:", e)
                raise

        # STEP 2 — OpenAI generation
        if image_file:

            response = client.images.edit(
                model="gpt-image-1",
                prompt=prompt,
                size=img_size,
                image=image_file
            )

        else:

            response = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=img_size
            )

        # STEP 3 — decode result
        image_base64 = response.data[0].b64_json
        result_image_bytes = base64.b64decode(image_base64)

        # STEP 4 — upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            result_image_bytes,
            folder="re_generated_posters"
        )

        return upload_result["secure_url"]

    except Exception as e:
        print("Image regeneration failed:", e)
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