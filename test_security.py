from app.core.security import validate_api_keys

try:
    validate_api_keys()
    print("Validation des clés API réussie.")

except ValueError as error:
    print(f"Erreur : {error}")
