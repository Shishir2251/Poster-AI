from PIL import Image, ImageDraw, ImageFont
import uuid

def render_poster(image_path, headline, content, font_path):

    base = Image.open(image_path).convert("RGB")

    draw = ImageDraw.Draw(base)

    headline_font = ImageFont.truetype(font_path, 60)
    content_font = ImageFont.truetype(font_path, 35)

    draw.text((50, 80), headline, fill="white", font=headline_font)

    draw.text((50, 200), content, fill="white", font=content_font)

    output_path = f"generated/{uuid.uuid4()}.png"

    base.save(output_path)

    return output_path