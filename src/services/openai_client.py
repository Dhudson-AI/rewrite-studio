import os
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set. Create a .env file with your key.")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=api_key)


def chat_completion(
    messages: List[Dict[str, str]],
    model: str | None = None,
    temperature: float = 0.7,
) -> str:
    response = client.chat.completions.create(
        model=model or MODEL,
        messages=messages,
        temperature=temperature,
    )
    content = response.choices[0].message.content or ""
    return content.strip()
