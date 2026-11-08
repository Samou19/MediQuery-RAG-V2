import json
from pathlib import Path

from app.services.chunking import create_chunks
from app.services.embeddings import generate_embeddings
from app.services.ingestion import extract_pdf
from app.services.text_cleaning import clean_documents

# 1. Extraction
documents = extract_pdf("data/raw/parcours_de_soins_diabete_type_2.pdf")

# 2. Nettoyage
cleaned_documents = clean_documents(documents)

# 3. Chunking
chunks = create_chunks(cleaned_documents, chunk_size=1000, chunk_overlap=150)

# 4. Génération des embeddings
embedded_chunks = generate_embeddings(chunks, batch_size=64)

# Sauvegarde locale des embeddings
output_path = Path("data/processed/embedded_chunks.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with output_path.open("w", encoding="utf-8") as file:
    json.dump(embedded_chunks, file, ensure_ascii=False)

print(f"Embeddings sauvegardés dans : {output_path}")

# 5. Vérifications
print("\nSTATISTIQUES DES EMBEDDINGS")
print("Nombre de chunks :", len(embedded_chunks))

if embedded_chunks:
    first = embedded_chunks[0]

    print("Premier chunk ID :", first["chunk_id"])
    print("Page source :", first["metadata"]["page"])
    print("Dimension du vecteur :", len(first["vector"]))
    print("Premières valeurs :", first["vector"][:5])

    dimensions = {len(chunk["vector"]) for chunk in embedded_chunks}

    print("Dimensions présentes :", dimensions)

    ids = [chunk["chunk_id"] for chunk in embedded_chunks]

    print("Nombre d'identifiants uniques :", len(set(ids)))
    print("Identifiants uniques :", len(ids))
