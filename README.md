# AI Chatbot Projekt

Tento projekt je asynchronní klient-server aplikace poskytující moderní, vložitelný (embeddable) chatbot widget s backendem připraveným na napojení umělé inteligence a vektorové databáze.

Projekt je strukturován jako repozitář složený ze dvou samostatných, ale propojených mikroslužeb.

## Struktura repozitáře

- **[`/chat-widget`](./chat-widget/)**
  - Klientská část (JavaScript, CSS, HTML).
  - Proxy server v PHP (`api.php`), který ošetřuje CORS, Rate-Limiting a bezpečně přeposílá dotazy na Python API.
  - Více informací v [dokumentaci k widgetu](./chat-widget/README.md).

- **[`/chat-api`](./chat-api/)**
  - Backendová mikroslužba v Pythonu (FastAPI).
  - Slouží jako mozek chatu (zpracovává dotazy, připraveno pro LangChain/LLM modely).
  - Více informací v [dokumentaci k API](./chat-api/README.md).

- **[`/data-vectorizer`](./data-vectorizer/)**
  - Nezávislý ETL skript v Pythonu.
  - Vytěžuje obsah z MySQL databáze, segmentuje jej a pomocí lokálního AI modelu ukládá do vektorové databáze (ChromaDB) pro potřeby chatbota.
  - Více informací v [dokumentaci k vektorizátoru](./data-vectorizer/README.md).

## Jak spustit celý projekt pro vývoj

Pro lokální otestování celé aplikace potřebujete spustit obě části na různých portech.

1. **Spuštění Python API (mozek chatu)**
   Před spuštěním se ujistěte, že máte **aktivované virtuální prostředí**.
   ```bash
   cd chat-api
   # Windows: .\venv\Scripts\activate
   # Linux/macOS: source venv/bin/activate
   uvicorn main:app --reload
   ```
   *Poběží na `http://127.0.0.1:8000`*

2. **Spuštění PHP serveru (klientská část a proxy)**
   ```bash
   cd chat-widget
   php -S localhost:8080
   ```
   *Poběží na `http://localhost:8080`*

Následně otevřete v prohlížeči adresu `http://localhost:8080/client/index.html` a otestujte chatovací okno.
