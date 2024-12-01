"""
Tento skript slouží ke zpracování XML souborů uložených v zadané složce. Extrahuje informace
o číslech žádostí, datu podání a klasifikaci IPCR (MPT) a ukládá je do CSV souboru.
Funkce skriptu krok za krokem:

1. Načtení seznamu platných Application Numbers z Excelového souboru `faktovka.xlsx`.
   - Excel soubor musí obsahovat sloupec `Application_number`.
   - Používají se pouze ty záznamy z XML, které odpovídají číslům z Excelového souboru.

2. Zpracování XML souborů:
   - Iteruje přes všechny XML soubory ve složce zadané v `folder_path`.
   - Z každého souboru extrahuje:
     - Číslo žádosti (`Application Number`) pomocí namespace `pat` a `com`.
     - Datum podání (`Filing Date`).
       - Přeskočí soubory s datem podání <= 2012.
     - Klasifikaci IPCR (`MPT`).
       - Zabezpečí, že nedojde k duplikaci IPCR klasifikací.

3. Uložení výsledků do CSV:
   - Výstupní soubor je uložen na cestě definované `output_csv`.
   - Každý záznam obsahuje:
     - Číslo žádosti (`Application Number`),
     - Klasifikaci MPT (`MPT`),
     - Datum podání (`Filing Date`),
     - Název zpracovaného souboru (`File Name`).

4. Ošetření chyb:
   - Pokud dojde k chybě při zpracování XML souboru nebo jeho částí, zobrazí se odpovídající chybová zpráva.
   - Pokud datum podání není ve správném formátu, soubor se přeskočí.

5. Výstup:
   - Vytvořený CSV soubor obsahuje všechny zpracované informace a je uložen ve formátu UTF-8 se správnou podporou českých znaků.
   - Název souboru je definován v `output_csv`.

Poznámky:
- Namespace `pat` a `com` je předdefinován pro práci se standardní strukturou XML dokumentů.
- Pokud `Application_number` není nalezen v Excelovém souboru, zpracování se ukončí s chybovou zprávou.
- Skript zabezpečuje, že nedochází k duplikaci IPCR klasifikací v rámci jednoho záznamu.
"""

import csv
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd

# Cesty k souborům
folder_path = r'C:\Users\Lenovo\Desktop\PROJEKT DATA PV\XML'
output_csv = r'C:\Users\Lenovo\Python\PROJEKT\MPTPV.csv'
excel_file_path = r'C:\Users\Lenovo\Desktop\faktovka.xlsx'

print("work in process")

# Načtení Excel souboru s Application Numbers
try:
    excel_data = pd.read_excel(excel_file_path)
    if 'Application_number' not in excel_data.columns:
        raise KeyError("Sloupec 'Application_number' nebyl nalezen v Excel souboru. Zkontrolujte název sloupce.")
    valid_application_numbers = set(excel_data['Application_number'].astype(str))
except Exception as e:
    print(f"Chyba při načítání Excel souboru: {e}")
    exit()

# Namespace dictionary for XML parsing (including 'com' and 'pat' namespaces)
namespaces = {
    'pat': 'http://www.wipo.int/standards/XMLSchema/ST96/Patent',
    'com': 'http://www.wipo.int/standards/XMLSchema/ST96/Common'
}

# Open CSV file for writing with UTF-8 encoding that supports Czech characters
with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write header
    headers = ['Application Number', 'MPT', 'Filing Date', 'File Name']
    csv_writer.writerow(headers)

    # Loop through all XML files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xml'):
            file_path = os.path.join(folder_path, file_name)
            
            # Parse the XML file
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
                # Extract Application Number
                application_number_element = root.find('.//pat:ApplicationIdentification/com:ApplicationNumber/com:ApplicationNumberText', namespaces)
                application_number = application_number_element.text.strip() if application_number_element is not None else 'N/A'
                
                # Přeskočit zpracování, pokud Application Number není v Excel souboru
                if application_number not in valid_application_numbers:
                    continue

                # Extract Filing Date and check if it is <= 2012
                filing_date_element = root.find('.//pat:ApplicationIdentification/pat:FilingDate', namespaces)
                if filing_date_element is not None:
                    filing_date = filing_date_element.text.strip()
                    # Convert string to datetime object
                    try:
                        filing_date_obj = datetime.strptime(filing_date, '%Y-%m-%d')
                    except ValueError:
                        print(f"Error parsing filing date {filing_date} in file {file_name}")
                        continue
                    
                    # Skip if filing date is <= 2012
                    if filing_date_obj.year <= 2012:
                        continue  # Skip this file and move to the next one
                
                # Extract IPCRClassification (MPT) and avoid duplicates
                ipcr_classifications = set()  # Use a set to avoid duplicates
                bibliographic_data = root.find('.//pat:BibliographicData', namespaces)
                if bibliographic_data is not None:
                    for ipcr_bag in bibliographic_data.findall('.//pat:IPCRClassificationBag', namespaces):
                        for ipcr_classification in ipcr_bag.findall('.//pat:IPCRClassification', namespaces):
                            section = ipcr_classification.find('.//pat:Section', namespaces)
                            cls = ipcr_classification.find('.//pat:Class', namespaces)
                            if section is not None and cls is not None:
                                ipcr_classifications.add(f"{section.text}{cls.text}")

                # Write each unique IPCR classification in a new row
                for mpt in sorted(ipcr_classifications):
                    csv_writer.writerow([
                        application_number,
                        mpt,
                        filing_date,
                        file_name
                    ])
                    
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

print(f"CSV file created: {output_csv}")
