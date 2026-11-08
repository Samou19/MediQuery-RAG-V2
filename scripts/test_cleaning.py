from app.services.ingestion import extract_pdf
from app.services.text_cleaning import clean_documents

# Extraction du PDF
documents = extract_pdf("data/raw/parcours_de_soins_diabete_type_2.pdf")

# Nettoyage
cleaned_documents = clean_documents(documents)

# Afficher les premières pages
for document in cleaned_documents[:5]:
    print("\n" + "=" * 60)
    print("PAGE :", document["metadata"]["page"])
    print("=" * 60)
    print(document["text"][:1000])

# Statistiques
total_chars = sum(len(document["text"]) for document in cleaned_documents)

print("\nSTATISTIQUES APRÈS NETTOYAGE")
print("Pages conservées :", len(cleaned_documents))
print("Caractères :", total_chars)
print(
    "Moyenne de caractères par page :", round(total_chars / len(cleaned_documents), 2)
)
