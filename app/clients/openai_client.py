import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_text(prompt):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=1.2,
        top_p=0.95,
        presence_penalty=0.6,
        frequency_penalty=0.5,
        messages=[
            {
                "role": "system",
                "content": "You generate unique creative poster marketing copy every time."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content