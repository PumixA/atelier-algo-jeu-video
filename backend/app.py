from __future__ import annotations

import os
import sys
from flask import Flask, jsonify, request
import psycopg2

# --- chemin pour importer src/* peu importe le cwd ---
BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.partC_graphs import dijkstra, astar, detect_cycle_with_dsu
from src.partD_streaming import reservoir_sampling, CountMinSketch
from src.partE_security import sha256_text, sha256_file, BloomFilter

app = Flask(__name__)
try:
    app.json.ensure_ascii = False
except Exception:
    # Compat: si l'attribut n'existe pas (vieille version)
    from flask.json.provider import DefaultJSONProvider
    class UTF8JSONProvider(DefaultJSONProvider):
        def dumps(self, obj, **kwargs):
            kwargs.setdefault("ensure_ascii", False)
            return super().dumps(obj, **kwargs)
    app.json_provider_class = UTF8JSONProvider
    app.json = UTF8JSONProvider(app)

BLOOM = BloomFilter(m=2048, k=4)

# ---------- Utilitaires ----------
@app.get("/health")
def health():
    return jsonify({"status": "ok", "message": "Service en ligne"}), 200

@app.get("/")
def index():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "rule": str(rule),
            "methods": sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"}),
            "endpoint": rule.endpoint
        })
    return jsonify({
        "message": "Serveur de l'atelier algo en ligne 🎮",
        "routes_disponibles": routes
    }), 200

@app.route("/ping-db")
def ping_db():
    try:
        conn = psycopg2.connect(
            dbname="algo_db", user="postgres", password="postgres",
            host="db", port="5432"
        )
        with conn, conn.cursor() as cur:
            cur.execute("SELECT NOW();")
            result = cur.fetchone()
        return jsonify({"db_time": str(result[0])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- PARTIE C : Pathfinding ----------
@app.post("/pathfinding")
def pathfinding():
    try:
        data = request.get_json(force=True)
        grid = data["grid"]
        start = tuple(data["start"])
        goal = tuple(data["goal"])
        algo = data.get("algorithm", "dijkstra").lower()

        if algo == "astar":
            dist, path, explored = astar(grid, start, goal)
            algo_name = "A*"
        else:
            dist, path, explored = dijkstra(grid, start, goal)
            algo_name = "Dijkstra"

        if dist == float("inf") or not path:
            return jsonify({
                "message": "Aucun chemin possible sur cette carte.",
                "algorithm": algo_name,
                "distance": None,
                "path_length": 0,
                "explored_nodes": explored
            }), 200

        return jsonify({
            "message": "Chemin trouvé avec succès.",
            "algorithm": algo_name,
            "distance": dist,
            "path_length": len(path),
            "explored_nodes": explored,
            "path": path
        }), 200
    except Exception as e:
        return jsonify({"message": "Erreur interne (pathfinding).", "error": str(e)}), 500

# ---------- PARTIE C : Détection de cycle ----------
@app.post("/guilds/cycle")
def guilds_cycle():
    try:
        data = request.get_json(force=True)
        n = int(data["n"])
        edges = [tuple(e) for e in data["edges"]]
        has_cycle = detect_cycle_with_dsu(edges, n)
        return jsonify({
            "message": "Cycle détecté." if has_cycle else "Aucun cycle détecté.",
            "has_cycle": has_cycle
        }), 200
    except Exception as e:
        return jsonify({"message": "Erreur interne (guilds/cycle).", "error": str(e)}), 500

# ---------- PARTIE D : Reservoir Sampling ----------

@app.post("/reservoir")
def reservoir_route():
    """
    Body JSON attendu:
    {
      "stream": [ .. liste de valeurs .. ],
      "k": 3,
      "seed": 42   # optionnel (entier)
    }
    """
    try:
        data = request.get_json(force=True)
        stream = data["stream"]
        k = int(data["k"])
        seed = data.get("seed", None)
        sample = reservoir_sampling(stream, k, seed)
        return jsonify({
            "message": "Échantillon généré.",
            "n": len(stream),
            "k": k,
            "sample": sample
        }), 200
    except KeyError as e:
        return jsonify({"message": "Requête invalide.", "error": f"Champ manquant: {e}"}), 400
    except Exception as e:
        return jsonify({"message": "Erreur interne (reservoir).", "error": str(e)}), 500


# ---------- PARTIE D : Count-Min Sketch ----------

@app.post("/cms")
def cms_route():
    """
    Body JSON attendu (exemple):
    {
      "depth": 5,
      "width": 200,
      "adds": [["pikachu", 3], ["bulbasaur", 1], ["pikachu", 2]],
      "queries": ["pikachu", "mew"]
    }

    - Crée un CMS en mémoire (stateless par requête),
      applique les 'adds', puis renvoie les estimations pour 'queries'.
    """
    try:
        data = request.get_json(force=True)
        depth = int(data.get("depth", 5))
        width = int(data.get("width", 200))
        adds = data.get("adds", [])         # liste de [key, count]
        queries = data.get("queries", [])   # liste de clés

        cms = CountMinSketch(depth, width)
        for pair in adds:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                return jsonify({"message": "Requete invalide.", "error": "Chaque 'adds' doit être [key, count]."}), 400
            key, count = pair
            cms.add(str(key), int(count))

        estimates = {}
        for q in queries:
            estimates[str(q)] = cms.estimate(str(q))

        return jsonify({
            "message": "Estimations CMS calculées.",
            "depth": depth,
            "width": width,
            "added": len(adds),
            "estimated": estimates
        }), 200
    except Exception as e:
        return jsonify({"message": "Erreur interne (cms).", "error": str(e)}), 500


# ---------- E1 : SHA-256 (texte ou fichier) ----------

@app.post("/sha256")
def sha256_route():
    """
    Deux modes:
    1) JSON: { "text": "bonjour", "salt": "pepper" }
    2) multipart/form-data: file=@monfichier.bin ; (salt optionnel)
    """
    try:
        # multipart (fichier) ?
        if "file" in request.files:
            fileobj = request.files["file"]
            salt = request.form.get("salt", "")
            # limite optionnelle (5 Mo)
            if request.content_length and request.content_length > 5 * 1024 * 1024:
                return jsonify({"message": "Fichier trop volumineux (max 5 Mo)."}), 413
            hexa = sha256_file(fileobj, salt)
            return jsonify({
                "message": "Empreinte SHA-256 calculée (fichier).",
                "hash": hexa
            }), 200

        # JSON (texte)
        data = request.get_json(force=True)
        text = data.get("text", "")
        salt = data.get("salt", "")
        if text == "":
            return jsonify({"message": "Requête invalide.", "error": "Champ 'text' requis."}), 400
        hexa = sha256_text(text, salt)
        return jsonify({
            "message": "Empreinte SHA-256 calculée (texte).",
            "hash": hexa
        }), 200

    except Exception as e:
        return jsonify({"message": "Erreur interne (sha256).", "error": str(e)}), 500


# ---------- E2 : Bloom Filter (global en mémoire) ----------

@app.post("/bloom/add")
def bloom_add_route():
    """
    JSON attendu:
    {
      "items": ["pikachu", "bulbasaur"],
      "reset": false,      # optionnel: True pour réinitialiser
      "m": 4096,           # optionnel: redimensionner (si reset=true)
      "k": 5               # optionnel: changer nb de hash (si reset=true)
    }
    """
    try:
        data = request.get_json(force=True)
        items = data.get("items", [])
        reset = bool(data.get("reset", False))

        global BLOOM
        # reset demandé ?
        if reset:
            m = int(data.get("m", 2048))
            k = int(data.get("k", 4))
            BLOOM = BloomFilter(m=m, k=k)

        if not isinstance(items, list):
            return jsonify({"message": "Requête invalide.", "error": "items doit être une liste."}), 400

        BLOOM.add_many(items)
        return jsonify({
            "message": "Éléments ajoutés au filtre de Bloom.",
            "added": items,
            "m": BLOOM.m,
            "k": BLOOM.k
        }), 200

    except Exception as e:
        return jsonify({"message": "Erreur interne (bloom/add).", "error": str(e)}), 500


@app.post("/bloom/check")
def bloom_check_route():
    """
    JSON attendu:
    {
      "items": ["pikachu", "mew"]
    }
    """
    try:
        data = request.get_json(force=True)
        items = data.get("items", [])
        if not isinstance(items, list):
            return jsonify({"message": "Requête invalide.", "error": "items doit être une liste."}), 400

        results = BLOOM.check_many(items)
        present = {str(k): bool(v) for k, v in zip(items, results)}
        return jsonify({
            "message": "Vérification effectuée (présence probable).",
            "present": present,
            "m": BLOOM.m,
            "k": BLOOM.k
        }), 200

    except Exception as e:
        return jsonify({"message": "Erreur interne (bloom/check).", "error": str(e)}), 500



# ---------- Lancement unique ----------
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")        # docker-compose mettra HOST=0.0.0.0
    port = int(os.getenv("PORT", "5000"))        # local par défaut 5000 (évite conflit 8000)
    app.run(host=host, port=port, debug=False)
