#!/usr/bin/env python3
"""Create scan records for all clients."""

import sqlite3

DB_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/db/prospects.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all clients with websites
    cursor.execute("""
        SELECT id, name, website
        FROM companies
        WHERE status = 'client' AND website IS NOT NULL
    """)
    clients = cursor.fetchall()

    print(f"Creating scans for {len(clients)} clients...\n")

    created = 0
    skipped = 0
    for company_id, name, website in clients:
        # Check if scan exists
        cursor.execute("SELECT id FROM scans WHERE company_id = ?", (company_id,))
        if cursor.fetchone():
            print(f"  Skipped (exists): {name}")
            skipped += 1
            continue

        # Create scan record
        cursor.execute("""
            INSERT INTO scans (
                company_id, url, scan_status, opportunity_score
            ) VALUES (?, ?, 'completed', 0)
        """, (company_id, website))

        print(f"  Created: {name}")
        created += 1

    conn.commit()
    conn.close()

    print(f"\nDone! Created {created}, skipped {skipped}")

if __name__ == "__main__":
    main()
