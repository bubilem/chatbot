# Chat Widget – Embeddable Chatbot UI + PHP Proxy

Tato složka obsahuje vizuální část chatbota (**JavaScript widget**) a **PHP server**, který zajišťuje bezpečnou komunikaci s Python API. Aplikace je navržena jako **embeddable widget** – lze ho vložit na jakýkoliv existující web přidáním jediného řádku HTML.

---

## Struktura složky

```
chat-widget/
├── client/
│   ├── index.html     ← Testovací stránka s widgetem (pro lokální vývoj)
│   ├── widget.js      ← Hlavní logika widgetu (IIFE, fetch, UI)
│   └── widget.css     ← Styly widgetu s CSS proměnnými pro snadnou customizaci
└── server/
    └── api.php        ← PHP proxy: CORS, rate limiting, cURL na Python API
```

---

## Principy a architektura

### Jak widget funguje

Widget je napsán jako **IIFE** (Immediately Invoked Function Expression):

```javascript
(function() {
    // Celý kód widgetu je uzavřen v anonymní funkci.
    // Žádná globální proměnná není vytvořena – žádný konflikt s hostitelskou stránkou.
})();
```

Při načtení skriptu widget automaticky:
1. Detekuje svoji vlastní cestu (z `<script src>` tagu)
2. Dynamicky vloží `widget.css` do `<head>` stránky
3. Vytvoří celou HTML strukturu chatovacího okna a tlačítka
4. Připojí vše na konec `<body>`

Tím je widget **zcela autonomní** – nevyžaduje žádné další HTML na hostitelské stránce.

### PHP Proxy Server (`server/api.php`)

Přímý přístup z prohlížeče na Python API (port 8000) by způsoboval CORS problémy a bezpečnostní rizika. PHP proxy server slouží jako **bezpečná brána**:

```
Prohlížeč (widget.js)
    │  POST /server/api.php
    ▼
api.php:
  1. Ověří HTTP metodu (musí být POST)
  2. Zkontroluje Rate Limiting (max 1 req/s na session)
  3. Validuje vstup (délka, prázdná zpráva)
  4. Přepošle dotaz na Python API přes cURL (timeout 5s)
  5. Vrátí JSON odpověď
    │
    ▼
Python FastAPI (chat-api, port 8000) – interní, nedostupný zvenčí
```

---

## Spuštění vývojového serveru

```powershell
cd chat-widget
php -S localhost:8080
```

Poté otevřete v prohlížeči: **`http://localhost:8080/client/index.html`**

> [!IMPORTANT]
> PHP server musí mít povolené `sessions` (standardně jsou povolené). Ujistěte se, že máte PHP 7.4+ nebo ideálně PHP 8.x.

---

## Vložení widgetu na cizí web (Embed)

Pro nasazení chatbota na jakýkoliv web stačí přidat **jeden řádek** před ukončovací tag `</body>`:

```html
<script src="https://vase-domena.cz/cesta/k/widget.js"></script>
```

> [!IMPORTANT]
> **Před nasazením** je nutné v souboru `client/widget.js` nastavit absolutní URL adresu PHP proxy:
>
> ```javascript
> // widget.js, řádek s API_URL
> const API_URL = 'https://vase-domena.cz/cesta/k/server/api.php';
> ```
>
> Relativní cesta `'../server/api.php'` funguje pouze pro lokální testování.

---

## Konfigurace vzhledu (Customizace)

Widget používá **CSS Custom Properties (proměnné)** definované v bloku `:root` na začátku souboru `widget.css`. Tím je úprava barev a rozměrů extrémně jednoduchá.

### Přehled konfigurovatelných proměnných

```css
:root {
    /* === Barvy === */
    --chatbot-primary: #667eea;           /* Hlavní barva (header, tlačítka) */
    --chatbot-primary-hover: #5a6fe0;     /* Hover stav tlačítek */
    --chatbot-gradient-end: #764ba2;      /* Konec gradientu v headeru */
    --chatbot-bg-window: #ffffff;         /* Pozadí okna */
    --chatbot-bg-messages: #f8f9fa;       /* Pozadí oblasti zpráv */
    --chatbot-text-dark: #333333;         /* Barva textu zpráv agenta */
    --chatbot-text-light: #ffffff;        /* Barva textu na barevném pozadí */
    --chatbot-border-color: #e9ecef;      /* Barva ohraničení */
    --chatbot-input-border: #ced4da;      /* Ohraničení vstupního pole */

    /* === Rozměry a pozice === */
    --chatbot-width: 350px;              /* Šířka chatovacího okna */
    --chatbot-height: 500px;             /* Výška chatovacího okna */
    --chatbot-spacing-bottom: 20px;      /* Vzdálenost od spodního okraje */
    --chatbot-spacing-right: 20px;       /* Vzdálenost od pravého okraje */
    --chatbot-z-index: 9999;             /* Vrstva nad ostatním obsahem */
}
```

### Příklad – Zelená varianta widgetu

Barvy lze přepsat přímo v HTML hostitelské stránky (bez nutnosti upravovat `widget.css`):

```html
<style>
  :root {
    --chatbot-primary: #10b981;
    --chatbot-primary-hover: #059669;
    --chatbot-gradient-end: #047857;
  }
</style>
<script src="https://vase-domena.cz/cesta/k/widget.js"></script>
```

---

## Bezpečnostní mechanismy

### Prevence XSS (Cross-Site Scripting)

Nejzávažnější hrozbou pro chatbot je **XSS útok**, kdy útočník pošle jako zprávu škodlivý HTML/JS kód.

**Ochrana ve `widget.js`:**
```javascript
// ✅ BEZPEČNÉ – text se zobrazí jako čistý text, nikdy se nespustí jako kód
msgDiv.textContent = text;

// ❌ NEBEZPEČNÉ – text by se interpretoval jako HTML
// msgDiv.innerHTML = text;
```

**Ochrana v `api.php`:**
- Odpověď je vždy odesílána s hlavičkou `Content-Type: application/json`
- Prohlížeč data interpretuje jako JSON, nikdy jako HTML k renderování

### Rate Limiting (ochrana proti spamu)

| Vrstva | Mechanismus | Limit |
|---|---|---|
| Frontend (`widget.js`) | `isSending` flag | Blokuje tlačítko do přijetí odpovědi |
| Frontend (`index.html`) | HTML `maxlength` | Max 500 znaků na vstup |
| Backend (`api.php`) | PHP session timestamp | Max 1 požadavek za sekundu |
| Backend (`api.php`) | Délka stringu | Max 500 znaků (server-side) |

### CORS (Cross-Origin Resource Sharing)

PHP proxy aktuálně odesílá hlavičku `Access-Control-Allow-Origin: *`, která povoluje přístup z libovolné domény. Toto je vhodné **pouze pro vývoj**.

> [!WARNING]
> **V produkci** změňte v `server/api.php` na konkrétní doménu vašeho webu:
> ```php
> // Místo:
> header("Access-Control-Allow-Origin: *");
>
> // Použijte:
> header("Access-Control-Allow-Origin: https://vase-domena.cz");
> ```
> Jinak může kdokoliv z internetu posílat požadavky na vaše API.

---

## Popis souborů

### `client/widget.js`

Celý widget v jednom souboru. Klíčové části:

| Část | Účel |
|---|---|
| CSS injection | Automaticky vloží `widget.css` do `<head>` |
| HTML creation | Dynamicky vytvoří HTML strukturu a připojí na `<body>` |
| Event listeners | Kliknutí, stisknutí Enter, zavření okna |
| `appendMessage()` | Přidá bublinu zprávy do okna (XSS-safe) |
| `sendMessage()` | Odešle zprávu přes `fetch()`, zobrazí loading, zpracuje odpověď |

### `client/widget.css`

CSS soubor s plně konfigurovatelným design systémem:
- **CSS Custom Properties** pro jednoduchou customizaci
- **Smooth animace** (`cubic-bezier`, `fadeIn keyframe`)
- **`pointer-events: none`** na `.hidden` třídě pro správné potlačení interakce

### `server/api.php`

PHP proxy s následujícími ochranami:
- `session_start()` pro rate limiting (1 req/s)
- Validace metody (pouze POST), délky a prázdné zprávy
- cURL volání na Python API s timeout 5 sekund
- Logging chyb přes `error_log()` (nezobrazí se uživateli)
