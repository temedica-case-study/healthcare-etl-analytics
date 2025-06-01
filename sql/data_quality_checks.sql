-- 1. Missing patient_id in visits
SELECT * FROM visits WHERE patient_id IS NULL;

-- 2. Missing visit_id in diagnoses or multiple diagnoses with null visit_id
SELECT * FROM diagnoses WHERE visit_id IS NULL;

-- 3. Invalid dates (visit_date > today)
SELECT * FROM visits WHERE visit_date > CURRENT_DATE;

-- 4. Diagnoses codes not matching ICD10 pattern
SELECT * FROM diagnoses
WHERE NOT (code ~ '^[A-TV-Z][0-9][0-9AB]\.[0-9A-TV-Z]{1,4}$');

-- 5. Patients without any visits (possible, but worth flagging)
SELECT p.* FROM patients p
LEFT JOIN visits v ON p.patient_id = v.patient_id
WHERE v.visit_id IS NULL;

-- 6. Treatments referencing a non-existent diagnosis
SELECT t.* FROM treatments t
LEFT JOIN diagnoses d ON t.diagnosis_id = d.diagnosis_id
WHERE d.diagnosis_id IS NULL;
