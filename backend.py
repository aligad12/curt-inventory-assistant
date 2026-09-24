import os
from dotenv import load_dotenv
from google import genai
from fastapi import FastAPI
from pydantic import BaseModel
from google.genai import types
from google.genai.errors import APIError

from database import get_all_parts
from tools import check_stock, list_by_category, flag_shortage

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Describe the tools to Gemini ---
tools_list = [check_stock, list_by_category, flag_shortage]

config = types.GenerateContentConfig(
    system_instruction=(
        "You are CURT's inventory assistant for a Formula Student racing team. "
        "Answer questions about parts stock and location using tools provided. "
        "Always call a tool rather than guessing numbers or locations."
        "If the user's question is missing key details (like which item they mean), " # i added these here to count for the fallback like the one in phase1
        "ask a clarifying question instead of guessing or calling a tool with incomplete information."
    ), # so The LLM don't just make a guess and call a tool with incomplete information, it will ask for clarification instead.
    tools=tools_list,
)
sessions: dict[str,list] = {}

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    reply: str

@app.get("/inventory")
def inventory():
    """Return a list of all parts in the inventory."""
    return get_all_parts()

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if req.session_id not in sessions:
        sessions[req.session_id] = client.chats.create(
            model="gemini-3.6-flash",
            config=config
        )

    chat_session = sessions[req.session_id]
    try:
        response = chat_session.send_message(req.message)
        return ChatResponse(reply=response.text)
    except APIError as e:
        if getattr(e, "code", None) == 429:
            return ChatResponse(reply="I'm getting a lot of requests right now — please wait a few seconds and try again.")
        return ChatResponse(reply="The AI service is temporarily unavailable — please try again in a moment.")