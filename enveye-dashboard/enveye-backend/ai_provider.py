import json
from openai import OpenAI
import google.generativeai as genai
from config_loader import CONFIG
import os

# Load from config
AI_VENDOR = CONFIG["ai"]["vendor"].lower()
MODEL_NAME = CONFIG["ai"]["model"]

# Configure clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
perplexity_client = OpenAI(api_key=os.getenv("PERPLEXITY_API_KEY"))


def send_prompt(messages):
    if AI_VENDOR == "openai":
        return _send_openai(messages)
    elif AI_VENDOR == "gemini":
        return _send_gemini(messages)
    elif AI_VENDOR == "perplexity":
        return _send_perplexity(messages)
    else:
        raise ValueError(f"Unsupported AI_VENDOR: {AI_VENDOR}")

def _send_openai(messages):
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    response = openai_client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages
    )
    return response.choices[0].message.content.strip()

def _send_gemini(messages):
    if isinstance(messages, list):
        prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])
    else:
        prompt = messages

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text.strip()
    
def _send_perplexity(messages):
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    response = perplexity_client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages
    )
    return response.choices[0].message.content.strip()
