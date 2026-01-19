from db import get_conn
import pandas as pd

def fetch_df(query, params=None):
    conn = get_conn()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df
# utils/queries.py
from db import get_conn
import pandas as pd

def fetch_df(query, params=None):
    """
    Exécute une requête SELECT et retourne un DataFrame.
    params : tuple pour requêtes paramétrées.
    """
    conn = get_conn()
    try:
        df = pd.read_sql(query, conn, params=params)
    finally:
        conn.close()
    return df

def execute_update(df, table, if_exists="append"):
    """
    Met à jour la base SQL avec le contenu d'un DataFrame.
    df : DataFrame à insérer
    table : nom de la table dans la base
    if_exists : "append" ou "replace"
    """
    if df.empty:
        print("Le DataFrame est vide. Rien à insérer.")
        return

    conn = get_conn()
    try:
        df.to_sql(table, conn, if_exists=if_exists, index=False)
        print(f"{len(df)} lignes insérées dans la table '{table}'")
    finally:
        conn.close()
