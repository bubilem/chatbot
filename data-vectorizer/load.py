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
    """
    if not transformed_chunks:
        print("Žádná data k uložení.")
        return
        
    print(f"Připravuji uložení {len(transformed_chunks)} záznamů do vektorové databáze...")
    
    vector_store = get_chroma_db()
    
    texts = [chunk['text'] for chunk in transformed_chunks]
    metadatas = [chunk['metadata'] for chunk in transformed_chunks]
    ids = [chunk['id'] for chunk in transformed_chunks]
    
    # Přidá dokumenty do databáze (při existenci stejného ID to bohužel defaultně hodí chybu, proto se u updatů použijí jiné techniky, 
    # nebo nejprve smazat. Prozatím provádíme append).
    # add_texts interně volá Chroma kolekci
    print("Generuji vektory (embeddings) a ukládám do databáze... (Toto může chvíli trvat)")
    
    # Pro jistotu můžeme vyčistit stará data, pokud chceme plný reset:
    # (Odkomentovat v budoucnu pro úplný re-index)
    # vector_store.delete_collection()
    
    vector_store.add_texts(
        texts=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    print("Uložení dokončeno!")

if __name__ == "__main__":
    # Test initialization
    store = get_chroma_db()
    print("ChromaDB úspěšně načtena.")
