# backend.py
import os
import streamlit as st
import openai
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from chromadb import PersistentClient
from embedder import OpenAIEmbedder

load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chroma setup
chroma = PersistentClient(path="chroma_db")
embedder = OpenAIEmbedder()
collection = chroma.get_or_create_collection(
    name="tamu_data",
    embedding_function=embedder
)

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_msg = body.get("message", "")

    results = collection.query(query_texts=[user_msg], n_results=5)
    context = "\n---\n".join(results["documents"][0])

    prompt = f"{context}\n\nUser: {user_msg}\nAI:"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a friendly Texas A&M football assistant. Keep it casual and helpful."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        reply = f"[Error]: {str(e)}"

    return {"response": reply}
