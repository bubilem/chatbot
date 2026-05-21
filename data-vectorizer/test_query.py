from load import get_chroma_db


def search(query, top_k=3):
    print(f"\n[AI] Hledám v databázi nejrelevantnější obsah pro: '{query}'")

    # Načte existující databázi
    vector_store = get_chroma_db()

    # Provede sémantické vyhledávání
    # similarity_search_with_score vrací dokument a jeho "vzdálenost" od dotazu
    # (u výchozí ChromaDB metriky L2 znamená menší číslo = vyšší podobnost)
    results = vector_store.similarity_search_with_score(query, k=top_k)

    print(f"\nNalezeno {len(results)} výsledků:\n")
    separator = "=" * 50
    divider = "-" * 50
    for idx, (doc, score) in enumerate(results, 1):
        print(separator)
        print(f"Výsledek {idx} | Skóre vzdálenosti: {score:.4f}")
        print(f"Typ obsahu: {doc.metadata.get('type')}")
        print(f"Zdrojová URL: {doc.metadata.get('url')}")
        print(f"ID modulu: {doc.metadata.get('source_id')}")
        print(divider)
        # Vypíšeme prvních 500 znaků textu, aby se terminál nezahltil
        snippet = doc.page_content[:500]
        if len(doc.page_content) > 500:
            snippet += "..."
        print(f"{snippet}\n")

if __name__ == "__main__":
    print("Vítejte v testovacím vyhledávání! (Pro ukončení napište 'q')")
    while True:
        user_query = input("\nZadejte svůj dotaz: ")
        if not user_query.strip():
            continue
        if user_query.strip().lower() in ['q', 'quit', 'exit', 'konec']:
            break

        search(user_query)
