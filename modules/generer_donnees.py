# generer_donnees.py
import pandas as pd
from utils.queries import fetch_df

def generer_donnees():
    """Récupère toutes les données nécessaires depuis la base SQL"""
    
    examens_df = fetch_df("SELECT * FROM examens")
    profs_df = fetch_df("SELECT * FROM professeurs")
    salles_df = fetch_df("SELECT * FROM salles")
    inscriptions_df = fetch_df("SELECT * FROM inscriptions")
    examen_salles_df = fetch_df("SELECT * FROM examen_salles")
    modules_df = fetch_df("SELECT * FROM modules")
    formations_df = fetch_df("SELECT * FROM formations")
    departements_df = fetch_df("SELECT * FROM departements")
    surveillances_df = fetch_df("SELECT * FROM surveillances")
    

    return {
        "examens": examens_df,
        "profs": profs_df,
        "salles": salles_df,
        "inscriptions": inscriptions_df,
        "examen_salles": examen_salles_df,
        "modules": modules_df,
        "formations": formations_df,
        "departements": departements_df,
        "surveillances": surveillances_df

        
    }
