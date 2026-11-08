from app.services.chunking import create_chunks
from app.services.ingestion import extract_pdf
from app.services.text_cleaning import clean_documents

# 1. Extraction
documents = extract_pdf("data/raw/parcours_de_soins_diabete_type_2.pdf")

# 2. Nettoyage
cleaned_documents = clean_documents(documents)

# 3. Chunking
chunks = create_chunks(cleaned_documents, chunk_size=1000, chunk_overlap=150)

# 4. Affichage des premiers chunks
for chunk in chunks[:5]:
    print("\n" + "=" * 70)
    print("CHUNK ID :", chunk["chunk_id"])
    print("PAGE :", chunk["metadata"]["page"])
    print("LONGUEUR :", len(chunk["text"]))
    print("=" * 70)
    print(chunk["text"])


# 5. Statistiques
lengths = [len(chunk["text"]) for chunk in chunks]

print("\nSTATISTIQUES DU CHUNKING")
print("Nombre de pages :", len(cleaned_documents))
print("Nombre de chunks :", len(chunks))
print("Taille moyenne :", round(sum(lengths) / len(lengths), 2))
print("Taille minimale :", min(lengths))
print("Taille maximale :", max(lengths))
print("Chunk supérieur à 1000 caractères :", sum(length > 1000 for length in lengths))
