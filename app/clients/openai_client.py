import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_marketing_copy(prompt):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.9,
        messages=[
            {"role":"system","content":"You are a marketing poster copywriter."},
            {"role":"user","content":prompt}
        ]
    )

    return response.choices[0].message.content