import streamlit as st
from db import get_conn

st.set_page_config(page_title="EDT Examens", layout="wide")
st.title("📅 Système d’Optimisation des Examens")

# Test connexion DB
try:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    st.success("Connexion à PostgreSQL OK")
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Erreur DB : {e}")

st.markdown("""
### Acteurs disponibles
- Administrateur
- Vice-Doyen
- Chef de Département
- Étudiant/Professeur
""")
