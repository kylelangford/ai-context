#!/usr/bin/env python3
"""
Website Opportunity Scanner CLI

Usage:
    python scan_cli.py <url>                 Scan a single URL
    python scan_cli.py company <name>        Scan a company by name
    python scan_cli.py top <n>               Scan top N prospects by fit score
    python scan_cli.py segment <segment>     Scan all in a segment
    python scan_cli.py results               Show latest scan results
    python scan_cli.py opportunities         Show high-opportunity prospects
"""

import sys
import sqlite3
from scanner import WebsiteScanner, save_scan_result, format_scan_result

DB_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/db/prospects.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def scan_url(url: str, company_id: int = 0, company_name: str = None):
    """Scan a single URL."""
    scanner = WebsiteScanner()
    result = scanner.scan(company_id, url)

    if company_id > 0:
        scan_id = save_scan_result(result)
        print(f"Scan saved with ID: {scan_id}")

    print(format_scan_result(result, company_name or url))
    return result


def scan_company(name: str):
    """Scan a company by name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, website FROM companies
        WHERE name LIKE ?
    """, (f"%{name}%",))
    row = cursor.fetchone()
    conn.close()

    if not row:
        print(f"Company not found: {name}")
        return None

    company_id, company_name, website = row

    if not website:
        print(f"No website on file for {company_name}")
        # Try to infer from name
        print("You can add a website with: add website <company> <url>")
        return None

    return scan_url(website, company_id, company_name)


def scan_top(n: int = 10):
    """Scan top N prospects by fit score."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.website, c.fit_score
        FROM companies c
        LEFT JOIN scans s ON c.id = s.company_id
        WHERE c.website IS NOT NULL
        AND (s.id IS NULL OR s.scan_date < datetime('now', '-7 days'))
        ORDER BY c.fit_score DESC
        LIMIT ?
    """, (n,))
    companies = cursor.fetchall()
    conn.close()

    if not companies:
        print("No companies with websites to scan (or all recently scanned)")
        return

    print(f"Scanning top {len(companies)} prospects...\n")

    for company_id, name, website, fit_score in companies:
        print(f"\n--- {name} (fit: {fit_score}) ---")
        scan_url(website, company_id, name)


def scan_segment(segment: str):
    """Scan all companies in a segment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.website
        FROM companies c
        WHERE c.segment = ? AND c.website IS NOT NULL
        ORDER BY c.fit_score DESC
    """, (segment,))
    companies = cursor.fetchall()
    conn.close()

    if not companies:
        print(f"No companies with websites in segment: {segment}")
        return

    print(f"Scanning {len(companies)} companies in {segment}...\n")

    for company_id, name, website in companies:
        scan_url(website, company_id, name)


def show_results():
    """Show latest scan results."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, s.opportunity_score, s.cms_detected,
               s.lighthouse_performance, s.lighthouse_accessibility,
               s.ai_suggested_pitch, s.scan_date
        FROM scans s
        JOIN companies c ON s.company_id = c.id
        ORDER BY s.scan_date DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No scan results yet. Run: scan <url> or scan company <name>")
        return

    print(f"\n{'Company':<35} {'Opp':>4} {'CMS':<12} {'Perf':>5} {'A11y':>5} {'Pitch':<30}")
    print("-" * 100)
    for row in rows:
        name, opp, cms, perf, a11y, pitch, date = row
        print(f"{(name or '')[:34]:<35} {opp or 0:>4} {(cms or '-')[:11]:<12} {perf or '-':>5} {a11y or '-':>5} {(pitch or '-')[:29]:<30}")


def show_opportunities():
    """Show high-opportunity prospects."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, c.segment, c.fit_score, s.opportunity_score,
               s.cms_detected, s.ai_summary, s.ai_suggested_pitch
        FROM scans s
        JOIN companies c ON s.company_id = c.id
        WHERE s.opportunity_score >= 60
        AND s.id = (SELECT MAX(s2.id) FROM scans s2 WHERE s2.company_id = c.id)
        ORDER BY s.opportunity_score DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No high-opportunity prospects found. Run scans first.")
        return

    print("\n🎯 HIGH OPPORTUNITY PROSPECTS\n")
    for row in rows:
        name, segment, fit, opp, cms, summary, pitch = row
        print(f"{'='*60}")
        print(f"{name} — {opp}/100 opportunity (fit: {fit})")
        print(f"Segment: {segment} | CMS: {cms or 'Unknown'}")
        if summary:
            print(f"Summary: {summary}")
        if pitch:
            print(f"Suggested pitch: {pitch}")
    print(f"{'='*60}\n")


def add_website(company_name: str, url: str):
    """Add a website URL to a company."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE companies SET website = ? WHERE name LIKE ?
    """, (url, f"%{company_name}%"))
    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_updated:
        print(f"Added website {url} to {company_name}")
    else:
        print(f"Company not found: {company_name}")


def show_help():
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "help":
        show_help()
    elif cmd == "company" and len(sys.argv) > 2:
        scan_company(" ".join(sys.argv[2:]))
    elif cmd == "top":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        scan_top(n)
    elif cmd == "segment" and len(sys.argv) > 2:
        scan_segment(sys.argv[2])
    elif cmd == "results":
        show_results()
    elif cmd == "opportunities":
        show_opportunities()
    elif cmd == "add-website" and len(sys.argv) > 3:
        add_website(sys.argv[2], sys.argv[3])
    elif cmd.startswith("http") or "." in cmd:
        scan_url(cmd)
    else:
        print(f"Unknown command: {cmd}")
        show_help()
