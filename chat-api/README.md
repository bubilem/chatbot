# Python Bot API (`chat-api`)

Tato složka obsahuje backendovou mikroslužbu naprogramovanou v Pythonu s využitím frameworku **FastAPI**. Implementuje architekturu **RAG (Retrieval-Augmented Generation)** – na každý uživatelský dotaz nejprve vyhledá relevantní obsah v ChromaDB a poté předá kontext lokálnímu LLM modelu (Ollama), který vygeneruje smysluplnou odpověď.

---

## Architektura RAG pipeline

```
POST /chat  {"message": "Jaká je otevírací doba?"}
     │
     ▼
retriever.py → similarity_search v ChromaDB
     │          (embedding model: multilingual-e5-small)
     │          Vrátí top-3 nejrelevantnější textové bloky
     │
     ▼
llm.py → ChatOllama (llama3.2 nebo jiný model)
     │   Prompt: SystemPrompt + Kontext z DB + Otázka uživatele
     │
     ▼
{"response": "Škola je otevřena pondělí–pátek 7–17 hod..."}
```

> [!IMPORTANT]
> Embedding model v `chat-api` musí být **identický** s modelem použitým při vektorizaci v `data-vectorizer`. Záměna způsobí nekompatibilní vektory a nesmyslné výsledky vyhledávání.
> Správný model: `intfloat/multilingual-e5-small` (nastaven jako výchozí v `.env.example`).

---

## Struktura složky

```
chat-api/
├── main.py           ← FastAPI aplikace, lifespan, endpointy /  a /chat
├── retriever.py      ← Singleton ChromaDB, sémantické vyhledávání
├── llm.py            ← Singleton Ollama klient, sestavení promptu, generování odpovědi
├── requirements.txt  ← Python závislosti s fixovanými verzemi
├── .env.example      ← Šablona konfigurace (zkopírujte na .env a vyplňte)
├── .env              ← Vaše konfigurace (NENÍ v Gitu!)
└── chroma_db/        ← Vektorová databáze (plní data-vectorizer, NENÍ v Gitu)
```

---

## Předpoklady – Ollama

Ollama je lokální LLM runtime, který umožňuje spouštět jazykové modely na vašem počítači bez cloudu.

### 1. Instalace Ollama

Stáhněte a nainstalujte z: **[ollama.com](https://ollama.com)**

### 2. Stažení modelu

```bash
# Doporučeno: llama3.2 (~2 GB)
ollama pull llama3.2

# Alternativy pro lepší češtinu:
ollama pull mistral      # ~4 GB
ollama pull gemma2:9b    # ~5.5 GB
```

### 3. Spuštění Ollama serveru

```bash
ollama serve
```

> Ollama poběží na `http://localhost:11434`. Musí běžet souběžně s `chat-api`.

---

## Instalace a spuštění

### Krok 1 – Virtuální prostředí

```powershell
# Windows (PowerShell) – z kořene repozitáře
cd chat-api
python -m venv venv
.\venv\Scripts\activate
```

```bash
# Linux / macOS
cd chat-api
python3 -m venv venv
source venv/bin/activate
```

### Krok 2 – Instalace závislostí

```bash
pip install -r requirements.txt
```

> [!NOTE]
> Instalace `sentence-transformers` a `chromadb` může trvat několik minut a vyžaduje ~1 GB místa na disku. Při prvním spuštění API se navíc stáhne embedding model (~100–300 MB).

**Přehled závislostí:**

| Balíček | Verze | Účel |
|---|---|---|
| `fastapi` | 0.115.5 | Web framework |
| `uvicorn[standard]` | 0.32.1 | ASGI server |
| `pydantic` | 2.10.3 | Validace dat |
| `langchain` | 0.3.7 | Orchestrace AI |
| `langchain-chroma` | 0.1.4 | LangChain → ChromaDB wrapper |
| `langchain-huggingface` | 0.1.2 | LangChain → HuggingFace embeddings |
| `langchain-ollama` | 0.2.3 | LangChain → Ollama LLM |
| `chromadb` | 0.5.15 | Vektorová databáze |
| `sentence-transformers` | 3.3.1 | Inference embedding modelu |
| `python-dotenv` | 1.0.1 | Načítání `.env` |

### Krok 3 – Konfigurace

```bash
cp .env.example .env
```

Výchozí hodnoty jsou funkční pro lokální vývoj. Upravte dle potřeby:

```ini
CHROMA_DB_DIR=./chroma_db        # Kde jsou uložena vektorizovaná data
OLLAMA_MODEL=llama3.2            # Název staženého Ollama modelu
RETRIEVAL_TOP_K=3                # Počet chunků předaných LLM jako kontext
```

### Krok 4 – Naplnění ChromaDB

Před spuštěním chat-api musíte mít naplněnou vektorovou databázi. Spusťte ETL pipeline z `data-vectorizer/`:

```bash
cd ../data-vectorizer
# Ujistěte se, že .env má CHROMA_DB_DIR=../chat-api/chroma_db
.\venv\Scripts\activate
python main.py
```

### Krok 5 – Spuštění API

```bash
cd ../chat-api
.\venv\Scripts\activate
uvicorn main:app --reload
```

Výstup při úspěšném startu:
```
10:00:00 [INFO] __main__: ═══════════════════════════════════
10:00:00 [INFO] __main__: Spouštím Chatbot API...
10:00:00 [INFO] retriever: Inicializuji embedding model: intfloat/multilingual-e5-small
10:00:18 [INFO] retriever: ChromaDB připravena. Počet záznamů v kolekci: 214
10:00:18 [INFO] __main__: API připraveno na http://127.0.0.1:8000
```

---

## API Dokumentace

| URL | Popis |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger UI – interaktivní testování |
| `http://127.0.0.1:8000/redoc` | ReDoc – přehledná dokumentace |

### `GET /` – Health Check

```json
{
  "status": "ok",
  "service": "chatbot-api",
  "version": "0.2.0",
  "llm_model": "llama3.2",
  "retrieval_top_k": 3
}
```

### `POST /chat` – Zpracování dotazu

**Požadavek:**
```json
{ "message": "Jaká je otevírací doba?" }
```

**Odpověď:**
```json
{ "response": "Muzeum je otevřeno od pondělí do pátku 9:00–17:00, o víkendech 10:00–16:00. [Zdroj: /o-nas/otviraci-doba]" }
```

**Chybové stavy:**

| HTTP kód | Situace |
|---|---|
| `422 Unprocessable Entity` | Chybí `message` nebo je prázdná |
| `503 Service Unavailable` | Ollama neběží nebo model není stažen |

---

## Popis souborů

### `retriever.py`

- **Singleton** `_vector_store` – ChromaDB + embedding model se inicializují jednou při startu
- `get_vector_store()` – připojí se k `CHROMA_DB_DIR`, načte embedding model
- `retrieve_context(query, top_k)` – vektorizuje dotaz, hledá top-K nejpodobnějších chunků, vrátí je jako formátovaný string s URL zdroji

### `llm.py`

- **Singleton** `_llm` – ChatOllama klient
- `SYSTEM_PROMPT` – instrukce pro LLM: odpovídat v češtině, pouze z kontextu, bez halucinací
- `generate_answer(context, question)` – sestaví zprávy `[SystemMessage, HumanMessage]` a asynchronně zavolá `llm.ainvoke()`

### `main.py`

- **Lifespan** – inicializuje ChromaDB a Ollama při startu (ne per-request)
- `GET /` – health check s informacemi o konfiguraci
- `POST /chat` – RAG pipeline: retrieve → generate → response

---

## Řešení problémů

| Problém | Příčina | Řešení |
|---|---|---|
| `503 Service Unavailable` | Ollama neběží | Spusťte `ollama serve` |
| `model "llama3.2" not found` | Model není stažen | Spusťte `ollama pull llama3.2` |
| Pomalý start API (~30s) | Načítání embedding modelu | Normální chování při prvním startu |
| Prázdné/irelevantní odpovědi | Prázdná nebo neaktuální ChromaDB | Spusťte `python main.py` v `data-vectorizer/` |
| `SyntaxError` při startu | Python verze < 3.10 | Použijte Python 3.11 nebo 3.12 |
