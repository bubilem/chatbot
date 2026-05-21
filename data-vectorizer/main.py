import time

from extract import extract_data
from load import load_to_chroma
from transform import transform_data

def run_etl_pipeline():
    """Spustí kompletní proces: Extract -> Transform -> Load"""
    print("=" * 50)
    print("Spouštím vektorizaci databáze pro AI Chatbota")
    print("=" * 50)
    
    start_time = time.time()
    
    # 1. EXTRACT
    raw_data = extract_data()
    if not raw_data:
        print("Konec: Nebyla nalezena žádná data.")
        return

    # 2. TRANSFORM
    chunks = transform_data(raw_data)
    if not chunks:
        print("Konec: Nepodařilo se vytvořit žádné bloky textu.")
        return

    # 3. LOAD
    load_to_chroma(chunks)
    
    end_time = time.time()
    print("=" * 50)
    print(f"Vektorizace úspěšně dokončena za {end_time - start_time:.2f} sekund!")
    print("=" * 50)

if __name__ == "__main__":
    run_etl_pipeline()
