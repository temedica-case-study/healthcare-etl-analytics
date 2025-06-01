import json
import os
import psycopg2
import pytest
from typing import Any, Dict
from psycopg2.extensions import connection as _connection
from etl.load_patient_data import connect_db, process_single_file

@pytest.fixture(scope="module")
def pg_conn() -> _connection:
    """
    Fixture to create a temporary Postgres DB for testing locally. Uses a mock file created in this script.
    """
    conn: _connection = connect_db("healthdb", "etl_loader", "etl_pass", "localhost", "5432")
    # Create schema (assuming schema.sql is idempotent)
    schema_sql_path = os.path.join(os.path.dirname(__file__), "../../sql/schema.sql")
    with open(schema_sql_path, "r") as f:
        conn.cursor().execute(f.read())
    conn.commit()
    yield conn
    conn.close()

def test_etl_single_json(pg_conn: _connection, tmp_path: Any) -> None:
    # 1. Create a sample JSON file
    sample: Dict[str, Any] = {
        "patient_id": "P-TEST-1",
        "name": "Alice Test",
        "visits": [
            {
                "visit_id": "V-TEST-001",
                "date": "2023-05-10",
                "diagnoses": [
                    {
                        "code": "E11.9",
                        "description": "Type 2 diabetes",
                        "treatments": [
                            {"drug": "Metformin", "dose": "500mg"}
                        ]
                    }
                ],
                "provider_notes": {
                    "text": "Test note.",
                    "author": "Dr. Test"
                }
            }
        ]
    }
    json_file = tmp_path / "patient_test.json"
    with open(json_file, "w") as f:
        json.dump(sample, f)

    # 2. Run ETL on that one file
    cur = pg_conn.cursor()
    process_single_file(cur, str(json_file))
    pg_conn.commit()

    # 3. Assert patient row
    cur.execute("SELECT name FROM patients WHERE patient_id='P-TEST-1';")
    row = cur.fetchone()
    assert row is not None and row[0] == "Alice Test"

    # 4. Assert visit row
    cur.execute("SELECT visit_date FROM visits WHERE visit_id='V-TEST-001';")
    row = cur.fetchone()
    assert row is not None and str(row[0]) == "2023-05-10"

    # 5. Assert diagnosis & treatment
    cur.execute("""
        SELECT t.drug
        FROM treatments t
        JOIN diagnoses d ON t.diagnosis_id = d.diagnosis_id
        WHERE d.code='E11.9';
    """)
    row = cur.fetchone()
    assert row is not None and row[0] == "Metformin"

    # 6. Assert provider note
    cur.execute("SELECT author, text FROM provider_notes WHERE visit_id='V-TEST-001';")
    row = cur.fetchone()
    assert row is not None and row[0] == "Dr. Test" and row[1] == "Test note."
