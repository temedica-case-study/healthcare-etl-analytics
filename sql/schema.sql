-- ----------------------------------------------------------------
-- 1. Create “patients” table
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR PRIMARY KEY,
    name        VARCHAR NOT NULL
);

-- ----------------------------------------------------------------
-- 2. Create “visits” table
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS visits (
    visit_id   VARCHAR PRIMARY KEY,
    patient_id VARCHAR NOT NULL REFERENCES patients(patient_id),
    visit_date DATE NOT NULL
);

-- ----------------------------------------------------------------
-- 3. Create “diagnoses” table
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS diagnoses (
    diagnosis_id BIGSERIAL PRIMARY KEY,
    visit_id     VARCHAR NOT NULL REFERENCES visits(visit_id),
    code         VARCHAR NOT NULL,
    description  VARCHAR
);

-- ----------------------------------------------------------------
-- 4. Create “treatments” table
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS treatments (
    treatment_id BIGSERIAL PRIMARY KEY,
    diagnosis_id BIGINT NOT NULL REFERENCES diagnoses(diagnosis_id),
    drug         VARCHAR NOT NULL,
    dose         VARCHAR
);

-- ----------------------------------------------------------------
-- 5. Create “provider_notes” table
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS provider_notes (
    note_id  BIGSERIAL PRIMARY KEY,
    visit_id VARCHAR NOT NULL REFERENCES visits(visit_id),
    text     TEXT,
    author   VARCHAR
);
