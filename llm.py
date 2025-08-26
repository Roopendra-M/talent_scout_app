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

FALLBACK_QUESTIONS = [
    QAItem(question="What is the difference between a list and a tuple in Python?", kind="Open"),
    QAItem(question="Explain how Docker helps in software deployment.", kind="Open"),
    QAItem(question="Which SQL command is used to remove duplicate rows?", kind="Open"),
    QAItem(question="You have experience with Pandas. How would you merge two DataFrames?", kind="Open"),
    QAItem(question="What are the benefits of using Git for version control?", kind="Open"),
]

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
    if target_lang == "English":
        return text
    models = {
        "Hindi": "Helsinki-NLP/opus-mt-en-hi",
        "Other": "Helsinki-NLP/opus-mt-en-fr"  # fallback demo
    }
    model = models.get(target_lang)
    if not model: return text
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
    n = random.randint(n_min, n_max)
    prompt = f"Generate {n} {language} technical interview questions about: {', '.join(techs)}."
    output = call_hf(prompt)
    questions = []

    if output:
        lines = [l.strip(" -1234567890.") for l in output.split("\n") if l.strip()]
        for l in lines:
            if len(questions) >= n:
                break
            translated = translate_text(l, language)
            questions.append(QAItem(question=translated, kind="Open"))
    else:
        fallback = random.sample(FALLBACK_QUESTIONS, k=min(n, len(FALLBACK_QUESTIONS)))
        questions = [QAItem(question=translate_text(q.question, language), kind=q.kind) for q in fallback]

    return questions
