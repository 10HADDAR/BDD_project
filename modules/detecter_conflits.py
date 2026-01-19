# modules/detecter_conflits.py
import pandas as pd

def detecter_conflits(data):
    """
    Détecte tous les conflits dans les données brutes.
    data : dict contenant DataFrames 'examens', 'inscriptions', 'profs', 'salles', 'examens_salles', 'modules', 'formations', 'departements'
    Retourne un dict avec les DataFrames des conflits
    """
    examens = data["examens"]
    inscriptions = data["inscriptions"]
    surveillances = data.get("surveillances", pd.DataFrame())
    profs = data["profs"]
    salles = data["salles"]
    examen_salles = data["examen_salles"]
    modules = data["modules"]
    formations = data["formations"]
    departements = data["departements"]

    conflits = {}

    # --- 1. Étudiants : max 1 examen par jour ---
    insc_exam = inscriptions.merge(examens[['id_examen','id_module','date_examen']], on='id_module')
    etud_conflicts = insc_exam.groupby(['id_etudiant','date_examen']).size()
    etud_conflicts = etud_conflicts[etud_conflicts > 1].reset_index(name='nb_examens')
    conflits['etudiants'] = etud_conflicts

    # --- 2. Professeurs : max 3 examens/jour ---
    if not surveillances.empty:
        surv_conflicts = surveillances.merge(examens[['id_examen','date_examen']], on='id_examen')
        prof_conflicts = surv_conflicts.groupby(['id_prof','date_examen']).size()
        prof_conflicts = prof_conflicts[prof_conflicts > 3].reset_index(name='nb_surveillances')
        conflits['profs'] = prof_conflicts
    else:
        conflits['profs'] = pd.DataFrame()

    # --- 3. Salles : capacité ---
    df_salle = examens.merge(examen_salles, on='id_examen')
    nb_etudiants = inscriptions.groupby('id_module').size().reset_index(name='nb_etudiants')
    df_salle = df_salle.merge(nb_etudiants, on='id_module')
    df_salle = df_salle.merge(salles, on='id_salle')
    salles_conflicts = df_salle[df_salle['nb_etudiants'] > df_salle['capacite_examen']]
    conflits['salles'] = salles_conflicts

    return conflits
