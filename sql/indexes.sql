-- Index on treatments.drug for faster drug lookups
CREATE INDEX IF NOT EXISTS idx_treatments_drug ON treatments(drug);

-- Index on visits.visit_date for date range queries
CREATE INDEX IF NOT EXISTS idx_visits_visit_date ON visits(visit_date);

-- Index on diagnoses.code for fast code-based filters
CREATE INDEX IF NOT EXISTS idx_diagnoses_code ON diagnoses(code);

-- Additional composite index if BI queries often filter by (drug, visit_date)
CREATE INDEX IF NOT EXISTS idx_treatments_drug_date
  ON treatments(drug)
  INCLUDE (diagnosis_id);
