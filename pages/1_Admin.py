# pages/1_Admin.py
import streamlit as st
import pandas as pd
import math
from modules.generer_donnees import generer_donnees
from modules.detecter_conflits import detecter_conflits
from modules.etape7_optimizer_pro import etape7_optimizer_pro
from modules.optimiseur import optimiseur

st.title("Administrateur - Génération et optimisation des surveillances")

# --- Étape 1 : Génération des données brutes ---
data = generer_donnees()

# Vérification des colonnes essentielles
required_cols_examens = ["id_examen","id_module","date_examen","heure_debut","duree_minutes"]
required_cols_profs = ["id_prof","nom","prenom","id_dept"]
required_cols_surveillances = ["id_examen","id_prof","id_salle"]

examens_df = data.get("examens", pd.DataFrame(columns=required_cols_examens))
profs_df = data.get("profs", pd.DataFrame(columns=required_cols_profs))
surveillances_df = data.get("surveillances", pd.DataFrame(columns=required_cols_surveillances))

for col in required_cols_examens:
    if col not in examens_df.columns:
        examens_df[col] = None
for col in required_cols_profs:
    if col not in profs_df.columns:
        profs_df[col] = None
for col in required_cols_surveillances:
    if col not in surveillances_df.columns:
        surveillances_df[col] = None

st.subheader("📊 Données importées")
st.write("Examens :", examens_df.shape[0], "lignes")
st.write("Professeurs :", profs_df.shape[0], "lignes")
st.write("Surveillances :", surveillances_df.shape[0], "lignes")

# --- Étape 2 : Détection des conflits ---
conflits = detecter_conflits(data)
st.subheader("⚠️ Conflits détectés")

# Conflits étudiants
st.markdown("### 🎓 Étudiants (max 1 examen/jour)")
if conflits["etudiants"].empty:
    st.success("Aucun conflit détecté.")
else:
    st.dataframe(conflits["etudiants"])

# Conflits professeurs
st.markdown("### 👨‍🏫 Professeurs (max 3 examens/jour)")
if conflits["profs"].empty:
    st.success("Aucun conflit détecté.")
else:
    st.dataframe(conflits["profs"])

# Conflits salles
st.markdown("### 🏫 Salles (capacité dépassée)")
if conflits["salles"].empty:
    st.success("Aucun conflit détecté.")
else:
    st.dataframe(conflits["salles"])

# --- Étape 3 : Optimisation intermédiaire ---
examens_list, profs_list, prof_dept, exam_dept_map, exam_dates = etape7_optimizer_pro(data)
st.subheader("🛠️ Optimisation intermédiaire")
st.write("Données préparées pour l'optimisation finale.")

# --- Étape 4 : Optimisation finale ---
optimiseur_input = {
    "examens_list": examens_list,
    "profs_list": profs_list,
    "prof_dept": prof_dept,
    "exam_dept_map": exam_dept_map,
    "exam_dates": exam_dates,
    "data": data
}

df_result = optimiseur(optimiseur_input)

# --- AJOUT DES COLONNES SUPPLÉMENTAIRES AVANT LES COLONNES EXISTANTES ---
if not df_result.empty:

    # Modules
    if "modules" in data:
        df_result = df_result.merge(
            data["modules"][["id_module","libelle"]],
            left_on="identifiant_module",
            right_on="id_module",
            how="left"
        )
        df_result = df_result.rename(columns={"libelle":"Nom module"})
    else:
        df_result["Nom module"] = None

    # Groupes
    if "groupes" in data:
        df_result = df_result.merge(
            data["groupes"][["id_groupe","nom"]],
            left_on="identifiant_session",
            right_on="id_groupe",
            how="left"
        )
        df_result = df_result.rename(columns={"nom":"Nom_groupe"})
    else:
        df_result["Nom_groupe"] = None

    # Départements
    if "departements" in data:
        df_result = df_result.merge(
            data["departements"][["id_dept","nom"]],
            on="id_dept",
            how="left"
        )
        df_result = df_result.rename(columns={"nom":"Nom_departement"})
    else:
        df_result["Nom_departement"] = None

    # Formations
    if "formations" in data:
        df_result = df_result.merge(
            data["formations"][["id_formation","nom"]],
            on="id_formation",
            how="left"
        )
        df_result = df_result.rename(columns={"nom":"Nom_formation"})
    else:
        df_result["Nom_formation"] = None

    # Renommer les colonnes existantes
    df_result = df_result.rename(columns={
        "identifiant_module": "ID module",
        "identifiant_session": "ID session",
        "date_examen": "Date",
        "heure_debut": "Heure",
        "duree_minutes": "Durée (min)",
        "etat_examen": "État examen",
        "id_salle": "ID salle",
        "nb_etudiants": "Nb étudiants",
        "capacité_examen": "Capacité salle",
        "type_salle": "Type salle",
        "bloc": "Bloc"
    })

# --- Fonction pour répartir les étudiants selon la capacité ---
def repartir_salles(df):
    nouvelles_lignes = []

    for idx, row in df.iterrows():
        nb_etudiants = row["Nb étudiants"]
        capacite = row["Capacité salle"]

        if nb_etudiants > capacite and capacite > 0:
            nb_groupes = math.ceil(nb_etudiants / capacite)
            etudiants_par_groupe = math.ceil(nb_etudiants / nb_groupes)

            for i in range(nb_groupes):
                nouvelle_ligne = row.copy()
                nouvelle_ligne["Nb étudiants"] = etudiants_par_groupe
                nouvelle_ligne["ID salle"] = f"{row['ID salle']}_{i+1}"  # Identifiant de salle temporaire
                nouvelles_lignes.append(nouvelle_ligne)
        else:
            nouvelles_lignes.append(row)

    return pd.DataFrame(nouvelles_lignes)

# --- Étape 5 : Affichage corrigé et mise à jour ---
if st.button("💾 Mettre à jour la base avec le planning optimisé"):
    if df_result.empty:
        st.warning("Aucun résultat à mettre à jour.")
    else:
        # Appliquer la répartition des salles
        df_corrige = repartir_salles(df_result)

        st.subheader("📊 Planning corrigé selon capacité des salles")
        st.dataframe(df_corrige)

        # Mise à jour dans la base
        from utils.queries import execute_update
        execute_update(df_corrige, table="surveillances")
        st.success("La base a été mise à jour avec succès !")
