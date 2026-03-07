#!/usr/bin/env python3
"""One-time script to purge historical findings table in Turso.

Run this ONCE against production to reclaim storage and write budget.
The findings table accumulated ~5M rows/day with no consumer.

Usage:
    TURSO_DATABASE_URL=libsql://... TURSO_AUTH_TOKEN=... python scripts/purge_findings_history.py
"""

from crawlers.db import connect

def main():
    conn = connect()

    # Check current size
    row = conn.execute("SELECT COUNT(*) FROM findings").fetchone()
    print(f"Current findings rows: {row[0]:,}")

    row = conn.execute("SELECT COUNT(*) FROM findings_latest").fetchone()
    print(f"Current findings_latest rows: {row[0]:,}")

    if row[0] == 0:
        print("findings table is already empty. Nothing to purge.")
        return

    # Purge in batches to avoid locking
    print("Purging findings table...")
    total_deleted = 0
    while True:
        conn.execute("DELETE FROM findings WHERE rowid IN (SELECT rowid FROM findings LIMIT 50000)")
        conn.commit()
        remaining = conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0]
        deleted_this_batch = row[0] - remaining - total_deleted if total_deleted == 0 else 0
        total_deleted = row[0] - remaining
        print(f"  Deleted so far: {total_deleted:,} / {row[0]:,} ({remaining:,} remaining)")
        if remaining == 0:
            break

    print(f"Purge complete. Deleted {total_deleted:,} rows.")

    # Also clean old scans and crawl_runs (keep last 30 days)
    conn.execute("DELETE FROM scans WHERE started_at < datetime('now', '-30 days')")
    conn.execute("DELETE FROM crawl_runs WHERE started_at < datetime('now', '-30 days')")
    conn.commit()
    print("Cleaned old scans and crawl_runs (>30 days)")


if __name__ == "__main__":
    main()
