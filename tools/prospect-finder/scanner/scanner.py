#!/usr/bin/env python3
"""
AI Website Opportunity Scanner

Scans prospect websites to detect:
- CMS and tech stack
- Performance issues (via PageSpeed API)
- Accessibility problems
- SEO basics
- Outdated libraries
- Privacy/cookie compliance
- Redesign signals

Outputs an opportunity score with AI-generated pitch recommendations.
"""

import re
import json
import sqlite3
import requests
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

# Import patterns
from tech_patterns import (
    CMS_PATTERNS, FRAMEWORK_PATTERNS, ANALYTICS_PATTERNS,
    HOSTING_PATTERNS, OUTDATED_LIBRARIES, PRIVACY_PATTERNS,
    REDESIGN_SIGNALS, KEY_PAGES
)

DB_PATH = "/Users/kylelangford/ai-context/tools/prospect-finder/db/prospects.db"

# PageSpeed API (free tier)
PAGESPEED_API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


@dataclass
class TechDetection:
    category: str
    name: str
    version: Optional[str] = None
    is_outdated: bool = False
    latest_version: Optional[str] = None
    confidence: int = 100


@dataclass
class Signal:
    signal_type: str
    title: str
    detail: Optional[str] = None
    severity: str = "medium"
    opportunity_weight: int = 5


@dataclass
class PageScan:
    url: str
    page_type: str
    status_code: int = 0
    title: str = ""
    meta_description: str = ""
    h1_text: str = ""
    word_count: int = 0
    load_time_ms: int = 0
    issues: List[str] = field(default_factory=list)


@dataclass
class ScanResult:
    company_id: int
    url: str

    # Tech detection
    cms_detected: Optional[str] = None
    cms_version: Optional[str] = None
    framework_detected: Optional[str] = None
    tech_stack: List[TechDetection] = field(default_factory=list)
    outdated_libraries: List[str] = field(default_factory=list)
    hosting_detected: Optional[str] = None
    analytics_detected: Optional[str] = None

    # Domain/SEO metrics
    domain_age_years: Optional[float] = None
    domain_created: Optional[str] = None
    backlink_count: Optional[int] = None
    referring_domains: Optional[int] = None

    # Funding/News
    recent_funding: Optional[str] = None
    funding_amount: Optional[str] = None
    funding_date: Optional[str] = None

    # Performance
    lighthouse_performance: Optional[int] = None
    lighthouse_accessibility: Optional[int] = None
    lighthouse_best_practices: Optional[int] = None
    lighthouse_seo: Optional[int] = None
    first_contentful_paint: Optional[float] = None
    largest_contentful_paint: Optional[float] = None
    page_size_kb: Optional[int] = None

    # SEO
    has_meta_description: bool = False
    has_og_tags: bool = False
    has_structured_data: bool = False
    has_sitemap: bool = False
    has_robots_txt: bool = False
    mobile_friendly: bool = True
    https_enabled: bool = False
    seo_issues: List[str] = field(default_factory=list)

    # Accessibility
    accessibility_errors: int = 0
    accessibility_warnings: int = 0
    accessibility_issues: List[str] = field(default_factory=list)

    # Content
    copyright_year: Optional[int] = None
    broken_links_count: int = 0
    broken_links: List[str] = field(default_factory=list)

    # Privacy
    has_cookie_banner: bool = False
    has_privacy_policy: bool = False

    # Signals
    hiring_web_roles: bool = False
    recent_rebrand: bool = False
    redesign_signals: List[str] = field(default_factory=list)
    signals: List[Signal] = field(default_factory=list)

    # Pages
    pages: List[PageScan] = field(default_factory=list)

    # Scores
    performance_score: int = 0
    accessibility_score: int = 0
    seo_score: int = 0
    security_score: int = 0
    opportunity_score: int = 0
    aio_score: int = 0  # All-In-One composite score

    # AI analysis
    ai_summary: str = ""
    ai_opportunity_reasons: List[str] = field(default_factory=list)
    ai_suggested_pitch: str = ""


class WebsiteScanner:
    """Scans websites for opportunity signals."""

    def __init__(self, pagespeed_api_key: Optional[str] = None):
        self.pagespeed_api_key = pagespeed_api_key
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; OpportunityScanner/1.0)'
        })

    def scan(self, company_id: int, url: str, company_name: str = None) -> ScanResult:
        """Run full scan on a website."""
        result = ScanResult(company_id=company_id, url=url)
        self._company_name = company_name  # Store for funding check

        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        result.url = url
        result.https_enabled = url.startswith('https://')

        print(f"Scanning {url}...")

        try:
            # Fetch homepage
            homepage = self._fetch_page(url)
            if homepage:
                result.pages.append(homepage)

                # Detect technologies
                self._detect_technologies(result, homepage)

                # Check SEO basics
                self._check_seo(result, homepage)

                # Check privacy
                self._check_privacy(result, homepage)

                # Extract copyright year
                self._extract_copyright(result, homepage)

            # Fetch key pages
            for page_path in KEY_PAGES[1:]:  # Skip homepage
                page_url = urljoin(url, page_path)
                page = self._fetch_page(page_url)
                if page and page.status_code == 200:
                    result.pages.append(page)

            # Check robots.txt and sitemap
            self._check_robots_sitemap(result, url)

            # Check domain age and backlinks
            self._check_domain_age(result, url)
            self._check_backlinks(result, url)

            # Check for funding news (if we have company name)
            if self._company_name:
                self._check_funding(result, self._company_name)

            # Run PageSpeed if available
            if self.pagespeed_api_key:
                self._run_pagespeed(result, url)
            else:
                self._run_pagespeed_free(result, url)

            # Check for hiring signals
            self._check_hiring_signals(result)

            # Generate signals from findings
            self._generate_signals(result)

            # Calculate scores
            self._calculate_scores(result)

            # Generate AI summary (placeholder - needs LLM integration)
            self._generate_ai_summary(result)

        except Exception as e:
            print(f"Error scanning {url}: {e}")
            result.signals.append(Signal(
                signal_type="error",
                title="Scan Error",
                detail=str(e),
                severity="low"
            ))

        return result

    def _fetch_page(self, url: str) -> Optional[PageScan]:
        """Fetch a page and extract basic info."""
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=15, allow_redirects=True)
            load_time = int((time.time() - start_time) * 1000)

            page = PageScan(
                url=url,
                page_type=self._guess_page_type(url),
                status_code=response.status_code,
                load_time_ms=load_time
            )

            if response.status_code == 200:
                html = response.text

                # Extract title
                title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.I | re.S)
                if title_match:
                    page.title = title_match.group(1).strip()

                # Extract meta description
                desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.I)
                if not desc_match:
                    desc_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']', html, re.I)
                if desc_match:
                    page.meta_description = desc_match.group(1).strip()

                # Extract H1
                h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.S)
                if h1_match:
                    page.h1_text = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()

                # Word count (rough)
                text = re.sub(r'<[^>]+>', ' ', html)
                text = re.sub(r'\s+', ' ', text)
                page.word_count = len(text.split())

                # Store HTML for tech detection
                page._html = html
                page._headers = dict(response.headers)

            return page

        except requests.RequestException as e:
            print(f"  Failed to fetch {url}: {e}")
            return None

    def _guess_page_type(self, url: str) -> str:
        """Guess the type of page from URL."""
        path = urlparse(url).path.lower()
        if path in ['/', '']:
            return 'homepage'
        for ptype in ['about', 'contact', 'services', 'careers', 'jobs', 'blog', 'news', 'products', 'solutions']:
            if ptype in path:
                return ptype
        return 'other'

    def _detect_technologies(self, result: ScanResult, homepage: PageScan):
        """Detect CMS, frameworks, and other technologies."""
        if not hasattr(homepage, '_html'):
            return

        html = homepage._html
        headers = getattr(homepage, '_headers', {})

        # Detect CMS
        for cms, patterns in CMS_PATTERNS.items():
            detected = False

            # Check HTML patterns
            for pattern in patterns.get('html', []):
                if re.search(pattern, html, re.I):
                    detected = True
                    break

            # Check header patterns
            for header, pattern in patterns.get('headers', {}).items():
                if header.lower() in {k.lower(): v for k, v in headers.items()}:
                    header_val = headers.get(header, '')
                    if re.search(pattern, header_val, re.I):
                        detected = True
                        break

            if detected:
                result.cms_detected = cms
                result.tech_stack.append(TechDetection(
                    category="cms",
                    name=cms,
                    confidence=90
                ))
                break

        # Detect frameworks
        frameworks_found = []
        for framework, patterns in FRAMEWORK_PATTERNS.items():
            for pattern in patterns.get('html', []):
                if re.search(pattern, html, re.I):
                    frameworks_found.append(framework)
                    result.tech_stack.append(TechDetection(
                        category="framework",
                        name=framework,
                        confidence=80
                    ))
                    break

        if frameworks_found:
            result.framework_detected = ', '.join(frameworks_found)

        # Detect analytics
        analytics_found = []
        for analytics, patterns in ANALYTICS_PATTERNS.items():
            for pattern in patterns.get('html', []):
                if re.search(pattern, html, re.I):
                    analytics_found.append(analytics)
                    result.tech_stack.append(TechDetection(
                        category="analytics",
                        name=analytics,
                        confidence=90
                    ))
                    break

        if analytics_found:
            result.analytics_detected = ', '.join(analytics_found)

        # Detect hosting/CDN
        for hosting, patterns in HOSTING_PATTERNS.items():
            for header, pattern in patterns.get('headers', {}).items():
                header_lower = {k.lower(): v for k, v in headers.items()}
                if header.lower() in header_lower:
                    if re.search(pattern, header_lower[header.lower()], re.I):
                        result.hosting_detected = hosting
                        result.tech_stack.append(TechDetection(
                            category="hosting",
                            name=hosting,
                            confidence=95
                        ))
                        break

        # Check for outdated libraries
        for lib, info in OUTDATED_LIBRARIES.items():
            for pattern, version, severity in info['outdated_patterns']:
                if re.search(pattern, html, re.I):
                    result.outdated_libraries.append(f"{lib} {version}")
                    result.tech_stack.append(TechDetection(
                        category="library",
                        name=lib,
                        version=version,
                        is_outdated=True,
                        latest_version=info['current'],
                        confidence=85
                    ))
                    result.signals.append(Signal(
                        signal_type="outdated_tech",
                        title=f"Outdated {lib.title()}",
                        detail=f"Running {version}, current is {info['current']}",
                        severity=severity,
                        opportunity_weight=8 if severity == "critical" else 5
                    ))

    def _check_seo(self, result: ScanResult, homepage: PageScan):
        """Check basic SEO factors."""
        if not hasattr(homepage, '_html'):
            return

        html = homepage._html

        # Meta description
        result.has_meta_description = bool(homepage.meta_description)
        if not result.has_meta_description:
            result.seo_issues.append("Missing meta description")

        # Open Graph tags
        result.has_og_tags = bool(re.search(r'<meta[^>]*property=["\']og:', html, re.I))
        if not result.has_og_tags:
            result.seo_issues.append("Missing Open Graph tags")

        # Structured data
        result.has_structured_data = bool(re.search(r'application/ld\+json|itemtype="http://schema\.org', html, re.I))

        # Check for title issues
        if not homepage.title:
            result.seo_issues.append("Missing page title")
        elif len(homepage.title) > 60:
            result.seo_issues.append("Title too long (>60 chars)")

        # Check for H1
        if not homepage.h1_text:
            result.seo_issues.append("Missing H1 tag")

        # Check viewport meta (mobile-friendly)
        if not re.search(r'<meta[^>]*name=["\']viewport["\']', html, re.I):
            result.mobile_friendly = False
            result.seo_issues.append("Missing viewport meta tag")

    def _check_privacy(self, result: ScanResult, homepage: PageScan):
        """Check privacy/cookie compliance."""
        if not hasattr(homepage, '_html'):
            return

        html = homepage._html

        # Cookie banner detection
        for pattern in PRIVACY_PATTERNS['cookie_banners']:
            if re.search(pattern, html, re.I):
                result.has_cookie_banner = True
                break

        # Privacy policy link
        for pattern in PRIVACY_PATTERNS['privacy_policy_links']:
            if re.search(pattern, html, re.I):
                result.has_privacy_policy = True
                break

        if not result.has_cookie_banner:
            result.signals.append(Signal(
                signal_type="privacy",
                title="No Cookie Consent",
                detail="No cookie consent banner detected",
                severity="medium",
                opportunity_weight=4
            ))

    def _extract_copyright(self, result: ScanResult, homepage: PageScan):
        """Extract copyright year from page."""
        if not hasattr(homepage, '_html'):
            return

        html = homepage._html

        # Look for copyright year patterns
        year_match = re.search(r'(?:©|&copy;|copyright)\s*(\d{4})', html, re.I)
        if year_match:
            result.copyright_year = int(year_match.group(1))
            current_year = datetime.now().year

            if result.copyright_year < current_year - 1:
                result.signals.append(Signal(
                    signal_type="stale_content",
                    title="Outdated Copyright",
                    detail=f"Copyright shows {result.copyright_year} (current: {current_year})",
                    severity="low",
                    opportunity_weight=3
                ))

    def _check_robots_sitemap(self, result: ScanResult, base_url: str):
        """Check for robots.txt and sitemap."""
        # Check robots.txt
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=10)
            result.has_robots_txt = response.status_code == 200
        except:
            result.has_robots_txt = False

        # Check sitemap
        try:
            sitemap_url = urljoin(base_url, '/sitemap.xml')
            response = self.session.get(sitemap_url, timeout=10)
            result.has_sitemap = response.status_code == 200
        except:
            result.has_sitemap = False

        if not result.has_sitemap:
            result.seo_issues.append("No sitemap.xml found")

    def _check_domain_age(self, result: ScanResult, url: str):
        """Check domain age using Wayback Machine API."""
        try:
            domain = urlparse(url).netloc.replace('www.', '')

            # Use Wayback Machine CDX API to find first snapshot
            cdx_url = f"http://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=1&from=1990"
            response = requests.get(cdx_url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:  # First row is headers
                    timestamp = data[1][1]  # timestamp field
                    year = int(timestamp[:4])
                    month = int(timestamp[4:6])
                    day = int(timestamp[6:8])

                    first_date = datetime(year, month, day)
                    result.domain_created = first_date.strftime('%Y-%m-%d')

                    age_days = (datetime.now() - first_date).days
                    result.domain_age_years = round(age_days / 365.25, 1)

                    print(f"  Domain age: {result.domain_age_years} years (first seen: {result.domain_created})")

                    # Signal for old domains
                    if result.domain_age_years >= 10:
                        result.signals.append(Signal(
                            signal_type="domain_age",
                            title="Established Domain",
                            detail=f"Domain is {result.domain_age_years} years old",
                            severity="low",
                            opportunity_weight=3
                        ))
        except Exception as e:
            print(f"  Domain age check failed: {e}")

    def _check_backlinks(self, result: ScanResult, url: str):
        """Check backlink count using free APIs."""
        domain = urlparse(url).netloc.replace('www.', '')

        # Method 1: Try Moz Link Explorer free API via their website
        # Method 2: Use CommonCrawl index to estimate
        # Method 3: Estimate from domain age + site characteristics

        # First try: Check if domain is indexed well (Google site: search estimate)
        try:
            # Use Bing to estimate indexed pages as proxy for authority
            bing_url = f"https://www.bing.com/search?q=site%3A{domain}"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(bing_url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Look for result count in page
                import re
                match = re.search(r'([\d,]+)\s*results?', response.text, re.I)
                if match:
                    indexed_pages = int(match.group(1).replace(',', ''))
                    # Rough estimate: indexed pages * 5-10 = backlinks
                    estimated_backlinks = indexed_pages * 7
                    result.backlink_count = estimated_backlinks
                    print(f"  Est. backlinks: ~{estimated_backlinks:,} ({indexed_pages:,} indexed pages)")
                    return
        except Exception as e:
            print(f"  Bing check failed: {e}")

        # Fallback: Estimate from domain age
        if result.domain_age_years and result.backlink_count is None:
            # Very rough estimate based on age
            # Older domains generally have more backlinks
            age_factor = min(result.domain_age_years, 20)  # Cap at 20 years
            estimated = int(age_factor * 500)  # ~500 links per year for established site
            result.backlink_count = estimated
            print(f"  Est. backlinks (from age): ~{estimated:,}")

    def _check_funding(self, result: ScanResult, company_name: str):
        """Check for recent funding announcements."""
        try:
            # Clean company name for search
            search_name = re.sub(r'\s*(Inc\.?|LLC|Corp\.?|Corporation|Company|Co\.?)\s*$', '', company_name, flags=re.I).strip()

            # Search Bing News for funding announcements
            search_url = f"https://www.bing.com/news/search?q={requests.utils.quote(search_name + ' funding raised series')}"

            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                # Decode URL-encoded content and normalize
                from html import unescape
                html = unescape(response.text)

                # Check if company name appears near funding keywords
                company_lower = search_name.lower()
                html_lower = html.lower()

                # Only proceed if company name is actually in the results
                if company_lower not in html_lower:
                    return

                # Look for funding patterns in results
                funding_patterns = [
                    r'raises?\s+\$?([\d,.]+)\s*(million|billion|m|b)\b',
                    r'series\s+([A-E])\s*(?:funding|round)?',
                    r'\$?([\d,.]+)\s*(million|billion|m|b)\s+(?:funding|investment|round)',
                    r'secured?\s+\$?([\d,.]+)\s*(million|billion|m|b)',
                    r'funding\s+(?:of\s+)?\$?([\d,.]+)\s*(million|billion|m|b)',
                ]

                for pattern in funding_patterns:
                    match = re.search(pattern, html, re.I)
                    if match:
                        # Extract amount
                        if 'series' in pattern.lower():
                            result.recent_funding = f"Series {match.group(1).upper()}"
                        else:
                            amount = match.group(1).replace(',', '')
                            unit = match.group(2).upper()
                            if unit in ['M', 'MILLION']:
                                result.funding_amount = f"${amount}M"
                            elif unit in ['B', 'BILLION']:
                                result.funding_amount = f"${amount}B"
                            result.recent_funding = f"Raised {result.funding_amount}"

                        print(f"  Funding detected: {result.recent_funding}")

                        # Add high-value signal
                        result.signals.append(Signal(
                            signal_type="funding",
                            title="Recent Funding",
                            detail=result.recent_funding,
                            severity="high",
                            opportunity_weight=10
                        ))
                        return

                # Also check for IPO, acquisition, merger
                if re.search(rf'{re.escape(company_lower)}.*?\b(IPO|goes?\s+public|acquisition|acquired|merger)\b', html_lower):
                    result.recent_funding = "Major event (IPO/M&A)"
                    print(f"  Major event detected: IPO or M&A activity")
                    result.signals.append(Signal(
                        signal_type="funding",
                        title="Major Corporate Event",
                        detail="IPO, acquisition, or merger activity detected",
                        severity="high",
                        opportunity_weight=8
                    ))

        except Exception as e:
            print(f"  Funding check failed: {e}")

    def _run_pagespeed_free(self, result: ScanResult, url: str):
        """Run PageSpeed Insights (free tier, limited)."""
        try:
            params = {
                'url': url,
                'strategy': 'mobile',
                'category': ['performance', 'accessibility', 'seo', 'best-practices']
            }
            if self.pagespeed_api_key:
                params['key'] = self.pagespeed_api_key

            print(f"  Running PageSpeed analysis...")
            response = requests.get(PAGESPEED_API, params=params, timeout=60)

            if response.status_code == 200:
                data = response.json()

                # Extract Lighthouse scores
                categories = data.get('lighthouseResult', {}).get('categories', {})

                if 'performance' in categories:
                    result.lighthouse_performance = int(categories['performance'].get('score', 0) * 100)
                if 'accessibility' in categories:
                    result.lighthouse_accessibility = int(categories['accessibility'].get('score', 0) * 100)
                if 'best-practices' in categories:
                    result.lighthouse_best_practices = int(categories['best-practices'].get('score', 0) * 100)
                if 'seo' in categories:
                    result.lighthouse_seo = int(categories['seo'].get('score', 0) * 100)

                # Extract performance metrics
                audits = data.get('lighthouseResult', {}).get('audits', {})
                if 'first-contentful-paint' in audits:
                    result.first_contentful_paint = audits['first-contentful-paint'].get('numericValue', 0) / 1000
                if 'largest-contentful-paint' in audits:
                    result.largest_contentful_paint = audits['largest-contentful-paint'].get('numericValue', 0) / 1000

                print(f"  Performance: {result.lighthouse_performance}, Accessibility: {result.lighthouse_accessibility}")

        except Exception as e:
            print(f"  PageSpeed API error: {e}")

    def _run_pagespeed(self, result: ScanResult, url: str):
        """Run PageSpeed with API key."""
        self._run_pagespeed_free(result, url)

    def _check_hiring_signals(self, result: ScanResult):
        """Check careers page for web-related job postings."""
        careers_page = None
        for page in result.pages:
            if page.page_type in ['careers', 'jobs']:
                careers_page = page
                break

        if careers_page and hasattr(careers_page, '_html'):
            html = careers_page._html.lower()
            for role in REDESIGN_SIGNALS['job_postings']:
                if role in html:
                    result.hiring_web_roles = True
                    result.redesign_signals.append(f"Hiring: {role}")
                    result.signals.append(Signal(
                        signal_type="hiring",
                        title="Hiring Web Talent",
                        detail=f"Job posting for {role} detected",
                        severity="high",
                        opportunity_weight=9
                    ))
                    break

    def _generate_signals(self, result: ScanResult):
        """Generate opportunity signals from findings."""
        # Performance signals
        if result.lighthouse_performance is not None:
            if result.lighthouse_performance < 50:
                result.signals.append(Signal(
                    signal_type="performance",
                    title="Poor Performance",
                    detail=f"Lighthouse performance score: {result.lighthouse_performance}/100",
                    severity="high",
                    opportunity_weight=8
                ))
            elif result.lighthouse_performance < 70:
                result.signals.append(Signal(
                    signal_type="performance",
                    title="Moderate Performance Issues",
                    detail=f"Lighthouse performance score: {result.lighthouse_performance}/100",
                    severity="medium",
                    opportunity_weight=5
                ))

        # Accessibility signals
        if result.lighthouse_accessibility is not None:
            if result.lighthouse_accessibility < 70:
                result.signals.append(Signal(
                    signal_type="accessibility",
                    title="Accessibility Issues",
                    detail=f"Lighthouse accessibility score: {result.lighthouse_accessibility}/100",
                    severity="high",
                    opportunity_weight=8
                ))

        # HTTPS
        if not result.https_enabled:
            result.signals.append(Signal(
                signal_type="security",
                title="No HTTPS",
                detail="Site not using HTTPS",
                severity="critical",
                opportunity_weight=7
            ))

        # SEO issues
        if len(result.seo_issues) >= 3:
            result.signals.append(Signal(
                signal_type="seo",
                title="Multiple SEO Issues",
                detail=f"{len(result.seo_issues)} SEO issues detected",
                severity="medium",
                opportunity_weight=5
            ))

        # CMS-specific signals
        if result.cms_detected:
            if result.cms_detected == 'drupal':
                # Check for Drupal version in outdated list
                for lib in result.outdated_libraries:
                    if 'drupal' in lib.lower():
                        result.signals.append(Signal(
                            signal_type="cms_upgrade",
                            title="Drupal Upgrade Needed",
                            detail=f"Running outdated Drupal version",
                            severity="high",
                            opportunity_weight=9
                        ))
                        break

    def _calculate_scores(self, result: ScanResult):
        """Calculate opportunity and component scores."""
        # Performance score
        result.performance_score = result.lighthouse_performance or 50

        # Accessibility score
        result.accessibility_score = result.lighthouse_accessibility or 50

        # SEO score
        seo_base = result.lighthouse_seo or 50
        seo_penalty = len(result.seo_issues) * 5
        result.seo_score = max(0, seo_base - seo_penalty)

        # Security score
        security_score = 100
        if not result.https_enabled:
            security_score -= 30
        if not result.has_cookie_banner:
            security_score -= 15
        if not result.has_privacy_policy:
            security_score -= 10
        result.security_score = max(0, security_score)

        # Opportunity score (inverse of quality - worse site = more opportunity)
        # Weight signals by their opportunity_weight
        signal_score = sum(s.opportunity_weight for s in result.signals)

        # Normalize to 0-100
        # More signals = higher opportunity
        base_opportunity = min(100, signal_score * 3)

        # Boost for outdated tech
        if result.outdated_libraries:
            base_opportunity += 10

        # Boost for hiring signals
        if result.hiring_web_roles:
            base_opportunity += 15

        # Boost for poor performance
        if result.lighthouse_performance and result.lighthouse_performance < 50:
            base_opportunity += 10

        result.opportunity_score = min(100, base_opportunity)

        # AIO Score: All-In-One composite score
        # Formula: 30% fit + 25% opportunity + 15% domain + 15% funding + 15% hiring
        # Note: fit_score comes from the company record, not the scan
        aio = 0

        # Opportunity component (25%)
        aio += result.opportunity_score * 0.25

        # Domain age component (15%) - older domains = more established = higher score
        if result.domain_age_years:
            # Scale: 0 years = 0, 5+ years = 15, 10+ years = full 15
            domain_factor = min(result.domain_age_years / 10, 1.0) * 15
            aio += domain_factor

        # Funding component (15%) - recent funding = budget available
        if result.recent_funding:
            aio += 15  # Full points for any funding signal

        # Hiring component (15%) - hiring web roles = active intent
        if result.hiring_web_roles:
            aio += 15  # Full points for hiring signals

        # Base score for having scan data (fills remaining 30% partially)
        # This will be combined with fit_score from company in the UI
        aio += 10  # Base points for having a scan

        result.aio_score = min(100, int(aio))

    def _generate_ai_summary(self, result: ScanResult):
        """Generate AI summary of the opportunity.

        Note: This is a template-based version. In production, this would
        call Claude or another LLM to generate a more nuanced summary.
        """
        # Collect reasons
        reasons = []

        if result.cms_detected:
            reasons.append(f"{result.cms_detected.title()} CMS detected")

        for lib in result.outdated_libraries:
            reasons.append(f"Outdated {lib}")

        if result.lighthouse_performance and result.lighthouse_performance < 70:
            reasons.append(f"Performance issues (score: {result.lighthouse_performance})")

        if result.lighthouse_accessibility and result.lighthouse_accessibility < 80:
            reasons.append(f"Accessibility gaps (score: {result.lighthouse_accessibility})")

        if result.hiring_web_roles:
            reasons.append("Actively hiring web talent")

        if result.seo_issues:
            reasons.append(f"{len(result.seo_issues)} SEO issues")

        if not result.has_cookie_banner:
            reasons.append("Missing cookie consent")

        result.ai_opportunity_reasons = reasons

        # Generate summary
        summary_parts = []
        if result.cms_detected:
            summary_parts.append(f"{result.cms_detected.title()} site")
        if result.outdated_libraries:
            summary_parts.append("running outdated libraries")
        if result.lighthouse_performance and result.lighthouse_performance < 60:
            summary_parts.append("with poor mobile performance")
        if result.lighthouse_accessibility and result.lighthouse_accessibility < 70:
            summary_parts.append("and accessibility issues")
        if result.hiring_web_roles:
            summary_parts.append(". Actively hiring web roles")

        result.ai_summary = " ".join(summary_parts) if summary_parts else "Website analyzed"

        # Generate pitch
        pitches = []
        if result.cms_detected == 'drupal' and result.outdated_libraries:
            pitches.append("Drupal modernization")
        elif result.cms_detected == 'wordpress' and result.outdated_libraries:
            pitches.append("WordPress upgrade")
        elif result.cms_detected in ['aem', 'sitecore']:
            pitches.append("Enterprise CMS optimization")

        if result.lighthouse_accessibility and result.lighthouse_accessibility < 80:
            pitches.append("accessibility remediation")

        if result.lighthouse_performance and result.lighthouse_performance < 60:
            pitches.append("performance optimization")

        if not result.has_cookie_banner or not result.has_privacy_policy:
            pitches.append("privacy compliance")

        result.ai_suggested_pitch = " + ".join(pitches) if pitches else "Website audit and optimization"


def save_scan_result(result: ScanResult):
    """Save scan result to database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert main scan record
    cursor.execute("""
        INSERT INTO scans (
            company_id, url, scan_status, pages_crawled,
            opportunity_score, performance_score, accessibility_score, seo_score, security_score, aio_score,
            cms_detected, cms_version, framework_detected, hosting_detected,
            tech_stack, outdated_libraries,
            lighthouse_performance, lighthouse_accessibility, lighthouse_best_practices, lighthouse_seo,
            first_contentful_paint, largest_contentful_paint,
            has_meta_description, has_og_tags, has_structured_data, has_sitemap, has_robots_txt,
            mobile_friendly, https_enabled, seo_issues,
            accessibility_errors, accessibility_warnings, accessibility_issues,
            copyright_year, broken_links_count, broken_links,
            analytics_detected, has_cookie_banner, has_privacy_policy,
            hiring_web_roles, recent_rebrand, redesign_signals,
            ai_summary, ai_opportunity_reasons, ai_suggested_pitch,
            domain_age_years, domain_created, backlink_count, referring_domains,
            recent_funding, funding_amount, funding_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        result.company_id, result.url, 'completed', len(result.pages),
        result.opportunity_score, result.performance_score, result.accessibility_score, result.seo_score, result.security_score, result.aio_score,
        result.cms_detected, result.cms_version, result.framework_detected, result.hosting_detected,
        json.dumps([asdict(t) for t in result.tech_stack]), json.dumps(result.outdated_libraries),
        result.lighthouse_performance, result.lighthouse_accessibility, result.lighthouse_best_practices, result.lighthouse_seo,
        result.first_contentful_paint, result.largest_contentful_paint,
        result.has_meta_description, result.has_og_tags, result.has_structured_data, result.has_sitemap, result.has_robots_txt,
        result.mobile_friendly, result.https_enabled, json.dumps(result.seo_issues),
        result.accessibility_errors, result.accessibility_warnings, json.dumps(result.accessibility_issues),
        result.copyright_year, result.broken_links_count, json.dumps(result.broken_links),
        result.analytics_detected, result.has_cookie_banner, result.has_privacy_policy,
        result.hiring_web_roles, result.recent_rebrand, json.dumps(result.redesign_signals),
        result.ai_summary, json.dumps(result.ai_opportunity_reasons), result.ai_suggested_pitch,
        result.domain_age_years, result.domain_created, result.backlink_count, result.referring_domains,
        result.recent_funding, result.funding_amount, result.funding_date
    ))

    scan_id = cursor.lastrowid

    # Insert signals
    for signal in result.signals:
        cursor.execute("""
            INSERT INTO scan_signals (scan_id, signal_type, signal_title, signal_detail, severity, opportunity_weight)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (scan_id, signal.signal_type, signal.title, signal.detail, signal.severity, signal.opportunity_weight))

    # Insert pages
    for page in result.pages:
        cursor.execute("""
            INSERT INTO scan_pages (scan_id, url, page_type, title, meta_description, status_code, load_time_ms, h1_text, word_count, issues)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, page.url, page.page_type, page.title, page.meta_description, page.status_code, page.load_time_ms, page.h1_text, page.word_count, json.dumps(page.issues)))

    # Insert tech detections
    for tech in result.tech_stack:
        cursor.execute("""
            INSERT INTO scan_technologies (scan_id, category, name, version, is_outdated, latest_version, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (scan_id, tech.category, tech.name, tech.version, tech.is_outdated, tech.latest_version, tech.confidence))

    conn.commit()
    conn.close()

    return scan_id


def format_scan_result(result: ScanResult, company_name: str) -> str:
    """Format scan result for display."""
    lines = [
        f"\n{'='*60}",
        f"{company_name} — {result.opportunity_score}/100 opportunity",
        f"{'='*60}",
        ""
    ]

    # Tech stack
    if result.cms_detected:
        lines.append(f"CMS: {result.cms_detected.title()}")
    if result.framework_detected:
        lines.append(f"Framework: {result.framework_detected}")
    if result.hosting_detected:
        lines.append(f"Hosting: {result.hosting_detected}")

    lines.append("")

    # Scores
    if result.lighthouse_performance is not None:
        lines.append(f"Performance: {result.lighthouse_performance}/100")
    if result.lighthouse_accessibility is not None:
        lines.append(f"Accessibility: {result.lighthouse_accessibility}/100")
    if result.lighthouse_seo is not None:
        lines.append(f"SEO: {result.lighthouse_seo}/100")

    lines.append("")

    # Signals
    if result.signals:
        lines.append("Signals:")
        for signal in sorted(result.signals, key=lambda s: -s.opportunity_weight)[:5]:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(signal.severity, "⚪")
            lines.append(f"  {severity_icon} {signal.title}")
            if signal.detail:
                lines.append(f"     {signal.detail}")

    lines.append("")

    # AI Summary
    if result.ai_summary:
        lines.append(f"Summary: {result.ai_summary}")
    if result.ai_suggested_pitch:
        lines.append(f"Suggested pitch: {result.ai_suggested_pitch}")

    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python scanner.py <url or company_id>")
        print("       python scanner.py scan-all")
        print("       python scanner.py scan-top <n>")
        sys.exit(1)

    scanner = WebsiteScanner()

    if sys.argv[1] == "scan-all":
        # Scan all companies with websites
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, website FROM companies WHERE website IS NOT NULL")
        companies = cursor.fetchall()
        conn.close()

        for company_id, name, url in companies:
            result = scanner.scan(company_id, url, company_name=name)
            save_scan_result(result)
            print(format_scan_result(result, name))

    elif sys.argv[1] == "scan-top":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, website FROM companies
            WHERE website IS NOT NULL
            ORDER BY fit_score DESC
            LIMIT ?
        """, (n,))
        companies = cursor.fetchall()
        conn.close()

        for company_id, name, url in companies:
            result = scanner.scan(company_id, url, company_name=name)
            save_scan_result(result)
            print(format_scan_result(result, name))

    else:
        # Single URL scan
        url = sys.argv[1]
        result = scanner.scan(0, url)
        print(format_scan_result(result, url))
