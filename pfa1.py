"""
=============================================================================
  BIA4 — Web Scraping Prix Historiques CSE (Stooq avec API Key)
  Projet : Tableau de Bord Décisionnel pour le Suivi des Investissements
  Marché : CSE | Devise : MAD
=============================================================================

  COMMENT OBTENIR TON API KEY STOOQ (gratuit, ~2 minutes)
  ─────────────────────────────────────────────────────────
  1. Ouvre : https://stooq.com/q/d/?s=bcp.ca&get_apikey
  2. Résous le captcha
  3. Copie le lien CSV affiché en bas de la page
     Ex: https://stooq.com/q/d/l/?s=bcp.ca&i=d&apikey=abc123def456...
  4. Extrait la valeur après &apikey=  (32 caractères)
  5. Colle-la dans STOOQ_API_KEY ci-dessous

  INSTALLATION  :  pip install requests pandas
  EXÉCUTION     :  python scraping_cse_BIA4.py
  IMPORT Power BI : Obtenir données > Texte/CSV > Sep: ; > UTF-8

=============================================================================
"""

import requests
import pandas as pd
import time
import logging
import os
import sys
from io import StringIO
from datetime import datetime, date

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraping_cse.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# =============================================================================
#  ★ CONFIGURATION — REMPLIR ICI ★
# =============================================================================

# Coller ta clé API Stooq ici (obtenue sur https://stooq.com/q/d/?s=bcp.ca&get_apikey)
STOOQ_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

OUTPUT_DIR             = "."
DELAY_BETWEEN_REQUESTS = 1.5    # secondes entre requêtes
MAX_RETRIES            = 3
RETRY_DELAY            = 5.0

STOOQ_URL = "https://stooq.com/q/d/l/?s={ticker}.ca&i=d&apikey={apikey}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


# =============================================================================
#  RÉFÉRENTIEL DES 29 ACTIFS
# =============================================================================

TICKERS_MAP = {

    # ── Banques ───────────────────────────────────────────────────────────────
    "BCP"  : {"nom": "Banque Centrale Populaire", "isin": "MA0000011884", "secteur": "Banques",                         "indice": "MSI20", "type": "Action", "stooq": "bcp"},
    "CFG"  : {"nom": "CFG Bank",                  "isin": "MA0000012351", "secteur": "Banques",                         "indice": "MASI",  "type": "Action", "stooq": "cfg"},
    "ATW"  : {"nom": "Attijariwafa Bank",          "isin": "MA0000011488", "secteur": "Banques",                         "indice": "MSI20", "type": "Action", "stooq": "atw"},
    "BOA"  : {"nom": "Bank of Africa",             "isin": "MA0000011819", "secteur": "Banques",                         "indice": "MASI",  "type": "Action", "stooq": "boa"},
    "CIH"  : {"nom": "CIH Bank",                   "isin": "MA0000011264", "secteur": "Banques",                         "indice": "MASI",  "type": "Action", "stooq": "cih"},
    "BMCI" : {"nom": "BMCI",                        "isin": "MA0000010621", "secteur": "Banques",                         "indice": "MASI",  "type": "Action", "stooq": "bmc"},

    # ── Télécommunications ────────────────────────────────────────────────────
    "IAM"  : {"nom": "Maroc Telecom",              "isin": "MA0000010373", "secteur": "Télécommunications",              "indice": "MSI20", "type": "Action", "stooq": "iam"},

    # ── Immobilier ────────────────────────────────────────────────────────────
    "ADH"  : {"nom": "Groupe Addoha",              "isin": "MA0000011884", "secteur": "Immobilier",                      "indice": "MASI",  "type": "Action", "stooq": "adh"},
    "ESP"  : {"nom": "Résidences Dar Saada",       "isin": "MA0000012096", "secteur": "Immobilier",                      "indice": "MASI",  "type": "Action", "stooq": "rds"},
    "IMM"  : {"nom": "Immorente Invest",           "isin": "MA0000012658", "secteur": "Immobilier",                      "indice": "MASI",  "type": "Action", "stooq": "imr"},

    # ── Santé ─────────────────────────────────────────────────────────────────
    "AKD"  : {"nom": "Akdital",                    "isin": "MA0000012890", "secteur": "Santé",                           "indice": "MASI",  "type": "Action", "stooq": "akd"},

    # ── Agroalimentaire ───────────────────────────────────────────────────────
    "CSR"  : {"nom": "Cosumar",                    "isin": "MA0000010555", "secteur": "Agroalimentaire & Boissons",      "indice": "MSI20", "type": "Action", "stooq": "csr"},
    "MUT"  : {"nom": "Mutandis SCA",               "isin": "MA0000012360", "secteur": "Agroalimentaire & Boissons",      "indice": "MASI",  "type": "Action", "stooq": "mut"},

    # ── BTP & Matériaux ───────────────────────────────────────────────────────
    "TGCC" : {"nom": "TGCC S.A",                   "isin": "MA0000012245", "secteur": "BTP & Matériaux de Construction", "indice": "MASI",  "type": "Action", "stooq": "tgcc"},
    "SGTM" : {"nom": "SGTM",                        "isin": "MA0000010257", "secteur": "BTP & Matériaux de Construction", "indice": "MASI",  "type": "Action", "stooq": "sgt"},
    "LHM"  : {"nom": "LafargeHolcim Maroc",        "isin": "MA0000011553", "secteur": "BTP & Matériaux de Construction", "indice": "MSI20", "type": "Action", "stooq": "lhm"},

    # ── Transport ─────────────────────────────────────────────────────────────
    "CTM"  : {"nom": "CTM",                        "isin": "MA0000010928", "secteur": "Transport",                       "indice": "MASI",  "type": "Action", "stooq": "ctm"},

    # ── Distribution ──────────────────────────────────────────────────────────
    "NKL"  : {"nom": "Ennakl Automobiles",         "isin": "TN0007110015", "secteur": "Distribution",                    "indice": "MASI",  "type": "Action", "stooq": "nkl",
               "note": "Valeur tunisienne cotée CSE"},

    # ── Technologie ───────────────────────────────────────────────────────────
    "HPS"  : {"nom": "HPS",                        "isin": "MA0000011736", "secteur": "Technologie",                     "indice": "MASI",  "type": "Action", "stooq": "hps"},

    # ── Industrie ─────────────────────────────────────────────────────────────
    "CMGP" : {"nom": "CMGP Group",                 "isin": "MA0000012484", "secteur": "Industrie",                       "indice": "MASI",  "type": "Action", "stooq": "cmgp"},

    # ── Mines & Métaux ────────────────────────────────────────────────────────
    "MNG"  : {"nom": "Managem",                    "isin": "MA0000011462", "secteur": "Mines",                           "indice": "MSI20", "type": "Action", "stooq": "mng"},
    "SMI"  : {"nom": "SMI (Société Minière)",      "isin": "MA0000010521", "secteur": "Mines",                           "indice": "MASI",  "type": "Action", "stooq": "smi"},
    "ALM"  : {"nom": "Aluminium du Maroc",         "isin": "MA0000011199", "secteur": "Industrie",                       "indice": "MASI",  "type": "Action", "stooq": "alm"},
    "SNP"  : {"nom": "Sonasid",                    "isin": "MA0000010679", "secteur": "Sidérurgie",                      "indice": "MASI",  "type": "Action", "stooq": "snp"},

    # ── Pétrole ───────────────────────────────────────────────────────────────
    "TMA"  : {"nom": "Total Maroc",                "isin": "MA0000010894", "secteur": "Pétrole & Gaz",                   "indice": "MASI",  "type": "Action", "stooq": "tma"},

    # ── Chimie ────────────────────────────────────────────────────────────────
    "OCP"  : {"nom": "OCP S.A",                    "isin": "MA0000012270", "secteur": "Chimie",                          "indice": "MSI20", "type": "Action", "stooq": "ocp"},

    # ── Assurance ─────────────────────────────────────────────────────────────
    "WAA"  : {"nom": "Wafa Assurance",             "isin": "MA0000011405", "secteur": "Assurances",                      "indice": "MASI",  "type": "Action", "stooq": "waa"},

    # ── Papier ────────────────────────────────────────────────────────────────
    "MDP"  : {"nom": "Med Paper",                  "isin": "MA0000011728", "secteur": "Papier & Emballage",              "indice": "MASI",  "type": "Action", "stooq": "mdp"},

    # ── Tourisme ──────────────────────────────────────────────────────────────
    "RIS"  : {"nom": "Risma",                      "isin": "MA0000011900", "secteur": "Tourisme & Hôtellerie",           "indice": "MASI",  "type": "Action", "stooq": "ris"},
}


# =============================================================================
#  VALIDATION API KEY
# =============================================================================

def check_api_key(api_key: str) -> bool:
    """Vérifie que la clé API est bien renseignée et non factice."""
    if not api_key or api_key == "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
        log.error("=" * 62)
        log.error("  ❌ API KEY STOOQ NON CONFIGURÉE")
        log.error("  Suis les étapes suivantes pour l'obtenir (gratuit) :")
        log.error("  1. Ouvre : https://stooq.com/q/d/?s=bcp.ca&get_apikey")
        log.error("  2. Résous le captcha")
        log.error("  3. Copie la valeur après &apikey= dans le lien CSV")
        log.error("  4. Remplace XXXXXXXX... par ta clé dans STOOQ_API_KEY")
        log.error("=" * 62)
        return False
    if len(api_key) < 20:
        log.error(f"  ❌ Clé API trop courte ({len(api_key)} car.) — vérifier la copie")
        return False
    return True


# =============================================================================
#  PARSING CSV STOOQ
# =============================================================================

def parse_stooq_csv(raw_text: str, ticker: str) -> pd.DataFrame:
    """
    Parse la réponse CSV de Stooq.
    Cherche la ligne d'en-tête 'Date' pour ignorer tout texte parasite éventuel.
    """
    lines = raw_text.strip().splitlines()

    # Détecter un message d'erreur Stooq (apikey invalide, rate limit...)
    if lines and "apikey" in lines[0].lower():
        log.error(f"  ❌ Stooq réclame une API key pour {ticker} — clé manquante ou invalide")
        return pd.DataFrame()
    if lines and any(kw in raw_text.lower() for kw in ["exceeded", "limit", "blocked", "error"]):
        log.warning(f"  ⚠️  Message Stooq pour {ticker} : {lines[0][:120]}")
        return pd.DataFrame()

    # Trouver la ligne d'en-tête CSV (commence par "Date")
    header_idx = next(
        (i for i, line in enumerate(lines) if line.strip().lower().startswith("date")),
        None
    )
    if header_idx is None:
        log.warning(f"  ⚠️  {ticker} : en-tête CSV introuvable | Réponse: {repr(raw_text[:150])}")
        return pd.DataFrame()

    csv_clean = "\n".join(lines[header_idx:])
    try:
        df = pd.read_csv(StringIO(csv_clean))
    except Exception as e:
        log.warning(f"  ⚠️  {ticker} : erreur parsing CSV : {e}")
        return pd.DataFrame()

    if "Date" not in df.columns or "Close" not in df.columns:
        log.warning(f"  ⚠️  {ticker} : colonnes inattendues : {list(df.columns)}")
        return pd.DataFrame()

    return df.dropna(subset=["Date", "Close"])


# =============================================================================
#  COLLECTE STOOQ
# =============================================================================

def fetch_stooq(session: requests.Session, ticker: str, info: dict) -> pd.DataFrame:
    stooq_ticker = info.get("stooq", ticker.lower())
    url = STOOQ_URL.format(ticker=stooq_ticker, apikey=STOOQ_API_KEY)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log.info(f"  [{attempt}/{MAX_RETRIES}] GET {url.replace(STOOQ_API_KEY, '***')}")
            resp = session.get(url, timeout=25)

            if resp.status_code == 429:
                log.warning(f"  ⚠️  Rate limit (429) — attente {RETRY_DELAY * 3}s")
                time.sleep(RETRY_DELAY * 3)
                continue
            if resp.status_code != 200:
                log.warning(f"  ⚠️  HTTP {resp.status_code} pour {ticker}")
                time.sleep(RETRY_DELAY)
                continue

            df_raw = parse_stooq_csv(resp.text, ticker)
            if df_raw.empty:
                return pd.DataFrame()

            df_out = pd.DataFrame({
                "Date"              : pd.to_datetime(df_raw["Date"], errors="coerce").dt.date,
                "Ticker"            : ticker,
                "ISIN"              : info["isin"],
                "Nom"               : info["nom"],
                "Secteur"           : info.get("secteur", ""),
                "Indice"            : info.get("indice", "MASI"),
                "Type_Instrument"   : info.get("type", "Action"),
                "Prix_Open"         : pd.to_numeric(df_raw.get("Open"),   errors="coerce"),
                "Prix_High"         : pd.to_numeric(df_raw.get("High"),   errors="coerce"),
                "Prix_Low"          : pd.to_numeric(df_raw.get("Low"),    errors="coerce"),
                "Prix_Close"        : pd.to_numeric(df_raw["Close"],       errors="coerce"),
                "Volume_Journalier" : pd.to_numeric(df_raw.get("Volume"),  errors="coerce"),
                "Devise"            : "MAD",
                "Source"            : "STOOQ",
            }).dropna(subset=["Date", "Prix_Close"])

            log.info(
                f"  ✅ {ticker} — {len(df_out)} lignes | "
                f"{df_out['Date'].min()} → {df_out['Date'].max()}"
            )
            return df_out

        except requests.exceptions.RequestException as e:
            log.warning(f"  ⚠️  Réseau {ticker} (tentative {attempt}) : {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            log.error(f"  ❌ Erreur inattendue {ticker} : {e}")
            break

    log.error(f"  ❌ {ticker} — Échec après {MAX_RETRIES} tentatives")
    return pd.DataFrame()


# =============================================================================
#  VOLUME MOYEN 30 JOURS
# =============================================================================

def add_volume_moyen_30j(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "Volume_Journalier" not in df.columns:
        return df
    df = df.sort_values(["Ticker", "Date"]).copy()
    df["Volume_Moyen_30j"] = (
        df.groupby("Ticker")["Volume_Journalier"]
          .transform(lambda x: x.rolling(window=30, min_periods=1).mean().round(0))
    )
    return df


# =============================================================================
#  MODE FALLBACK — DONNÉES SIMULÉES
# =============================================================================

PRIX_REFERENCE = {
    "BCP"  : [240, 350],  "CFG"  : [80,  215],  "ATW"  : [420, 700],
    "BOA"  : [185, 260],  "CIH"  : [280, 390],  "BMCI" : [420, 620],
    "IAM"  : [130, 165],  "ADH"  : [10,   36],  "ESP"  : [90,  185],
    "IMM"  : [75,   95],  "AKD"  : [350, 1250], "CSR"  : [160, 270],
    "MUT"  : [200, 250],  "TGCC" : [280, 820],  "SGTM" : [700, 850],
    "LHM"  : [1500,1900], "CTM"  : [880,1200],  "NKL"  : [4,   12],
    "HPS"  : [580, 1200], "CMGP" : [340, 800],  "MNG"  : [8500,14000],
    "SMI"  : [7000,10500],"ALM"  : [1600,2000], "SNP"  : [1800,2200],
    "TMA"  : [1600,1900], "OCP"  : [130, 220],  "WAA"  : [5000,5800],
    "MDP"  : [20,   30],  "RIS"  : [280, 380],
}

def generate_fallback_data(tickers_map: dict, start_date: str = "2022-01-01") -> pd.DataFrame:
    import numpy as np
    np.random.seed(42)
    log.warning("  MODE FALLBACK — Données SIMULÉES (Source = SIMULE)")
    all_rows = []
    dates = pd.date_range(start=start_date, end=date.today(), freq="B")
    for ticker, info in tickers_map.items():
        p_range  = PRIX_REFERENCE.get(ticker, [100, 300])
        p_init   = (p_range[0] + p_range[1]) / 2
        rets     = np.random.normal(0.0002, 0.013, size=len(dates))
        prices   = [p_init]
        for r in rets[1:]:
            prices.append(max(round(prices[-1] * (1 + r), 2), p_range[0] * 0.5))
        vol_base = int(p_init * 600)
        for i, d in enumerate(dates):
            p   = prices[i]
            vol = max(0, int(np.random.normal(vol_base, vol_base * 0.4)))
            all_rows.append({
                "Date"              : d.date(),
                "Ticker"            : ticker,
                "ISIN"              : info["isin"],
                "Nom"               : info["nom"],
                "Secteur"           : info.get("secteur", ""),
                "Indice"            : info.get("indice", "MASI"),
                "Type_Instrument"   : info.get("type", "Action"),
                "Prix_Open"         : round(p * 1.002, 2),
                "Prix_High"         : round(p * 1.012, 2),
                "Prix_Low"          : round(p * 0.988, 2),
                "Prix_Close"        : p,
                "Volume_Journalier" : vol,
                "Devise"            : "MAD",
                "Source"            : "SIMULE",
            })
    return add_volume_moyen_30j(pd.DataFrame(all_rows))


# =============================================================================
#  MAIN
# =============================================================================

def main():
    log.info("=" * 62)
    log.info("  BIA4 — Scraping Prix Historiques CSE via Stooq  [v4]")
    log.info(f"  Exécution : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"  Actifs    : {len(TICKERS_MAP)}")
    log.info("=" * 62)

    # Vérification clé API avant tout
    if not check_api_key(STOOQ_API_KEY):
        log.warning("\n→ Lancement en mode FALLBACK (données simulées)")
        log.warning("  Configure STOOQ_API_KEY puis relance le script.\n")
        Prix_Historique = generate_fallback_data(TICKERS_MAP)
        _export(Prix_Historique, rapport=[], mode="FALLBACK — CLÉ API MANQUANTE")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    session  = requests.Session()
    session.headers.update(HEADERS)
    rapport  = []
    all_data = []

    # ── Collecte ──────────────────────────────────────────────────────────────
    for ticker, info in TICKERS_MAP.items():
        log.info(f"\n→ Collecte : {ticker} ({info['nom']})")
        df_ticker = fetch_stooq(session, ticker, info)

        statut = "OK" if not df_ticker.empty else "ECHEC"
        rapport.append({
            "Ticker"       : ticker,
            "Nom"          : info["nom"],
            "ISIN"         : info["isin"],
            "Stooq_Ticker" : info.get("stooq", ticker.lower()) + ".ca",
            "Statut"       : statut,
            "Lignes"       : len(df_ticker),
            "Date_Min"     : str(df_ticker["Date"].min()) if statut == "OK" else "",
            "Date_Max"     : str(df_ticker["Date"].max()) if statut == "OK" else "",
        })
        if not df_ticker.empty:
            all_data.append(df_ticker)

        time.sleep(DELAY_BETWEEN_REQUESTS)

    # ── Consolidation ─────────────────────────────────────────────────────────
    n_ok    = sum(1 for r in rapport if r["Statut"] == "OK")
    n_echec = sum(1 for r in rapport if r["Statut"] == "ECHEC")

    if all_data:
        Prix_Historique = pd.concat(all_data, ignore_index=True)
        Prix_Historique = add_volume_moyen_30j(Prix_Historique)
        Prix_Historique.sort_values(["Ticker", "Date"], inplace=True)

        # Fallback partiel pour actifs manquants
        if n_echec > 0:
            tickers_ok = set(Prix_Historique["Ticker"].unique())
            manquants  = {t: i for t, i in TICKERS_MAP.items() if t not in tickers_ok}
            if manquants:
                log.warning(f"\n⚠️  {len(manquants)} actifs sans données → données simulées")
                df_fb = generate_fallback_data(manquants)
                Prix_Historique = pd.concat([Prix_Historique, df_fb], ignore_index=True)
                Prix_Historique.sort_values(["Ticker", "Date"], inplace=True)

        mode = f"STOOQ ({n_ok}/{len(TICKERS_MAP)} actifs OK)"
    else:
        log.warning("\n⚠️  Aucune donnée collectée → fallback total")
        Prix_Historique = generate_fallback_data(TICKERS_MAP)
        mode = "FALLBACK TOTAL"
        for r in rapport:
            r["Statut"] = "SIMULE"
            r["Lignes"] = len(Prix_Historique[Prix_Historique["Ticker"] == r["Ticker"]])

    _export(Prix_Historique, rapport, mode)


def _export(Prix_Historique: pd.DataFrame, rapport: list, mode: str):
    """Exporte les CSV et affiche le résumé final."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    n_lignes = len(Prix_Historique)

    # Prix_Historique.csv
    COLS = [
        "Date", "Ticker", "ISIN", "Nom", "Secteur", "Indice", "Type_Instrument",
        "Prix_Open", "Prix_High", "Prix_Low", "Prix_Close",
        "Volume_Journalier", "Volume_Moyen_30j", "Devise", "Source",
    ]
    for c in COLS:
        if c not in Prix_Historique.columns:
            Prix_Historique[c] = None

    Prix_Historique[COLS].to_csv(
        os.path.join(OUTPUT_DIR, "Prix_Historique.csv"),
        index=False, encoding="utf-8-sig", sep=";"
    )
    log.info(f"\n✅ Prix_Historique.csv — {n_lignes} lignes")

    # Dim_Actifs.csv
    dim = pd.DataFrame([{
        "Ticker"          : t,
        "ISIN"            : i["isin"],
        "Nom"             : i["nom"],
        "Secteur"         : i.get("secteur", ""),
        "Type_Instrument" : i.get("type", "Action"),
        "Indice"          : i.get("indice", "MASI"),
        "Marche"          : "CSE",
        "Devise"          : "MAD",
        "Stooq_Ticker"    : i.get("stooq", t.lower()) + ".ca",
        "Note"            : i.get("note", ""),
    } for t, i in TICKERS_MAP.items()])
    dim.to_csv(os.path.join(OUTPUT_DIR, "Dim_Actifs.csv"), index=False, encoding="utf-8-sig", sep=";")
    log.info(f"✅ Dim_Actifs.csv — {len(dim)} actifs")

    # scraping_report.csv
    if rapport:
        df_rpt = pd.DataFrame(rapport)
        df_rpt["Date_Execution"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df_rpt.to_csv(os.path.join(OUTPUT_DIR, "scraping_report.csv"), index=False, encoding="utf-8-sig", sep=";")

    log.info("\n" + "=" * 62)
    log.info(f"  RÉSUMÉ  |  {mode}")
    log.info(f"  Lignes  : {n_lignes}")
    log.info("  Fichiers : Prix_Historique.csv | Dim_Actifs.csv | scraping_report.csv")
    log.info("=" * 62)
    log.info("\n✅ Terminé. Power BI : Obtenir données > Texte/CSV > Sep: ; > UTF-8")


if __name__ == "__main__":
    main()