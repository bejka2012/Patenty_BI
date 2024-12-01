"""
Tento skript slouží k analýze PDF souborů uložených ve složce a jejích podsložkách. 
Cílem je identifikovat řádky obsahující text odpovídající regulárnímu výrazu 
pro "Příjmy z licenčních smluv" a z těchto řádků extrahovat číselné hodnoty (A, B, C), 
kde A + B = C.

### Funkce skriptu:

1. **Načítání textu z PDF souborů:**
   - Funkce `extract_text_from_pdf(pdf_path)` iteruje přes všechny stránky PDF a extrahuje text.

2. **Vyhledávání odpovídajících řádků:**
   - Regulární výraz `pattern` hledá řádky obsahující text "Příjmy z licenčních smluv" (s volitelným "(2)").
   - Funkce `find_lines_with_pattern(text, pattern)` identifikuje odpovídající řádky v textu.

3. **Zpracování čísel na řádcích:**
   - Funkce `parse_number(number_str)` převádí čísla s čárkou na desetinná čísla.
   - Funkce `find_combination(numbers)` hledá správnou kombinaci čísel A, B, C, kde A + B = C.
   - Funkce `process_line_for_numbers(line)` extrahuje čísla z řádku, hledá kombinaci A, B, C a vrací je.

4. **Iterace přes PDF soubory:**
   - Skript prochází všechny PDF soubory ve složce `pdf_folder` a jejích podsložkách pomocí `os.walk`.
   - Pro každý soubor:
     - Extrahuje text.
     - Vyhledává řádky odpovídající regulárnímu výrazu.
     - Ze zjištěných řádků se pokouší identifikovat čísla A, B, C.

5. **Ukládání výsledků:**
   - Výsledky jsou zapisovány do CSV souboru `output.csv` ve složce `pdf_folder`.
   - Každý řádek obsahuje:
     - Název podsložky (`Nazev podsložky`),
     - Název PDF souboru (`Nazev souboru`),
     - Řádek odpovídající vzoru (`Matching Line`),
     - Číselné hodnoty A, B, C (pokud jsou nalezeny; jinak `None`).

6. **Ošetření chyb:**
   - Skript ošetřuje chyby při čtení PDF souborů a pokračuje se zpracováním dalších souborů, pokud k chybě dojde.
   - Chyby jsou zobrazeny na konzoli.

### Výstup:
- CSV soubor `output.csv` obsahuje následující sloupce:
  - Název podsložky,
  - Název PDF souboru,
  - Řádek textu odpovídající vzoru,
  - Hodnoty A, B, C, kde A + B = C (nebo `None`, pokud nebyly nalezeny).

### Poznámky:
- Regulární výraz je robustní vůči mezera/znakové variace (například "Příjmy z l i c e n č n í ch smluv").
- Skript předpokládá, že čísla na řádcích jsou oddělena mezerami.
- Pokud A + B = C není nalezeno, záznam se uloží s hodnotami `None`.
"""



import os
import re
import csv
from PyPDF2 import PdfReader

# Cesta k hlavní složce s podsložkami a PDF soubory
pdf_folder = r"C:\Users\Lenovo\Desktop\vsechnyUNI\Patenty_vyrocni_zpravy"

# Cesta k výstupnímu CSV souboru
output_file_path = os.path.join(pdf_folder, "output.csv")

# Regulární výraz pro hledání řádků s textem "Příjmy z licenčních smluv" s volitelným "(2)"
pattern = re.compile(r'[Pp].+y.+z(.)?l(\s.)?i(\s.)?c(\s.)?e(\s.)?n(\s.)?č(\s.)?n(\s.)?í(\s.)?ch(\s.)? s(\s.)?m(\s.)?l(\s.)?u(\s.)?v( \(2\))?')

# Funkce pro načtení textu z PDF
def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page_num in range(len(reader.pages)):
        text += reader.pages[page_num].extract_text()
    return text

# Funkce pro hledání odpovídajících řádků
def find_lines_with_pattern(text, pattern):
    lines = text.splitlines()  # Rozdělit text na řádky
    matching_lines = [line.strip() for line in lines if pattern.search(line)]  # Odstranit prázdné znaky pomocí strip()
    return matching_lines

# Funkce pro převod čísla s čárkou na desetinné číslo
def parse_number(number_str):
    # Nahraď čárku tečkou pro správný převod na číslo
    return float(number_str.replace(",", "."))

# Funkce pro nalezení správné kombinace A + B = C
def find_combination(numbers):
    # Pokud máme pouze 2 čísla, může se jednat o A = C a B = 0
    if len(numbers) == 2:
        A, C = numbers
        B = 0
        if A == C:
            return A, B, C
    
    # Pokud máme více než 2 čísla, hledáme kombinaci A + B = C
    for i in range(1, len(numbers)):
        try:
            A = float(''.join(map(lambda x: str(int(x)), numbers[:i])))  # Spojíme první část
            for j in range(i+1, len(numbers)+1):
                B = float(''.join(map(lambda x: str(int(x)), numbers[i:j])))  # Spojíme druhou část
                C = float(''.join(map(lambda x: str(int(x)), numbers[j:])))  # Spojíme zbytek
                if A + B == C:
                    return A, B, C
        except ValueError:
            # Pokud dojde k chybě, vrátíme None
            continue
    return None

# Funkce pro zpracování řádku a nalezení čísel A, B, C
def process_line_for_numbers(line):
    # Najdi čísla na konci řádku po textu "smluv" nebo "smluv (x)"
    match = re.search(r"smluv(?:\s*\(\d*\))?\s*(.*)", line)
    if match:
        numbers_str = match.group(1).strip()
        if numbers_str:
            try:
                # Rozděl čísla podle mezer
                numbers = [parse_number(num) for num in numbers_str.split()]

                # Najdi kombinaci A + B = C
                result = find_combination(numbers)
                if result:
                    A, B, C = result
                    return A, B, C
            except ValueError:
                # Pokud dojde k chybě při zpracování čísel, vrátíme None
                return None
    return None

# Otevřít výstupní CSV soubor pro zápis (přepíše existující soubor)
with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Zapsat hlavičku do CSV
    csvwriter.writerow(['Nazev podsložky', 'Nazev souboru', 'Matching Line', 'A', 'B', 'C'])

    # Projít všechny PDF soubory ve složce a v podsložkách
    for root, dirs, files in os.walk(pdf_folder):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                folder_name = os.path.basename(root)  # Název podsložky
                print(f"Zpracovávám soubor: {filename} v podsložce: {folder_name}")
                
                try:
                    # Načíst text z PDF
                    text = extract_text_from_pdf(pdf_path)
                    
                    # Najít řádky s požadovaným vzorem
                    matching_lines = find_lines_with_pattern(text, pattern)
                    
                    # Zapsat nalezené řádky do CSV a hledat A, B, C
                    if matching_lines:
                        for line in matching_lines:
                            numbers = process_line_for_numbers(line)
                            if numbers:
                                A, B, C = numbers
                                csvwriter.writerow([folder_name, filename, line, A, B, C])
                            else:
                                csvwriter.writerow([folder_name, filename, line, None, None, None])
                    else:
                        print(f"V souboru {filename} nebyly nalezeny odpovídající řádky.")
                
                except Exception as e:
                    # Pokud dojde k jakékoli chybě, soubor přeskoč a pokračuj
                    print(f"Chyba při zpracování souboru {filename}: {e}")
                    continue
