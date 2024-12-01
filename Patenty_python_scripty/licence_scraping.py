"""
Tento skript slouží ke stahování patentových dat z webové stránky pomocí iterativního procházení stránek.
Extrahovaná data jsou uložena do CSV souboru.

Funkce skriptu krok za krokem:

1. Definice základní URL (`base_url`) bez parametrů stránkování.
   - Každá stránka je identifikována parametrem `pRadStart`, který označuje začátek záznamů na stránce (00, 20, 40, ...).

2. Funkce `fetch_data(start)`:
   - Generuje URL s daným parametrem `start`.
   - Odesílá HTTP GET požadavek na server a ověřuje úspěšnost (status 200).
   - Pomocí knihovny BeautifulSoup parsuje HTML stránky a extrahuje řádky tabulky s třídou `trdata`.
   - Z každého řádku tabulky extrahuje jednotlivé sloupce:
     - Kód patentu (`Patent Code`)
     - Číslo patentu (`Patent Number`)
     - ID patentu (`Patent ID`)
     - Status patentu (`Status`)
     - Patentové třídy (`Classes`)
     - Název patentu (`Title`)
     - Organizaci (`Organization`).
   - Výsledná data jsou uložena do seznamu.

3. Funkce `save_to_csv(data, filename)`:
   - Přijímá seznam dat a ukládá je do CSV souboru ve formátu UTF-8.
   - Do prvního řádku zapisuje hlavičky sloupců.

4. Funkce `main()`:
   - Definuje celkový počet záznamů (`total_records`) a počet záznamů na stránku (`records_per_page`).
   - Iteruje přes stránky dat (v krocích po `records_per_page`) a volá funkci `fetch_data` pro stažení dat z každé stránky.
   - Mezi požadavky vkládá pauzu (`time.sleep(10)`), aby se server nepřetěžoval.
   - Stahování je přerušeno, pokud dojde k chybě při stahování konkrétní stránky.
   - Po stažení všech dat je volána funkce `save_to_csv`, která uloží data do souboru `malicenci.csv`.

5. Spuštění skriptu:
   - Skript se spouští funkcí `main()` a uloží výsledky do souboru `malicenci.csv`.

Poznámky:
- Skript obsahuje jednoduché ošetření chyb při stahování dat (např. HTTP status code).
- Pauzy mezi požadavky jsou nastaveny na 10 sekund, aby nedocházelo k přetěžování serveru.
- Stránkování je implementováno pomocí iterace od 0 do přibližného počtu záznamů (`total_records`).

Výstup:
- Výsledný soubor `malicenci.csv` obsahuje extrahovaná data z patentových stránek.
"""


import requests
from bs4 import BeautifulSoup
import csv
import time

# Základní URL stránky bez parametru pRadStart
base_url = "https://isdv.upv.gov.cz/webapp/resdb.print_vysledek.Vysledek?pIdDotaz=RES0000000032737595ctFSDVuH&pLang=CS&pRadStart=00"

# Funkce pro stažení dat ze stránky
def fetch_data(start):
    # Vytvoříme URL, která obsahuje správnou hodnotu start (00, 20, 40, ..., 100, 120, ...)
    url = f"{base_url}{start}"
    print(f"Stahuji data z URL: {url}")  # Pro kontrolu tiskneme URL

    response = requests.get(url)
    
    # Ověření, že request byl úspěšný
    if response.status_code != 200:
        print(f"Chyba při stahování stránky: {response.status_code}")
        return None

    # Parsování HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Najdeme všechny řádky s třídou "trdata"
    rows = soup.find_all('tr', class_='trdata')

    data = []
    for row in rows:
        # Extrahujeme jednotlivé sloupce (td) z řádku
        cols = row.find_all('td')
        
        # Každý sloupec obsahuje specifická data
        patent_code = cols[1].get_text(strip=True)
        patent_number = cols[2].get_text(strip=True)
        patent_id = cols[3].get_text(strip=True)
        patent_status = cols[4].get_text(strip=True)
        patent_classes = cols[5].get_text(strip=True)
        patent_title = cols[6].get_text(strip=True)
        organization = cols[7].get_text(strip=True)

        # Uložíme řádek jako seznam
        data.append([patent_code, patent_number, patent_id, patent_status, patent_classes, patent_title, organization])

    return data

# Uložení dat do CSV souboru
def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Předpokládáme názvy sloupců podle dat, která extrahujeme
        writer.writerow(['Patent Code', 'Patent Number', 'Patent ID', 'Status', 'Classes', 'Title', 'Organization'])
        writer.writerows(data)

# Hlavní logika pro stránkování a stahování dat
def main():
    all_data = []
    total_records = 700  # Přibližný celkový počet záznamů
    records_per_page = 500  # Kolik záznamů je na jedné stránce

    for start in range(0, total_records, records_per_page):
        formatted_start = str(start)  # Upravíme start na prosté číslo
        print(f"Stahuji data od záznamu {formatted_start}...")
        data = fetch_data(formatted_start)
        if data:
            all_data.extend(data)
        else:
            print(f"Nepodařilo se stáhnout data pro start {formatted_start}. Končím.")
            break  # Pokud se nepodaří stáhnout data, přestaneme procházet další stránky
        time.sleep(10)  # Pauza mezi requesty, aby se server nepřetěžoval

    # Uložení dat do CSV souboru
    save_to_csv(all_data, 'malicenci.csv')
    print("Data byla uložena do 'malicenci.csv'.")

if __name__ == "__main__":
    main()
