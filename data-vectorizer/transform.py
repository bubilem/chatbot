from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter


def clean_html(raw_html):
    """Odstraní HTML značky z textu a vrátí čistý text."""
    if not raw_html:
        return ""
    # BeautifulSoup parseuje HTML a vyčistí tagy
    soup = BeautifulSoup(raw_html, "html.parser")
    # Získáme text oddělený mezerami místo tagů
    text = soup.get_text(separator=" ", strip=True)
    return text

def transform_data(extracted_docs):
    """
    Vyčistí HTML a rozseká texty na menší odstavce (chunks).
    Vrací seznam slovníků ve formátu vhodném pro uložení:
    [{'id': '...', 'text': '...', 'metadata': {...}}]
    """
    print("Čištění textu a chunking (rozdělování na bloky)...")

    # LangChain Splitter - rozdělí text tak, aby nechal odstavce v celku (pokud možno)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,       # Maximální počet znaků v jednom chunku
        chunk_overlap=100,    # Kolik znaků se má překrývat s předchozím chunkem pro kontext
        separators=["\n\n", "\n", ".", " ", ""]
    )

    transformed_chunks = []

    for doc in extracted_docs:
        raw_content = doc.get('content', '')
        clean_content = clean_html(raw_content)

        if not clean_content:
            continue

        # Rozsekání čistého textu
        chunks = text_splitter.split_text(clean_content)

        for idx, chunk_text in enumerate(chunks):
            chunk_id = f"{doc['id']}_chunk_{idx}"
            transformed_chunks.append({
                'id': chunk_id,
                'text': chunk_text,
                'metadata': {
                    'url': doc['url'],
                    'type': doc['type'],
                    'source_id': doc['id']
                }
            })

    print(f"Transformace dokončena. Z původních {len(extracted_docs)} záznamů vzniklo {len(transformed_chunks)} chunků.")
    return transformed_chunks

if __name__ == "__main__":
    # Test
    test_docs = [
        {'id': 'test_1', 'url': '/test', 'type': 'article', 'content': '<p>Tohle je testovací článek.</p><b>Důležitá informace</b>!'}
    ]
    chunks = transform_data(test_docs)
    for c in chunks:
        print(c)
