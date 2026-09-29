#!/usr/bin/env python3
"""Import existing clients from client-roster.json into the prospects database."""

import json
import sqlite3
import os

DB_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/db/prospects.db"
CLIENTS_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/client-roster.json"

def map_segment(industry):
    """Map industry to segment."""
    industry_lower = industry.lower() if industry else ""
    if "health" in industry_lower or "insurance" in industry_lower:
        return "Healthcare"
    if "education" in industry_lower or "edtech" in industry_lower:
        return "Higher Ed"
    if "media" in industry_lower or "publishing" in industry_lower:
        return "Publishing"
    if "nonprofit" in industry_lower:
        return "Nonprofit"
    if "energy" in industry_lower or "utility" in industry_lower:
        return "Energy"
    if "software" in industry_lower or "saas" in industry_lower or "martech" in industry_lower:
        return "SaaS"
    if "manufacturing" in industry_lower:
        return "Manufacturing"
    if "entertainment" in industry_lower or "celebrity" in industry_lower:
        return "Entertainment"
    if "consumer" in industry_lower or "retail" in industry_lower:
        return "Consumer"
    if "architecture" in industry_lower or "design" in industry_lower:
        return "Professional Services"
    if "real estate" in industry_lower:
        return "Real Estate"
    return "Other"

def main():
    # Load clients
    with open(CLIENTS_PATH, 'r') as f:
        data = json.load(f)
    clients = data.get('clients', [])

    print(f"Found {len(clients)} clients to import")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    imported = 0
    skipped = 0

    for client in clients:
        name = client.get('name')
        if not name:
            continue

        # Check if already exists
        cursor.execute("SELECT id FROM companies WHERE name = ?", (name,))
        if cursor.fetchone():
            print(f"  Skipped (exists): {name}")
            skipped += 1
            continue

        # Map fields
        industry = client.get('industry', '')
        segment = map_segment(industry)
        org_type = client.get('orgType', '')
        size_range = client.get('size', '')
        geography = client.get('geography', '')
        budget_estimate = client.get('budgetTier', '')
        characteristics = client.get('characteristics', [])
        tags = ', '.join(characteristics) if characteristics else ''

        # Insert
        cursor.execute("""
            INSERT INTO companies (
                name, industry, segment, org_type, size_range, geography,
                budget_estimate, fit_score, status, stage, tags, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            industry,
            segment,
            org_type,
            size_range,
            geography,
            budget_estimate,
            100,  # Fit score = 100 for existing clients
            'client',  # Status
            'customer',  # Stage
            tags,
            'client-roster'
        ))

        print(f"  Imported: {name} ({segment})")
        imported += 1

    conn.commit()
    conn.close()

    print(f"\nDone! Imported {imported}, skipped {skipped} (already exist)")

if __name__ == "__main__":
    main()
