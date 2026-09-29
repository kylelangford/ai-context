#!/usr/bin/env python3
"""
Prospect Search CLI - Find and add new companies

Usage:
    python search_cli.py url <url>              Scrape companies from a URL (directory/list)
    python search_cli.py add <name> [website]   Add a single company
    python search_cli.py bulk <file>            Import from CSV file
    python search_cli.py find-website <name>    Find website for a company
    python search_cli.py pending                Show companies without scans
"""

import sys
import re
import sqlite3
import csv
import json
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "--break-system-packages", "-q"])
    import requests
    from bs4 import BeautifulSoup

DB_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/db/prospects.db"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}


def get_connection():
    return sqlite3.connect(DB_PATH)


def extract_companies_from_url(url: str) -> List[Dict]:
    """Scrape a URL for company names and links."""
    print(f"Scraping {url}...")

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch URL: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    companies = []
    seen_names = set()

    # Strategy 1: Look for lists of links (common in directories)
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)

        # Skip navigation, social, common non-company links
        skip_patterns = ['twitter', 'facebook', 'linkedin', 'instagram', 'youtube',
                        'privacy', 'terms', 'contact', 'about', 'login', 'signup',
                        'home', 'menu', 'search', 'javascript:', '#', 'mailto:']

        if any(p in href.lower() for p in skip_patterns):
            continue
        if any(p in text.lower() for p in skip_patterns):
            continue

        # Skip very short or very long text
        if len(text) < 3 or len(text) > 100:
            continue

        # Skip if just numbers or common words
        if text.lower() in ['read more', 'learn more', 'view', 'see all', 'more']:
            continue

        # Check if link looks like a company website
        is_external = href.startswith('http') and urlparse(url).netloc not in href

        name_lower = text.lower()
        if name_lower not in seen_names:
            seen_names.add(name_lower)

            company = {
                'name': text,
                'website': href if is_external else None,
                'source_url': url
            }
            companies.append(company)

    # Strategy 2: Look for company names in headings/lists
    for tag in soup.find_all(['h2', 'h3', 'h4', 'li', 'td']):
        text = tag.get_text(strip=True)

        # Skip if too short/long
        if len(text) < 3 or len(text) > 80:
            continue

        # Skip common non-company text
        if text.lower() in seen_names:
            continue

        # Look for links within the element
        link = tag.find('a', href=True)
        website = None
        if link:
            href = link.get('href', '')
            if href.startswith('http') and urlparse(url).netloc not in href:
                website = href

        # Check if this looks like a company name (capitalized, not a sentence)
        if re.match(r'^[A-Z][A-Za-z0-9\s\-\&\.\']+$', text) and ' ' not in text or text.istitle():
            name_lower = text.lower()
            if name_lower not in seen_names:
                seen_names.add(name_lower)
                companies.append({
                    'name': text,
                    'website': website,
                    'source_url': url
                })

    print(f"Found {len(companies)} potential companies")
    return companies


def find_website_for_company(name: str) -> Optional[str]:
    """Try to find a company's website via URL guessing and search."""
    print(f"  Searching for {name} website...")

    # Strategy 1: Guess common URL patterns
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name).lower()
    slug = clean_name.replace(' ', '')
    slug_dash = clean_name.replace(' ', '-')

    guesses = [
        f"https://www.{slug}.com",
        f"https://www.{slug}.org",
        f"https://www.{slug}.edu",
        f"https://www.{slug_dash}.com",
        f"https://{slug}.com",
        f"https://{slug}.org",
    ]

    for url in guesses:
        try:
            # Use GET with stream=True to avoid downloading full page
            resp = requests.get(url, headers=HEADERS, timeout=5, allow_redirects=True, stream=True)
            # Accept 2xx, 3xx, and 403 (some sites block bots but still resolve)
            if resp.status_code < 404:
                final_url = resp.url if resp.url else url
                print(f"  Found via guess: {final_url}")
                resp.close()
                return final_url
            resp.close()
        except:
            continue

    # Strategy 2: Try Bing search
    search_url = f"https://www.bing.com/search?q={name}+official+website"
    try:
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Look for result links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')

            # Skip Bing internal links
            if 'bing.com' in href or 'microsoft.com' in href:
                continue

            # Skip social media, Wikipedia, etc.
            skip_domains = ['wikipedia', 'linkedin', 'facebook', 'twitter',
                          'instagram', 'youtube', 'crunchbase', 'bloomberg',
                          'glassdoor', 'indeed', 'yelp']

            if any(d in href.lower() for d in skip_domains):
                continue

            # Return first likely company website
            if href.startswith('http'):
                print(f"  Found via search: {href}")
                return href

    except Exception as e:
        print(f"  Search failed: {e}")

    return None


def add_company(name: str, website: str = None, segment: str = None,
                org_type: str = None, similar_to: str = None) -> Optional[int]:
    """Add a company to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if already exists
    cursor.execute("SELECT id FROM companies WHERE name LIKE ?", (f"%{name}%",))
    existing = cursor.fetchone()
    if existing:
        print(f"  Company already exists: {name} (ID: {existing[0]})")
        conn.close()
        return existing[0]

    # Insert new company
    cursor.execute("""
        INSERT INTO companies (name, website, segment, org_type, similar_to, fit_score, status)
        VALUES (?, ?, ?, ?, ?, ?, 'new')
    """, (name, website, segment, org_type, similar_to, 50))

    company_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(f"  Added: {name} (ID: {company_id})")
    return company_id


def scrape_and_add(url: str, segment: str = None, auto_find_websites: bool = False):
    """Scrape URL and add companies to database."""
    companies = extract_companies_from_url(url)

    if not companies:
        print("No companies found on page")
        return

    # Show preview
    print(f"\nFound {len(companies)} potential companies:")
    print("-" * 50)
    for i, c in enumerate(companies[:20]):
        website_status = "has website" if c['website'] else "no website"
        print(f"  {i+1}. {c['name']} ({website_status})")

    if len(companies) > 20:
        print(f"  ... and {len(companies) - 20} more")

    print("-" * 50)

    # Confirm before adding
    response = input(f"\nAdd these {len(companies)} companies? [y/N/number to limit]: ").strip().lower()

    if response == 'n' or response == '':
        print("Cancelled")
        return

    limit = len(companies)
    if response.isdigit():
        limit = int(response)
    elif response != 'y':
        print("Cancelled")
        return

    # Add companies
    added = 0
    for company in companies[:limit]:
        name = company['name']
        website = company['website']

        # Try to find website if missing and auto_find enabled
        if not website and auto_find_websites:
            website = find_website_for_company(name)

        result = add_company(name, website, segment)
        if result:
            added += 1

    print(f"\nAdded {added} companies to database")


def import_csv(filepath: str, segment: str = None):
    """Import companies from CSV file."""
    print(f"Importing from {filepath}...")

    added = 0
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name') or row.get('Name') or row.get('company') or row.get('Company')
            website = row.get('website') or row.get('Website') or row.get('url') or row.get('URL')
            seg = row.get('segment') or row.get('Segment') or segment

            if name:
                result = add_company(name, website, seg)
                if result:
                    added += 1

    print(f"Imported {added} companies")


def show_pending():
    """Show companies that haven't been scanned."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.website, c.segment
        FROM companies c
        LEFT JOIN scans s ON c.id = s.company_id
        WHERE s.id IS NULL
        ORDER BY c.fit_score DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("All companies have been scanned!")
        return

    print(f"\n{len(rows)} companies pending scan:")
    print(f"{'ID':<5} {'Name':<40} {'Website':<30} {'Segment':<15}")
    print("-" * 95)
    for row in rows:
        id, name, website, segment = row
        print(f"{id:<5} {(name or '')[:39]:<40} {(website or '-')[:29]:<30} {(segment or '-')[:14]:<15}")


def show_help():
    print(__doc__)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "help":
        show_help()

    elif cmd == "url" and len(sys.argv) > 2:
        url = sys.argv[2]
        segment = sys.argv[3] if len(sys.argv) > 3 else None
        auto_find = "--find-websites" in sys.argv or "-f" in sys.argv
        scrape_and_add(url, segment, auto_find)

    elif cmd == "add" and len(sys.argv) > 2:
        name = sys.argv[2]
        website = sys.argv[3] if len(sys.argv) > 3 else None
        segment = sys.argv[4] if len(sys.argv) > 4 else None
        add_company(name, website, segment)

    elif cmd == "bulk" and len(sys.argv) > 2:
        filepath = sys.argv[2]
        segment = sys.argv[3] if len(sys.argv) > 3 else None
        import_csv(filepath, segment)

    elif cmd == "find-website" and len(sys.argv) > 2:
        name = " ".join(sys.argv[2:])
        website = find_website_for_company(name)
        if website:
            print(f"Found: {website}")
        else:
            print("No website found")

    elif cmd == "pending":
        show_pending()

    else:
        print(f"Unknown command: {cmd}")
        show_help()
