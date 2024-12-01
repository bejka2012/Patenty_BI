import pdfplumber
import csv
import os
import re

# Vstupni a vystupni slozky
input_folder = r"C:\Users\beata\OneDrive\Dokumenty\Others\IT\Digitální akademie Czechitas\Projekt_DA_patenty\Patenty_vyrocni_zpravy\21_VSCHT"
output_file = r"C:\Users\beata\OneDrive\Dokumenty\Others\IT\Digitální akademie Czechitas\Projekt_DA_patenty\Patenty_python\vystup.csv"

# Inicializace listu pro ukladani vysledku

# Pruchod vsemi PDF soubory ve slozce
for filename in os.listdir(input_folder):
    print(f"In process {filename}: ", end = ' ')
    results = []
    if filename.endswith(".pdf"):
        filepath = os.path.join(input_folder, filename)
        university_name = os.path.basename(os.path.dirname(filepath)).split('_')[1]
        university_number = os.path.basename(os.path.dirname(filepath)).split('_')[0]
        year_match = re.search(r'\d{4}', filename)
        year = year_match.group() if year_match else None

        with pdfplumber.open(filepath) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):

        # Extract tables from each page
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row[0] == "A.1":
                            last_number = next((x for x in reversed(row) if x is not None), None)
                            # results.append([numbers.group(1), page_number])
                            results.append([university_number, university_name, year, last_number, page_number])
        if len(results) == 0:
            print("A.1 record was not found!")
            with open("unprocessed.txt", mode="a", newline="", encoding="utf-8") as file:
                file.write(filename + "\n")
        else :
            print("Success")
            
        with open(output_file, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if os.path.getsize(output_file) == 0:#
                writer.writerow(["Cislo Univerzity", "Nazev Univerzity", "Rok", "Nalezene Cislo", "Cislo Stranky"])
            writer.writerows(results)

print(f"Skript byl úspěšně dokončen. Výsledky jsou uloženy v souboru: {output_file}")
                         

