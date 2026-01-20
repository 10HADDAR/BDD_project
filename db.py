import os
import psycopg2

def get_conn():
    return psycopg2.connect(os.environ["postgresql://exams_db_user:9Rob3mujL5dIt5G2ze7GOG8lCAoqCVYd@dpg-d5nd24hr0fns73fgrgbg-a/exams_db"])