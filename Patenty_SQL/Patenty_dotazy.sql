SELECT TOP 50 * FROM licencni_prijmy
SELECT TOP 50 * FROM Seznam_univerzit
SELECT TOP 50 * FROM Applicants
SELECT TOP 50 * FROM casova_osa
SELECT TOP 50 * FROM MPTapi
SELECT TOP 50 * FROM MPTdata1

SELECT * FROM MPTdata1

DROP TABLE vysledekstav2

EXEC sp_rename 'malicenci_2.Patent_number', 'Application_number', 'COLUMN'
EXEC sp_rename 'Seznam_univerzit.Zkratka', 'Zkratka_univerzity', 'COLUMN'



SELECT * FROM vysledekstav2
SELECT * FROM Applicants

SELECT 
    *
FROM 
    Applicants a 
    LEFT JOIN vysledekstav3 v ON a.API = v.API
WHERE 
    STAV IS NULL



SELECT * FROM Applicants
WHERE Applicant_Name LIKE N'%Vysoká%'

SELECT 
    Popis
    
FROM casova_osa
GROUP BY Popis

SELECT 
    LEFT(FILE_name,25) AS Typ3
FROM MPTdata1
GROUP BY LEFT(FILE_name,25)

SELECT 
    *,
    CONCAT('EP/', Application_number) as API
FROM MPTdata1

SELECT 
    *
FROM
    MPTdate1 M
    JOIN Applicants A ON 

SELECT 
    *
FROM MPT
UNION ALL
SELECT 
    *
FROM MPTapi


UPDATE MPTdata1
SET 'API' = CONCAT('EP/', Application_Number);