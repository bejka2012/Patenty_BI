import pdfplumber
import csv
import os
import re

# Vstupni a vystupni slozky
input_folder = r"C:\Users\beata\OneDrive\Dokumenty\Others\IT\Digitální akademie Czechitas\Projekt_DA_patenty\Patenty_vyrocni_zpravy\25_VUTtest"
output_file = r"C:\Users\beata\OneDrive\Dokumenty\Others\IT\Digitální akademie Czechitas\Projekt_DA_patenty\Patenty_python\vystup.csv"

# Inicializace listu pro ukladani vysledku
results = []

# Pruchod vsemi PDF soubory ve slozce
for filename in os.listdir(input_folder):
    if filename.endswith(".pdf"):
        filepath = os.path.join(input_folder, filename)
        university_name = os.path.basename(os.path.dirname(filepath)).split('_')[1]
        university_number = os.path.basename(os.path.dirname(filepath)).split('_')[0]
        year = 2000

        with pdfplumber.open(filepath) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                # print(text)
                if text:
                    for line in text.split('\n'):
                        if "Příjmy z licenčních smluv" in line:
                            # Extrakce posledniho cisla v radku
                            numbers = re.search(r"A\.1\s+Příjmy z licenčních smluv (?:\(2\))?\s+(?:\d{1,3}(?: \d{3})*(?:,\d+)?)?\s+(?:\d{1,3}(?: \d{3})*(?:,\d+)?)?\s+(\d{1,3}(?: \d{3})*(?:,\d+)?)*", line)
                            if numbers:
                                print(numbers.group(1))
                                # found_number = numbers[-1].replace(" ", "")
                                results.append([numbers.group(1), page_number])
                                results.append([university_number, university_name, year, numbers.group(1), page_number])

# Serazeni vysledku podle roku sestupne
# results.sort(key=lambda x: x[2], reverse=True)

# Ulozeni vysledku do CSV souboru
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Cislo Univerzity", "Nazev Univerzity", "Rok", "Nalezene Cislo", "Cislo Stranky"])
    writer.writerows(results)

print(f"Skript byl úspěšně dokončen. Výsledky jsou uloženy v souboru: {output_file}")
