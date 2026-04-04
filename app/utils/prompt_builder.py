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

    prompt = f"""
    Create a premium marketing poster using the provided image as the main subject.
    Do not modify the product in the image.

    Add typography, layout, and branding elements only.

    Content:
    Title: {data.title}
    Subtitle: {data.subtitle}
    Description: {data.description}
    Brand: {data.brand_name}
    CTA: {data.cta}

    Style:
    {data.style}
    {data.poster_style}
    {data.design_style_prompt}

    Colors:
    Primary: {data.primary_color}
    Secondary: {data.secondary_color}

    Layout:
    Title at top, image center, CTA at bottom.

    Ensure clean composition, clear hierarchy, and proper margins.
    Output format: {data.output_format}
    """

    return prompt