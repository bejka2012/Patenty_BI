"""
Tento skript stahuje všechny ZIP soubory z uvedené webové stránky, extrahuje jejich obsah
a přesouvá XML soubory do specifikované složky. Zbytek obsahu je smazán. Výsledky jsou
zalogovány do CSV souboru.

### Funkce:
1. `download_zip(url, download_folder)`: Stahuje ZIP soubory ze zadané URL do složky.
2. `extract_zip(zip_path, extract_to)`: Extrahuje obsah ZIP souboru do určené složky.
3. `move_xml_files(extract_folder, target_folder)`: Přesouvá XML soubory do cílové složky
   a maže ostatní soubory.
4. `create_log(csv_file, zip_filename, xml_files)`: Ukládá informace o zpracování do CSV souboru.

### Proces:
- Stahování všech ZIP souborů z webové stránky.
- Extrakce obsahu ZIP souborů.
- Přesun XML souborů do cílové složky a mazání ostatních souborů.
- Zalogování výsledků zpracování do souboru `log.csv`.

### Výstup:
- XML soubory v cílové složce.
- Log CSV obsahující název ZIP souboru a seznam zpracovaných XML souborů.
"""


import requests
import zipfile
import os
import shutil
import csv
from bs4 import BeautifulSoup

# Funkce pro stažení souboru ze zadané URL
def download_zip(url, download_folder):
    try:
        print(f"Stahuji soubor z: {url}")
        response = requests.get(url)
        response.raise_for_status()  # Ověří, zda nedošlo k chybě
        filename = os.path.join(download_folder, url.split("/")[-1])
        with open(filename, "wb") as file:
            file.write(response.content)
        print(f"Soubor stažen: {filename}")
        return filename
    except Exception as e:
        print(f"Chyba při stahování souboru: {e}")
        return None

# Funkce pro extrahování zip souboru do zadané složky
def extract_zip(zip_path, extract_to):
    try:
        print(f"Extrahuji soubor: {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"Extrahováno do: {extract_to}")
    except Exception as e:
        print(f"Chyba při extrahování ZIP souboru: {e}")

# Funkce pro hledání XML souborů a jejich přesunutí do jiné složky
def move_xml_files(extract_folder, target_folder):
    xml_files = []
    print(f"Hledám XML soubory ve složce: {extract_folder}")
    try:
        for root, dirs, files in os.walk(extract_folder):
            for file in files:
                if file.endswith('.xml'):
                    # Přesun XML souboru do zadané složky
                    source_path = os.path.join(root, file)
                    target_path = os.path.join(target_folder, file)
                    shutil.move(source_path, target_path)
                    xml_files.append(file)
                else:
                    # Pokud není soubor XML, smažeme ho
                    os.remove(os.path.join(root, file))
        print(f"Přesunuto XML souborů: {xml_files}")
    except Exception as e:
        print(f"Chyba při přesunu XML souborů: {e}")
    return xml_files

# Funkce pro vytvoření CSV logu
def create_log(csv_file, zip_filename, xml_files):
    try:
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([zip_filename] + xml_files)
        print(f"Log vytvořen pro soubor: {zip_filename}")
    except Exception as e:
        print(f"Chyba při vytváření logu: {e}")

# Hlavní skript pro provedení celého procesu
def main():
    # URL stránky
    base_url = "https://isdv.upv.gov.cz/webapp/webapp.pubsrv.seznam?pid=41"
    
    # Cílové složky
    download_folder = r"C:\Users\Lenovo\Desktop\PROJEKT DATA XML"
    xml_target_folder = os.path.join(download_folder, "XML")
    log_file = os.path.join(download_folder, "log.csv")
    
    # Vytvoření složek, pokud neexistují
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(xml_target_folder, exist_ok=True)
    
    # Stáhneme stránku a zpracujeme odkazy na ZIP soubory
    try:
        print(f"Stahuji stránku: {base_url}")
        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Hledání všech .zip odkazů
        zip_links = [link['href'] for link in soup.find_all('a') if link['href'].endswith('.zip')]
        if not zip_links:
            print("Nebyl nalezen žádný odkaz na ZIP soubor.")
            return
        
        for zip_link in zip_links:
            full_zip_url = f"https://isdv.upv.gov.cz{zip_link}"
            
            # Stažení ZIP souboru
            zip_file = download_zip(full_zip_url, download_folder)
            if not zip_file:
                continue
            
            # Extrakce ZIP souboru
            extract_folder = os.path.splitext(zip_file)[0]  # Cílová složka pro extrakci
            os.makedirs(extract_folder, exist_ok=True)
            extract_zip(zip_file, extract_folder)
            
            # Přesun XML souborů a smazání ostatních
            xml_files = move_xml_files(extract_folder, xml_target_folder)
            
            # Logování výsledků
            create_log(log_file, os.path.basename(zip_file), xml_files)
            
            # Smazání extrahované složky a původního ZIP souboru
            shutil.rmtree(extract_folder)
            os.remove(zip_file)
    
    except Exception as e:
        print(f"Chyba při zpracování stránky nebo souborů: {e}")

if __name__ == "__main__":
    main()