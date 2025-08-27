import os
import random
import requests
import streamlit as st
import functools
from models import QAItem

HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"

# Hugging Face token
HF_TOKEN = os.getenv("HF_TOKEN") or st.secrets.get("HUGGINGFACE_API_TOKEN", None)
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# ---- Fallback Questions ----
FALLBACK_QUESTIONS_EN = [
    QAItem(question="What is the difference between a list and a tuple in Python?", kind="Open"),
    QAItem(question="Explain how Docker helps in software deployment.", kind="Open"),
    QAItem(question="Which SQL command is used to remove duplicate rows?", kind="Open"),
    QAItem(question="You have experience with Pandas. How would you merge two DataFrames?", kind="Open"),
    QAItem(question="What are the benefits of using Git for version control?", kind="Open"),
]

FALLBACK_QUESTIONS_HI = [
    QAItem(question="Python में list और tuple में क्या अंतर है?", kind="Open"),
    QAItem(question="Docker सॉफ्टवेयर डिप्लॉयमेंट में कैसे मदद करता है, समझाइए।", kind="Open"),
    QAItem(question="SQL में duplicate rows को हटाने के लिए कौन सा command इस्तेमाल होता है?", kind="Open"),
    QAItem(question="Pandas का उपयोग करते हुए आप दो DataFrames को कैसे merge करेंगे?", kind="Open"),
    QAItem(question="Git का version control में उपयोग करने के क्या लाभ हैं?", kind="Open"),
]

EXIT_KEYWORDS = ["bye", "exit", "quit"]

# ---- HuggingFace Call with Caching ----
@functools.lru_cache(maxsize=128)
def call_hf(prompt: str):
    if not HF_TOKEN:
        print("⚠️ No Hugging Face token set, using fallback questions.")
        return None
    try:
        resp = requests.post(HF_API_URL, headers=HEADERS, json={"inputs": prompt}, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "").strip()
        else:
            print(f"HF API Error {resp.status_code}: {resp.text}")
            return None
    except Exception as e:
        print("HF Exception:", e)
        return None

# ---- Sentiment Analysis ----
def analyze_sentiment(text: str) -> str:
    if not text.strip():
        return "Neutral"
    try:
        url = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
        resp = requests.post(url, headers=HEADERS, json={"inputs": text}, timeout=20)
        if resp.status_code == 200:
            result = resp.json()[0]
            label = result[0]["label"]
            return label
    except Exception as e:
        print("Sentiment error:", e)
    return "Neutral"

# ---- Translation Support ----
def translate_text(text: str, target_lang: str) -> str:
    if target_lang.lower() == "english":
        return text
    models = {
        "hindi": "Helsinki-NLP/opus-mt-en-hi",
        "other": "Helsinki-NLP/opus-mt-en-fr"  # fallback demo
    }
    model = models.get(target_lang.lower())
    if not model:
        return text
    try:
        url = f"https://api-inference.huggingface.co/models/{model}"
        resp = requests.post(url, headers=HEADERS, json={"inputs": text}, timeout=20)
        if resp.status_code == 200:
            return resp.json()[0]['translation_text']
    except Exception as e:
        print("Translation error:", e)
    return text

# ---- Question Generation ----
def generate_questions(techs, language="English", n_min=3, n_max=5):
    """
    Generate technical interview questions based on tech stack and selected language.
    Falls back to predefined questions if LLM/translation fails.
    """
    n = min(len(techs), random.randint(n_min, n_max))
    questions = []

    # Try Hugging Face LLM if token is set
    prompt = f"Generate {n} technical interview questions about: {', '.join(techs)}."
    output = call_hf(prompt)

    if output:
        lines = [l.strip(" -1234567890.") for l in output.split("\n") if l.strip()]
        for l in lines[:n]:
            translated = translate_text(l, language)
            questions.append(QAItem(question=translated, kind="Open"))
    else:
        # Fallback questions
        fallback = FALLBACK_QUESTIONS_HI if language.lower() == "hindi" else FALLBACK_QUESTIONS_EN
        fallback_sample = random.sample(fallback, k=min(n, len(fallback)))
        for q in fallback_sample:
            questions.append(QAItem(question=q.question, kind=q.kind))

    return questions
