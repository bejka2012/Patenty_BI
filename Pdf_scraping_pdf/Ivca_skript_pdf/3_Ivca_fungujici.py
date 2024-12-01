import os
import re
import csv
from PyPDF2 import PdfReader

# Cesta k složce s PDF soubory
pdf_folder = r"C:\Users\beata\OneDrive\Dokumenty\Others\IT\Digitální akademie Czechitas\Projekt_DA_patenty\Patenty_vyrocni_zpravy\14_UK"

# Cesta k výstupnímu CSV souboru
output_file = r"C:\Users\beata\OneDrive\Dokumenty\Others\IT\Digitální akademie Czechitas\Projekt_DA_patenty\Patenty_python\vystupIvca.csv"

# Regulární výraz pro hledání řádků s textem "Příjmy z licenčních smluv" s volitelným "(2)"
pattern = re.compile(r'Příjmy z licenčních smluv( \(2\))?')

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
        A = float(''.join(map(lambda x: str(int(x)), numbers[:i])))  # Spojíme první část
        for j in range(i+1, len(numbers)+1):
            B = float(''.join(map(lambda x: str(int(x)), numbers[i:j])))  # Spojíme druhou část
            C = float(''.join(map(lambda x: str(int(x)), numbers[j:])))  # Spojíme zbytek
            if A + B == C:
                return A, B, C
    return None

# Funkce pro zpracování řádku a nalezení čísel A, B, C
def process_line_for_numbers(line):
    # Najdi čísla na konci řádku po textu "smluv" nebo "smluv (x)"
    match = re.search(r"smluv(?:\s*\(\d*\))?\s*(.*)", line)
    if match:
        numbers_str = match.group(1).strip()
        if numbers_str:
            # Rozděl čísla podle mezer
            numbers = [parse_number(num) for num in numbers_str.split()]

            # Najdi kombinaci A + B = C
            result = find_combination(numbers)
            if result:
                A, B, C = result
                return A, B, C
    return None

# Otevřít výstupní CSV soubor pro zápis (přepíše existující soubor)
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    
    # Zapsat hlavičku do CSV
    csvwriter.writerow(['Filename', 'Matching Line', 'A', 'B', 'C'])

    # Projít všechny PDF soubory ve složce a hledat odpovídající řádky
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"Zpracovávám soubor: {filename}")
            
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
                        csvwriter.writerow([filename, line, A, B, C])
                    else:
                        csvwriter.writerow([filename, line, None, None, None])
            else:
                print(f"V souboru {filename} nebyly nalezeny odpovídající řádky.")
