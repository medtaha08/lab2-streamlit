"""
=============================================================================
  BIA4 — Fusion fichiers Investing.com (Excel + CSV) → Power BI
  Projet : Tableau de Bord Décisionnel pour le Suivi des Investissements
  Marché : CSE | Devise : MAD
=============================================================================

  ÉTAPES
  ──────
  1. Sur Investing.com, chercher chaque actif par son nom complet
     Ex : "Banque Centrale Populaire" (pas "BCP Maroc")

  2. Onglet "Données historiques" → Période : 01/01/2015 → aujourd'hui
     → Cliquer "Télécharger" → fichier Excel (.xlsx) ou CSV

  3. Renommer le fichier avec le ticker exact :
       BCP.xlsx  ou  BCP.csv
       IAM.xlsx  ou  IAM.csv
       etc. (voir TICKERS_MAP ci-dessous)

  4. Placer TOUS les fichiers dans le dossier :  data_cse/

  5. Lancer :  python fusion_BIA4.py

  INSTALLATION
  ────────────
  pip install pandas openpyxl

  FICHIERS PRODUITS
  ─────────────────
  Prix_Historique.csv   → Table principale Power BI
  Dim_Actifs.csv        → Référentiel actifs
  fusion_report.csv     → Actifs OK / manquants / erreurs
  fusion.log            → Logs complets

  IMPORT POWER BI
  ───────────────
  Obtenir les données > Texte/CSV > Séparateur : ; > Encodage : UTF-8

=============================================================================
"""

import pandas as pd
import os
import logging
import sys
from datetime import datetime, date

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("fusion.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# =============================================================================
#  CONFIGURATION
# =============================================================================

INPUT_DIR  = "data_cse"   # dossier contenant les fichiers téléchargés
OUTPUT_DIR =r"C:\Users\CHOUACHELHASSANE\Downloads\PROJET"           # dossier de sortie


# =============================================================================
#  RÉFÉRENTIEL DES ACTIFS
#  Nommer les fichiers exactement comme les clés ci-dessous :
#    BCP.xlsx, IAM.xlsx, ADH.xlsx ...
# =============================================================================

TICKERS_MAP = {

    # ── Banques ───────────────────────────────────────────────────────────────
    "BCP"  : {"nom": "Banque Centrale Populaire", "isin": "MA0000011884", "secteur": "Banques",                         "indice": "MSI20", "type": "Action"},
    "CFG"  : {"nom": "CFG Bank",                  "isin": "MA0000012351", "secteur": "Banques",                         "indice": "MASI",  "type": "Action"},
    "ATW"  : {"nom": "Attijariwafa Bank",          "isin": "MA0000011488", "secteur": "Banques",                         "indice": "MSI20", "type": "Action"},
    "BOA"  : {"nom": "Bank of Africa",             "isin": "MA0000011819", "secteur": "Banques",                         "indice": "MASI",  "type": "Action"},
    "CIH"  : {"nom": "CIH Bank",                   "isin": "MA0000011264", "secteur": "Banques",                         "indice": "MASI",  "type": "Action"},
    "BMCI" : {"nom": "BMCI",                        "isin": "MA0000010621", "secteur": "Banques",                         "indice": "MASI",  "type": "Action"},
    "SGTM" : {"nom": "SGTM",                        "isin": "MA0000010257", "secteur": "BTP & Matériaux de Construction", "indice": "MASI",  "type": "Action"},

    # ── Télécommunications ────────────────────────────────────────────────────
    "IAM"  : {"nom": "Maroc Telecom",              "isin": "MA0000010373", "secteur": "Télécommunications",              "indice": "MSI20", "type": "Action"},

    # ── Immobilier ────────────────────────────────────────────────────────────
    "ADH"  : {"nom": "Groupe Addoha",              "isin": "MA0000011884", "secteur": "Immobilier",                      "indice": "MASI",  "type": "Action"},
    "ESP"  : {"nom": "Résidences Dar Saada",       "isin": "MA0000012096", "secteur": "Immobilier",                      "indice": "MASI",  "type": "Action"},
    "IMM"  : {"nom": "Immorente Invest",           "isin": "MA0000012658", "secteur": "Immobilier",                      "indice": "MASI",  "type": "Action"},

    # ── Santé ─────────────────────────────────────────────────────────────────
    "AKD"  : {"nom": "Akdital",                    "isin": "MA0000012890", "secteur": "Santé",                           "indice": "MASI",  "type": "Action"},

    # ── Agroalimentaire ───────────────────────────────────────────────────────
    "CSR"  : {"nom": "Cosumar",                    "isin": "MA0000010555", "secteur": "Agroalimentaire & Boissons",      "indice": "MSI20", "type": "Action"},
    "MUT"  : {"nom": "Mutandis SCA",               "isin": "MA0000012360", "secteur": "Agroalimentaire & Boissons",      "indice": "MASI",  "type": "Action"},

    # ── BTP & Matériaux ───────────────────────────────────────────────────────
    "TGCC" : {"nom": "TGCC S.A",                   "isin": "MA0000012245", "secteur": "BTP & Matériaux de Construction", "indice": "MASI",  "type": "Action"},
    "LHM"  : {"nom": "LafargeHolcim Maroc",        "isin": "MA0000011553", "secteur": "BTP & Matériaux de Construction", "indice": "MSI20", "type": "Action"},

    # ── Transport ─────────────────────────────────────────────────────────────
    "CTM"  : {"nom": "CTM",                        "isin": "MA0000010928", "secteur": "Transport",                       "indice": "MASI",  "type": "Action"},

    # ── Distribution ──────────────────────────────────────────────────────────
    "NKL"  : {"nom": "Ennakl Automobiles",         "isin": "TN0007110015", "secteur": "Distribution",                    "indice": "MASI",  "type": "Action"},

    # ── Technologie ───────────────────────────────────────────────────────────
    "HPS"  : {"nom": "HPS",                        "isin": "MA0000011736", "secteur": "Technologie",                     "indice": "MASI",  "type": "Action"},

    # ── Industrie ─────────────────────────────────────────────────────────────
    "CMGP" : {"nom": "CMGP Group",                 "isin": "MA0000012484", "secteur": "Industrie",                       "indice": "MASI",  "type": "Action"},

    # ── Mines & Métaux ────────────────────────────────────────────────────────
    "MNG"  : {"nom": "Managem",                    "isin": "MA0000011462", "secteur": "Mines",                           "indice": "MSI20", "type": "Action"},
    "SMI"  : {"nom": "SMI (Société Minière)",      "isin": "MA0000010521", "secteur": "Mines",                           "indice": "MASI",  "type": "Action"},
    "ALM"  : {"nom": "Aluminium du Maroc",         "isin": "MA0000011199", "secteur": "Industrie",                       "indice": "MASI",  "type": "Action"},
    "SNP"  : {"nom": "Sonasid",                    "isin": "MA0000010679", "secteur": "Sidérurgie",                      "indice": "MASI",  "type": "Action"},

    # ── Pétrole ───────────────────────────────────────────────────────────────
    "TMA"  : {"nom": "Total Maroc",                "isin": "MA0000010894", "secteur": "Pétrole & Gaz",                   "indice": "MASI",  "type": "Action"},

    # ── Assurance ─────────────────────────────────────────────────────────────
    "WAA"  : {"nom": "Wafa Assurance",             "isin": "MA0000011405", "secteur": "Assurances",                      "indice": "MASI",  "type": "Action"},

    # ── Papier ────────────────────────────────────────────────────────────────
    "MDP"  : {"nom": "Med Paper",                  "isin": "MA0000011728", "secteur": "Papier & Emballage",              "indice": "MASI",  "type": "Action"},

    # ── Tourisme ──────────────────────────────────────────────────────────────
    "RIS"  : {"nom": "Risma",                      "isin": "MA0000011900", "secteur": "Tourisme & Hôtellerie",           "indice": "MASI",  "type": "Action"},
}


# =============================================================================
#  PARSERS — FORMATS INVESTING.COM
# =============================================================================

MOIS_FR = {
    "janv": "01", "janv.": "01", "janvier": "01",
    "févr": "02", "févr.": "02", "février": "02",
    "mars": "03",
    "avr":  "04", "avr.":  "04", "avril":  "04",
    "mai":  "05",
    "juin": "06",
    "juil": "07", "juil.": "07", "juillet": "07",
    "août": "08",
    "sept": "09", "sept.": "09", "septembre": "09",
    "oct":  "10", "oct.":  "10", "octobre":  "10",
    "nov":  "11", "nov.":  "11", "novembre": "11",
    "déc":  "12", "déc.":  "12", "décembre": "12",
}

def parse_date_fr(val):
    """Parse date Investing.com : '13 mai 2026', '2026-05-13', datetime, etc."""
    if pd.isna(val) or val is None:
        return None
    # Déjà un objet date/datetime (cas Excel)
    if isinstance(val, (datetime, date)):
        return val.date() if isinstance(val, datetime) else val
    if hasattr(val, 'date'):
        return val.date()
    text = str(val).strip().strip('"')
    # Formats ISO / numériques
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    # Format français texte : "13 mai 2026"
    parts = text.lower().split()
    if len(parts) == 3:
        mois = MOIS_FR.get(parts[1].rstrip("."))
        if mois:
            try:
                return datetime.strptime(f"{parts[2]}-{mois}-{parts[0].zfill(2)}", "%Y-%m-%d").date()
            except ValueError:
                pass
    return None


def parse_number(val) -> float:
    """Parse nombre Investing.com : '1 289,50' ou '1,289.50' ou 1289.5"""
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    text = str(val).strip().strip('"').replace("\xa0", "").replace(" ", "")
    if not text or text == "-":
        return None
    # Format européen : point = milliers, virgule = décimale → "1.234,56"
    if "," in text and "." in text:
        if text.index(".") < text.index(","):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def parse_volume(val) -> float:
    """Parse volume avec suffixes K/M/B : '12,34K' → 12340"""
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    text = str(val).strip().strip('"').replace("\xa0", "").replace(" ", "")
    if not text or text == "-":
        return None
    mult = 1
    if text.upper().endswith("B"):
        mult, text = 1_000_000_000, text[:-1]
    elif text.upper().endswith("M"):
        mult, text = 1_000_000, text[:-1]
    elif text.upper().endswith("K"):
        mult, text = 1_000, text[:-1]
    v = parse_number(text)
    return round(v * mult) if v is not None else None


# =============================================================================
#  LECTURE FICHIER (EXCEL OU CSV)
# =============================================================================

# Mapping colonnes Investing.com (FR + EN) → noms standards
COL_MAP = {
    "date"        : "Date",
    "prix"        : "Prix_Close",  "price"     : "Prix_Close",
    "close"       : "Prix_Close",  "dernier"   : "Prix_Close",
    "last"        : "Prix_Close",  "clôture"   : "Prix_Close",
    "cloture"     : "Prix_Close",
    "ouv."        : "Prix_Open",   "ouv"       : "Prix_Open",
    "open"        : "Prix_Open",   "ouverture" : "Prix_Open",
    "plus haut"   : "Prix_High",   "high"      : "Prix_High",  "max": "Prix_High",
    "plus bas"    : "Prix_Low",    "low"       : "Prix_Low",   "min": "Prix_Low",
    "vol."        : "Volume_Journalier", "vol"  : "Volume_Journalier",
    "volume"      : "Volume_Journalier",
}

def read_file(filepath: str, ticker: str, info: dict) -> pd.DataFrame:
    """
    Lit un fichier Excel (.xlsx) ou CSV depuis Investing.com.
    Gère automatiquement :
      - Détection de l'extension
      - Colonnes en français ET en anglais
      - Dates texte français ou ISO
      - Nombres avec virgule décimale
      - Volumes avec K/M/B
    """
    ext = os.path.splitext(filepath)[1].lower()

    # ── Lecture brute ─────────────────────────────────────────────────────────
    try:
        if ext in [".xlsx", ".xls"]:
            # Excel — pandas lit directement, dates souvent déjà parsées
            df_raw = pd.read_excel(filepath, dtype=str, engine="openpyxl")
            log.info(f"  Format : Excel ({ext})")
        else:
            # CSV — détecter le séparateur
            with open(filepath, "r", encoding="utf-8-sig", errors="replace") as f:
                first = f.readline()
            sep = ";" if first.count(";") > first.count(",") else ","
            df_raw = pd.read_csv(filepath, sep=sep, encoding="utf-8-sig", dtype=str)
            log.info(f"  Format : CSV (séparateur='{sep}')")
    except Exception as e:
        log.error(f"  ❌ Impossible de lire {filepath} : {e}")
        return pd.DataFrame()

    # ── Nettoyage colonnes ────────────────────────────────────────────────────
    df_raw.columns = [str(c).strip().strip('"').strip() for c in df_raw.columns]
    log.info(f"  Colonnes brutes : {list(df_raw.columns)}")

    # Renommer selon le mapping
    rename = {c: COL_MAP[c.lower()] for c in df_raw.columns if c.lower() in COL_MAP}
    df_raw = df_raw.rename(columns=rename)

    # Vérifications minimales
    if "Date" not in df_raw.columns:
        log.error(f"  ❌ Colonne 'Date' introuvable | Colonnes : {list(df_raw.columns)}")
        return pd.DataFrame()
    if "Prix_Close" not in df_raw.columns:
        log.error(f"  ❌ Colonne prix introuvable | Colonnes : {list(df_raw.columns)}")
        log.error(f"     Renomme manuellement la colonne du prix de clôture en 'Prix_Close'")
        return pd.DataFrame()

    # ── Parsing valeurs ───────────────────────────────────────────────────────
    df_out = pd.DataFrame()
    df_out["Date"]       = df_raw["Date"].apply(parse_date_fr)
    df_out["Prix_Close"] = df_raw["Prix_Close"].apply(parse_number)
    df_out["Prix_Open"]  = df_raw["Prix_Open"].apply(parse_number)  if "Prix_Open"  in df_raw.columns else None
    df_out["Prix_High"]  = df_raw["Prix_High"].apply(parse_number)  if "Prix_High"  in df_raw.columns else None
    df_out["Prix_Low"]   = df_raw["Prix_Low"].apply(parse_number)   if "Prix_Low"   in df_raw.columns else None
    df_out["Volume_Journalier"] = df_raw["Volume_Journalier"].apply(parse_volume) if "Volume_Journalier" in df_raw.columns else None

    # ── Enrichissement ────────────────────────────────────────────────────────
    df_out["Ticker"]          = ticker
    df_out["ISIN"]            = info["isin"]
    df_out["Nom"]             = info["nom"]
    df_out["Secteur"]         = info.get("secteur", "")
    df_out["Indice"]          = info.get("indice", "MASI")
    df_out["Type_Instrument"] = info.get("type", "Action")
    df_out["Devise"]          = "MAD"
    df_out["Source"]          = "INVESTING_COM"

    # ── Nettoyage final ───────────────────────────────────────────────────────
    avant = len(df_out)
    df_out = df_out.dropna(subset=["Date", "Prix_Close"])
    df_out = df_out[df_out["Prix_Close"] > 0]
    df_out = df_out.sort_values("Date").drop_duplicates(subset=["Date"])
    apres  = len(df_out)

    if avant != apres:
        log.info(f"  ℹ️  {avant - apres} lignes ignorées (date/prix invalide ou doublon)")

    return df_out


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
#  MAIN
# =============================================================================

def main():
    log.info("=" * 62)
    log.info("  BIA4 — Fusion Investing.com → Power BI")
    log.info(f"  Exécution : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"  Dossier source : {os.path.abspath(INPUT_DIR)}")
    log.info("=" * 62)

    if not os.path.isdir(INPUT_DIR):
        log.error(f"\n❌ Dossier '{INPUT_DIR}/' introuvable.")
        log.error(f"   Crée le dossier et place tes fichiers dedans :")
        log.error(f"   data_cse/BCP.xlsx, data_cse/IAM.xlsx, etc.")
        return

    # Indexer tous les fichiers disponibles (Excel + CSV, insensible à la casse)
    fichiers = {}
    for f in os.listdir(INPUT_DIR):
        nom, ext = os.path.splitext(f)
        if ext.lower() in [".xlsx", ".xls", ".csv"]:
            fichiers[nom.upper()] = os.path.join(INPUT_DIR, f)

    log.info(f"\n📂 Fichiers trouvés dans {INPUT_DIR}/ : {len(fichiers)}")
    for t in sorted(fichiers):
        log.info(f"   ✓ {os.path.basename(fichiers[t])}")

    # ── Lecture et fusion ─────────────────────────────────────────────────────
    all_data = []
    rapport  = []

    for ticker, info in TICKERS_MAP.items():
        log.info(f"\n→ {ticker} ({info['nom']})")

        if ticker not in fichiers:
            log.warning(f"  ⚠️  Fichier manquant : {ticker}.xlsx ou {ticker}.csv")
            rapport.append({
                "Ticker"  : ticker, "Nom"     : info["nom"],
                "Statut"  : "MANQUANT", "Lignes"  : 0,
                "Date_Min": "", "Date_Max": "",
                "Message" : f"{ticker}.xlsx absent du dossier {INPUT_DIR}/",
            })
            continue

        df = read_file(fichiers[ticker], ticker, info)

        if df.empty:
            rapport.append({
                "Ticker"  : ticker, "Nom"     : info["nom"],
                "Statut"  : "ERREUR", "Lignes"  : 0,
                "Date_Min": "", "Date_Max": "",
                "Message" : "Fichier lu mais aucune ligne valide — vérifier colonnes",
            })
            continue

        log.info(
            f"  ✅ {len(df)} lignes | "
            f"{df['Date'].min()} → {df['Date'].max()} | "
            f"Clôture : {df['Prix_Close'].min():.2f} → {df['Prix_Close'].max():.2f} MAD"
        )
        rapport.append({
            "Ticker"  : ticker, "Nom"     : info["nom"],
            "Statut"  : "OK",   "Lignes"  : len(df),
            "Date_Min": str(df["Date"].min()),
            "Date_Max": str(df["Date"].max()),
            "Message" : "",
        })
        all_data.append(df)

    # ── Consolidation ─────────────────────────────────────────────────────────
    if not all_data:
        log.error("\n❌ Aucun fichier valide traité.")
        log.error(f"   Place tes fichiers Excel dans {INPUT_DIR}/ et relance.")
        return

    Prix_Historique2 = pd.concat(all_data, ignore_index=True)
    Prix_Historique2 = add_volume_moyen_30j(Prix_Historique2)
    Prix_Historique2.sort_values(["Ticker", "Date"], inplace=True)

    # ── Export Prix_Historique.csv ────────────────────────────────────────────
    COLS = [
        "Date", "Ticker", "ISIN", "Nom", "Secteur", "Indice", "Type_Instrument",
        "Prix_Open", "Prix_High", "Prix_Low", "Prix_Close",
        "Volume_Journalier", "Volume_Moyen_30j", "Devise", "Source",
    ]
    for c in COLS:
        if c not in Prix_Historique2.columns:
            Prix_Historique2[c] = None

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    Prix_Historique2[COLS].to_csv(
        os.path.join(OUTPUT_DIR, "Prix_Historique2.csv"),
        index=False, encoding="utf-8-sig", sep=";"
    )

    # ── Export Dim_Actifs.csv ─────────────────────────────────────────────────
    dim = pd.DataFrame([{
        "Ticker"          : t, "ISIN"            : i["isin"],
        "Nom"             : i["nom"], "Secteur"  : i.get("secteur", ""),
        "Type_Instrument" : i.get("type", "Action"),
        "Indice"          : i.get("indice", "MASI"),
        "Marche"          : "CSE", "Devise"       : "MAD",
    } for t, i in TICKERS_MAP.items()])
    dim.to_csv(os.path.join(OUTPUT_DIR, "Dim_Actifs.csv"), index=False, encoding="utf-8-sig", sep=";")

    # ── Export rapport ────────────────────────────────────────────────────────
    df_rpt = pd.DataFrame(rapport)
    df_rpt["Date_Execution"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_rpt.to_csv(os.path.join(OUTPUT_DIR, "fusion_report.csv"), index=False, encoding="utf-8-sig", sep=";")

    # ── Résumé ────────────────────────────────────────────────────────────────
    n_ok       = sum(1 for r in rapport if r["Statut"] == "OK")
    n_manquant = sum(1 for r in rapport if r["Statut"] == "MANQUANT")
    n_erreur   = sum(1 for r in rapport if r["Statut"] == "ERREUR")

    log.info("\n" + "=" * 62)
    log.info("  RÉSUMÉ FINAL")
    log.info("=" * 62)
    log.info(f"  ✅ Actifs intégrés    : {n_ok} / {len(TICKERS_MAP)}")
    log.info(f"  ⚠️  Fichiers manquants : {n_manquant}")
    log.info(f"  ❌ Erreurs parsing    : {n_erreur}")
    log.info(f"  📊 Total lignes       : {len(Prix_Historique2)}")
    log.info(f"  📅 Période couverte   : {Prix_Historique2['Date'].min()} → {Prix_Historique2['Date'].max()}")
    log.info("  Fichiers produits :")
    log.info(f"    Prix_Historique2.csv  ({len(Prix_Historique2)} lignes)")
    log.info(f"    Dim_Actifs.csv       ({len(dim)} actifs)")
    log.info("    fusion_report.csv    (détail par actif)")
    log.info("    fusion.log           (logs complets)")
    log.info("=" * 62)

    if n_manquant > 0:
        manquants = [r["Ticker"] for r in rapport if r["Statut"] == "MANQUANT"]
        log.info(f"\n⚠️  Actifs manquants : {', '.join(manquants)}")
        log.info("   → Chercher par nom complet sur https://fr.investing.com")
        log.info("   → Onglet 'Données historiques' → Télécharger → renommer TICKER.xlsx")

    log.info("\n✅ Terminé.")
    log.info("   Power BI : Obtenir les données > Texte/CSV > Sep: ; > UTF-8")


if __name__ == "__main__":
    main()