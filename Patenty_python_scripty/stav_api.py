"""
Tento skript slouží ke stažení a uložení stavu dokumentů z veřejné databáze pomocí API.
Funkce skriptu krok za krokem:

1. Načtení dat z Excelového souboru `Results.xlsx` ze zvoleného listu `skoly data` a z vybraných sloupců Application_Number a 
    API.
   
2. Pro každý záznam v sloupci `API`:
   - Sestaví URL pro získání stavu dokumentu.
   - Odešle požadavek (HTTP GET) na server API.
   - Získá XML odpověď a pokusí se extrahovat text z elementu `<Name>` s atributem `lang="cs"`.
   - Pokud je odpověď úspěšná, přidá nalezený stav do seznamu `statuses`. V případě chyby přidá popis chyby.

3. Přidání výsledného seznamu stavů jako nový sloupec `STAV` do datového rámce `output_data`.

4. Uložení `output_data` do souboru CSV `vysledekstav.csv`.

Poznámky:
- Kód ošetřuje chyby při volání API (např. nedostupný server nebo špatná odpověď) a místo toho vrací odpovídající zprávu.
- Změny jsou uloženy pouze do nového CSV souboru, původní Excelový soubor zůstává nezměněn.
- Kód předpokládá, že API vždy vrací XML odpověď s požadovanou strukturou.

Výstup:
- CSV soubor `vysledekstav.csv` obsahující sloupce `Application_Number`, `API` a přidaný sloupec `STAV` s výslednými stavy dokumentů.
"""
import pandas as pd
import requests
import xml.etree.ElementTree as ET

data=pd.read_excel("Results.xlsx", sheet_name="skoly data")
statuses=[]
output_data = data[["Application_Number", "API"]]

for line in data["API"]:
    
    url=f"https://isdv.upv.gov.cz/webapp/resdb.ipr.status?pspis={line}"
    
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the XML content of the response
            root = ET.fromstring(response.content)
            
            # Find the <Name> element with lang="cs"
            status_name_cs = root.find(".//Name[@lang='cs']")
            
            # Extract the text if the element is found, else set a default message
            status = status_name_cs.text if status_name_cs is not None else "Status not found"
        else:
            status = "Error fetching data"

    except Exception as e:
        status = f"Request failed: {e}"
   
    # Append the status to the list
    statuses.append(status)

# Add the statuses to the output dataframe as a new column "STAV"
output_data["STAV"] = statuses

# Save the output dataframe to a new CSV file
output_data.to_csv("vysledekstav.csv", index=False)
