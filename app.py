import streamlit as st
from db import get_conn
import pandas as pd

st.set_page_config(page_title="EDT Examens", layout="wide")
st.title("📅 Système d’Optimisation des Examens")

st.markdown("""
### Acteurs disponibles
- Administrateur
- Vice-Doyen
- Chef de Département
- Étudiant/Professeur
""")

# Exemple : afficher la liste des examens depuis PostgreSQL
def load_examens():
    conn = get_conn()
    try:
        df = pd.read_sql("SELECT * FROM examens;", conn)
        return df
    except Exception as e:
        st.error(f"Impossible de charger les examens : {e}")
        return pd.DataFrame()
    finally:
        conn.close()

if st.checkbox("Afficher les examens"):
    df_examens = load_examens()
    st.dataframe(df_examens)
