import random

design_elements = [
    "cinematic lighting",
    "soft gradient background",
    "3D product render",
    "studio lighting",
    "ultra realistic",
    "futuristic glow",
    "premium advertisement style"
]

def build_prompt(data):

    random_style = random.choice(design_elements)

    prompt = f"""
    Create a professional marketing poster.

    Title: {data.title}

    Subtitle: {data.subtitle}

    Description: {data.description}

    Brand: {data.brand_name}

    Call To Action: {data.cta_text}

    Style: {data.style}

    Poster style: {random_style}

    Design should look like a premium product advertisement poster.
    Clean typography, modern layout, visually appealing.
    """

    return prompt