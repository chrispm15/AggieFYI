# backend.py
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import openai
from chromadb import PersistentClient
from embedder import OpenAIEmbedder
from search_and_scrape import run_search_and_summarize
from datetime import datetime


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
today = datetime.now().strftime("%m/%d/%Y")
app = FastAPI()
gptModel = 'gpt-3.5-turbo-0125'


EVALUATION_PROMPT = """
You're an AI assistant. The user has sent a message, and you've been provided some internal context (such as documents, notes, or background info).
Your job is to determine:

- Is the user's message an actual information-seeking question?
- AND does the context contain enough relevant information to answer it?

If the message is small talk, a greeting, or doesn't require specific information, answer YES — context is sufficient.

Only respond with one word: YES or NO.

Context:
{context}

Message:
{question}

Answer:
"""

def gpt_should_fallback(question: str, context: str) -> bool:
    prompt = EVALUATION_PROMPT.format(context=context[:3000], question=question)
    try:
        response = openai.ChatCompletion.create(
            model=gptModel,
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["choices"][0]["message"]["content"].strip().lower()
        print(f"[GPT Fallback Decision] {answer}")
        return "no" in answer
    except Exception as e:
        print(f"[ERROR] GPT fallback check failed: {e}")
        return False  # Be safe — fallback only if GPT explicitly says no


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chroma = PersistentClient(path="chroma_db")
embedder = OpenAIEmbedder()
collection = chroma.get_or_create_collection(name="tamu_data", embedding_function=embedder)

SIMILARITY_THRESHOLD = .6

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_msg = body.get("message", "").strip()
    print(f"\n[USER] {user_msg} [TODAY'S DATE={today}]")

    # --- Chroma Phase ---
    chroma_results = collection.query(query_texts=[user_msg], n_results=10)
    docs = chroma_results["documents"][0]
    distances = chroma_results["distances"][0]
    SIMILARITY_THRESHOLD = 0.75  # You can tune this

    # Generate Chroma context
    chroma_context = ""
    for i, (doc, dist) in enumerate(zip(docs, distances)):
        print(f"  -> Doc {i + 1} | Distance: {dist:.4f}")
        chroma_context += f"\n[Chroma Doc {i + 1}] (Distance: {dist:.4f})\n{doc.strip()}\n"

    # Let GPT decide if fallback is needed
    should_fallback = gpt_should_fallback(user_msg, chroma_context)

    search_context = ""
    if should_fallback:
        print("[INFO] Chroma results were weak. Falling back to Brave.")
        summaries = run_search_and_summarize(user_msg)
        for i, s in enumerate(summaries):
            search_context += f"\n[Search Result {i + 1}]\n{s.strip()}\n"
    else:
        print("[INFO] Using Chroma only. No search needed.")

    # --- Compose Prompt ---
    full_context = f"\n{chroma_context.strip()}\n\n\n{search_context.strip()}"
    prompt = f"{full_context.strip()}\n\nUser: {user_msg}\nToday's Date: {today}\nAI:"

    try:
        response = openai.ChatCompletion.create(
            model=gptModel,
            messages=[
                {"role": "system", "content": "You are an AI insider for all things Texas A&M Athletics. You work with sources and monitor every corner of the community to deliver the most informed, latest intel on all things Texas A&M University and Aggie Athletics."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        reply = f"[Error]: {str(e)}"

    print(f"[RESPONSE] {reply[:250]}...\n")
    return {"response": reply}
