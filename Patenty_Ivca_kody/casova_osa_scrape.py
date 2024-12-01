"""
Tento skript slouží ke stahování dat o přihláškách patentů z veřejného rozhraní ISDV
a k vytváření časových os pro každou přihlášku. Výsledky jsou uloženy do CSV souboru. Nutno podotknout, že kód
je nefunkční, protože se mi nepodařilo vyřešit problém se získáním pD, které se generuje dynamicky pro každý
jednotlivý dotaz. Pokud jsem pD nastavila dle aktuálního get_id přímo na webu, tak kód stáhnul data, ale
úplně stejná pro jakékoli hodnoty. Snažila jsem se nastavit kód tak, aby pro každý dotaz nejprve získal
id dotaz, ale nefungovalo to.

### Funkce skriptu:

1. **Načtení dat z Excel souboru:**
   - Skript načítá Excel soubor `results.xlsx` obsahující sloupce `Application_Number` (čísla přihlášek)
     a `TYP_CISLO` (typy patentů).
   - Pracuje s prvním listem `skoly data`. 

2. **Iterace přes přihlášky a typy patentů:**
   - Zpracovává prvních několik přihlášek pro ukázkové použití.
   - Pro každou přihlášku provádí následující kroky:

   **Krok 1: Získání iddotaz**
   - Pomocí API získá jedinečný identifikátor dotazu (`iddotaz`).

   **Krok 2: Inicializace dotazu**
   - Vytvoří dotaz na základě čísla přihlášky (`Application_Number`) a typu patentu (`TYP_CISLO`).
   - Odesílá POST požadavek na server pro inicializaci dotazu.

   **Krok 2.5: Validace hitlistu**
   - Ověřuje, zda je dotaz správně připravený a výsledky jsou dostupné.

   **Krok 3: Provedení dotazu**
   - Spouští dotaz a ověřuje jeho úspěšnost.

   **Krok 4: Získání pIdSpis**
   - Načítá jedinečný identifikátor patentu (`pIdSpis`) z výsledků dotazu.

   **Krok 5: Stahování časové osy**
   - Odesílá POST požadavek k získání časové osy (například dat událostí spojených s přihláškou).
   - Časová osa obsahuje:
     - Datum události.
     - Popis události.

3. **Uložení dat do CSV:**
   - Výsledky časových os pro jednotlivé přihlášky jsou ukládány do CSV souboru `casova_osa.csv`.
   - Každý řádek obsahuje:
     - Číslo přihlášky (`Nazev prihlasky`),
     - Datum (`Datum`),
     - Popis události (`Popis`).

### Funkce:
- `get_dotaz_id()`: Získá jedinečný `iddotaz` z API.
- `validate_hitlist()`: Ověří dostupnost výsledků dotazu.
- `execute_dotaz(iddotaz)`: Spustí dotaz a ověří jeho úspěšnost.
- `get_pIdSpis(iddotaz)`: Načte `pIdSpis` z výsledků dotazu.
- `main()`: Hlavní funkce, která iteruje přes přihlášky a řídí celý proces stahování.

### Ošetření chyb:
- Skript kontroluje stavové kódy HTTP požadavků a zpracovává chyby jako:
  - Nedostupnost serveru.
  - Neúspěšná inicializace nebo provedení dotazu.
  - Chyby při zpracování HTML odpovědí.

### Výstup:
- CSV soubor `casova_osa.csv` obsahuje časové osy pro jednotlivé přihlášky.

### Poznámky:
- Skript zahrnuje pauzy (`time.sleep`) mezi požadavky, aby se server nepřetěžoval.
- Předpokládá specifickou strukturu odpovědí serveru, která musí být konzistentní.
- 
"""



import requests
import pandas as pd
import csv
import time
from bs4 import BeautifulSoup


# Funkce pro získání iddotaz
def get_dotaz_id():
    """Získá nový iddotaz ze serveru."""
    url = "https://isdv.upv.gov.cz/webapp/resdb.dotaz.getDotazID"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Chyba při získávání iddotaz, status code: {response.status_code}")
        return None
    return response.text.strip()

# Funkce pro validaci hitlistu
def validate_hitlist():
    """Validuje seznam výsledků před provedením dotazu."""
    url = "https://isdv.upv.gov.cz/webapp/resdb.hitlist.isEmpty"
    params = {
        "pFrmId": "PT",
        "pD": int(time.time() * 1000)  # Generování pD
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
    }
    response = requests.post(url, params=params, headers=headers)
    if response.status_code == 200:
        print("Odpověď serveru (validate_hitlist):")
        print(response.text.strip())
        if response.text.strip() == "A":
            print("Validace hitlistu byla úspěšná.")
            return True
        else:
            print("Validace hitlistu selhala.")
            return False
    else:
        print(f"Chyba při validaci hitlistu, status code: {response.status_code}")
        print(f"Odpověď serveru:\n{response.text}")
        return False

# Funkce pro spuštění dotazu
def execute_dotaz(iddotaz):
    """Spustí dotaz a vrátí potvrzení."""
    url = f"https://isdv.upv.gov.cz/webapp/resdb.dotaz.proveddotazsql"
    params = {
        "PIDDOTAZ": iddotaz,
        "PPOZICE": "0"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
    }
    print(f"Volám execute_dotaz s params: {params}")
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        print("Odpověď serveru (execute_dotaz):")
        print(response.text.strip())
        if "OK" in response.text.strip():
            print("Dotaz byl úspěšně proveden.")
            return True
        else:
            print("Dotaz nebyl úspěšně proveden. Odpověď serveru nenaznačuje úspěch.")
            return False
    else:
        print(f"Chyba při provádění dotazu, status code: {response.status_code}")
        print(f"Odpověď serveru:\n{response.text}")
        return False

# Funkce pro získání pIdSpis
def get_pIdSpis(iddotaz):
    """Načte pIdSpis z výsledků dotazu."""
    url = f"https://isdv.upv.gov.cz/webapp/resdb.print_vysledek.Vysledek"
    params = {
        "pIdDotaz": iddotaz,
        "pLang": "CS",
        "pRadStart": "0"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        print(f"Chyba při získávání pIdSpis pro iddotaz {iddotaz}, status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    spis_element = soup.find('input', {'class': 'hitlist', 'data-id': True})
    if spis_element:
        return spis_element['data-id']

    print(f"pIdSpis nebyl nalezen pro iddotaz {iddotaz}.")
    return None

# Hlavní logika pro čtení dat a generování časové osy
def main():
    # Načtení seznamu přihlášek a typů patentu ze souboru results.xlsx
    excel_data = pd.read_excel('results.xlsx', sheet_name="skoly data")
    application_numbers = excel_data['Application_Number'].tolist()
    patent_types = excel_data['TYP_CISLO'].tolist()  # Dynamické načtení typu patentu

    # Otevřeme soubor CSV pro zápis všech dat
    with open('casova_osa.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Zapisujeme hlavičku CSV souboru
        writer.writerow(["Nazev prihlasky", "Datum", "Popis"])

        # Iterace přes první tři přihlášky a typy patentu
        for application_number, patent_type in zip(application_numbers[:3], patent_types[:3]):
            print(f"Zpracovávám přihlášku: {application_number} s typem patentu: {patent_type}")

            # Krok 1: Získání iddotaz
            iddotaz = get_dotaz_id()
            if not iddotaz:
                print(f"Chyba při získávání iddotaz pro {application_number}")
                continue

            # Krok 2: Inicializace dotazu pomocí POST požadavku
            url1 = "https://isdv.upv.gov.cz/webapp/!resdb.formxml.make"
            data1 = {
                "idform": "PT",
                "formtyp": "A",
                "iddotaz": iddotaz,
                "iduser": "-1",
                "lan": "CS",
                "dotaz/polozka[2]/@co": "CIPV",
                "dotaz/polozka[2]/@jak": "=",
                "dotaz/polozka[2]/hodnota": application_number,
                "dotaz/polozka[9]/@co": "SKUP",
                "dotaz/polozka[9]/hodnota": patent_type,
            }

            response1 = requests.post(url1, data=data1)
            if response1.status_code != 200:
                print(f"Chyba při inicializaci dotazu pro {application_number}, status code: {response1.status_code}")
                continue

            print("Dotaz úspěšně inicializován.")

            # Krok 2.5: Validace hitlistu
            if not validate_hitlist():
                print("Validace hitlistu selhala, přerušení procesu.")
                continue

            # Krok 3: Provedení dotazu
            if not execute_dotaz(iddotaz):
                print("Dotaz nebyl úspěšně proveden, přerušení procesu.")
                continue

            # Krok 4: Získání pIdSpis z výsledků dotazu
            pIdSpis = get_pIdSpis(iddotaz)
            if not pIdSpis:
                print(f"Chyba: Nepodařilo se získat pIdSpis pro {application_number}")
                continue

            print(f"Získaný pIdSpis: {pIdSpis}")

            # Krok 5: Získání časové osy (POST)
            url3 = "https://isdv.upv.gov.cz/webapp/resdb.print_detail.Detail"
            data3 = {
                "pIdSpis": pIdSpis,
                "pLang": "CS",
                "pIdDotaz": iddotaz,
                "pD": int(time.time() * 1000)
            }

            response3 = requests.post(url3, data=data3)
            if response3.status_code != 200:
                print(f"Chyba při získávání časové osy pro {application_number}, status code: {response3.status_code}")
                continue

            # Zpracování odpovědi
            soup = BeautifulSoup(response3.text, 'html.parser')
            casosaobal_div = soup.find('div', {'class': 'casosaobal'})
            if casosaobal_div:
                timeline_points = casosaobal_div.find_all('div', {'class': 'tlpoint'})
                for point in timeline_points:
                    date = point.find('span', {'class': 'dtm'}).text.strip()
                    description = point.find('p').text.strip()
                    writer.writerow([application_number, date, description])

                print(f"Data pro přihlášku {application_number} byla úspěšně uložena.")
            else:
                print(f"Data pro přihlášku {application_number} nebyla nalezena.")

    print("Proces stahování dokončen.")

if __name__ == "__main__":
    main()
