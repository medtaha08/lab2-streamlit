# utils.py
# Fonctions utilitaires pour récupérer les données Google Play Store

import pandas as pd
from google_play_scraper import search, app

LANG = "en"
COUNTRY = "us"

def search_apps(query: str
, n_results: int = 20) -> pd.DataFrame:
    """
    Prend un terme de recherche et retourne un DataFrame avec les résultats.
    Utilisée dans la Page 1 pour afficher le tableau de résultats.
    """
    try:
        results = search(query, lang=LANG, country=COUNTRY, n_hits=n_results)
        apps_data = []
        for r in results:
            # Récupérer les détails complets de chaque app
            try:
                details = app(r["appId"], lang=LANG, country=COUNTRY)
                apps_data.append({
                    "appId":       details.get("appId"),
                    "title":       details.get("title"),
                    "developer":   details.get("developer"),
                    "genre":       details.get("genre"),
                    "score":       details.get("score"),
                    "ratings":     details.get("ratings"),
                    "installs":    details.get("installs"),
                    "minInstalls": details.get("minInstalls"),
                    "free":        details.get("free"),
                    "price":       details.get("price"),
                    "description": details.get("description"),
                    "summary":     details.get("summary"),
                    "icon":        details.get("icon"),
                    "url":         details.get("url"),
                })
            except:
                continue
        return pd.DataFrame(apps_data)
    except Exception as e:
        return pd.DataFrame()