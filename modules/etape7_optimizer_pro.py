# etape7_optimizer_pro.py
import pandas as pd

def etape7_optimizer_pro(data):
    """
    Prépare les données pour l'optimisation :
    - Crée les listes d'examens et professeurs
    - Map dept_prof / dept_exam
    - Map date_examen pour contraintes
    """
    examens = data["examens"]
    profs = data["profs"]
    modules = data["modules"]
    formations = data["formations"]

    # Liste d'examens et profs
    examens_list = examens["id_examen"].tolist()
    profs_list = profs["id_prof"].tolist()

    # Map prof -> dept
    prof_dept = dict(zip(profs["id_prof"], profs["id_dept"]))

    # Map exam -> dept
    exam_dept = examens.merge(modules, on="id_module").merge(formations, on="id_formation")
    exam_dept_map = dict(zip(exam_dept["id_examen"], exam_dept["id_dept"]))

    # Date examen
    exam_dates = dict(zip(examens["id_examen"], examens["date_examen"]))

    return examens_list, profs_list, prof_dept, exam_dept_map, exam_dates
