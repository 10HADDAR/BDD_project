import psycopg2

def get_conn():
    return psycopg2.connect(
        host="localhost",
        database="exams_db",
        user="postgres",
        password="postgres",  # ⚠️ PAS D’ACCENTS
        port="5432",
        options="-c client_encoding=UTF8"
    )
