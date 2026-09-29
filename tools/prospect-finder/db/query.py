#!/usr/bin/env python3
"""Query helpers for the prospects database."""

import sqlite3
import sys
from datetime import datetime

DB_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/db/prospects.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def print_table(rows, headers):
    """Print rows as a formatted table."""
    if not rows:
        print("No results found.")
        return

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell) if cell else ""))

    # Print header
    header_row = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))

    # Print rows
    for row in rows:
        print(" | ".join(str(cell if cell else "").ljust(widths[i]) for i, cell in enumerate(row)))

def hot_prospects():
    """Show high-fit prospects with recent signals."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, segment, fit_score, signal_type, similar_to, status
        FROM companies
        WHERE fit_score >= 75 AND status NOT IN ('won', 'lost', 'dormant')
        ORDER BY fit_score DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    print_table(rows, ["Company", "Segment", "Fit", "Signal", "Similar To", "Status"])
    conn.close()

def by_segment(segment):
    """Show prospects in a specific segment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, fit_score, match_tier, similar_to, status
        FROM companies
        WHERE segment = ?
        ORDER BY fit_score DESC
    """, (segment,))
    rows = cursor.fetchall()
    print_table(rows, ["Company", "Fit", "Tier", "Similar To", "Status"])
    conn.close()

def search(query):
    """Search companies by name or tags."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, segment, fit_score, tags
        FROM companies
        WHERE name LIKE ? OR tags LIKE ?
        ORDER BY fit_score DESC
    """, (f"%{query}%", f"%{query}%"))
    rows = cursor.fetchall()
    print_table(rows, ["Company", "Segment", "Fit", "Tags"])
    conn.close()

def pipeline():
    """Show pipeline summary by status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status, COUNT(*) as count, ROUND(AVG(fit_score), 1) as avg_fit
        FROM companies
        GROUP BY status
        ORDER BY
            CASE status
                WHEN 'won' THEN 1
                WHEN 'negotiating' THEN 2
                WHEN 'pitched' THEN 3
                WHEN 'outreach' THEN 4
                WHEN 'researching' THEN 5
                WHEN 'new' THEN 6
                ELSE 7
            END
    """)
    rows = cursor.fetchall()
    print_table(rows, ["Status", "Count", "Avg Fit"])
    conn.close()

def segments():
    """Show prospect counts by segment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT segment, COUNT(*) as count, ROUND(AVG(fit_score), 1) as avg_fit
        FROM companies
        GROUP BY segment
        ORDER BY count DESC
    """)
    rows = cursor.fetchall()
    print_table(rows, ["Segment", "Count", "Avg Fit"])
    conn.close()

def show(company_name):
    """Show full details for a company."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM companies WHERE name LIKE ?
    """, (f"%{company_name}%",))
    row = cursor.fetchone()

    if not row:
        print(f"Company not found: {company_name}")
        return

    columns = [desc[0] for desc in cursor.description]
    print(f"\n{'='*60}")
    for i, col in enumerate(columns):
        if row[i]:
            print(f"{col}: {row[i]}")
    print(f"{'='*60}\n")
    conn.close()

def update_status(company_name, new_status):
    """Update a company's status."""
    valid_statuses = ['new', 'researching', 'outreach', 'pitched', 'negotiating', 'won', 'lost', 'dormant']
    if new_status not in valid_statuses:
        print(f"Invalid status. Choose from: {', '.join(valid_statuses)}")
        return

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE companies SET status = ? WHERE name LIKE ?
    """, (new_status, f"%{company_name}%"))
    conn.commit()
    print(f"Updated {cursor.rowcount} record(s)")
    conn.close()

def add_note(company_name, note_text):
    """Add a note to a company."""
    conn = get_connection()
    cursor = conn.cursor()

    # Find company
    cursor.execute("SELECT id FROM companies WHERE name LIKE ?", (f"%{company_name}%",))
    result = cursor.fetchone()
    if not result:
        print(f"Company not found: {company_name}")
        return

    company_id = result[0]
    cursor.execute("""
        INSERT INTO notes (company_id, content) VALUES (?, ?)
    """, (company_id, note_text))
    conn.commit()
    print(f"Note added to {company_name}")
    conn.close()

def log_outreach(company_name, activity_type, outcome=None):
    """Log an outreach activity."""
    conn = get_connection()
    cursor = conn.cursor()

    # Find company
    cursor.execute("SELECT id FROM companies WHERE name LIKE ?", (f"%{company_name}%",))
    result = cursor.fetchone()
    if not result:
        print(f"Company not found: {company_name}")
        return

    company_id = result[0]
    cursor.execute("""
        INSERT INTO outreach (company_id, activity_type, outcome) VALUES (?, ?, ?)
    """, (company_id, activity_type, outcome))
    conn.commit()
    print(f"Logged {activity_type} for {company_name}")
    conn.close()

def export_csv(filename=None):
    """Export all prospects to CSV."""
    import csv
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, segment, industry, fit_score, match_tier, similar_to, status,
               budget_estimate, signal_type, headquarters, tags
        FROM companies
        ORDER BY fit_score DESC
    """)
    rows = cursor.fetchall()
    headers = ["Name", "Segment", "Industry", "Fit Score", "Tier", "Similar To",
               "Status", "Budget", "Signal", "HQ", "Tags"]

    if not filename:
        filename = f"/Users/kylelangford/ai-context/tools/prospect-finder/exports/prospects_{datetime.now().strftime('%Y%m%d')}.csv"

    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    print(f"Exported {len(rows)} prospects to {filename}")
    conn.close()

def help_text():
    print("""
Prospect Database Query Tool
=============================

Commands:
  hot                      Show top 20 high-fit prospects
  segment <name>           Show prospects by segment (healthcare, higher-ed, etc.)
  search <query>           Search by company name or tags
  show <company>           Show full details for a company
  pipeline                 Show pipeline summary by status
  segments                 Show counts by segment

Updates:
  status <company> <status>   Update status (new/researching/outreach/pitched/won/lost)
  note <company> <text>       Add a note to a company
  log <company> <type>        Log outreach (email/call/meeting/linkedin)

Export:
  export                   Export all prospects to CSV

Examples:
  python query.py hot
  python query.py segment healthcare
  python query.py search bcbs
  python query.py show "Point32Health"
  python query.py status "Point32Health" outreach
  python query.py note "HCSC" "Met with CMO at conference"
  python query.py log "Brown" email
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        help_text()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "hot":
        hot_prospects()
    elif command == "segment" and len(sys.argv) > 2:
        by_segment(sys.argv[2])
    elif command == "search" and len(sys.argv) > 2:
        search(sys.argv[2])
    elif command == "show" and len(sys.argv) > 2:
        show(sys.argv[2])
    elif command == "pipeline":
        pipeline()
    elif command == "segments":
        segments()
    elif command == "status" and len(sys.argv) > 3:
        update_status(sys.argv[2], sys.argv[3])
    elif command == "note" and len(sys.argv) > 3:
        add_note(sys.argv[2], " ".join(sys.argv[3:]))
    elif command == "log" and len(sys.argv) > 3:
        log_outreach(sys.argv[2], sys.argv[3])
    elif command == "export":
        export_csv()
    else:
        help_text()
