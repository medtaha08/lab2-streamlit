import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Mapping tickers portefeuille -> codes CSE
TICKERS_MAP = {
    "ADH": {"nom": "Groupe Addoha", "isin": "MA0000011884"},
    "IAM": {"nom": "Maroc Telecom", "isin": "MA0000010373"},
    "BCP": {"nom": "Banque Centrale Populaire", "isin": "MA0000012278"},
    "TGCC": {"nom": "TGCC S.A", "isin": "MA0000012245"},
    "MUT": {"nom": "Mutandis SCA", "isin": "MA0000012245"},
    "CFG": {"nom": "CFG Bank", "isin": "MA0000012351"},
    "HPS": {"nom": "HPS", "isin": "MA0000011736"},
    "CTM": {"nom": "CTM", "isin": "MA0000010928"},
    "CMGP": {"nom": "CMGP Group", "isin": "MA0000012245"},
    "AKD": {"nom": "Akdital", "isin": "MA0000012890"},
    # ... (29 actifs au total)
}

def fetch_prices_casablanca(ticker: str, isin: str, date_debut: str = "2015-01-01") -> pd.DataFrame:
    """
    Collecte les prix historiques depuis casablanca-bourse.com.
    Retourne un DataFrame avec colonnes : Date, Ticker, Prix_Close, Volume.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
    })
    
    base_url = "https://www.casablanca-bourse.com/bourseweb/"
    url = f"{base_url}cours-historique.aspx?code={isin}"
    
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Erreur collecte {ticker}: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", {"id": "GridView1"})
    
    if not table:
        logging.warning(f"Table non trouvee pour {ticker}")
        return pd.DataFrame()

    rows = table.find_all("tr")[1:]  # skip header
    data = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            try:
                data.append({
                    "Date": pd.to_datetime(cols[0].text.strip(), format="%d/%m/%Y"),
                    "Ticker": ticker,
                    "Prix_Close": float(cols[1].text.strip().replace(" ", "").replace(",", ".")),
                    "Volume": int(cols[2].text.strip().replace(" ", "").replace("\xa0", "")),
                })
            except (ValueError, IndexError) as e:
                logging.debug(f"Ligne ignoree ({ticker}): {e}")
                
    return pd.DataFrame(data)

def collect_all_tickers(tickers_map: dict, output_path: str = "Prix_Historique.csv") -> None:
    """Boucle sur tous les tickers et consolide dans un seul CSV."""
    all_data = []
    
    for ticker, info in tickers_map.items():
        logging.info(f"Collecte : {ticker} ({info['nom']})")
        df = fetch_prices_casablanca(ticker, info["isin"])
        if not df.empty:
            all_data.append(df)
        
        time.sleep(1.2) # pause entre requetes pour la sécurité

    if all_data:
        prix_hist = pd.concat(all_data, ignore_index=True)
        prix_hist.sort_values(["Ticker", "Date"], inplace=True)
        prix_hist.to_csv(output_path, index=False, encoding="utf-8-sig")
        logging.info(f"Export : {len(prix_hist)} lignes -> {output_path}")
    else:
        logging.error("Aucune donnee collectee.")

if __name__ == "__main__":
    collect_all_tickers(TICKERS_MAP)