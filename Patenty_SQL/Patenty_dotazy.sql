SELECT TOP 50 * FROM vysledek_stav
SELECT TOP 50 * FROM Seznam_univerzit
SELECT TOP 50 * FROM applicants_2
SELECT TOP 50 * FROM casova_osa
SELECT TOP 50 * FROM MPTapi
SELECT TOP 50 * FROM MPTdata1

SELECT * FROM licencni_prijmy

DROP TABLE licencni_prijmy

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
SET API = CONCAT('EP/', Application_Number);

ALTER TABLE licencni_prijmy
ALTER COLUMN Licencni_prijem INT

UPDATE licencni_prijmy
SET Licencni_prijem = Licencni_prijem *1000




ALTER TABLE licencni_prijmy
ADD IncomeCategory NVARCHAR(50)

UPDATE licencni_prijmy
SET IncomeCategory = 
    CASE
        WHEN Licencni_prijem <= 145000 THEN 'Low Income'
        WHEN Licencni_prijem <= 800000 THEN 'Medium Income'
        ELSE 'High Income'
    END

SELECT * FROM licencni_prijmy

SELECT ID_univerzita,
       CASE 
           WHEN ID_univerzita = 3 THEN 4
           WHEN ID_univerzita = 4 THEN 3
           ELSE ID_univerzita
       END AS new_ID_univerzita
FROM applicants_2;
