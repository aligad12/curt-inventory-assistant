from fastapi import FastAPI
from pydantic import BaseModel
from database import get_all_parts

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

@app.post("/chat", response_model = ChatResponse)
def chat(req: ChatRequest):
    # stub for now - Step 4b replaces this with real Gemini tool-calling
    return ChatResponse(reply = f"(stub) You Said: {req.message}")
