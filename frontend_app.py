# frontend_app.py
import streamlit as st
import requests
import uuid

from phase1_assistant import answer_question as phase1_answer
from database import get_all_parts

st.set_page_config(page_title="CURT Inventory Assistant", layout="wide")
st.image("assets/curt_logo_1.png", use_container_width=True)

BACKEND_URL = "http://127.0.0.1:8000"

# --- Session state setup ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": ..., "content": ...}
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # unique per browser session

# --- Sidebar: live inventory ---
with st.sidebar:
    st.header("📦 Current Inventory")
    try:
        parts = get_all_parts()
        st.dataframe(parts, use_container_width=True)
    except Exception as e:
        st.error(f"Couldn't load inventory: {e}")

    st.divider()
    phase = st.radio("Assistant Mode", ["Phase 1 (rule-based)", "Phase 2 (LLM)"])

# --- Main chat area ---
st.title("🏎️ CURT Inventory Assistant")

# Replay conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if question := st.chat_input("Ask about the inventory..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        if phase == "Phase 1 (rule-based)":
            answer = phase1_answer(question)
        else:
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"message": question, "session_id": st.session_state.session_id},
                    timeout=15,
                )
                resp.raise_for_status()
                answer = resp.json()["reply"]
            except requests.exceptions.ConnectionError:
                answer = "⚠️ Can't reach the backend. Is `uvicorn backend:app --reload` running?"
            except Exception as e:
                answer = f"⚠️ Error: {e}"

        st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})