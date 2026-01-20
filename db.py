import os
import psycopg2
from urllib.parse import urlparse

def get_conn():
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        # Valeur par défaut locale pour tests
        DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/exams_db"

    result = urlparse(DATABASE_URL)
    return psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
