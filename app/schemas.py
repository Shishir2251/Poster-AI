from pydantic import BaseModel
from typing import Optional

class PosterRequest(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    brand_name: Optional[str] = None
    cta_text: Optional[str] = None
    style: Optional[str] = None
    format: Optional[str] = None
    style_preset:Optional[str]= None

# TEXT_PLACEHOLDER_RULES = """
# =====================
# TEXT RENDERING (CRITICAL)
# =====================

# DO NOT render any real or readable text in the image.

# Instead, create clean visual placeholders for:
# - Title
# - Subtitle
# - CTA button
# - Brand name
# - Tagline
# - Contact info (phone, address, website)

# PLACEHOLDER RULES:
# - Use empty boxes, blurred lines, or abstract shapes to represent text areas
# - Maintain correct layout, spacing, and hierarchy
# - Ensure placeholders match expected text length visually
# - CTA must look like a button but contain NO text
# - Footer area must reserve space for contact details

# IMPORTANT:
# - Absolutely NO letters, NO numbers, NO readable characters
# - The image must look like a finished poster with missing text
# """

# HIERARCHY_RULES = """
# =====================
# VISUAL HIERARCHY (PLACEHOLDER-BASED)
# =====================

# The design must follow a clear visual hierarchy using placeholder elements:

# 1. Title Area (MOST dominant)
#    - Largest placeholder block
#    - Strong contrast
#    - Positioned at top

# 2. Subtitle Area
#    - Medium-sized placeholder
#    - Directly below title
#    - Lower visual weight than title

# 3. CTA Area (Button)
#    - Highly visible button shape
#    - Strong color contrast
#    - Clearly clickable appearance

# 4. Main Visual
#    - Central focal element (product/image)

# 5. Brand + Tagline Area
#    - Smaller placeholder blocks
#    - Near bottom of layout

# 6. Contact Info Area
#    - Smallest placeholder elements
#    - Positioned at very bottom

# IMPORTANT:
# - Use size, spacing, and contrast to express hierarchy
# - DO NOT use real text to indicate importance
# - All hierarchy must be conveyed visually through shapes and layout only
# """


TEXT_PLACEHOLDER_RULES = """
=====================
TEXT AREAS (CRITICAL)
=====================

Do NOT render any text, characters, letters, or numbers anywhere in the image.
Do NOT draw wireframe boxes, mockup bars, or UI placeholder shapes.

The image is a POSTER BACKGROUND — a designer will add all text afterward.

For areas where text will be placed:
- Keep the background CLEAN, FLAT, and HIGH CONTRAST
- No textures, no patterns, no decorative elements in text zones
- The background color alone should make text legible when added later
- Think: a billboard before the text is printed on it
"""

HIERARCHY_RULES = """
=====================
LAYOUT ZONES
=====================

Design the poster with these clear spatial zones:

TOP 30% OF CANVAS:
- Clean, uncluttered background
- Strong solid color or very subtle gradient
- Nothing here except background — this is where title/subtitle will be added

CENTER (30% to 72%):
- Main hero visual (product, subject, or key graphic)
- This is the only area with rich visual content

74% to 82% VERTICAL:
- A single solid-colored rounded button shape, centered
- Button must be EMPTY — no text, no icons inside it
- Use a contrasting accent color for the button

BOTTOM 15%:
- Clean solid color footer strip
- No elements, completely empty
- Must be high contrast for small text overlay later
"""

def get_language_rules(language: str):

    rtl_languages = ["hebrew"]

    rules = f"""
SCRIPT & LANGUAGE RULE (CRITICAL):
- All visible text MUST use the {language} script
- Do NOT mix scripts or languages unless the input itself mixes them
- The script/language of the INPUT is the law — match it exactly

VERBATIM CHARACTER RULE (ZERO TOLERANCE):
- Render every character EXACTLY as it appears in the input string
- Do NOT substitute visually similar characters
- Do NOT normalize, canonicalize, or recompose characters
- Do NOT correct spelling — if the input has a typo, render the typo
- Do NOT add, drop, reorder, or merge any character
- Do NOT insert characters not present in the input
- Character count in output MUST equal character count in input
- Word count in output MUST equal word count in input
- If unsure whether a character rendered correctly, err toward
  simpler, more standard glyph forms — never invent glyphs

WORD BOUNDARY RULE:
- Preserve exact spacing between words as in the input
- Do NOT merge separate words into one
- Do NOT split one word into multiple words
- Hyphenation is forbidden unless the input contains a hyphen

TEXT LAYOUT STABILITY:
- Prefer short text segments (1–3 words per line when possible)
- For longer text: split into semantically complete lines
- Avoid dense uninterrupted text blocks
- Avoid overlapping characters at any font size

TYPOGRAPHY SAFETY:
- Use only clean, standard letterforms
- Do NOT use decorative or stylized glyph variants
- Do NOT distort, stretch, skew, or warp any character
- Maintain consistent inter-character spacing throughout
"""

    if language.lower() in rtl_languages:
        rules += """
RTL LAYOUT RULE (HEBREW — CRITICAL):
- Text direction: right-to-left throughout
- Default text alignment: right
- Do NOT apply LTR alignment to any Hebrew text block
- Punctuation must follow Hebrew RTL conventions
- Numbers embedded in Hebrew text stay in their natural LTR
  reading order but do not break the RTL flow of surrounding text

HEBREW CHARACTER FIDELITY (ZERO TOLERANCE):
- Hebrew has 22 letters — each is distinct; do NOT substitute
  one for another (e.g. ב vs כ, ד vs ר, ה vs ח)
- Final-form letters (ך ם ן ף ץ) must be used ONLY at word-end;
  standard forms (כ מ נ פ צ) used mid-word — match input exactly
- Do NOT add or remove nikud (vowel marks) unless present in input
- Do NOT add or remove cantillation marks unless in input
- Shin dot and sin dot are distinct — match input exactly
- Every Hebrew letter in the input MUST appear in the output
- No Hebrew letter in the output may be absent from the input

HEBREW LAYOUT STABILITY:
- Break long Hebrew phrases into 2–4 word segments per line
- Never place more than 4–5 Hebrew words on a single line
- Each line must be semantically self-contained where possible
- Avoid right-edge clipping of the first letter of any RTL line
- Ensure the rightmost character of each line is fully visible
"""

    return rules