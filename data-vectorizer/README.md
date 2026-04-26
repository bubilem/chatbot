# Datový Vektorizátor – ETL Pipeline pro AI Chatbot

Tato složka obsahuje nezávislou komponentu pro **ETL (Extract, Transform, Load)** proces. Slouží k automatizovanému stažení textového obsahu z existující MySQL databáze webu, jeho vyčištění, segmentaci na logické bloky (**chunky**) a následné vektorizaci (**embeddings**) pomocí lokálního AI modelu. Výsledek se ukládá do lokální vektorové databáze **ChromaDB**.

Tato data jsou připravena pro integraci s `chat-api`, kde chatbot bude moci v databázi **sémanticky vyhledávat** – tzn. najít obsah podle *smyslu* dotazu, nikoli jen klíčových slov.

---

## Jak ETL pipeline funguje

```
MySQL (CMS databáze)
       │
       ▼
  [extract.py]   ← SQL SELECT z tabulek cms_article, cms_page a jejich modulů
       │           Výstup: [{'id': '...', 'url': '...', 'content': '<HTML>'}]
       │
       ▼
 [transform.py]  ← 1. Odstranění HTML tagů (BeautifulSoup)
       │           2. Rozdělení textu na chunky (LangChain RecursiveCharacterTextSplitter)
       │           Výstup: [{'id': '...', 'text': '...čistý text...', 'metadata': {...}}]
       │
       ▼
   [load.py]     ← Vektorizace textu (HuggingFace model multilingual-e5-small)
       │           Uložení vektorů + textu + metadata do ChromaDB
       │
       ▼
 chroma_db/      ← Lokální souborová vektorová databáze (připravena pro chatbota)
```

---

## Struktura složky

```
data-vectorizer/
├── main.py           ← Spouštěč: volá extract → transform → load v pořadí
├── extract.py        ← Extrakce dat z MySQL přes python-mysql-connector
├── transform.py      ← Čištění HTML + chunking textu
├── load.py           ← Vektorizace + upsert do ChromaDB
├── test_query.py     ← Interaktivní REPL pro testování sémantického vyhledávání
├── requirements.txt  ← Seznam Python závislostí s fixovanými verzemi
├── .env.example      ← Šablona konfiguračního souboru (zkopírujte na .env)
├── .env              ← Přístupové údaje k DB (NENÍ v Gitu!)
├── db-structure.md   ← Schéma MySQL tabulek, ze kterých se čerpají data
└── chroma_db/        ← Složka s lokální ChromaDB (generovaná, NENÍ v Gitu)
```

---

## Instalace a spuštění

### Předpoklady – Python na Windows

> [!WARNING]
> **Varování k verzi Pythonu:** Vyhněte se Pythonu 3.13. Starší závislosti (zejména `numpy` přes LangChain) mají problémy s kompilací kvůli změnám C-API. Používejte **Python 3.11 nebo 3.12**.

**Máte dvě možnosti:**

#### Možnost A: Python 3.12 + C++ Build Tools *(doporučeno)*

Moderní Python + nástroje pro kompilaci balíčků ze zdrojových kódů.

1. Ujistěte se, že máte nainstalovaný **Python 3.12**
2. Stáhněte a nainstalujte **[Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)**
3. V instalátoru zaškrtněte **„Desktop development with C++"**
4. Ponechte výchozí volitelné komponenty (MSVC, Windows SDK) a nainstalujte

#### Možnost B: Python 3.11 *(nejjednodušší)*

Pro Python 3.11 existují předkompilované binární balíčky (wheels) – žádná kompilace není potřeba.

---

### Krok 1 – Vytvoření a aktivace virtuálního prostředí

```powershell
# Windows (PowerShell) – z kořene repozitáře
cd data-vectorizer

# Vytvoření prostředí (pro vynucení verze: py -3.11 -m venv venv)
python -m venv venv

# Aktivace prostředí
.\venv\Scripts\activate
```

```bash
# Linux / macOS
cd data-vectorizer
python3 -m venv venv
source venv/bin/activate
```

> Po aktivaci se v terminálu vlevo zobrazí `(venv)`.

---

### Krok 2 – Instalace závislostí

```bash
pip install -r requirements.txt
```

> [!TIP]
> Pokud instalace vyprší chybou `TimeoutError: The read operation timed out` (u velkých balíčků jako `torch`), použijte prodloužený timeout:
> ```bash
> pip install --default-timeout=200 -r requirements.txt
> ```

**Závislosti projektu:**

| Balíček | Verze | Účel |
|---|---|---|
| `langchain` | 0.3.7 | Orchestrace AI procesů |
| `langchain-community` | 0.3.5 | Komunitní integrace (text splittery) |
| `langchain-huggingface` | 0.1.2 | Integrace HuggingFace modelů |
| `langchain-chroma` | 0.1.4 | LangChain wrapper pro ChromaDB |
| `chromadb` | 0.5.15 | Lokální vektorová databáze |
| `sentence-transformers` | 3.3.1 | Inference AI embedding modelu |
| `beautifulsoup4` | 4.12.3 | Parsování a čištění HTML |
| `mysql-connector-python` | 9.1.0 | Připojení k MySQL databázi |
| `python-dotenv` | 1.0.1 | Načítání proměnných ze souboru `.env` |

---

### Krok 3 – Konfigurace přístupu k databázi

```bash
# Zkopírujte šablonu
cp .env.example .env
```

Poté otevřete `.env` a vyplňte přístupové údaje k vaší MySQL databázi:

```ini
# MySQL přístupové údaje
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=vase_heslo
DB_NAME=jmeno_vasi_databaze

# Složka pro lokální vektorovou databázi (relativní cesta od data-vectorizer/)
CHROMA_DB_DIR=./chroma_db
```

> [!CAUTION]
> Soubor `.env` obsahuje hesla a nesmí být nikdy commitován do Gitu. Je správně přidán do `.gitignore`.

---

### Krok 4 – Spuštění ETL procesu (vektorizace)

```bash
python main.py
```

Při prvním spuštění proběhne stahování AI modelu `multilingual-e5-small` ze serverů HuggingFace (**~100–300 MB**). Při dalších spuštěních se model načte z lokální cache.

**Výstup úspěšného spuštění vypadá přibližně takto:**
```
==================================================
Spouštím vektorizaci databáze pro AI Chatbota
==================================================
Připojování k databázi...
Stahuji hlavní obsah článků...
Stahuji moduly článků...
Stahuji moduly stránek...
Úspěšně extrahováno celkem 87 záznamů.
Čištění textu a chunking (rozdělování na bloky)...
Transformace dokončena. Z původních 87 záznamů vzniklo 214 chunků.
Připravuji uložení 214 záznamů do vektorové databáze...
Kontroluji existující záznamy v databázi...
  Přidávám 214 nových záznamů...
Generuji vektory (embeddings) a ukládám do databáze... (Toto může chvíli trvat)
Uložení dokončeno!
==================================================
Vektorizace úspěšně dokončena za 47.23 sekund!
==================================================
```

---

## Testování vektorové databáze

Po úspěšné vektorizaci si můžete otestovat, jak dobře databáze odpovídá na dotazy v češtině:

```bash
python test_query.py
```

Spustí se interaktivní REPL, kde zadáte dotaz a skript vrátí nejrelevantnější chunky z databáze včetně skóre vzdálenosti:

```
Vítejte v testovacím vyhledávání! (Pro ukončení napište 'q')

Zadejte svůj dotaz: Jaká je otevírací doba?

[AI] Hledám v databázi nejrelevantnější obsah pro: 'Jaká je otevírací doba?'

Nalezeno 3 výsledků:

==================================================
Výsledek 1 | Skóre vzdálenosti: 0.2341
Typ obsahu: article
Zdrojová URL: /o-nas/otviraci-doba
ID modulu: article_42
--------------------------------------------------
Muzeum je otevřeno od pondělí do pátku 9:00–17:00...
```

> **Skóre vzdálenosti:** Nižší číslo = vyšší podobnost. Hodnoty pod 0.5 jsou zpravidla velmi relevantní.

---

## Popis jednotlivých souborů

### `extract.py` – Extrakce dat z MySQL

Načítá obsah z databáze přes tři SQL dotazy:

1. **Hlavní obsah článků** (`cms_article`) – perex + obsah publikovaných článků
2. **WYSIWYG moduly článků** (`cms_article_module`, `cms_article_module_data`) – rozšířený obsah z modulů
3. **WYSIWYG moduly stránek** (`cms_page`, `cms_box`, `cms_box_data`) – obsah stránek

Každý záznam obsahuje unikátní `id`, zdrojovou `url` a surový `content` (může obsahovat HTML tagy).

Schéma databázových tabulek je zdokumentováno v [`db-structure.md`](./db-structure.md).

---

### `transform.py` – Čištění a chunking

**1. Čištění HTML:**
```python
soup = BeautifulSoup(raw_html, "html.parser")
text = soup.get_text(separator=" ", strip=True)
# "<p>Ahoj <b>světe</b>!</p>" → "Ahoj světe !"
```

**2. Chunking (rozdělení na bloky):**
```python
RecursiveCharacterTextSplitter(
    chunk_size=800,    # Max. 800 znaků v jednom bloku
    chunk_overlap=100, # 100 znaků překryvu pro zachování kontextu
    separators=["\n\n", "\n", ".", " ", ""]  # Preferuje přirozené konce vět
)
```

Překryv (`chunk_overlap`) zajišťuje, že pokud je odpověď na dotaz na rozhraní dvou bloků, bude nalezena v obou a chatbot ji nezamešká.

---

### `load.py` – Vektorizace a uložení do ChromaDB

**AI model:** `intfloat/multilingual-e5-small`
- Open-source model optimalizovaný pro vícejazyčné texty včetně češtiny
- Běží lokálně na CPU (GPU volitelné přes `model_kwargs={'device': 'cuda'}`)
- Vytváří **384-dimenzionální vektory** reprezentující sémantický smysl textu

**Upsert logika:**
- Při každém spuštění skript zkontroluje, která ID v databázi již existují
- **Nové záznamy** jsou přidány, **existující** jsou aktualizovány
- Bezpečné opakované spuštění bez `DuplicateIDError`

---

### `main.py` – Orchestrátor ETL

Minimalistický skript, který spouští celý řetězec:

```python
raw_data = extract_data()    # 1. MySQL → surová data
chunks = transform_data()    # 2. Čištění + chunking
load_to_chroma(chunks)       # 3. Vektorizace + ChromaDB
```

Obsahuje měření celkového času a jasné výstupy do konzole pro každou fázi.

---

## Opakované spuštění a re-index

Skript lze spustit opakovaně:
- **Nové záznamy** z databáze jsou automaticky přidány
- **Změněný obsah** (stejné ID) je aktualizován

Pokud potřebujete **úplný reset** (smazání a nové naplnění celé databáze):

```bash
# Smažte složku s databází
rm -rf chroma_db/

# Spusťte vektorizaci znovu (vše bude přidáno jako nové)
python main.py
```
