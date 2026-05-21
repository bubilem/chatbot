import os
import logging

# Vypnutí ChromaDB telemetrie MUSÍ BÝT před importem ChromaDB
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Singleton instance – inicializuje se jednou při startu API a sdílí se napříč požadavky.
# Inicializace zahrnuje načtení embedding modelu (~500 MB), proto nesmí probíhat per-request.
_vector_store: Chroma | None = None


def get_vector_store() -> Chroma:
    """
    Vrátí singleton instanci ChromaDB s načteným embedding modelem.

    Při prvním volání inicializuje:
      - HuggingFace embedding model (intfloat/multilingual-e5-small)
      - Připojení k lokální ChromaDB v CHROMA_DB_DIR

    Embedding model MUSÍ být identický s modelem použitým v data-vectorizer/load.py,
    jinak vektory nejsou kompatibilní a vyhledávání vrací nesmyslné výsledky.
    """
    global _vector_store

    if _vector_store is not None:
        return _vector_store

    db_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    collection_name = os.getenv("CHROMA_COLLECTION", "chatbot_data")
    model_name = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-small")

    logger.info(f"Inicializuji embedding model: {model_name}")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    logger.info(f"Připojuji ChromaDB: {db_dir} (kolekce: {collection_name})")
    _vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=db_dir,
    )

    count = len(_vector_store.get(include=[])["ids"])
    logger.info(f"ChromaDB připravena. Počet záznamů v kolekci: {count}")

    return _vector_store


def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Provede sémantické vyhledávání v ChromaDB a vrátí naformátovaný kontext.

    Každý nalezený chunk je oddělen oddělovačem a doplněn zdrojovou URL,
    aby LLM mohl případně odkázat na zdroj informace.

    Args:
        query:  Uživatelský dotaz (bude vektorizován stejným embedding modelem)
        top_k:  Počet nejrelevantnějších chunků k vrácení (default: 3)

    Returns:
        Naformátovaný string s kontextem, nebo prázdný string pokud DB neobsahuje data.
    """
    vector_store = get_vector_store()

    try:
        results = vector_store.similarity_search_with_score(query, k=top_k)
    except Exception as e:
        logger.error(f"Chyba při vyhledávání v ChromaDB: {e}")
        return ""

    if not results:
        logger.info(f"Vyhledávání pro dotaz '{query}' nenalezlo žádné výsledky.")
        return ""

    context_parts = []
    for doc, score in results:
        url = doc.metadata.get("url", "")
        source_line = f"[Zdroj: {url}]" if url else ""
        # Nižší skóre = vyšší podobnost (L2 vzdálenost)
        logger.debug(f"Nalezen chunk score={score:.4f}, url={url}")
        context_parts.append(f"{doc.page_content}\n{source_line}".strip())

    return "\n\n---\n\n".join(context_parts)
