import pandas as pd
import math
from ortools.sat.python import cp_model

def optimiseur(input_dict):
    """
    Optimise automatiquement la répartition des surveillances
    Corrige aussi les conflits de capacité des salles
    """

    # -----------------------
    # Données
    # -----------------------
    data = input_dict["data"]

    examens = data["examens"]
    profs = data["profs"]
    salles = data["salles"]
    inscriptions = data["inscriptions"]
    examen_salles = data["examen_salles"]

    examens_list = input_dict["examens_list"]
    profs_list = input_dict["profs_list"]
    prof_dept = input_dict["prof_dept"]
    exam_dept_map = input_dict["exam_dept_map"]
    exam_dates = input_dict["exam_dates"]

    # -----------------------
    # OR-Tools : modèle
    # -----------------------
    model = cp_model.CpModel()

    x = {}
    for e in examens_list:
        for p in profs_list:
            x[(e, p)] = model.NewBoolVar(f"x_{e}_{p}")

    # -----------------------
    # Contraintes
    # -----------------------

    # 1. Un seul professeur par examen
    for e in examens_list:
        model.Add(sum(x[(e, p)] for p in profs_list) == 1)

    # 2. Max 3 examens / jour / prof
    for p in profs_list:
        for d in examens["date_examen"].unique():
            exams_day = examens[examens["date_examen"] == d]["id_examen"].tolist()
            model.Add(sum(x[(e, p)] for e in exams_day) <= 3)

    # 3. Équilibrage surveillances
    total_examens = len(examens_list)
    min_surv = total_examens // len(profs_list)
    max_surv = min_surv + 1

    for p in profs_list:
        model.Add(sum(x[(e, p)] for e in examens_list) >= min_surv)
        model.Add(sum(x[(e, p)] for e in examens_list) <= max_surv)

    # 4. Priorité département (soft)
    for e in examens_list:
        dept_e = exam_dept_map[e]
        for p in profs_list:
            if prof_dept[p] != dept_e:
                model.AddHint(x[(e, p)], 0)

    # -----------------------
    # Résolution
    # -----------------------
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 15
    status = solver.Solve(model)

    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("❌ Pas de solution trouvée")
        return pd.DataFrame()

    # -----------------------
    # POST-TRAITEMENT : correction capacité salles
    # -----------------------
    rows = []

    for e in examens_list:
        # Prof assigné
        prof_assigne = None
        for p in profs_list:
            if solver.BooleanValue(x[(e, p)]):
                prof_assigne = p
                break

        # Nombre d'étudiants de l'examen
        id_module = examens.loc[examens["id_examen"] == e, "id_module"].iloc[0]
        nb_etudiants = inscriptions[inscriptions["id_module"] == id_module].shape[0]

        # Salles possibles
        salles_e = examen_salles[examen_salles["id_examen"] == e]
        salles_ids = salles_e["id_salle"].tolist()

        salles_infos = salles[salles["id_salle"].isin(salles_ids)].copy()
        salles_infos = salles_infos.sort_values("capacite_examen", ascending=False)

        restant = nb_etudiants

        for _, salle in salles_infos.iterrows():
            if restant <= 0:
                break

            capacite = salle["capacite_examen"]
            affectes = min(capacite, restant)

            rows.append({
                "id_examen": e,
                "id_prof": prof_assigne,
                "id_salle": salle["id_salle"],
                "nb_etudiants_affectes": affectes
            })

            restant -= affectes

        if restant > 0:
            print(f"⚠️ Attention : capacité insuffisante pour l'examen {e}")

    surveillances_df = pd.DataFrame(rows)
    return surveillances_df
