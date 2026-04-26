# Python Bot API (`chat-api`)

Tato složka obsahuje backendovou mikroslužbu naprogramovanou v Pythonu s využitím frameworku **FastAPI**. Slouží jako centrální mozek chatbota – přijímá zprávy od PHP proxy, zpracuje je a vrátí odpověď.

**Aktuální stav:** Echo server (vrací zprávy zpět s prefixem `"Bot říká:"`). Kód je strukturálně připraven na integraci umělé inteligence.

---

## Struktura složky

```
chat-api/
├── main.py           ← Definice FastAPI aplikace, endpointy, CORS, validace
├── requirements.txt  ← Seznam Python závislostí s fixovanými verzemi
└── venv/             ← Virtuální prostředí (není v Gitu)
```

---

## Instalace a spuštění

### Předpoklady

- Python **3.11** nebo **3.12** (doporučeno)
- pip (součást Pythonu)

### Krok 1 – Vytvoření virtuálního prostředí

Virtuální prostředí izoluje závislosti tohoto projektu od ostatních Python projektů na vašem počítači. Je silně doporučeno.

```powershell
# Windows (PowerShell) – z kořene repozitáře
cd chat-api
python -m venv venv
```

```bash
# Linux / macOS
cd chat-api
python3 -m venv venv
```

### Krok 2 – Aktivace virtuálního prostředí

```powershell
# Windows (PowerShell)
.\venv\Scripts\activate
```

```bash
# Linux / macOS
source venv/bin/activate
```

> Po aktivaci se v terminálu vlevo zobrazí `(venv)`. Veškeré příkazy `pip` a `python` nyní pracují v izolovaném prostředí.

### Krok 3 – Instalace závislostí

```bash
pip install -r requirements.txt
```

**Závislosti projektu:**

| Balíček | Verze | Účel |
|---|---|---|
| `fastapi` | 0.115.5 | Web framework pro REST API |
| `uvicorn[standard]` | 0.32.1 | ASGI server pro spuštění FastAPI |
| `pydantic` | 2.10.3 | Validace dat vstupů/výstupů |

### Krok 4 – Spuštění vývojového serveru

```bash
uvicorn main:app --reload
```

> API poběží na **`http://127.0.0.1:8000`**
> Flag `--reload` způsobí automatický restart serveru po každé změně kódu (vhodné pro vývoj).

---

## API Dokumentace

FastAPI automaticky generuje interaktivní dokumentaci. Zatímco server běží, otevřete v prohlížeči:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

### Endpointy

#### `GET /` – Health Check

Ověří, že API je dostupné. Vhodné pro monitoring a load-balancery.

**Odpověď:**
```json
{
  "status": "ok",
  "service": "chatbot-api"
}
```

#### `POST /chat` – Zpracování zprávy

Zpracuje uživatelskou zprávu a vrátí odpověď chatbota.

**Požadavek (Request Body):**
```json
{
  "message": "Ahoj, jak funguje tento chatbot?"
}
```

**Odpověď (Response):**
```json
{
  "response": "Bot říká: Ahoj, jak funguje tento chatbot?"
}
```

**Chybové stavy:**

| HTTP kód | Situace |
|---|---|
| `422 Unprocessable Entity` | Chybí pole `message`, nebo je zpráva prázdná |
| `500 Internal Server Error` | Neočekávaná chyba na serveru |

---

## Architektura kódu (`main.py`)

```python
# CORS Middleware – povolí komunikaci z PHP proxy
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# Pydantic model – automaticky validuje vstup
class ChatRequest(BaseModel):
    message: str
    # @field_validator zajistí, že zpráva není prázdný string

# Endpoint – přijme validovaný request, vrátí response
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest): ...
```

Celý kód je **asynchronní** (`async def`), čímž umožňuje obsloužit více požadavků najednou bez blokování.

---

## CORS (Cross-Origin Resource Sharing)

API má nastavený CORS middleware, který umožňuje komunikaci z PHP proxy serveru. Aktuálně je povolený `*` (všechny domény) – vhodné pro vývoj.

> [!WARNING]
> **V produkci** nahraďte `allow_origins=["*"]` konkrétní doménou vašeho webu:
> ```python
> allow_origins=["https://vase-domena.cz"]
> ```

---

## Budoucí rozvoj – Integrace AI

Kód je strukturálně připraven pro rozšíření. Plánovaná integrace v `async def chat()`:

```python
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI  # nebo Ollama/Gemini

async def chat(request: ChatRequest):
    # 1. Najít relevantní dokumenty ve vektorové databázi
    docs = vector_store.similarity_search(request.message, k=3)
    context = "\n".join([d.page_content for d in docs])

    # 2. Sestavit prompt s kontextem a odeslat LLM
    llm = ChatOpenAI(model="gpt-4o-mini")
    answer = await llm.ainvoke(f"Kontext: {context}\nDotaz: {request.message}")

    return ChatResponse(response=answer.content)
```

**Plánované integrační kroky:**
- Napojení na ChromaDB z `data-vectorizer` pro sémantické vyhledávání
- Integrace LangChain pro orchestraci LLM volání
- Podpora LLM modelů: OpenAI GPT, Ollama (lokální), Google Gemini
