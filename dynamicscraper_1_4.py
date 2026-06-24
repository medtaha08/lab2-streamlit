import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time

# 1. Configuration simplifiée
options = Options()
# options.add_argument("--headless") # Désactive le headless pour VOIR ce qui bloque
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--remote-allow-origins=*")

DRIVER_PATH = r"C:\Users\CHOUACHELHASSANE\Downloads\edgedriver_win64\msedgedriver.exe"

ROOT_DATA_PATH = "./data_cse"

try:
    driver = webdriver.Edge(service=Service(DRIVER_PATH), options=options)
    url = "https://www.producthunt.com/search?q=mental+health+ai"
    
    print("Ouverture du navigateur...")
    driver.get(url)
    
    # 2. Pause généreuse pour laisser le JS et les protections charger
    print("Attente de 10 secondes (chargement complet)...")
    time.sleep(10) 

    # 3. Extraction par tag générique (plus robuste)
    # On cherche tous les boutons, puis on filtre ceux qui ont le bon attribut
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    
    products = []
    for btn in all_buttons:
        data_test = btn.get_attribute("data-test")
        if data_test and "spotlight-result-product" in data_test:
            try:
                # On essaie d'extraire le texte brut du bouton
                text_content = btn.text.split('\n')
                if len(text_content) >= 2:
                    name = text_content[0]
                    tagline = text_content[1]
                    
                    products.append({
                        "id": data_test.split('-')[-1],
                        "name": name,
                        "tagline": tagline
                    })
                    print(f"✅ Trouvé : {name}")
            except:
                continue

    # 4. Sauvegarde
    if products:
        with open("producthunt.json", "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        pd.DataFrame(products).to_csv("producthunt.csv", index=False)
        print(f"\nSuccès ! {len(products)} produits extraits.")
    else:
        print("Désolé, aucun produit trouvé. Le site bloque peut-être ton IP ou le driver.")

except Exception as e:
    print(f"Erreur : {e}")

finally:
    if 'driver' in locals():
        driver.quit()