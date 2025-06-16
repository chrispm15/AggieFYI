# frontend.py
import streamlit as st
import requests


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

# Render chat history
for chat in st.session_state.history:
    if chat["role"] == "user":
        st.chat_message("user", avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShhpeGUQdo2u3Gqihqdz97NkpwPdGeNZMuiA&s").write(chat["content"])
    else:
        st.chat_message("assistant", avatar='https://pbs.twimg.com/profile_images/1567934217719320576/Ni7dxbry_400x400.jpg').write(chat["content"])

# Chat input
user_input = st.chat_input("Type your question here...")

if user_input:
    # Show user's message immediately
    st.chat_message("user", avatar="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShhpeGUQdo2u3Gqihqdz97NkpwPdGeNZMuiA&s").write(user_input)

    # Add user message to history
    st.session_state.history.append({"role": "user", "content": user_input})

    # Show spinner and get assistant response
    with st.spinner("Thinking..."):
        try:
            res = requests.post("http://localhost:8000/chat", json={"message": user_input})
            res.raise_for_status()
            data = res.json()
            reply = data.get("response", "[No reply received]")
        except Exception as e:
            reply = f"[Backend error]: {e}"

    # Show assistant response
    st.chat_message("assistant", avatar="https://pbs.twimg.com/profile_images/1567934217719320576/Ni7dxbry_400x400.jpg").write(reply)

    # Add assistant reply to history
    st.session_state.history.append({"role": "assistant", "content": reply})


