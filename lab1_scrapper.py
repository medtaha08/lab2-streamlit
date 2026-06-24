import requests

# URL GitHub search
url = "https://github.com/search?q=mental+health+ai&type=repositories"

# Headers 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
}

# request
response = requests.get(url, headers=headers)

# status code
print(f"Status Code: {response.status_code}")

# Writing HTML in file
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Done! Ouvrez output.txt pour voir le HTML")