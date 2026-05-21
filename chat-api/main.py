import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

import llm as llm_module
import retriever

load_dotenv()

VERSION = "0.2.0"

# Nastavení logování pro přehledný výstup v terminálu
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan – inicializace při startu, úklid při vypnutí
# ---------------------------------------------------------------------------
# FastAPI lifespan je moderní náhrada za @app.on_event("startup").
# Kód před `yield` běží při startu serveru, kód za `yield` při vypnutí.
# Zde inicializujeme ChromaDB a embedding model JEDNOU – ne při každém požadavku,
# protože načítání modelu trvá ~10–30 sekund.

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 55)
    logger.info("Spouštím Chatbot API...")
    logger.info("=" * 55)

    # Inicializace ChromaDB a embedding modelu (pomalé – jen jednou)
    try:
        retriever.get_vector_store()
    except Exception as e:
        logger.error(f"VAROVÁNÍ: ChromaDB se nepodařilo inicializovat: {e}")
        logger.error("API poběží, ale vyhledávání v databázi bude nedostupné.")

    # Inicializace Ollama klienta (rychlé – jen vytvoří objekt, nepřipojuje se)
    try:
        llm_module.get_llm()
    except Exception as e:
        logger.error(f"VAROVÁNÍ: Ollama klient se nepodařilo inicializovat: {e}")

    logger.info("API připraveno na http://127.0.0.1:8000")
    logger.info("Dokumentace: http://127.0.0.1:8000/docs")
    logger.info("=" * 55)

    yield  # Server nyní zpracovává požadavky

    logger.info("Chatbot API se vypíná.")


# ---------------------------------------------------------------------------
# Aplikace
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Chatbot Bot API",
    description=(
        "RAG (Retrieval-Augmented Generation) backend pro AI Chatbot. "
        "Přijímá uživatelské dotazy, vyhledá relevantní obsah v ChromaDB "
        "a vygeneruje odpověď pomocí lokálního Ollama LLM modelu."
    ),
    version=VERSION,
    lifespan=lifespan,
)

# CORS – povolení komunikace z PHP proxy a vývojového prostředí.
# V produkci nahraďte "*" konkrétní doménou, např. ["https://vase-domena.cz"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# ---------------------------------------------------------------------------
# Pydantic modely (validace vstupů a výstupů)
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Zpráva nesmí být prázdná.")
        if len(v) > 500:
            raise ValueError("Zpráva nesmí být delší než 500 znaků.")
        return v


class ChatResponse(BaseModel):
    response: str


# ---------------------------------------------------------------------------
# Endpointy
# ---------------------------------------------------------------------------

@app.get("/", summary="Health check", tags=["Status"])
async def health_check():
    """
    Ověří, že API je dostupné a vrátí základní informace o konfiguraci.
    Vhodné pro monitoring, load-balancery a rychlé ověření stavu.
    """
    return {
        "status": "ok",
        "service": "chatbot-api",
        "version": VERSION,
        "llm_model": os.getenv("OLLAMA_MODEL", "llama3.2"),
        "retrieval_top_k": int(os.getenv("RETRIEVAL_TOP_K", 3)),
    }


@app.post("/chat", response_model=ChatResponse, summary="Odeslat zprávu", tags=["Chat"])
async def chat(request: ChatRequest):
    """
    Zpracuje uživatelský dotaz pomocí RAG pipeline:

    1. **Retrieve** – Vyhledá nejrelevantnější textové bloky v ChromaDB
       pomocí sémantického vyhledávání (embedding modelu).
    2. **Generate** – Předá nalezený kontext + dotaz lokálnímu Ollama LLM,
       který vygeneruje faktickou odpověď.

    Pokud ChromaDB nebo Ollama není dostupné, vrátí HTTP 503.
    """
    top_k = int(os.getenv("RETRIEVAL_TOP_K", 3))

    try:
        # Krok 1: Retrieve – sémantické vyhledávání v ChromaDB
        context = retriever.retrieve_context(request.message, top_k=top_k)

        # Krok 2: Generate – LLM sestaví odpověď z kontextu
        answer = await llm_module.generate_answer(context, request.message)

    except Exception as e:
        logger.error(f"Chyba při zpracování dotazu: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=(
                "Chatbot je momentálně nedostupný. "
                "Ujistěte se, že Ollama server běží (ollama serve)."
            ),
        )

    return ChatResponse(response=answer)


# ---------------------------------------------------------------------------
# Spuštění (pouze pro přímé volání: python main.py)
# ---------------------------------------------------------------------------
# Doporučený způsob spuštění je: uvicorn main:app --reload

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
