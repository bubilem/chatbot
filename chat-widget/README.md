# Chat Widget (Klient & PHP Proxy)

Tato složka obsahuje vizuální část chatbota a PHP server, který zajišťuje bezpečnou komunikaci. Aplikace je navržena tak, aby bylo možné chatovací okno snadno vložit na jakýkoliv web.

## Principy a architektura

Aplikace je navržena jako asynchronní klient-server architektura:

### Klientská část (Frontend)
- **Umístění:** `/client`
- Klientskou část tvoří JavaScriptový widget, který je navržen jako embeddable skript.
- **Izolace:** Skript si sám dynamicky vytvoří HTML strukturu a automaticky připojí CSS (`widget.css`).
- **Konfigurace:** Barvy, stíny a rozměry lze snadno upravovat pomocí CSS proměnných v bloku `:root` na začátku souboru `widget.css`.

### PHP Proxy Server (Backend pro klienta)
- **Umístění:** `/server/api.php`
- Ošetřuje HTTP hlavičky, CORS a provádí Rate Limiting (max 1 požadavek za sekundu).
- Zabraňuje přímému přístupu zvenčí do Python API a na pozadí volá pomocí cURL interní `chat-api`.
- Obsahuje ochranu proti XSS (prohlížeč data z API interpretuje jako čistý text/JSON) a `TIMEOUT` pro případ nedostupnosti Python API.

## Nasazení (Embed) na cizí web

Pro nasazení widgetu na jakýkoliv jiný web stačí přidat tento jeden řádek před ukončovací tag `</body>` do dané webové stránky:

```html
<script src="http://vase-domena.cz/cesta/k/widget.js"></script>
```

> **Poznámka:** V souboru `client/widget.js` (u definice `API_URL`) musíte nastavit absolutní cestu k vašemu souboru `server/api.php`, aby skript dokázal komunikovat se serverem, ať je spuštěn odkudkoliv.

## Konfigurace vzhledu (Customizace)

Díky použití CSS proměnných je změna vzhledu (např. barev, aby ladily s hostitelským webem) velmi jednoduchá. Všechny klíčové hodnoty jsou na začátku souboru `client/widget.css`. 

Změnu můžete provést buď přímou úpravou `widget.css`, nebo přepsáním proměnných pro konkrétní stránku. Například pro zeleného chatbota stačí do HTML přidat:

```html
<style>
  :root {
    --chatbot-primary: #10b981;
    --chatbot-primary-hover: #059669;
    --chatbot-gradient-end: #047857;
  }
</style>
```

## Bezpečnost a ochrana proti zneužití

Aplikace obsahuje silné bezpečnostní mechanismy proti zneužití a XSS:

### Prevence XSS (Cross-Site Scripting)
- **Frontend:** V souboru `widget.js` se pro vykreslování příchozích zpráv (od uživatele i ze serveru) používá vlastnost `textContent` (`msgDiv.textContent = text;`). Na rozdíl od `innerHTML` nedochází k interpretaci přijatého textu jako HTML kódu. Pokud uživatel do chatu napíše zákeřný skript `<script>alert(1)</script>`, prohlížeč ho bezpečně vykreslí jen jako čistý text.
- **Backend:** PHP API vrací data striktně s hlavičkou `Content-Type: application/json`. Díky tomu prohlížeč interpretuje odpověď jako data a nesnaží se v ní hledat spustitelný kód, i kdyby uživatel přistoupil k API napřímo.

### Ochrana formuláře a API (Rate Limiting)
- **Frontend prevence spamu:** HTML vstup omezuje zprávu na maximálně 500 znaků (`maxlength="500"`). Tlačítko pro odeslání se po kliknutí zablokuje a uvolní se až po přijetí odpovědi, čímž se efektivně brání dvojitému a násobnému odeslání.
- **Backend Rate Limiting a validace:** API v PHP kontroluje maximální délku 500 znaků a brání prázdným zprávám. Pomocí PHP sessions je zaveden **Rate Limiting**, který neumožní uživateli odeslat více než 1 zprávu za sekundu (odpovídá chybovým kódem `429 Too Many Requests`).
- **CORS:** Server aktuálně pro testovací účely povoluje všechny domény (`Access-Control-Allow-Origin: *`). V produkci zde musí být definována pouze konkrétní doména, na které se widget nachází, aby API nemohl využívat kdokoliv z cizího webu.
