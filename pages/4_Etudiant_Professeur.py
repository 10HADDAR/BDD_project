import streamlit as st
from modules.generer_donnees import generer_donnees
import pandas as pd

st.title("Étudiant / Professeur - Consultation planning personnalisé")

# --- Génération des données ---
data = generer_donnees()

# --- Vérification des colonnes essentielles ---
required_cols_surveillances = ["id_examen", "id_prof", "id_salle"]
if "surveillances" in data:
    surveillances = data["surveillances"]
else:
    surveillances = pd.DataFrame(columns=required_cols_surveillances)

for col in required_cols_surveillances:
    if col not in surveillances.columns:
        st.warning(f"La colonne '{col}' est manquante dans la table surveillances. Les données pourraient être incomplètes.")
        surveillances[col] = None

# --- Choix de rôle ---
role = st.radio("Je suis :", ["Étudiant", "Professeur"])

# --- ETUDIANT ---
if role == "Étudiant":
    if "inscriptions" not in data or data["inscriptions"].empty:
        st.warning("⚠️ Aucune inscription trouvée.")
    else:
        etudiants = data["inscriptions"]["id_etudiant"].unique()
        etu_select = st.selectbox("Saisir votre Id", etudiants)

        modules_etu = data["inscriptions"][data["inscriptions"]["id_etudiant"] == etu_select]

        if "examens" in data:
            modules_etu = modules_etu.merge(data["examens"], on="id_module", how="left")
        else:
            for col in ["date_examen","heure_debut","duree_minutes","id_examen"]:
                modules_etu[col] = None

        if "modules" in data:
            modules_etu = modules_etu.merge(data["modules"][["id_module","libelle"]], on="id_module", how="left")
        else:
            modules_etu["libelle"] = None

        # ✅ CORRECTION ICI : une seule salle par examen
        if not surveillances.empty:
            surveillances_unique = surveillances.drop_duplicates(subset=["id_examen"])
            modules_etu = modules_etu.merge(
                surveillances_unique[["id_examen","id_salle"]],
                on="id_examen",
                how="left"
            )
        else:
            modules_etu["id_salle"] = None

        if "salles" in data:
            modules_etu = modules_etu.merge(data["salles"][["id_salle","nom"]], on="id_salle", how="left")
        else:
            modules_etu["nom"] = None

        # Renommer les colonnes pour l'affichage
        modules_etu_affichage = modules_etu.rename(columns={
            "libelle": "Nom module",
            "date_examen": "Date",
            "heure_debut": "Heure",
            "duree_minutes": "Durée (min)",
            "nom": "Salle"
        })

        st.subheader("📅 Planning étudiant")
        st.dataframe(modules_etu_affichage[["id_module","Nom module","Date","Heure","Durée (min)","Salle"]])

# --- PROFESSEUR ---
else:
    if surveillances.empty or "profs" not in data or data["profs"].empty:
        st.warning("⚠️ Aucun planning de surveillances trouvé pour les professeurs.")
    else:
        profs = data["profs"][["id_prof","nom","prenom"]].copy()
        profs["full_name"] = profs["prenom"] + " " + profs["nom"]
        prof_select = st.selectbox("Saisir votre full name ", profs["full_name"])

        id_prof = profs[profs["full_name"] == prof_select]["id_prof"].values[0]

        planning_prof = surveillances[surveillances["id_prof"] == id_prof]

        if "examens" in data:
            planning_prof = planning_prof.merge(data["examens"], on="id_examen", how="left")
        else:
            for col in ["id_module","date_examen","heure_debut","duree_minutes"]:
                planning_prof[col] = None

        if "modules" in data:
            planning_prof = planning_prof.merge(data["modules"][["id_module","libelle"]], on="id_module", how="left")
        else:
            planning_prof["libelle"] = None

        if "salles" in data:
            planning_prof = planning_prof.merge(data["salles"][["id_salle","nom"]], on="id_salle", how="left")
        else:
            planning_prof["nom"] = None

        # Renommer les colonnes pour l'affichage
        planning_prof_affichage = planning_prof.rename(columns={
            "libelle": "Nom module",
            "date_examen": "Date",
            "heure_debut": "Heure",
            "duree_minutes": "Durée (min)",
            "nom": "Salle"
        })

        st.subheader("📅 Planning professeur")
        st.dataframe(planning_prof_affichage[["id_examen","Nom module","Date","Heure","Durée (min)","Salle"]])