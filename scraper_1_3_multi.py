import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
import time

options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--remote-allow-origins=*")

DRIVER_PATH = r"C:\Users\CHOUACHELHASSANE\Downloads\edgedriver_win64\msedgedriver.exe"

driver = webdriver.Edge(service=Service(DRIVER_PATH), options=options)

all_products = []

try:
    for page in range(1, 6):  # 5 pages
        url = f"https://www.producthunt.com/search?q=mental+health+ai&page={page}"
        print(f"\nScraping page {page}...")
        driver.get(url)
        time.sleep(10)

        all_buttons = driver.find_elements(By.TAG_NAME, "button")

        for btn in all_buttons:
            data_test = btn.get_attribute("data-test")
            if data_test and "spotlight-result-product" in data_test:
                try:
                    text_content = btn.text.split('\n')
                    if len(text_content) >= 2:
                        name = text_content[0]
                        tagline = text_content[1]
                        product_id = data_test.split('-')[-1]

                        if not any(p["id"] == product_id for p in all_products):
                            all_products.append({
                                "id": product_id,
                                "name": name,
                                "tagline": tagline
                            })
                            print(f"✅ {name}")
                except:
                    continue

        # نحفظو بعد كل page
        with open("producthunt.json", "w", encoding="utf-8") as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        print(f"💾 {len(all_products)} produits sauvegardés jusqu'ici...")

finally:
    if all_products:
        pd.DataFrame(all_products).to_csv("producthunt.csv", index=False)
        print(f"\nDone! {len(all_products)} produits sauvegardés.")
    driver.quit()