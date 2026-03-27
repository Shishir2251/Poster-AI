import uuid
from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


async def generate_poster(prompt):

    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024"
    )

    image_base64 = result.data[0].b64_json

    file_name = f"poster_{uuid.uuid4()}.png"
    file_path = f"generated/{file_name}"

    import base64

    with open(f"generated/{file_name}", "wb") as f:
        f.write(base64.b64decode(image_base64))

    return  f"generated/{file_name}"