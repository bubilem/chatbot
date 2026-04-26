from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

app = FastAPI(
    title="Chatbot Bot API",
    description="Backendová mikroslužba pro AI Chatbot. Přijímá zprávy a vrací odpovědi.",
    version="0.1.0",
)

# CORS – povolení komunikace z PHP proxy a vývojového prostředí.
# V produkci nahraďte "*" konkrétní doménou, např. ["https://vase-domena.cz"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def message_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Zpráva nesmí být prázdná.")
        return v


class ChatResponse(BaseModel):
    response: str


@app.get("/", summary="Health check", tags=["Status"])
async def health_check():
    """Ověří, že API běží. Vhodné pro monitoring a load-balancery."""
    return {"status": "ok", "service": "chatbot-api"}


@app.post("/chat", response_model=ChatResponse, summary="Odeslat zprávu", tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Zpracuje uživatelskou zprávu a vrátí odpověď.

    Prozatím vrací zprávu nazpět s prefixem (echo server).
    V budoucnu bude napojeno na LangChain + LLM model.
    """
    # Prozatím jen zopakujeme zprávu
    # Zde se v budoucnu napojí AI a vektorová databáze
    reply = f"Bot říká: {request.message}"
    return ChatResponse(response=reply)

# Pro spuštění použijte:
# pip install -r requirements.txt
# uvicorn main:app --reload

