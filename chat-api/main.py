from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Chatbot Bot API")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Prozatím jen zopakujeme zprávu
    # Zde se v budoucnu napojí AI a vektorová databáze
    reply = f"Bot říká: {request.message}"
    return ChatResponse(response=reply)

# Pro spuštění použijte:
# pip install fastapi uvicorn
# uvicorn main:app --reload
