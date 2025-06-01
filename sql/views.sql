-- ----------------------------------------------------------------
-- Masked view: vw_patient_treatments
-- ----------------------------------------------------------------
CREATE OR REPLACE VIEW vw_patient_treatments AS
SELECT
    p.patient_id,
    -- Masked patient name: first character + '*****'
    CONCAT(SUBSTRING(p.name FROM 1 FOR 1), '*****') AS patient_name_masked,
    v.visit_id,
    v.visit_date,
    d.code AS diagnosis_code,
    d.description AS diagnosis_desc,
    t.drug,
    t.dose
FROM patients p
JOIN visits v ON p.patient_id = v.patient_id
JOIN diagnoses d ON v.visit_id = d.visit_id
JOIN treatments t ON d.diagnosis_id = t.diagnosis_id;


-- ----------------------------------------------------------------
-- Masked view: vw_patient_diagnoses
-- ----------------------------------------------------------------
CREATE OR REPLACE VIEW vw_patient_diagnoses AS
SELECT
    p.patient_id,
    CONCAT(SUBSTRING(p.name FROM 1 FOR 1), '*****') AS patient_name_masked,
    v.visit_id,
    v.visit_date,
    d.diagnosis_id,
    d.code AS diagnosis_code,
    d.description AS diagnosis_desc
FROM patients p
JOIN visits v ON p.patient_id = v.patient_id
JOIN diagnoses d ON v.visit_id = d.visit_id;


-- ----------------------------------------------------------------
-- Masked view: vw_visit_notes
-- ----------------------------------------------------------------
CREATE OR REPLACE VIEW vw_visit_notes AS
SELECT
    v.visit_id,
    v.patient_id,
    CONCAT(SUBSTRING(p.name FROM 1 FOR 1), '*****') AS patient_name_masked,
    v.visit_date,
    pn.note_id,
    pn.text AS note_text,
    pn.author AS note_author
FROM visits v
JOIN patients p ON v.patient_id = p.patient_id
LEFT JOIN provider_notes pn ON v.visit_id = pn.visit_id;
