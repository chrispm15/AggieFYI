# frontend.py
import streamlit as st
import requests
from streamlit.components.v1 import html


# Set up page config
st.set_page_config(
    page_title="Aggie FYI",
    page_icon="👍",  # You can use an emoji or a URL to an image
)

html("""
    <head>
        <meta property="og:title" content="Aggie.FYI" />
        <meta property="og:description" content="Your Texas A&M AI Insider" />
        <meta property="og:image" content="https://raw.githubusercontent.com/chrispm15/AggieFYI/main/static/img.png" />
        <meta property="og:url" content="https://www.aggie.fyi" />
        <meta name="twitter:card" content="summary_large_image" />
    </head>
""", height=0)


hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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

        .stMarkdown ul,
        .stMarkdown ol,
        .stMarkdown li,
        .stMarkdown p,
        .stChatMessage,
        .stChatMessage p,
        .stChatMessage pre,
        .stChatMessage code {
        color: #2c2c2c !important;
        background-color: transparent !important;
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
st.markdown("<h1 style='color:#500000;'>Aggie.FYI</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#363636;'>Your Texas A&M AI Insider</p>", unsafe_allow_html=True)

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
    with st.spinner("Asking Miss Rev..."):
        try:
            res = requests.post("https://aggiefyi.onrender.com/chat", json={"message": user_input})
            res.raise_for_status()
            data = res.json()
            reply = data.get("response", "[No reply received]")
        except Exception as e:
            reply = f"[Backend error]: {e}"

    # Show assistant response
    st.chat_message("assistant", avatar="https://pbs.twimg.com/profile_images/1567934217719320576/Ni7dxbry_400x400.jpg").write(reply)

    # Add assistant reply to history
    st.session_state.history.append({"role": "assistant", "content": reply})


