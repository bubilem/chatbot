import os

import mysql.connector
from dotenv import load_dotenv

# Načtení proměnných prostředí ze souboru .env
load_dotenv()

def get_db_connection():
    """Vytvoří připojení k databázi pomocí údajů v .env"""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "")
    )

def extract_data():
    """
    Spustí SQL dotazy pro získání obsahu a metadat z databáze.
    Vrací seznam slovníků: [{'id': id, 'url': url, 'type': typ_obsahu, 'content': text_nebo_html}]
    """
    print("Připojování k databázi...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    extracted_docs = []

    try:
        # 1. Články (základní texty)
        print("Stahuji hlavní obsah článků...")
        cursor.execute("""
            SELECT a.id, a.url, a.preface, a.content 
            FROM cms_article a JOIN cms_role r ON a.role = r.id
            WHERE a.publishDateFrom <= NOW() 
              AND (a.publishDateTo IS NULL OR NOW() <= a.publishDateTo) 
              AND a.publicate = 1 AND r.code = 'host';
        """)
        for row in cursor.fetchall():
            # Spojíme perex a hlavní obsah
            full_content = f"{row.get('preface', '')} {row.get('content', '')}"
            extracted_docs.append({
                'id': f"article_{row['id']}",
                'url': row['url'],
                'type': 'article',
                'content': full_content
            })

        # 2. Moduly článků (rozšířený obsah z modulů)
        print("Stahuji moduly článků...")
        cursor.execute("""
            SELECT a.id, m.id as module_id, a.url, d.value
            FROM cms_article a
            JOIN cms_role r ON a.role = r.id  AND r.code = 'host'
            JOIN cms_article_module m ON a.id = m.article AND m.modul = 'core/WysiwygModule'
            JOIN cms_article_module_data d ON m.id = d.module AND d.name = 'content'
            WHERE a.publishDateFrom <= NOW() 
              AND (a.publishDateTo IS NULL OR NOW() <= a.publishDateTo) 
              AND a.publicate = 1;
        """)
        for row in cursor.fetchall():
            extracted_docs.append({
                'id': f"article_{row['id']}_module_{row['module_id']}",
                'url': row['url'],
                'type': 'article_module',
                'content': row['value']
            })

        # 3. Stránky (obsah ze stránek přes CMS boxy)
        print("Stahuji moduly stránek...")
        cursor.execute("""
            SELECT p.id, b.id as box_id, p.url, d.value
            FROM cms_page p
            JOIN cms_role r ON p.role = r.id  AND r.code = 'host'
            JOIN cms_box b ON p.id = b.page AND b.modul = 'core/WysiwygModule'
            JOIN cms_box_data d ON b.id = d.box AND d.name = 'content'
            WHERE p.publishDateFrom <= NOW() 
              AND (p.publishDateTo IS NULL OR NOW() <= p.publishDateTo) 
              AND p.active = 1;
        """)
        for row in cursor.fetchall():
            extracted_docs.append({
                'id': f"page_{row['id']}_box_{row['box_id']}",
                'url': row['url'],
                'type': 'page_module',
                'content': row['value']
            })

    except Exception as e:
        print(f"Chyba při stahování dat z databáze: {e}")
    finally:
        cursor.close()
        conn.close()

    print(f"Úspěšně extrahováno celkem {len(extracted_docs)} záznamů.")
    return extracted_docs

if __name__ == "__main__":
    docs = extract_data()
    if docs:
        print("Ukázka prvního záznamu:", docs[0])
