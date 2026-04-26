# AI Chatbot – Modulární chatbot s vektorovým vyhledáváním

Tento projekt je plně modulární, asynchronní klient-server aplikace poskytující moderní, vložitelný (**embeddable**) chatbot widget s backendem připraveným pro napojení umělé inteligence (LLM) a vektorové databáze (ChromaDB).

## Architektura systému

Projekt je strukturován jako **monorepo** složené ze tří samostatných, ale vzájemně propojených komponent. Každá komponenta má svůj vlastní životní cyklus a může být nasazena nezávisle.

```
chatbot/
├── chat-widget/          ← Frontend widget (JS/CSS) + PHP proxy server
│   ├── client/           ← Embeddable JavaScript widget
│   └── server/           ← PHP proxy (CORS, rate limiting, cURL na Python API)
│
├── chat-api/             ← Python backend (FastAPI) – RAG pipeline
│   ├── main.py           ← REST API: GET / a POST /chat
│   ├── retriever.py      ← Singleton ChromaDB + sémantické vyhledávání
│   ├── llm.py            ← Singleton Ollama klient + sestavení promptu
│   └── chroma_db/        ← Vektorová databáze (plní data-vectorizer)
│
└── data-vectorizer/      ← ETL pipeline pro plnění vektorové databáze
    ├── extract.py        ← Extrakce dat z MySQL
    ├── transform.py      ← Čištění HTML + chunking textu
    ├── load.py           ← Vektorizace + uložení do chat-api/chroma_db
    └── main.py           ← Spouštěč celého ETL procesu
```

### Tok dat (jak systém funguje)

```
Uživatel → widget.js → api.php → chat-api (FastAPI)
                                       │
                              1. Vektorizace dotazu
                              (multilingual-e5-small)
                                       │
                              2. Similarity search v ChromaDB
                              (top-3 nejrelevantnější chunky)
                                       │
                              3. Sestavení promptu:
                              "Kontext: {chunky}\nOtázka: {zpráva}"
                                       │
                              4. Ollama LLM vygeneruje odpověď
                              (llama3.2 nebo jiný lokální model)
                                       │
                                   Odpověď ← ← ← ← ← ←
                                       │
     ◄──────────────────────  widget.js zobrazí zprávu
```

### Jak se data dostávají do vektorové databáze

```
MySQL databáze (CMS)
     │
     ▼
extract.py  ──►  transform.py  ──►  load.py  ──►  ChromaDB (chroma_db/)
 (SQL SELECT)   (HTML→text,       (HuggingFace       (lokální
                 chunking)         embeddings)         soubory)
```

---

## Komponenty

### [`/chat-widget`](./chat-widget/)
Klientská část (JavaScript, CSS) a PHP proxy server.
- Widget se vkládá jedním `<script>` tagem na jakýkoliv web
- PHP proxy ošetřuje CORS, Rate-Limiting a bezpečně přeposílá dotazy na Python API
- **→ [Dokumentace widgetu](./chat-widget/README.md)**

### [`/chat-api`](./chat-api/)
Backendová mikroslužba v Pythonu (FastAPI).
- Slouží jako mozek chatu – zpracovává dotazy
- Aktuálně echo server, připraveno pro integraci LangChain + LLM
- **→ [Dokumentace API](./chat-api/README.md)**

### [`/data-vectorizer`](./data-vectorizer/)
Nezávislý ETL skript v Pythonu.
- Vytěžuje textový obsah z MySQL databáze
- Segmentuje texty na logické bloky (chunky)
- Vektorizuje pomocí lokálního AI modelu a ukládá do ChromaDB
- **→ [Dokumentace vektorizátoru](./data-vectorizer/README.md)**

---

## Spuštění celého projektu (vývojové prostředí)

Pro lokální testování potřebujete spustit **dvě** komponenty zároveň v oddělených terminálech.

### 1. Spuštění Python API

```powershell
cd chat-api
# Aktivace virtuálního prostředí (Windows)
.\venv\Scripts\activate

# Instalace závislostí (pouze poprvé)
pip install -r requirements.txt

# Spuštění vývojového serveru
uvicorn main:app --reload
```

> API poběží na **`http://127.0.0.1:8000`**
> Interaktivní dokumentace: **`http://127.0.0.1:8000/docs`**

### 2. Spuštění PHP serveru (frontend + proxy)

```powershell
cd chat-widget
php -S localhost:8080
```

> Frontend poběží na **`http://localhost:8080`**

### 3. Otevření testovací stránky

Otevřete v prohlížeči: **`http://localhost:8080/client/index.html`**

---

## Technologický stack

| Vrstva | Technologie | Účel |
|---|---|---|
| Frontend widget | Vanilla JS + CSS | Embeddable chat UI |
| PHP proxy | PHP 8+ | CORS, Rate Limiting, bezpečná proxy |
| Python API | FastAPI + uvicorn | REST backend, RAG pipeline |
| RAG Retrieve | ChromaDB + sentence-transformers | Sémantické vyhledávání v obsahu |
| RAG Generate | Ollama + Llama 3.2 | Lokální LLM generování odpovědí |
| ETL pipeline | Python + LangChain | Příprava dat pro AI |
| Vektorová DB | ChromaDB | Ukládání a vyhledávání vektorů |
| Embedding model | BAAI/bge-m3 | Tvorba vektorů (vícejazyčné) |
| Zdrojová DB | MySQL | Obsah CMS webu |

---

## Bezpečnost (přehled)

| Hrozba | Ochrana |
|---|---|
| XSS | `textContent` místo `innerHTML` v JS |
| Spam / DDoS | Rate limiting (PHP session, 1 req/s) |
| Přímý přístup k Python API | PHP proxy jako jediný vstupní bod |
| Cross-origin zneužití | CORS (pro produkci nastavit konkrétní doménu) |
| Timeout & chyby sítě | cURL timeout 5s, error handling v JS |

---

## Vývojový stav a plánované funkce

- [x] Embeddable widget (JS + CSS)
- [x] PHP proxy s rate limitingem a validací
- [x] FastAPI skeleton s CORS a health-check endpointem
- [x] ETL pipeline (MySQL → ChromaDB)
- [x] Vektorové vyhledávání (test_query.py)
- [x] Integrace ChromaDB s chat-api (RAG retriever)
- [x] Integrace Ollama LLM s chat-api (generování odpovědí)
- [ ] Autentizace API klíčem
- [ ] Docker Compose pro jednoduchý deploy
- [ ] Ladění kvality odpovědí (prompt engineering, top-K, chunk size)
