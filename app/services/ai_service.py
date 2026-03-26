import random
from app.clients.openai_client import generate_text


STYLES = [
    "exciting marketing copy",
    "minimal modern advertising copy",
    "bold social media promotional text",
    "luxury brand marketing tone",
    "friendly engaging promotional text",
    "high-energy startup style marketing"
]


def generate_ai_content(headline, content, language):

    seed = random.randint(1000, 999999)

    style = random.choice(STYLES)

    prompt = f"""
Write a {style}.

Language must stay the same as the input.

Headline:
{headline}

Additional context:
{content}

Make the wording creative and different every time.

Random seed: {seed}
"""

    return generate_text(prompt)