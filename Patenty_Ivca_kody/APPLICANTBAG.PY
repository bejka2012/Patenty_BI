# Čte XML soubory z určeného adresáře a extrahuje informace o přihlašovatelích (např. jméno, země, číslo přihlášky, datum podání) z XML pomocí XPath dotazů s využitím jmenných prostorů.
# Filtruje záznamy na základě data podání (vynechává záznamy starší než rok 2012) a uloží extrahované informace do CSV souboru.
# Protože databázi stahujeme celou a teprve poté z ní extrahujeme vysoké školy, je důležité pro hodnotu Applicant Name zjistit, jestli se jedná o 
# organizaci nebo o osobu, která patent vlastní.


import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime

# Folder containing XML files
folder_path = r'C:\Users\Lenovo\Desktop\PROJEKT DATA EP\XML'
output_csv = r'C:\Users\Lenovo\Python\PROJEKT\applicants.csv'
print("work in progress")
# Namespace dictionary for XML parsing (including 'com' and 'pat' namespaces)
namespaces = {
    'pat': 'http://www.wipo.int/standards/XMLSchema/ST96/Patent',
    'com': 'http://www.wipo.int/standards/XMLSchema/ST96/Common'
}

# Open CSV file for writing with UTF-8 encoding that supports Czech characters
with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Write header
    headers = ['Applicant Name', 'Country Code', 'Application Number', 'File Name', 'Filing Date']
    csv_writer.writerow(headers)

    # Loop through all XML files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.xml'):
            file_path = os.path.join(folder_path, file_name)
            
            # Parse the XML file
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                
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
                
                # Extract Application Number
                application_number_element = root.find('.//pat:ApplicationIdentification/com:ApplicationNumber/com:ApplicationNumberText', namespaces)
                application_number = application_number_element.text.strip() if application_number_element is not None else 'N/A'
                
                # Extract Applicant information
                for applicant in root.findall('.//pat:ApplicantBag/pat:Applicant', namespaces):
                    # Try to get OrganizationStandardName or PersonFullName
                    org_name = applicant.find('.//com:OrganizationStandardName', namespaces)
                    person_name = applicant.find('.//com:PersonFullName', namespaces)
                    country_code_element = applicant.find('.//com:CountryCode', namespaces)
                    country_code = country_code_element.text.strip() if country_code_element is not None else 'N/A'

                    # Decide which name to use
                    if org_name is not None:
                        applicant_name = org_name.text.strip()
                    elif person_name is not None:
                        applicant_name = person_name.text.strip()
                    else:
                        applicant_name = 'N/A'
                    
                    # Write to CSV
                    csv_writer.writerow([
                        applicant_name, 
                        country_code,
                        application_number,
                        file_name,
                        filing_date
                    ])
                    
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

print(f"CSV file created: {output_csv}")
