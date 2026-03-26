from PIL import Image
from app.core.constants import POSTER_FORMATS, RTL_LANGUAGES, TEXT_SAFE_MARGIN
from typing import Dict


class LayoutEngine:

    def __init__(self):
        pass

    # ------------------------------------------------
    # Detect Image Orientation
    # ------------------------------------------------
    def detect_orientation(self, image: Image.Image):

        width, height = image.size

        if width > height:
            return "landscape"

        if height > width:
            return "portrait"

        return "square"

    # ------------------------------------------------
    # Resize Image To Poster Format
    # ------------------------------------------------
    def resize_canvas(self, image: Image.Image, format_type: str):

        width, height = POSTER_FORMATS.get(format_type, POSTER_FORMATS["square"])

        canvas = image.resize((width, height))

        return canvas

    # ------------------------------------------------
    # Determine Layout Type
    # ------------------------------------------------
    def select_layout(self, image: Image.Image):

        orientation = self.detect_orientation(image)

        if orientation == "portrait":
            return "top_text"

        if orientation == "landscape":
            return "left_text"

        return "center_text"

    # ------------------------------------------------
    # Check RTL
    # ------------------------------------------------
    def is_rtl(self, language: str):

        return language in RTL_LANGUAGES

    # ------------------------------------------------
    # Generate Layout Coordinates
    # ------------------------------------------------
    def generate_layout(
        self,
        image: Image.Image,
        format_type: str,
        language: str
    ) -> Dict:

        canvas = self.resize_canvas(image, format_type)

        width, height = canvas.size

        layout_type = self.select_layout(canvas)

        rtl = self.is_rtl(language)

        margin = TEXT_SAFE_MARGIN

        layout = {}

        if layout_type == "top_text":

            layout["headline"] = (
                margin,
                margin
            )

            layout["subheadline"] = (
                margin,
                margin + 120
            )

            layout["cta"] = (
                margin,
                height - 200
            )

        elif layout_type == "left_text":

            if rtl:

                layout["headline"] = (
                    width - 500,
                    margin
                )

                layout["subheadline"] = (
                    width - 500,
                    margin + 120
                )

            else:

                layout["headline"] = (
                    margin,
                    margin
                )

                layout["subheadline"] = (
                    margin,
                    margin + 120
                )

            layout["cta"] = (
                margin,
                height - 150
            )

        else:  # center layout

            layout["headline"] = (
                width // 2 - 250,
                height // 2 - 200
            )

            layout["subheadline"] = (
                width // 2 - 250,
                height // 2 - 100
            )

            layout["cta"] = (
                width // 2 - 200,
                height - 180
            )

        layout["canvas"] = canvas

        return layout

    # ------------------------------------------------
    # Apply Brand Kit Styling
    # ------------------------------------------------
    def apply_brandkit(
        self,
        layout: Dict,
        brandkit: Dict
    ):

        layout["brand"] = {}

        if not brandkit:
            return layout

        layout["brand"]["name"] = brandkit.get("brand_name")

        layout["brand"]["tagline"] = brandkit.get("tagline")

        layout["brand"]["logo"] = brandkit.get("logo")

        layout["brand"]["colors"] = brandkit.get("color_palette")

        layout["brand"]["headline_font"] = brandkit.get("headline_font")

        layout["brand"]["sub_font"] = brandkit.get("sub_font")

        return layout