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

    Call To Action: {data.cta}

    Style: {data.style}
    Poster Style: {data.poster_style}

    Design Style Prompt:
    {data.design_style_prompt}

    Brand Colors:
    Primary: {data.primary_color}
    Secondary: {data.secondary_color}

    Output Format:{data.output_format}

    Style Preset:{data.style_preset}

    The poster should look like a premium advertisement with modern layout,
    balanced typography, and strong visual hierarchy.
    """

    return prompt