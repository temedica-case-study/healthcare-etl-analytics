# Healthcare Patient Data Transformation & Analytics

## Overview

This repo contains a solution for ingesting nested JSON patient data into PostgreSQL and enabling BI analytics. It covers ETL, data quality, security, and performance.

### Components

- **ETL** (`etl/`): Python scripts to parse JSON and load into tables.  
- **Database Schema** (`sql/`):  
  - `schema.sql`: Tables (patients, visits, diagnoses, treatments, provider_notes).  
  - `views_masked.sql`: Views with PII masked for BI.  
  - `indexes.sql`: Index definitions.  
  - `data_quality_checks.sql`: Quality queries.  
- **BI Examples** (`bi/`): Power BI/Tableau example queries using masked views.  
- **Compliance** (`compliance/`): Placeholder for HIPAA/GDPR policies.  
- **Docs** (`docs/`): Placeholder for architecture and data flow diagrams.

## Getting Started

### 1. Initialize Database

```bash
psql -U postgres -c "CREATE DATABASE healthdb;"
psql -U postgres <<EOF
CREATE USER etl_loader WITH PASSWORD 'etl_pass';
CREATE USER bi_reader WITH PASSWORD 'bi_pass';
GRANT CONNECT ON DATABASE healthdb TO etl_loader, bi_reader;
\c healthdb
GRANT USAGE ON SCHEMA public TO etl_loader, bi_reader;
GRANT CREATE ON SCHEMA public TO etl_loader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bi_reader;
EOF
```

Load schema and masked views:

```bash
psql -U etl_loader -d healthdb -f sql/schema.sql
psql -U etl_loader -d healthdb -f sql/indexes.sql
psql -U etl_loader -d healthdb -f sql/views.sql
```

### 2. Run ETL

```bash
cd etl
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python load_patient_data.py \
  --input-dir tests/sample_jsons/ \
  --dbname healthdb \
  --dbuser etl_loader \
  --dbpass etl_pass
```

### 3. Validate Data Quality

```bash
psql -U etl_loader -d healthdb -f sql/data_quality_checks.sql
```

### 4. Run tests

```bash
cd ~/healthcare-etl-analytics
export PYTHONPATH="$PWD"
pytest etl/tests/test_etl_pipeline.py
```

### 5. BI Connection

- Use `bi_reader` credentials to connect BI tools to PostgreSQL and query masked views.

## Design & Assumptions

1. **Surrogate Keys**: `BIGSERIAL` keys simplify foreign keys and indexing. Natural columns also indexed.

2. **Python ETL**: Row-by-row parsing for flexibility and error handling. Bulk-load recommended for large amounts of records per day.

3. **PII Masking via Views**: Base tables store full PII under strict access. Masked views expose only pseudonymized names.

4. **Scalability**: Range partition `visits` by `visit_date`. Index frequently filtered columns (e.g., `treatments(drug)`, `diagnoses(code)`).

### Trade-offs

- **Row ETL vs. Bulk**: Python ETL is flexible but slower at scale; bulk-load recommended for high volume.
- **View Masking Overhead**: Mask functions add CPU cost; acceptable for BI.
