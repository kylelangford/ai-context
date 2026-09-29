#!/usr/bin/env python3
"""
Simple web server for the Lookalike Finder dashboard.
Run with: python3 server.py
Then open: http://localhost:5555
"""

import json
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os

DB_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/db/prospects.db"
PORT = 5555

class APIHandler(SimpleHTTPRequestHandler):
    """Handle API requests and serve static files."""

    def __init__(self, *args, **kwargs):
        # Serve files from the web directory
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # API routes
        if path == '/api/companies':
            self.send_json(self.get_companies(parsed.query))
        elif path.startswith('/api/company/'):
            company_id = path.split('/')[-1]
            self.send_json(self.get_company(company_id))
        elif path == '/api/segments':
            self.send_json(self.get_segments())
        elif path == '/api/scans':
            self.send_json(self.get_scans())
        elif path.startswith('/api/scan/'):
            company_id = path.split('/')[-1]
            self.send_json(self.get_scan(company_id))
        elif path == '/api/stats':
            self.send_json(self.get_stats())
        elif path.startswith('/api/lighthouse/'):
            company_id = path.split('/')[-1]
            self.send_json(self.run_lighthouse(company_id))
        elif path.startswith('/api/domain-metrics/'):
            company_id = path.split('/')[-1]
            self.send_json(self.run_domain_metrics(company_id))
        elif path == '/api/profiles':
            self.send_json(self.get_profiles())
        elif path == '/api/clients':
            self.send_json(self.get_clients())
        else:
            # Serve static files
            if path == '/':
                self.path = '/index.html'
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(body) if body else {}

        if path == '/api/notes':
            self.send_json(self.add_note(data))
        elif path.startswith('/api/company/') and path.endswith('/status'):
            company_id = path.split('/')[3]
            self.send_json(self.update_status(company_id, data))
        else:
            self.send_error(404, "Not found")

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def add_note(self, data):
        """Add a note to a company."""
        company_id = data.get('company_id')
        content = data.get('content', '').strip()
        note_type = data.get('note_type', 'general')
        title = data.get('title', '')

        if not company_id or not content:
            return {"error": "company_id and content are required"}

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notes (company_id, note_type, title, content)
            VALUES (?, ?, ?, ?)
        """, (company_id, note_type, title, content))
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {"success": True, "id": note_id}

    def update_status(self, company_id, data):
        """Update company status."""
        status = data.get('status')
        if not status:
            return {"error": "status required"}

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE companies SET status = ? WHERE id = ?", (status, company_id))
        conn.commit()
        conn.close()

        return {"success": True}

    def send_json(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_companies(self, query_string):
        """Get all companies with optional filtering."""
        params = parse_qs(query_string)
        segment = params.get('segment', [None])[0]
        status = params.get('status', [None])[0]
        sort = params.get('sort', ['fit_score'])[0]

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT c.*,
                   s.opportunity_score, s.cms_detected, s.lighthouse_performance,
                   s.lighthouse_accessibility, s.ai_suggested_pitch, s.scan_date
            FROM companies c
            LEFT JOIN scans s ON c.id = s.company_id
                AND s.id = (SELECT MAX(s2.id) FROM scans s2 WHERE s2.company_id = c.id)
            WHERE 1=1
        """
        args = []

        if segment:
            query += " AND c.segment = ?"
            args.append(segment)
        if status:
            query += " AND c.status = ?"
            args.append(status)

        if sort == 'opportunity':
            query += " ORDER BY s.opportunity_score DESC NULLS LAST, c.fit_score DESC"
        elif sort == 'name':
            query += " ORDER BY c.name ASC"
        else:
            query += " ORDER BY c.fit_score DESC"

        cursor.execute(query, args)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_company(self, company_id):
        """Get single company with all details."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get company
        cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
        company = cursor.fetchone()
        if not company:
            return {"error": "Company not found"}

        result = dict(company)

        # Get latest scan
        cursor.execute("""
            SELECT * FROM scans WHERE company_id = ? ORDER BY scan_date DESC LIMIT 1
        """, (company_id,))
        scan = cursor.fetchone()
        if scan:
            result['scan'] = dict(scan)

            # Get scan signals
            cursor.execute("""
                SELECT * FROM scan_signals WHERE scan_id = ? ORDER BY opportunity_weight DESC
            """, (scan['id'],))
            result['signals'] = [dict(row) for row in cursor.fetchall()]

            # Get tech stack
            cursor.execute("""
                SELECT * FROM scan_technologies WHERE scan_id = ?
            """, (scan['id'],))
            result['technologies'] = [dict(row) for row in cursor.fetchall()]

        # Get notes
        cursor.execute("""
            SELECT * FROM notes WHERE company_id = ? ORDER BY created_at DESC
        """, (company_id,))
        result['notes'] = [dict(row) for row in cursor.fetchall()]

        # Get outreach
        cursor.execute("""
            SELECT * FROM outreach WHERE company_id = ? ORDER BY activity_date DESC
        """, (company_id,))
        result['outreach'] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return result

    def get_segments(self):
        """Get segment summary."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT segment, COUNT(*) as count, ROUND(AVG(fit_score), 1) as avg_fit
            FROM companies
            GROUP BY segment
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [{"segment": r[0], "count": r[1], "avg_fit": r[2]} for r in rows]

    def get_scans(self):
        """Get recent scans."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.name, c.segment, s.*
            FROM scans s
            JOIN companies c ON s.company_id = c.id
            ORDER BY s.scan_date DESC
            LIMIT 50
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_scan(self, company_id):
        """Get scan details for a company."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM scans WHERE company_id = ? ORDER BY scan_date DESC LIMIT 1
        """, (company_id,))
        scan = cursor.fetchone()

        if not scan:
            return {"error": "No scan found"}

        result = dict(scan)

        # Get signals
        cursor.execute("""
            SELECT * FROM scan_signals WHERE scan_id = ?
        """, (scan['id'],))
        result['signals'] = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return result

    def run_lighthouse(self, company_id):
        """Run Lighthouse analysis for a company."""
        import requests as req

        PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get company website
        cursor.execute("SELECT website FROM companies WHERE id = ?", (company_id,))
        company = cursor.fetchone()
        if not company or not company['website']:
            conn.close()
            return {"error": "Company not found or no website"}

        url = company['website']
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        try:
            # Run PageSpeed API
            params = {
                'url': url,
                'strategy': 'mobile',
                'category': ['performance', 'accessibility', 'seo', 'best-practices']
            }

            response = req.get(PAGESPEED_API, params=params, timeout=60)

            if response.status_code != 200:
                conn.close()
                return {"error": f"PageSpeed API error: {response.status_code}"}

            data = response.json()
            categories = data.get('lighthouseResult', {}).get('categories', {})

            scores = {
                'lighthouse_performance': int(categories.get('performance', {}).get('score', 0) * 100) if 'performance' in categories else None,
                'lighthouse_accessibility': int(categories.get('accessibility', {}).get('score', 0) * 100) if 'accessibility' in categories else None,
                'lighthouse_seo': int(categories.get('seo', {}).get('score', 0) * 100) if 'seo' in categories else None,
                'lighthouse_best_practices': int(categories.get('best-practices', {}).get('score', 0) * 100) if 'best-practices' in categories else None,
            }

            # Check if there's an existing scan for this company
            cursor.execute("SELECT id FROM scans WHERE company_id = ? ORDER BY scan_date DESC LIMIT 1", (company_id,))
            existing_scan = cursor.fetchone()

            if existing_scan:
                # Update existing scan
                cursor.execute("""
                    UPDATE scans SET
                        lighthouse_performance = ?,
                        lighthouse_accessibility = ?,
                        lighthouse_seo = ?,
                        lighthouse_best_practices = ?
                    WHERE id = ?
                """, (
                    scores['lighthouse_performance'],
                    scores['lighthouse_accessibility'],
                    scores['lighthouse_seo'],
                    scores['lighthouse_best_practices'],
                    existing_scan['id']
                ))
            else:
                # Create new scan record
                cursor.execute("""
                    INSERT INTO scans (company_id, url, scan_status,
                        lighthouse_performance, lighthouse_accessibility,
                        lighthouse_seo, lighthouse_best_practices)
                    VALUES (?, ?, 'lighthouse_only', ?, ?, ?, ?)
                """, (
                    company_id, url,
                    scores['lighthouse_performance'],
                    scores['lighthouse_accessibility'],
                    scores['lighthouse_seo'],
                    scores['lighthouse_best_practices']
                ))

            conn.commit()
            conn.close()

            return {"success": True, "scores": scores}

        except Exception as e:
            conn.close()
            return {"error": str(e)}

    def run_domain_metrics(self, company_id):
        """Run domain age, backlinks, and funding analysis for a company."""
        import re
        from datetime import datetime
        from urllib.parse import urlparse
        from html import unescape

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get company info
        cursor.execute("SELECT name, website FROM companies WHERE id = ?", (company_id,))
        company = cursor.fetchone()
        if not company or not company['website']:
            conn.close()
            return {"error": "Company not found or no website"}

        url = company['website']
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        company_name = company['name']
        results = {}

        # Check domain age using Wayback Machine
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            cdx_url = f"http://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=1&from=1990"
            response = req.get(cdx_url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:
                    timestamp = data[1][1]
                    year = int(timestamp[:4])
                    month = int(timestamp[4:6])
                    day = int(timestamp[6:8])
                    first_date = datetime(year, month, day)
                    results['domain_created'] = first_date.strftime('%Y-%m-%d')
                    age_days = (datetime.now() - first_date).days
                    results['domain_age_years'] = round(age_days / 365.25, 1)
        except Exception as e:
            print(f"Domain age check failed: {e}")

        # Check backlinks using Bing indexed pages
        try:
            domain = urlparse(url).netloc.replace('www.', '')
            bing_url = f"https://www.bing.com/search?q=site%3A{domain}"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = req.get(bing_url, headers=headers, timeout=10)

            if response.status_code == 200:
                match = re.search(r'([\d,]+)\s*results?', response.text, re.I)
                if match:
                    indexed_pages = int(match.group(1).replace(',', ''))
                    results['backlink_count'] = indexed_pages * 7
        except Exception as e:
            print(f"Backlink check failed: {e}")

        # Check for funding
        try:
            search_name = re.sub(r'\s*(Inc\.?|LLC|Corp\.?|Corporation|Company|Co\.?)\s*$', '', company_name, flags=re.I).strip()
            search_url = f"https://www.bing.com/news/search?q={req.utils.quote(search_name + ' funding raised series')}"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = req.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                html = unescape(response.text)
                company_lower = search_name.lower()

                if company_lower in html.lower():
                    funding_patterns = [
                        r'raises?\s+\$?([\d,.]+)\s*(million|billion|m|b)\b',
                        r'series\s+([A-E])\s*(?:funding|round)?',
                        r'\$?([\d,.]+)\s*(million|billion|m|b)\s+(?:funding|investment|round)',
                    ]

                    for pattern in funding_patterns:
                        match = re.search(pattern, html, re.I)
                        if match:
                            if 'series' in pattern.lower():
                                results['recent_funding'] = f"Series {match.group(1).upper()}"
                            else:
                                amount = match.group(1).replace(',', '')
                                unit = match.group(2).upper()
                                if unit in ['M', 'MILLION']:
                                    results['funding_amount'] = f"${amount}M"
                                elif unit in ['B', 'BILLION']:
                                    results['funding_amount'] = f"${amount}B"
                                results['recent_funding'] = f"Raised {results.get('funding_amount', '')}"
                            break
        except Exception as e:
            print(f"Funding check failed: {e}")

        # Update existing scan or create new record
        cursor.execute("SELECT id FROM scans WHERE company_id = ? ORDER BY scan_date DESC LIMIT 1", (company_id,))
        existing_scan = cursor.fetchone()

        if existing_scan:
            cursor.execute("""
                UPDATE scans SET
                    domain_age_years = COALESCE(?, domain_age_years),
                    domain_created = COALESCE(?, domain_created),
                    backlink_count = COALESCE(?, backlink_count),
                    recent_funding = COALESCE(?, recent_funding),
                    funding_amount = COALESCE(?, funding_amount)
                WHERE id = ?
            """, (
                results.get('domain_age_years'),
                results.get('domain_created'),
                results.get('backlink_count'),
                results.get('recent_funding'),
                results.get('funding_amount'),
                existing_scan['id']
            ))
        else:
            cursor.execute("""
                INSERT INTO scans (company_id, url, scan_status,
                    domain_age_years, domain_created, backlink_count,
                    recent_funding, funding_amount)
                VALUES (?, ?, 'domain_metrics_only', ?, ?, ?, ?, ?)
            """, (
                company_id, url,
                results.get('domain_age_years'),
                results.get('domain_created'),
                results.get('backlink_count'),
                results.get('recent_funding'),
                results.get('funding_amount')
            ))

        conn.commit()
        conn.close()

        return {"success": True, "metrics": results}

    def get_profiles(self):
        """Get search profiles for lookalike matching."""
        profiles_path = "/Users/kylelangford/ai-context/tools/prospect-finder/search-profiles.json"
        try:
            with open(profiles_path, 'r') as f:
                data = json.load(f)
                return data.get('searchProfiles', [])
        except Exception as e:
            return {"error": str(e)}

    def get_clients(self):
        """Get existing client roster (Brunello profiles)."""
        clients_path = "/Users/kylelangford/ai-context/tools/prospect-finder/client-roster.json"
        try:
            with open(clients_path, 'r') as f:
                data = json.load(f)
                return data.get('clients', [])
        except Exception as e:
            return {"error": str(e)}

    def get_stats(self):
        """Get dashboard stats."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        stats = {}

        cursor.execute("SELECT COUNT(*) FROM companies")
        stats['total_companies'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM companies WHERE status = 'new'")
        stats['new'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM companies WHERE status = 'client'")
        stats['clients'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM companies WHERE status != 'client'")
        stats['prospects'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM scans")
        stats['scans'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM companies WHERE website IS NOT NULL")
        stats['with_website'] = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(fit_score) FROM companies")
        stats['avg_fit'] = round(cursor.fetchone()[0] or 0, 1)

        cursor.execute("""
            SELECT AVG(opportunity_score) FROM scans
            WHERE id IN (SELECT MAX(id) FROM scans GROUP BY company_id)
        """)
        stats['avg_opportunity'] = round(cursor.fetchone()[0] or 0, 1)

        conn.close()
        return stats


def run_server():
    """Start the web server."""
    server = HTTPServer(('localhost', PORT), APIHandler)
    print(f"\n🚀 Lookalike Finder Dashboard")
    print(f"   Open: http://localhost:{PORT}")
    print(f"   Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run_server()
