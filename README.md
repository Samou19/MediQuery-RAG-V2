# MediQuery V2 — Assistant médical intelligent basé sur le RAG

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Qdrant](https://img.shields.io/badge/Vector_DB-Qdrant-red)
![Claude](https://img.shields.io/badge/LLM-Claude-orange)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-Cloud_Run-4285F4)
![Status](https://img.shields.io/badge/Status-Deployed-success)

MediQuery est un assistant médical intelligent permettant d'interroger une documentation médicale en langage naturel et d'obtenir des réponses contextualisées, accompagnées de leurs sources.

Basé sur une architecture **Retrieval-Augmented Generation (RAG)**, le projet combine recherche hybride, reranking et génération par LLM pour améliorer la pertinence et la traçabilité des réponses.

Le corpus documentaire utilisé est le guide HAS 2025 consacré au parcours de soins du patient adulte vivant avec un diabète de type 2.

## 🎯 Objectifs

- Interroger des documents médicaux en langage naturel.
- Retrouver les passages documentaires les plus pertinents.
- Générer des réponses contextualisées avec Claude.
- Citer les documents et pages sources.
- Signaler lorsque les informations disponibles sont insuffisantes.

## ⚙️ Architecture RAG

MediQuery V2 repose sur deux pipelines complémentaires :

### 1. Pipeline d'indexation documentaire (Offline)

```text
       Document PDF (HAS)
              |
              v
      Extraction du texte
            PyMuPDF
              |
              v
       Nettoyage du texte
              |
              v
           Chunking
    Découpage en segments
              |
              v
      Génération d'embeddings
      Voyage AI (voyage-4-lite)
              |
              v
          Indexation
            Qdrant
```

### 2. Pipeline de recherche et génération (Online)

```text
       Question utilisateur
              |
        +-----+-----+
        |           |
        v           v
   Dense Search  Sparse Search
   Voyage AI         BM25
        |           |
        +-----+-----+
              |
              v
          Fusion RRF
              |
              v
           Reranking
           Voyage AI
              |
              v
     Construction du contexte
              |
              v
       Prompt Engineering
              |
              v
          Claude API
              |
              v
      Réponse contextualisée
         + Sources citées
```

**Technologies clés :** PyMuPDF, Voyage AI, Qdrant, BM25, RRF, FastAPI et Anthropic Claude.

## 🚀 Fonctionnalités

- **Ingestion documentaire :** extraction, nettoyage et découpage des PDF.
- **Dense Retrieval :** recherche sémantique avec embeddings.
- **Sparse Retrieval :** recherche lexicale avec BM25.
- **Hybrid Search :** fusion des résultats avec Reciprocal Rank Fusion (RRF).
- **Reranking :** réorganisation des passages avec Voyage AI.
- **Génération contrôlée :** réponses contextualisées avec Claude.
- **Traçabilité :** références aux documents et pages sources.
- **Évaluation :** benchmark des performances de recherche.
- **API REST :** exposition du pipeline RAG avec FastAPI.
- **Interface conversationnelle :** application Streamlit avec historique et statistiques de session.

## 🛠️ Stack technique

| Domaine | Technologies |
|---|---|
| Langage | Python 3.12 |
| LLM | Anthropic Claude |
| Embeddings | Voyage AI |
| Vector Database | Qdrant Cloud |
| Recherche lexicale | BM25 |
| Recherche hybride | RRF |
| Reranking | Voyage AI |
| Backend | FastAPI |
| Frontend | Streamlit |
| Tests | Pytest, Locust |
| Conteneurisation | Docker |
| CI / Déploiement | Google Cloud Build |
| Infrastructure Cloud | Google Cloud Run |
| Gestion des secrets | Google Secret Manager |
| Monitoring | Prometheus, Grafana |

## ☁️ Déploiement sur Google Cloud Run

MediQuery V2 est conteneurisé avec Docker et déployé sur **Google Cloud Platform (GCP)** à l'aide de Google Cloud Run.

L'architecture de déploiement sépare le frontend et le backend afin d'assurer une meilleure isolation des responsabilités et de sécuriser les communications entre les services.

### 1. Architecture de déploiement

```text
                 UTILISATEUR
                      |
                      v
          +-------------------------+
          |       FRONTEND          |
          |       Streamlit         |
          |                         |
          |      Cloud Run          |
          |   mediquery-frontend    |
          |                         |
          |   Accès public HTTPS    |
          +------------+------------+
                       |
                       | HTTPS
                       | Identity Token
                       v
          +-------------------------+
          |        BACKEND          |
          |        FastAPI          |
          |                         |
          |       Cloud Run        |
          |     mediquery-api      |
          |                         |
          |     Accès privé         |
          +------------+------------+
                       |
             +---------+---------+
             |         |         |
             v         v         v
          Qdrant    Voyage AI   Claude
          Cloud       API        API

                       |
                       v
          +-------------------------+
          |    SECRET MANAGER       |
          |                         |
          | QDRANT_CLOUD_API_KEY    |
          | VOYAGE_API_KEY          |
          | ANTHROPIC_API_KEY       |
          +-------------------------+
```

### 2. Services Google Cloud utilisés

| Service | Rôle |
|---|---|
| Google Cloud Run | Hébergement du frontend et du backend |
| Google Cloud Build | Construction des images Docker |
| Artifact Registry | Stockage des images Docker |
| Secret Manager | Stockage sécurisé des clés API |
| IAM | Gestion des identités et permissions |
| Cloud Logging | Consultation des logs et diagnostic |

### 3. Séparation des services

Deux services Cloud Run indépendants sont déployés :

**Frontend — `mediquery-frontend`**
- Application Streamlit.
- Accessible publiquement via HTTPS.
- Communique avec le backend via une API REST.
- Utilise un jeton d'identité Google pour authentifier les appels.

**Backend — `mediquery-api`**
- API FastAPI exposant le pipeline RAG.
- Service privé, non accessible anonymement.
- Accès autorisé au compte de service du frontend via le rôle `roles/run.invoker`.
- Connexion à Qdrant Cloud et aux API Voyage AI et Anthropic.

### 4. Gestion des secrets et sécurité

Les clés API ne sont pas intégrées dans l'image Docker ni exposées dans le code source.

Elles sont stockées dans Google Secret Manager et injectées dans le backend au démarrage des révisions Cloud Run.

Les comptes de service sont séparés :

- `mediquery-frontend` : autorisé à invoquer uniquement le backend.
- `mediquery-backend` : autorisé à accéder aux secrets nécessaires au fonctionnement du pipeline RAG.

Cette séparation repose sur le principe du moindre privilège (Least Privilege).

### 5. Déploiement continu

Le processus de déploiement repose sur les étapes suivantes :

1. Construction de l'image Docker.
2. Publication de l'image dans Artifact Registry via Cloud Build.
3. Déploiement du backend FastAPI sur Cloud Run.
4. Configuration des variables d'environnement et des secrets.
5. Attribution des permissions IAM entre les services.
6. Déploiement du frontend Streamlit sur Cloud Run.
7. Vérification du fonctionnement et consultation des logs Cloud Logging.

**Région de déploiement :** `europe-west1`

## 📊 Résultats

### Corpus documentaire

- 1 document médical de référence (HAS, 2025).
- 113 pages.
- 420 chunks indexés dans Qdrant.
- Embeddings de dimension 1 024.

### Benchmark de recherche

| Méthode | Recall@5 | MRR@5 | nDCG@5 |
|---|---:|---:|---:|
| Dense Retrieval | 0.7133 | 0.7500 | 0.6627 |
| BM25 | 0.3783 | 0.3833 | 0.3113 |
| RRF | 0.7067 | 0.6533 | 0.5953 |
| **RRF + Reranking** | **0.8050** | **0.7750** | **0.7504** |

Le pipeline RRF + Reranking obtient les meilleurs résultats sur les trois métriques évaluées.

*Benchmark réalisé sur un jeu de 10 questions annotées. Résultats indicatifs, non représentatifs d'une validation médicale.*

### Tests

- 5 tests fonctionnels réussis.
- 0 % d'échec observé lors des tests de charge à 5 et 10 utilisateurs.
- Déploiement fonctionnel sur Google Cloud Run.

## 🖥️ Démonstration

**Application en ligne :**

[Accéder à MediQuery V2](https://mediquery-frontend-891727482225.europe-west1.run.app)

*Captures d'écran à ajouter :*

<!-- Remplacer les chemins par les captures du dépôt -->
<!-- ![Interface MediQuery](docs/images/interface.png) -->
<!-- ![Réponse et sources](docs/images/reponse_sources.png) -->
<!-- ![Benchmark RAG](docs/images/benchmark.png) -->

## ⚠️ Avertissement médical

MediQuery est un projet expérimental à vocation pédagogique et technique. Il ne constitue pas un dispositif médical et ne remplace pas l'avis d'un professionnel de santé.

## 👨‍💻 Auteur

**Data Scientist / AI Engineer**

Projet personnel de mise en pratique des architectures RAG, de la recherche hybride, des bases vectorielles et de l'intégration des LLM dans une application IA.
