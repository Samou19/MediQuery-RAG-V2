import os
import time

import requests
import streamlit as st
from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2 import id_token

# ==================================================
# CONFIGURATION
# ==================================================

API_URL = os.getenv("API_URL", "http://localhost:8000")
USE_CLOUD_AUTH = os.getenv("USE_CLOUD_AUTH", "false").lower() == "true"

st.set_page_config(
    page_title="MediQuery V2",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# STYLE CSS
# ==================================================

st.markdown(
    """
    <style>
        .block-container {
            max-width: 1150px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .main-title {
            font-size: 2.2rem;
            font-weight: 750;
            color: #1E3A5F;
            margin-bottom: 0;
        }

        .subtitle {
            color: #64748b;
            font-size: 1rem;
            margin-top: 5px;
        }

        div[data-testid="stChatMessage"] {
            border-radius: 12px;
            padding: 1rem;
        }

        div[data-testid="stChatMessage"] h1 {
            font-size: 1.5rem !important;
        }

        div[data-testid="stChatMessage"] h2 {
            font-size: 1.25rem !important;
        }

        div[data-testid="stChatMessage"] h3 {
            font-size: 1.1rem !important;
        }

        .source-card {
            background-color: #F1F5F9;
            border-left: 4px solid #3B82F6;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
        }

        .disclaimer {
            font-size: 0.85rem;
            color: #64748b;
        }

        section[data-testid="stSidebar"] {
            border-right: 1px solid #e5e7eb;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0

if "total_response_time" not in st.session_state:
    st.session_state.total_response_time = 0.0


# ==================================================
# APPEL API FASTAPI
# ==================================================


def ask_mediquery(question: str) -> dict:
    """Envoie une question au backend FastAPI."""

    headers = {}

    # Authentification Google uniquement sur Cloud Run
    if USE_CLOUD_AUTH:
        token = id_token.fetch_id_token(
            GoogleAuthRequest(),
            API_URL,
        )

        headers["Authorization"] = f"Bearer {token}"

    response = requests.post(
        f"{API_URL}/chat/",
        json={"question": question},
        headers=headers,
        timeout=(10, 180),
    )

    response.raise_for_status()

    return response.json()


# ==================================================
# AFFICHAGE DES SOURCES
# ==================================================


def display_sources(sources: list):
    """Affiche les sources documentaires utilisées."""

    if not sources:
        st.info("Aucune source documentaire retournée.")
        return

    for index, source in enumerate(sources, start=1):
        filename = source.get("filename", "Document")
        page = source.get("page")
        chunk_id = source.get("chunk_id")
        score = source.get("score")

        with st.container(border=True):
            st.markdown(f"**Source {index} — {filename}**")

            col1, col2, col3 = st.columns(3)

            col1.caption(f"Page : {page if page is not None else 'Non renseignée'}")

            col2.caption(
                f"Chunk : {chunk_id if chunk_id is not None else 'Non renseigné'}"
            )

            if score is not None:
                col3.caption(f"Score : {score:.4f}")


# ==================================================
# AFFICHAGE DES PERFORMANCES
# ==================================================


def display_timings(timings: dict):
    """Affiche les temps de traitement du pipeline RAG."""

    if not timings:
        return

    st.markdown("**Temps de traitement**")

    total = timings.get("total")

    if total is not None:
        st.metric("Temps total", f"{total / 1000:.2f} s")

    with st.expander("Détail des performances"):
        for name, value in timings.items():
            st.write(f"**{name.replace('_', ' ').capitalize()} :** {value:.2f} ms")


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.title("🩺 MediQuery V2")

    st.caption("Assistant médical intelligent basé sur le RAG")

    st.divider()

    st.subheader("À propos")

    st.write(
        """
        MediQuery permet d'interroger une documentation
        médicale en langage naturel.

        Les réponses sont générées à partir du guide HAS
        sur le diabète de type 2.
        """
    )

    st.divider()

    st.subheader("Statistiques de session")

    st.metric(
        "Questions posées",
        st.session_state.total_questions,
    )

    st.metric(
        "Échanges",
        len(st.session_state.messages) // 2,
    )

    if st.session_state.total_questions > 0:
        average_time = (
            st.session_state.total_response_time / st.session_state.total_questions
        )

        st.metric(
            "Temps moyen de réponse",
            f"{average_time:.2f} s",
        )

    st.divider()

    if st.button(
        "🗑️ Nouvelle conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.total_questions = 0
        st.session_state.total_response_time = 0.0

        st.rerun()

    st.caption("Version 2.0.0")


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="main-title">MediQuery 🩺</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Votre assistant intelligent pour explorer la documentation médicale."
    "</div>",
    unsafe_allow_html=True,
)

st.divider()


# ==================================================
# AVERTISSEMENT MEDICAL
# ==================================================

with st.expander("⚠️ Informations importantes"):
    st.warning(
        """
        MediQuery est un projet expérimental à vocation pédagogique
        et technique.

        Il ne constitue pas un dispositif médical et ne remplace
        pas l'avis d'un professionnel de santé.
        """
    )


# ==================================================
# SUGGESTIONS DE QUESTIONS
# ==================================================

if not st.session_state.messages:
    st.subheader("Comment puis-je vous aider ?")

    st.write("Voici quelques exemples de questions :")

    suggestions = [
        "Quelles sont les étapes du parcours de soins du diabète de type 2 ?",
        "Quelles mesures hygiéno-diététiques sont recommandées ?",
        "Comment organiser le suivi du patient diabétique ?",
        "Quelles sont les principales complications du diabète de type 2 ?",
    ]

    cols = st.columns(2)

    for index, suggestion in enumerate(suggestions):
        with cols[index % 2]:
            if st.button(
                suggestion,
                key=f"suggestion_{index}",
                use_container_width=True,
            ):
                st.session_state.pending_question = suggestion
                st.rerun()


# ==================================================
# HISTORIQUE DES CONVERSATIONS
# ==================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            sources = message.get("sources", [])

            if sources:
                with st.expander("📚 Sources documentaires"):
                    display_sources(sources)

            timings = message.get("timings_ms", {})

            if timings:
                with st.expander("⏱️ Performances"):
                    display_timings(timings)


# ==================================================
# SAISIE DE LA QUESTION
# ==================================================

question = st.chat_input("Posez votre question sur le diabète de type 2...")

pending_question = st.session_state.pop(
    "pending_question",
    None,
)

if pending_question:
    question = pending_question


# ==================================================
# TRAITEMENT DE LA QUESTION
# ==================================================

if question:
    # Enregistrement de la question
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    st.session_state.total_questions += 1

    with st.chat_message("user"):
        st.markdown(question)

    # Appel du backend
    with st.chat_message("assistant"):
        with st.spinner("Analyse de votre question..."):
            start_time = time.perf_counter()

            try:
                result = ask_mediquery(question)

                elapsed_time = time.perf_counter() - start_time

                answer = result.get(
                    "answer",
                    "Aucune réponse disponible.",
                )

                sources = result.get("sources", [])
                timings = result.get("timings_ms", {})

                st.markdown(answer)

                # Sources
                if sources:
                    with st.expander(
                        "📚 Sources documentaires",
                        expanded=True,
                    ):
                        display_sources(sources)

                # Performances
                if timings:
                    with st.expander("⏱️ Performances"):
                        display_timings(timings)

                # Temps total mesuré côté frontend
                st.caption(f"Temps de traitement côté interface : {elapsed_time:.2f} s")

                # Mise à jour des statistiques
                st.session_state.total_response_time += elapsed_time

                # Sauvegarde de la réponse
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                        "timings_ms": timings,
                    }
                )

            except requests.exceptions.Timeout:
                error_message = (
                    "Le traitement a dépassé le délai autorisé. Veuillez réessayer."
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

            except requests.exceptions.ConnectionError:
                error_message = (
                    "Impossible de joindre l'API MediQuery. "
                    "Vérifiez que le backend FastAPI est démarré."
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

            except requests.exceptions.HTTPError as error:
                error_message = f"Erreur HTTP lors de l'appel à l'API : {error}"

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

            except (ValueError, TypeError):
                error_message = "La réponse reçue de l'API est invalide."

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

            except Exception:
                error_message = "Une erreur inattendue est survenue."

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )

    # Rafraîchissement des statistiques et de l'historique
    st.rerun()
