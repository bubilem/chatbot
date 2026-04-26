import os

# Vypnutí ChromaDB telemetrie MUSÍ BÝT PŘED IMPORTEM samotné databáze
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

def get_chroma_db():
    """
    Inicializuje lokální Chroma databázi a model pro tvorbu vektorů (embeddings).
    """
    db_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    
    # Použijeme lokální open-source model doporučený pro češtinu
    model_name = "intfloat/multilingual-e5-small"
    
    # HuggingFaceEmbeddings automaticky stáhne model ze Sentence Transformers
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        # model_kwargs={'device': 'cpu'}, # Nebo 'cuda' pokud je k dispozici GPU
        # encode_kwargs={'normalize_embeddings': True}
    )
    
    # Připojíme / Vytvoříme instanci ChromaDB v dané složce
    vector_store = Chroma(
        collection_name="chatbot_data",
        embedding_function=embeddings,
        persist_directory=db_dir
    )
    return vector_store

def load_to_chroma(transformed_chunks):
    """
    Nahraje vyčištěné texty a metadata do vektorové databáze.

    Používá upsert logiku: zkontroluje, která ID v databázi již existují,
    a provede buď přidání nových, nebo aktualizaci stávajících záznamů.
    Bezpečně zvládá opakované spuštění bez DuplicateIDError.
    """
    if not transformed_chunks:
        print("Žádná data k uložení.")
        return

    print(f"Připravuji uložení {len(transformed_chunks)} záznamů do vektorové databáze...")

    vector_store = get_chroma_db()

    texts = [chunk['text'] for chunk in transformed_chunks]
    metadatas = [chunk['metadata'] for chunk in transformed_chunks]
    ids = [chunk['id'] for chunk in transformed_chunks]

    # Zjistíme, která ID v databázi již existují (include=[] vrátí jen ID, bez vektorů)
    print("Kontroluji existující záznamy v databázi...")
    existing = vector_store.get(ids=ids, include=[])
    existing_ids = set(existing.get('ids', []))

    # Rozdělíme na nové záznamy a záznamy k aktualizaci
    new_texts, new_metas, new_ids = [], [], []
    update_texts, update_metas, update_ids = [], [], []

    for text, meta, doc_id in zip(texts, metadatas, ids):
        if doc_id in existing_ids:
            update_texts.append(text)
            update_metas.append(meta)
            update_ids.append(doc_id)
        else:
            new_texts.append(text)
            new_metas.append(meta)
            new_ids.append(doc_id)

    print("Generuji vektory (embeddings) a ukládám do databáze... (Toto může chvíli trvat)")

    if new_ids:
        print(f"  Přidávám {len(new_ids)} nových záznamů...")
        vector_store.add_texts(texts=new_texts, metadatas=new_metas, ids=new_ids)

    if update_ids:
        print(f"  Aktualizuji {len(update_ids)} existujících záznamů...")
        vector_store.update_texts(texts=update_texts, metadatas=update_metas, ids=update_ids)

    print("Uložení dokončeno!")

if __name__ == "__main__":
    # Test initialization
    store = get_chroma_db()
    print("ChromaDB úspěšně načtena.")
