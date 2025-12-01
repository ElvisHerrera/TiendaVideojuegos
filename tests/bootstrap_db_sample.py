"""Helper to prepare DB for manual testing.

Usage (run on any machine that can access the PostgreSQL server configured in env or db.py):

    python3 tests/bootstrap_db_sample.py

It will call db.init_db() (create table if absent) and insert a single sample
videogame record with a tiny embedded PNG so you can test the preview/printing flow.
"""
import datetime
import os
import base64

import db


SAMPLE_PNG_B64 = (
    # 1x1 transparent PNG
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2NgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
)


def main():
    print("Using DB_HOST=%s DB_NAME=%s DB_USER=%s" % (
        os.getenv("DB_HOST", db.DB_HOST), os.getenv("DB_NAME", db.DB_NAME), os.getenv("DB_USER", db.DB_USER)
    ))

    print("Creating table if it does not exist...")
    try:
        db.init_db()
    except Exception as e:
        print("ERROR creating table:", e)
        return

    sample = {
        "title": "Prueba - Demo",
        "company": "ACME Studio",
        "release_date": datetime.date.today(),
        "image_data": base64.b64decode(SAMPLE_PNG_B64),
    }

    try:
        new_id = db.insert_product(sample)
        print("Inserted test videogame id=", new_id)
        print("Done — you can now open the app and print the sample entry.")
    except Exception as e:
        print("ERROR inserting sample:", e)


if __name__ == '__main__':
    main()
