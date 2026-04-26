# Datový Vektorizátor (ETL)

Tato složka obsahuje nezávislou komponentu pro ETL (Extract, Transform, Load) proces. Slouží k automatizovanému stažení textového obsahu (články, stránky, moduly) z existující MySQL databáze webu, jeho vyčištění, segmentaci na logické odstavce a následné vektorizaci (tzv. embeddings) pomocí lokálního AI modelu. Výsledek se ukládá do lokální vektorové databáze `ChromaDB`.

Tato data jsou připravena pro budoucí integraci s chatbotem, který v nich bude moci sémanticky vyhledávat odpovědi.

## Architektura a funkce

1. **`extract.py` (Extrakce)**
   - Využívá připravené SQL dotazy k načtení obsahu z tabulek `cms_article`, `cms_page` a navázaných WYSIWYG modulů.
   - Získává hlavní obsah i s metadaty (jako jsou zdrojové URL adresy).

2. **`transform.py` (Očištění a Chunking)**
   - Používá `BeautifulSoup` pro bezpečné odstranění HTML tagů z WYSIWYG editorů.
   - Používá `RecursiveCharacterTextSplitter` (z knihovny LangChain) k inteligentnímu rozdělení textů na odstavce (tzv. chunky) dlouhé zhruba 800 znaků s překryvem (100 znaků) pro zachování sémantického kontextu.

3. **`load.py` (Vektorizace a Uložení)**
   - Inicializuje lokální open-source jazykový model `intfloat/multilingual-e5-small` (optimalizovaný pro vektorizaci i v češtině).
   - Spravuje lokální souborovou databázi **ChromaDB** (ukládá se do složky `chroma_db/`), kam hotové texty, vektory a URL metadata ukládá.

4. **`main.py`**
   - Zastřešující skript, který celý výše popsaný řetězec spustí v jednom průchodu.

---

## Návod ke spuštění (Instalace)

Pro zprovoznění a spuštění procesu vektorizace postupujte následovně:

### 1. Požadavky a příprava prostředí

Vzhledem k povaze AI a data-science knihoven (zejména ChromaDB a `chroma-hnswlib`) existují na OS Windows specifika s kompilací, u kterých je nutné dodržet správný postup. 

**Příprava na Windows:**
> [!WARNING]
> **Varování k verzi Pythonu:** Vyhněte se prozatím používání nejnovějšího Pythonu 3.13. Starší závislosti jako `numpy` (které vyžaduje např. LangChain) s ním mají problémy s kompilací kvůli změnám v C-API, a to i s nainstalovanými C++ nástroji. Volte vždy Python 3.12 nebo 3.11.

Máte dvě možnosti, jak prostředí úspěšně zprovoznit:

*   **Možnost A: Python 3.12 + Instalace C++ Build Tools (Doporučeno)**
    Toto je ideální „zlatá střední cesta“. Moderní Python, ke kterému přidáte nástroje, jež zajistí úspěšnou automatickou kompilaci chybějících balíčků ze zdrojových kódů.
    1. Ujistěte se, že máte nainstalovaný **Python 3.12**.
    2. Stáhněte a nainstalujte [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
    3. V instalátoru zaškrtněte **„Vývoj desktopových aplikací pomocí C++“** (Desktop development with C++).
    4. Ponechte zaškrtnuté výchozí volitelné komponenty na pravé straně (MSVC, Windows SDK) a nainstalujte je.

*   **Možnost B: Pouze starší Python 3.11 (Nejjednodušší)**
    Pokud se chcete vyhnout objemné instalaci Build Tools, doporučujeme stáhnout a použít striktně **Python 3.11**. Pro tuto starší verzi totiž existují pro většinu AI knihoven již předkompilované balíčky (wheels), takže kompilace není vůbec nutná.

**Vytvoření a aktivace virtuálního prostředí:**
Doporučujeme nástroj spouštět v samostatném virtuálním prostředí. 

**Windows (PowerShell):**
```powershell
cd data-vectorizer

# Vytvoření prostředí (pokud chcete vynutit např. verzi 3.11, použijte: py -3.11 -m venv venv)
python -m venv venv

# Aktivace prostředí
.\venv\Scripts\activate
```

**Linux/macOS:**
```bash
cd data-vectorizer
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalace závislostí

S plně aktivním virtuálním prostředím (vlevo v terminálu svítí `(venv)`) nainstalujte potřebné knihovny:
```bash
pip install -r requirements.txt
```

> **Tip k instalaci:** Pokud by při instalaci (zejména u větších závislostí a modelů) došlo k vypršení časového limitu sítě (`TimeoutError: The read operation timed out`), použijte příkaz s prodlouženým limitem:
> `pip install --default-timeout=100 -r requirements.txt`

### 3. Konfigurace připojení k databázi (MySQL)

Nástroj potřebuje znát údaje k vaší databázi, odkud bude čerpat obsah:
1. Zkopírujte šablonu `.env.example` a přejmenujte ji na `.env`.
   ```bash
   cp .env.example .env
   ```
2. Otevřete nově vytvořený soubor `.env` a vyplňte aktuální přístupové údaje:
   ```ini
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=vase_heslo
   DB_NAME=jmeno_vasi_databaze
   ```

### 4. Spuštění vektorizace

Jakmile máte nastavené prostředí a `.env` soubor, spusťte hlavní skript:
```bash
python main.py
```

> **Důležitá poznámka k prvnímu spuštění:** 
> Při úplně prvním spuštění může skript běžet pomaleji. Důvodem je stahování jazykového modelu `multilingual-e5-small` ze serverů HuggingFace (velikost cca 100-300 MB). Při každém dalším spuštění již model načte lokálně z disku a proces proběhne výrazně rychleji.
