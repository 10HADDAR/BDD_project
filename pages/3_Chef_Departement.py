import streamlit as st
from utils.queries import fetch_df

st.title("Planning des Examens - Chef de Département")

# Liste des départements
departements_df = fetch_df("SELECT nom FROM departements ORDER BY nom")
liste_departements = ["Tous"] + departements_df['nom'].tolist()
dept = st.selectbox("Choisissez un département :", liste_departements)

# Requête dynamique
if dept == "Tous":
    query = """
    SELECT d.nom AS departement, m.libelle AS module, e.date_examen, e.heure_debut
    FROM examens e
    JOIN modules m ON m.id_module = e.id_module
    JOIN formations f ON f.id_formation = m.id_formation
    JOIN departements d ON d.id_dept = f.id_dept
    ORDER BY d.nom, e.date_examen, e.heure_debut
    """
    df = fetch_df(query)
else:
    query = """
    SELECT d.nom AS departement, m.libelle AS module, e.date_examen, e.heure_debut
    FROM examens e
    JOIN modules m ON m.id_module = e.id_module
    JOIN formations f ON f.id_formation = m.id_formation
    JOIN departements d ON d.id_dept = f.id_dept
    WHERE d.nom ILIKE %s
    ORDER BY e.date_examen, e.heure_debut
    """
    df = fetch_df(query, (f"%{dept}%",))

st.dataframe(df)

# Graphique : nombre d'examens par jour
st.subheader("Nombre d'examens par jour")
df_count = df.groupby("date_examen").size().reset_index(name="nb_examens")
st.bar_chart(df_count.set_index("date_examen"))
