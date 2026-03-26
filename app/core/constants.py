
# Poster Output Formats

POSTER_FORMATS = {
    "square": (1080, 1080),
    "story": (1080, 1920),
    "portrait": (1080, 1350),
    "landscape": (1920, 1080),
}

# Style Presets (from Figma UI)

STYLE_PRESETS = [
    "modern_minimal",
    "bold_vibrant",
    "dark_tech",
    "fun_playful",
    "corporate_blue",
    "luxury_premium"
]

# Regeneration Limits

MAX_REGENERATION_PER_PROMPT = 3

# Supported Languages

SUPPORTED_LANGUAGES = [
    "en",
    "he"
]

# RTL Languages

RTL_LANGUAGES = [
    "he",
    "ar",
    "fa",
    "ur"
]

# Default Colors

DEFAULT_COLOR_PALETTE = {
    "primary": "#2563EB",
    "secondary": "#9333EA",
    "accent": "#06B6D4",
    "text": "#FFFFFF"
}

# Safe Text Margins

TEXT_SAFE_MARGIN = 60

# Layout Zones

LAYOUT_ZONES = {
    "headline": (50, 80),
    "subheadline": (50, 200),
    "cta": (50, 900)
}

# BrandKit Limits

MAX_BRAND_COLORS = 5
MAX_LOGO_SIZE = 300