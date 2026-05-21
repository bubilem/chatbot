import logging
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

load_dotenv()

logger = logging.getLogger(__name__)

# Singleton instance LLM klienta
_llm: ChatOllama | None = None

# Systémový prompt definuje chování a osobnost chatbota.
# Klíčová instrukce: odpovídat POUZE na základě kontextu – zabraňuje "halucinacím".
SYSTEM_PROMPT = """Jsi pomocný a přátelský asistent webu. Vždy odpovídáš v češtině.

Tvoje pravidla:
1. Odpovídej VÝHRADNĚ na základě informací z poskytnutého kontextu.
2. Pokud kontext odpověď neobsahuje, upřímně to řekni – například: „Tuto informaci bohužel nemám k dispozici. Pro více informací nás kontaktujte."
3. Nevymýšlej žádné informace, ceny, data ani fakta, která nejsou v kontextu.
4. Odpovídej stručně a věcně. Pokud je to vhodné, použij odrážky pro přehlednost.
5. Pokud kontext obsahuje zdrojovou URL ([Zdroj: ...]), můžeš ji zmínit jako odkaz pro více informací."""


def get_llm() -> ChatOllama:
    """
    Vrátí singleton instanci ChatOllama klienta nakonfigurovaného dle .env.

    Konfigurace (z .env):
      OLLAMA_BASE_URL  – URL běžícího Ollama serveru (default: http://localhost:11434)
      OLLAMA_MODEL     – název modelu (default: llama3.2)

    Poznámka: ChatOllama se při inicializaci nepřipojuje k serveru –
    připojení nastane až při prvním volání. Proto chyby spojení zachycujeme
    v generate_answer(), ne zde.
    """
    global _llm

    if _llm is not None:
        return _llm

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")

    logger.info(f"Inicializuji Ollama klienta: model={model}, url={base_url}")

    _llm = ChatOllama(
        base_url=base_url,
        model=model,
        temperature=0.3,   # Nižší = konzistentnější, méně kreativní odpovědi (vhodné pro faktické odpovědi)
        num_ctx=4096,       # Kontextové okno – dostatek prostoru pro kontext + odpověď
    )

    return _llm


async def generate_answer(context: str, question: str) -> str:
    """
    Sestaví prompt z kontextu a otázky a asynchronně zavolá Ollama LLM.

    Pokud kontext je prázdný (ChromaDB nenašla relevantní dokumenty),
    LLM je o tom informován a odpovídá dle svého systémového promptu.

    Args:
        context:   Naformátovaný kontext z retriever.retrieve_context()
        question:  Původní uživatelský dotaz

    Returns:
        Vygenerovaná odpověď jako string.

    Raises:
        Exception: Pokud Ollama server není dostupný nebo model není stažen.
    """
    llm = get_llm()

    if context:
        user_content = (
            f"Kontext z databáze webu:\n\n{context}\n\n"
            f"---\n\nOtázka: {question}"
        )
    else:
        # Bez kontextu – LLM bude informován, že v databázi nic nebylo nalezeno
        user_content = (
            f"Otázka: {question}\n\n"
            f"(Poznámka pro asistenta: V databázi webu nebyly nalezeny žádné relevantní informace k této otázce.)"
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    logger.info(f"Volám Ollama LLM pro dotaz: '{question[:80]}...' (kontext: {'ano' if context else 'ne'})")
    response = await llm.ainvoke(messages)
    logger.info("Odpověď od LLM přijata.")

    return response.content
