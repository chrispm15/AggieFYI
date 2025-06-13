# frontend.py
import streamlit as st
import os
import openai
from dotenv import load_dotenv
from ingest import ingest_all
from embedder import OpenAIEmbedder
import chromadb

# Load env vars and OpenAI key
load_dotenv()
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Run ingestion
ingest_all()

# Set up page config
st.set_page_config(page_title="Texas A&M Chat", layout="centered")

# Custom styling
st.markdown("""
    <style>
        body, .stApp {
            background-color: #f8f6f0;
            color: #2c2c2c;
        }

        h1 {
            color: #500000;
        }

        .stChatMessage {
            color: #2c2c2c !important;
        }

        .stChatMessage pre,
        .stChatMessage code,
        .stChatMessage p {
            color: #2c2c2c !important;
            background-color: transparent !important;
            font-family: inherit !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='color:#500000;'>Texas A&M Athletics Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#363636;'>Ask anything about Texas A&M Football</p>", unsafe_allow_html=True)

# Chat session state
if "history" not in st.session_state:
    st.session_state.history = [{"role": "assistant", "content": "Howdy, what's on your mind?"}]

# Load ChromaDB and collection once
if "collection" not in st.session_state:
    chroma = chromadb.Client()
    embedder = OpenAIEmbedder()
    st.session_state.collection = chroma.get_or_create_collection(name="tamu_data", embedding_function=embedder)

# Render chat history
for chat in st.session_state.history:
    if chat["role"] == "user":
        st.chat_message("user", avatar="🧑").write(chat["content"])
    else:
        st.chat_message("assistant", avatar="🤠").write(chat["content"])

# Chat input
user_input = st.chat_input("Type your question here...")

if user_input:
    st.chat_message("user", avatar="🧑").write(user_input)
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.spinner("Thinking..."):
        # Query ChromaDB
        results = st.session_state.collection.query(query_texts=[user_input], n_results=5)
        context = "\n---\n".join(results["documents"][0])
        prompt = f"{context}\n\nUser: {user_input}\nAI:"

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
            reply = f"[OpenAI error]: {e}"

    st.chat_message("assistant", avatar="🤠").write(reply)
    st.session_state.history.append({"role": "assistant", "content": reply})
