# Schéma databáze (db-structure)

Tento dokument popisuje strukturu MySQL tabulek, ze kterých `extract.py` čerpá obsah pro vektorizaci. Zdrojová databáze je CMS systém spravující články, stránky a jejich moduly.

---

## Uživatelské role (`cms_role`)

Tabulka definuje role uživatelů. Extrakce filtruje obsah pouze pro roli s kódem `host` (veřejně přístupný obsah).

### `cms_role`

| Sloupec | Typ | Popis |
|---|---|---|
| `id` | INT UNSIGNED AUTO_INCREMENT PRIMARY KEY | Unikátní identifikátor role |
| `name` | VARCHAR(100) NOT NULL | Název role (např. „Veřejnost") |
| `level` | TINYINT UNSIGNED NOT NULL | Úroveň oprávnění |
| `code` | VARCHAR(50) NOT NULL | Kód role (extrakce filtruje `code = 'host'`) |

---

## Články

Články jsou hlavní obsahovou jednotkou CMS. Mohou mít přiřazeny rozšiřující moduly (WYSIWYG, galerie, atd.).

### `cms_article`

| Sloupec | Typ | Popis |
|---|---|---|
| `id` | MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY | Unikátní identifikátor článku |
| `url` | VARCHAR(1000) NOT NULL | Relativní URL adresa článku (použita jako metadata v ChromaDB) |
| `name` | VARCHAR(100) NOT NULL | Název / titulek článku |
| `preface` | TEXT NOT NULL | Perex (krátký úvod) |
| `content` | TEXT NOT NULL | Hlavní obsah článku (může obsahovat HTML) |
| `publishDateFrom` | DATETIME NOT NULL | Datum a čas začátku publikace |
| `publishDateTo` | DATETIME | Datum a čas konce publikace (NULL = bez omezení) |
| `publicate` | TINYINT NOT NULL | 1 = publikováno, 0 = skryto |
| `role` | INT UNSIGNED NOT NULL | FK → `cms_role.id` (přiřazená role) |

### `cms_article_module`

Propojení článků s moduly (každý článek může mít více modulů různých typů).

| Sloupec | Typ | Popis |
|---|---|---|
| `id` | MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY | Identifikátor instance modulu |
| `article` | MEDIUMINT UNSIGNED | FK → `cms_article.id` |
| `modul` | VARCHAR(100) NOT NULL | Identifikátor typu modulu (např. `core/WysiwygModule`) |
| `active` | TINYINT NOT NULL | 1 = aktivní, 0 = neaktivní |

### `cms_article_module_data`

Klíč-hodnota data konkrétního modulu.

| Sloupec | Typ | Popis |
|---|---|---|
| `module` | MEDIUMINT UNSIGNED | FK → `cms_article_module.id` (část primárního klíče) |
| `name` | VARCHAR(45) NOT NULL | Název parametru (extrakce čte `name = 'content'`) |
| `value` | TEXT | Hodnota parametru (HTML obsah WYSIWYG editoru) |

---

## Stránky

Stránky jsou statické obsahové jednotky (např. „O nás", „Kontakt"). Jejich obsah je spravován přes tzv. „boxy" (podobné modulům u článků).

### `cms_page`

| Sloupec | Typ | Popis |
|---|---|---|
| `id` | SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY | Unikátní identifikátor stránky |
| `url` | VARCHAR(100) NOT NULL | Relativní URL adresa stránky |
| `publishDateFrom` | DATETIME NOT NULL | Datum začátku dostupnosti |
| `publishDateTo` | DATETIME | Datum konce dostupnosti (NULL = bez omezení) |
| `active` | TINYINT NOT NULL | 1 = aktivní, 0 = skrytá |
| `role` | INT UNSIGNED NOT NULL | FK → `cms_role.id` |

### `cms_box`

Boxy jsou obsahové bloky přiřazené stránkám (analogie `cms_article_module`).

| Sloupec | Typ | Popis |
|---|---|---|
| `id` | MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY | Identifikátor boxu |
| `page` | SMALLINT UNSIGNED | FK → `cms_page.id` |
| `modul` | VARCHAR(100) NOT NULL | Typ modulu (extrakce čte `modul = 'core/WysiwygModule'`) |
| `active` | TINYINT NOT NULL | 1 = aktivní, 0 = neaktivní |

### `cms_box_data`

Klíč-hodnota data konkrétního boxu.

| Sloupec | Typ | Popis |
|---|---|---|
| `box` | MEDIUMINT UNSIGNED | FK → `cms_box.id` (část primárního klíče) |
| `name` | VARCHAR(45) NOT NULL | Název parametru (extrakce čte `name = 'content'`) |
| `value` | TEXT | Obsah boxu (HTML z WYSIWYG editoru) |

---

## SQL dotazy pro extrakci dat

Dotazy používané v `extract.py`. Filtrují pouze **publikovaný obsah** viditelný pro roli `host`.

### 1. Hlavní obsah článků

```sql
SELECT a.id, a.url, a.preface, a.content
FROM cms_article a
JOIN cms_role r ON a.role = r.id
WHERE a.publishDateFrom <= NOW()
  AND (a.publishDateTo IS NULL OR NOW() <= a.publishDateTo)
  AND a.publicate = 1
  AND r.code = 'host';
```

### 2. WYSIWYG moduly článků

```sql
SELECT a.id, m.id AS module_id, a.url, d.value
FROM cms_article a
JOIN cms_role r ON a.role = r.id AND r.code = 'host'
JOIN cms_article_module m ON a.id = m.article AND m.modul = 'core/WysiwygModule'
JOIN cms_article_module_data d ON m.id = d.module AND d.name = 'content'
WHERE a.publishDateFrom <= NOW()
  AND (a.publishDateTo IS NULL OR NOW() <= a.publishDateTo)
  AND a.publicate = 1;
```

### 3. WYSIWYG boxy stránek

```sql
SELECT p.id, b.id AS box_id, p.url, d.value
FROM cms_page p
JOIN cms_role r ON p.role = r.id AND r.code = 'host'
JOIN cms_box b ON p.id = b.page AND b.modul = 'core/WysiwygModule'
JOIN cms_box_data d ON b.id = d.box AND d.name = 'content'
WHERE p.publishDateFrom <= NOW()
  AND (p.publishDateTo IS NULL OR NOW() <= p.publishDateTo)
  AND p.active = 1;
```

---

## Vztahy mezi tabulkami (ER diagram)

```
cms_role (1)─────────────────────(N) cms_article
                                         │ (1)
                                         │
                                        (N)
                                  cms_article_module (1)──(N) cms_article_module_data
                                  [modul = 'core/WysiwygModule']
                                  [name  = 'content']

cms_role (1)─────────────────────(N) cms_page
                                       │ (1)
                                       │
                                      (N)
                                    cms_box (1)──(N) cms_box_data
                                    [modul = 'core/WysiwygModule']
                                    [name  = 'content']
```