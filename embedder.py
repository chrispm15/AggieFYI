# embedder.py
import os
import openai
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]

class OpenAIEmbedder:
    def __init__(self, model="text-embedding-3-small"):
        self.model = model

    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        response = openai.Embedding.create(input=input, model=self.model)
        embeddings = [r["embedding"] for r in response["data"]]
        print(f"🔎 EMBEDDING DIM: {len(embeddings[0])}")
        return embeddings

    def name(self):
        return self.model
