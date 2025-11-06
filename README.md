# 🎮 Atelier d’Algorithmique — Thème : Jeu Vidéo en Ligne

Ce projet sert de support à l’atelier d’algorithmique (M1) autour du thème **“Optimiser et sécuriser les données d’un jeu multijoueur”**.  
Il contient plusieurs modules (recherche, tri, graphes, streaming, sécurité) et une base de données Docker PostgreSQL.

---

## 🧱 Structure du projet

```

atelier-algo-jeu-video/
│
├── backend/
│   ├── app.py                # Serveur Flask principal
│   ├── requirements.txt      # Dépendances Python
│   └── src/                  # Modules d'exercices
│       ├── partA_text_search.py
│       ├── partB_selection.py
│       ├── partC_graphs.py
│       ├── partD_streaming.py
│       └── partE_security.py
│
├── docker-compose.yml        # Lancement Docker (Postgres + Flask)
├── Dockerfile                # Image du backend
└── README.md

````

---

## 🚀 Installation rapide

### 1️⃣ Prérequis

Assurez-vous d’avoir installé :
- **Docker** et **Docker Compose**
- **Git**
- **Python 3.11+** (si vous souhaitez exécuter le code localement sans Docker)

---

### 2️⃣ Cloner le projet

```bash
git clone git@github.com:PumixA/atelier-algo-jeu-video.git
cd atelier-algo-jeu-video
````

---

### 3️⃣ Lancer l’environnement Docker

```bash
docker compose up -d
```

💡 Cela lance :

* une base PostgreSQL (`algo_db`) sur le port `5433`
* un serveur Flask sur le port `8000`

---

### 4️⃣ Vérifier que tout fonctionne

Test du serveur :

```bash
curl http://localhost:8000
```

➡️ Réponse attendue :

```json
{"message": "Serveur de l'atelier algo en ligne 🎮"}
```

Test de la base :

```bash
curl http://localhost:8000/ping-db
```

➡️ Réponse attendue :

```json
{"db_time": "2025-11-06T13:42:17.123456"}
```

---

### 5️⃣ (Optionnel) Lancer les algorithmes localement

Depuis le dossier `backend/` :

```bash
pip install -r requirements.txt
python src/partA_text_search.py
```

Chaque fichier Python contient un **mini-exemple testable** et peut être lancé indépendamment.

---

## 👥 Répartition du travail (binôme)

| Étudiant         | Modules  | Domaines couverts                            |
| ---------------- | -------- | -------------------------------------------- |
| 🧑‍💻 **Melvin** | A & B    | Recherche de texte, top-K, fenêtre glissante |
| 👩‍💻 **Binôme** | C, D & E | Graphes, streaming, sécurité & intégrité     |

---

## 🔧 Commandes utiles

| Commande                   | Action                                |
| -------------------------- | ------------------------------------- |
| `docker compose up -d`     | Lance les conteneurs (base + serveur) |
| `docker compose down`      | Stoppe et supprime les conteneurs     |
| `docker ps`                | Liste les conteneurs actifs           |
| `docker logs algo_backend` | Affiche les logs du serveur Flask     |
| `git pull origin main`     | Met à jour le projet                  |
| `git push origin main`     | Envoie les changements sur GitHub     |

---

## 🧩 Objectif du projet

Mettre en pratique les grands algorithmes :

* **Recherche de motifs (KMP, Z, Rabin–Karp)**
* **Sélection et tri (Top-K, quickselect)**
* **Graphes et chemins (Dijkstra, A*)**
* **Streaming et comptage probabiliste (Reservoir Sampling, Count–Min Sketch)**
* **Sécurité et intégrité (SHA-256, Bloom Filter)**

Le tout appliqué à un univers cohérent : **un jeu multijoueur en ligne**.

---

## 🧠 Auteur

Projet réalisé dans le cadre du cours d’algorithmique (M1 — Xavier Quesnot)
👤 **Melvin Delorme (@PumixA)** — Étudiant en développement web