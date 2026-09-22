"""Executes every query in sql/ against data/saas_bi.db and prints results.

Every number in README.md / docs/dax_measures.md is copy-pasted from this
script's actual output.

Usage:
    python src/run_sql.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/saas_bi.db")
SQL_DIR = Path("sql")


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        print(f"\n{'=' * 70}\n{sql_file.name}\n{'=' * 70}")
        df = pd.read_sql_query(sql_file.read_text(), conn)
        print(df.to_string(index=False))
    conn.close()


if __name__ == "__main__":
    main()
