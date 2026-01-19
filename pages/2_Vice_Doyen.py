# pages/2_Vice_Doyen.py
import streamlit as st
from modules.generer_donnees import generer_donnees
from modules.detecter_conflits import detecter_conflits
import pandas as pd

st.title("Vice-Doyen / Doyen - Vue stratégique globale")

data = generer_donnees()
conflits = detecter_conflits(data)

st.subheader("📊 KPI globaux")
st.write("Nombre de conflits étudiants :", len(conflits["etudiants"]))
st.write("Nombre de conflits professeurs :", len(conflits["profs"]))
st.write("Nombre de conflits salles :", len(conflits["salles"]))

# Occupation globale des salles
examens = data["examens"].merge(data["examen_salles"], on="id_examen").merge(data["salles"], on="id_salle")
occupation = examens.groupby(["nom", "date_examen"]).size().reset_index(name="nb_examens")
st.write("Occupation des salles")
st.dataframe(occupation)
