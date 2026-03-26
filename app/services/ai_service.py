import random
from app.clients.openai_client import generate_marketing_copy

def generate_ai_content(headline, content, language):

    seed = random.randint(1,999999)

    prompt = f"""
Generate marketing poster text.

Language must stay the SAME as input language.

Language: {language}

Headline:
{headline}

Content:
{content}

Variation seed:
{seed}

Return short poster copy.
"""

    return generate_marketing_copy(prompt)