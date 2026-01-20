import os
import psycopg2
from urllib.parse import urlparse

def get_conn():
    """
    Retourne une connexion PostgreSQL.
    Fonctionne en local (localhost) ou sur Render (DATABASE_URL).
    """
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        # Valeur locale pour tests
        DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/exams_db"

    result = urlparse(DATABASE_URL)
    try:
        conn = psycopg2.connect(
            dbname=result.path[1:],  # ignore le slash initial
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    except Exception as e:
        print("❌ Erreur de connexion à PostgreSQL :", e)
        raise
