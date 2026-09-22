"""
Pre-migration fix script.
Clears stale pandesal migration records and drops incorrectly named tables
so that the squashed 0001_initial migration runs fresh.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pandesalhub.settings")
django.setup()

from django.db import connection

def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)",
        [table_name]
    )
    return cursor.fetchone()[0]

with connection.cursor() as cursor:
    # Check if the correct table already exists — if so, nothing to fix
    if table_exists(cursor, 'kakanin_kakanin'):
        print("==> Tables already correct, skipping pre-migrate fix.")
    else:
        print("==> kakanin_kakanin missing — clearing stale migration records...")

        # Delete stale pandesal migration records so Django re-applies them
        cursor.execute("DELETE FROM django_migrations WHERE app = 'pandesal'")
        print("==> Cleared pandesal entries from django_migrations.")

        # Drop the incorrectly named table if it exists (created by old migration)
        if table_exists(cursor, 'pandesal_kakanin'):
            cursor.execute('DROP TABLE IF EXISTS "pandesal_kakanin" CASCADE')
            print("==> Dropped old pandesal_kakanin table.")

        # Also drop any other tables that might be stale from old migrations
        stale_tables = [
            'kakanin_aboutpage',
            'kakanin_contactinfo',
        ]
        for tbl in stale_tables:
            if table_exists(cursor, tbl):
                cursor.execute(f'DROP TABLE IF EXISTS "{tbl}" CASCADE')
                print(f"==> Dropped stale table: {tbl}")

        print("==> Pre-migrate fix complete. Running fresh migrations now...")
