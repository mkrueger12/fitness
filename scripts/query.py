#!/usr/bin/env python3
"""
Query Coros activity data with SQL.

Usage:
    python scripts/query.py "SELECT * FROM activities WHERE type='Run' LIMIT 5"
    python scripts/query.py  # Interactive mode
"""

import csv
import sqlite3
import sys
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "data" / "coros_activities.csv"

def load_db():
    """Load CSV into SQLite and return connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        return conn

    # Create table with all columns as TEXT (flexible for mixed data)
    cols = rows[0].keys()
    conn.execute(f"CREATE TABLE activities ({', '.join(c + ' TEXT' for c in cols)})")

    placeholders = ', '.join('?' for _ in cols)
    for row in rows:
        conn.execute(f"INSERT INTO activities VALUES ({placeholders})", list(row.values()))

    conn.commit()
    return conn

def run_query(conn, sql):
    """Execute query and print results."""
    try:
        cur = conn.execute(sql)
        rows = cur.fetchall()
        if not rows:
            print("(no results)")
            return

        # Get column names
        cols = [d[0] for d in cur.description]

        # Calculate column widths
        widths = [len(c) for c in cols]
        for row in rows:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(str(val or "")))

        # Print header
        header = " | ".join(c.ljust(widths[i]) for i, c in enumerate(cols))
        print(header)
        print("-+-".join("-" * w for w in widths))

        # Print rows
        for row in rows:
            print(" | ".join(str(v or "").ljust(widths[i]) for i, v in enumerate(row)))

    except sqlite3.Error as e:
        print(f"Error: {e}")

def main():
    conn = load_db()

    if len(sys.argv) > 1:
        # Run query from command line
        run_query(conn, " ".join(sys.argv[1:]))
    else:
        # Interactive mode
        print("Coros Activity SQL Query")
        print("Table: activities")
        print("Columns: date, name, type, distance_mi, duration, pace, avg_hr,")
        print("         cadence, ascent_ft, descent_ft, calories, training_load,")
        print("         steps, sets, device")
        print("Type .quit to exit\n")

        while True:
            try:
                sql = input("sql> ").strip()
                if sql.lower() in (".quit", ".exit", "exit", "quit"):
                    break
                if sql:
                    run_query(conn, sql)
            except (EOFError, KeyboardInterrupt):
                print()
                break

if __name__ == "__main__":
    main()
