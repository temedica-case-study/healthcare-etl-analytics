-- Example BI Queries

-- 1. Patients prescribed a given drug in a date range (e.g., Metformin in Q2 2023)
SELECT
    patient_id,
    patient_name,
    visit_date,
    diagnosis_code,
    drug,
    dose
FROM vw_patient_treatments
WHERE drug = 'Metformin'
  AND visit_date BETWEEN '2023-04-01' AND '2023-06-30'
ORDER BY visit_date;

-- 2. Count of distinct diagnoses per patient in 2023
SELECT
    patient_id,
    patient_name,
    COUNT(DISTINCT diagnosis_code) AS distinct_diagnoses_2023
FROM vw_patient_diagnoses
WHERE visit_date BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY patient_id, patient_name
ORDER BY distinct_diagnoses_2023 DESC;

-- 3. List all visits in May 2023 with provider notes by Dr. Smith
SELECT
    note_author
    visit_id,
    patient_id,
    patient_name,
    visit_date,
    note_text
FROM vw_visit_notes
WHERE note_author = 'Dr. Smith'
  AND visit_date BETWEEN '2023-05-01' AND '2023-05-31'
ORDER BY visit_date;
