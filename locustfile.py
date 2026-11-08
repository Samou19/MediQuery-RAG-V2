from locust import HttpUser, between, task


class MediQueryUser(HttpUser):
    # Temps d'attente entre deux requêtes : 2 à 5 secondes
    wait_time = between(2, 5)

    @task
    def ask_question(self):

        payload = {
            "question": (
                "Quelles sont les étapes du parcours de soins du diabète de type 2 ?"
            )
        }

        with self.client.post(
            "/chat/", json=payload, name="/chat/", catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Erreur HTTP : {response.status_code}")
                return

            try:
                data = response.json()

                if data.get("status") != "success":
                    response.failure("Statut API différent de success")

                elif not data.get("answer"):
                    response.failure("Réponse vide")

                else:
                    response.success()

            except ValueError:
                response.failure("Réponse JSON invalide")
