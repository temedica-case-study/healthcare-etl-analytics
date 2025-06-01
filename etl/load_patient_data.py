#!/usr/bin/env python3
"""
etl/load_patient_data.py

Reads nested JSON patient records from a directory, flattens them,
and loads into PostgreSQL tables: patients, visits, diagnoses, treatments, provider_notes.
"""

import os
import argparse
import json
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Any, Dict, List, Optional
from psycopg2.extensions import connection as _connection, cursor as _cursor

def connect_db(dbname: str, user: str, password: str, host: str, port: str) -> _connection:
    """Establish a connection to PostgreSQL."""
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = False
    return conn

def insert_patient(cursor: _cursor, patient: Dict[str, Any]) -> None:
    """
    Insert into patients table. If patient already exists, do nothing.
    """
    sql = """
    INSERT INTO patients (patient_id, name)
    VALUES (%s, %s)
    ON CONFLICT (patient_id) DO NOTHING;
    """
    cursor.execute(sql, (patient["patient_id"], patient["name"]))

def insert_visit(cursor: _cursor, patient_id: str, visit: Dict[str, Any]) -> None:
    """
    Insert into visits table. If visit already exists, do nothing.
    """
    # Parse date (expecting YYYY-MM-DD)
    visit_date = datetime.strptime(visit["date"], "%Y-%m-%d").date()
    sql = """
    INSERT INTO visits (visit_id, patient_id, visit_date)
    VALUES (%s, %s, %s)
    ON CONFLICT (visit_id) DO NOTHING;
    """
    cursor.execute(sql, (visit["visit_id"], patient_id, visit_date))

def insert_diagnosis_and_treatments(cursor: _cursor, visit_id: str, diagnoses_list: List[Dict[str, Any]]) -> None:
    """
    For each diagnosis object, insert into diagnoses and associated treatments.
    """
    for diag in diagnoses_list:
        sql_diag = """
        INSERT INTO diagnoses (visit_id, code, description)
        VALUES (%s, %s, %s)
        RETURNING diagnosis_id;
        """
        cursor.execute(sql_diag, (visit_id, diag["code"], diag.get("description")))
        diag_id: int = cursor.fetchone()[0]
        # Insert nested treatments
        for tr in diag.get("treatments", []):
            sql_tr = """
            INSERT INTO treatments (diagnosis_id, drug, dose)
            VALUES (%s, %s, %s);
            """
            cursor.execute(sql_tr, (diag_id, tr["drug"], tr.get("dose")))

def insert_provider_notes(cursor: _cursor, visit_id: str, notes: Optional[Dict[str, Any]]) -> None:
    """
    Insert a provider_notes row. If none, skip.
    """
    if notes:
        sql_note = """
        INSERT INTO provider_notes (visit_id, text, author)
        VALUES (%s, %s, %s);
        """
        cursor.execute(sql_note, (visit_id, notes.get("text"), notes.get("author")))

def process_patient_record(cursor: psycopg2.extensions.cursor, data: Dict[str, Any]) -> None:
    """
    Given a single patient‐dict (not a list), flatten and insert into tables.
    """
    # 1. Insert patient
    insert_patient(cursor, data)
    patient_id = data["patient_id"]

    # 2. Process visits
    for visit in data.get("visits", []):
        visit_id = visit["visit_id"]
        insert_visit(cursor, patient_id, visit)

        # 3. Process diagnoses & treatments
        diag_list = visit.get("diagnoses", [])
        insert_diagnosis_and_treatments(cursor, visit_id, diag_list)

        # 4. Process provider_notes
        notes = visit.get("provider_notes", {})
        insert_provider_notes(cursor, visit_id, notes)

def process_single_file(cursor: psycopg2.extensions.cursor, file_path: str) -> None:
    """
    Read one JSON file; if it contains a dict, process it directly.
    If it contains a list, loop through each element.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        # JSON array → process each element as its own patient-record
        for element in data:
            if isinstance(element, dict):
                process_patient_record(cursor, element)
            else:
                # skip anything that isn’t a dict
                continue
    elif isinstance(data, dict):
        # single‐patient JSON object
        process_patient_record(cursor, data)
    else:
        # unexpected type; skip or log
        raise ValueError(f"File {file_path} does not contain a JSON object or array.")

def main(args: Any) -> None:
    conn = connect_db(
        args.dbname, args.dbuser, args.dbpass, args.dbhost, args.dbport
    )
    cur = conn.cursor()

    for filename in os.listdir(args.input_dir):
        if not filename.lower().endswith(".json"):
            continue
        file_path = os.path.join(args.input_dir, filename)
        try:
            process_single_file(cur, file_path)
            conn.commit()
            print(f"Loaded file: {filename}")
        except Exception as e:
            conn.rollback()
            print(f"ERROR loading {filename}: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL load nested JSON to Postgres")
    parser.add_argument("--input-dir", required=True, help="Directory with JSON files")
    parser.add_argument("--dbname", required=True)
    parser.add_argument("--dbuser", required=True)
    parser.add_argument("--dbpass", required=True)
    parser.add_argument("--dbhost", default="localhost")
    parser.add_argument("--dbport", default="5432")
    args = parser.parse_args()
    main(args)
