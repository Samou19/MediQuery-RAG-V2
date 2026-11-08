from pathlib import Path

from app.services.ingestion import extract_pdf

pdf_path = Path("data/raw/parcours_de_soins_diabete_type_2.pdf")

documents = extract_pdf(pdf_path)

print("Nombre de pages extraites :", len(documents))

# Vérifier les premières pages
for doc in documents[:5]:
    print("\n" + "=" * 60)
    print("PAGE :", doc["metadata"]["page"])
    print("=" * 60)
    print(doc["text"][:500])

# Vérifier les statistiques
total_chars = sum(len(doc["text"]) for doc in documents)

print("\nSTATISTIQUES")
print("Pages :", len(documents))
print("Caractères extraits :", total_chars)
print("Moyenne de caractères par page :", round(total_chars / len(documents), 2))
