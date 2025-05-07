import os
import json
from openai import OpenAI
import google.generativeai as genai

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)

# Select AI vendor
AI_VENDOR = os.getenv("AI_VENDOR", "openai").lower()

def send_prompt(messages):
    if AI_VENDOR == "openai":
        return _send_openai(messages)
    elif AI_VENDOR == "gemini":
        return _send_gemini(messages)
    else:
        raise ValueError(f"Unsupported AI_VENDOR: {AI_VENDOR}")

def _send_openai(messages):
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    return response.choices[0].message.content.strip()

def _send_gemini(messages):
    if isinstance(messages, list):
        prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])
    else:
        prompt = messages

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()
