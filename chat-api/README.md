# Python Bot API

Tato složka obsahuje backendovou mikroslužbu naprogramovanou v Pythonu s využitím frameworku **FastAPI**. Slouží jako centrální mozek pro chatbota.

Aktuálně funguje jako "echo" server (vrací zprávy zpět s prefixem "Bot říká:"), ale je připravena na integraci s umělou inteligencí.

## Instalace a spuštění

Pro běh této mikroslužby potřebujete nainstalovaný Python a příslušné balíčky.

1. **Instalace závislostí:**
   Doporučujeme vytvořit si virtuální prostředí (např. pomocí `python -m venv venv`), a následně jej **aktivovat**:

   **Windows (PowerShell):**
   ```powershell
   .\venv\Scripts\activate
   ```

   **Linux/macOS:**
   ```bash
   source venv/bin/activate
   ```

   Poté v aktivovaném prostředí nainstalujte potřebné knihovny:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

2. **Spuštění vývojového serveru:**
   Z této složky (`chat-api`) s **aktivním virtuálním prostředím** spusťte Uvicorn server:
   ```bash
   uvicorn main:app --reload
   ```
   Aplikace poběží na adrese `http://127.0.0.1:8000`.

## API Endpoints

FastAPI automaticky generuje interaktivní dokumentaci. Během toho, co server běží, ji najdete na adrese:
`http://127.0.0.1:8000/docs`

### `POST /chat`
Zpracovává zprávy z chatu. Přijímá a vrací data ve formátu JSON.

**Požadavek (Request):**
```json
{
  "message": "Ahoj bote!"
}
```

**Odpověď (Response):**
```json
{
  "response": "Bot říká: Ahoj bote!"
}
```

## Budoucí rozvoj (AI)

Tento kód je přímo připravený na implementaci inteligentní logiky. Plánuje se:
- Zpracování dotazů přes knihovnu LangChain.
- Vektorizace dat z SQL databáze webu a jejich ukládání do vektorové databáze (ChromaDB, Pinecone atd.).
- Integrace s LLM modelem (např. OpenAI API, Llama, nebo Gemini) k poskytování smysluplných kontextových odpovědí.
