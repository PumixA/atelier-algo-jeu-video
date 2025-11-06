from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "Serveur de l'atelier algo en ligne 🎮"})

@app.route("/ping-db")
def ping_db():
    try:
        conn = psycopg2.connect(
            dbname="algo_db",
            user="postgres",
            password="postgres",
            host="db",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"db_time": result[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
