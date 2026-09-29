-- Website Opportunity Scanner Schema Extension
-- Extends the prospects database with scan results

-- Scan results table - one record per scan
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- Scan metadata
    url TEXT NOT NULL,
    scan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    scan_status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
    scan_duration_seconds INTEGER,
    pages_crawled INTEGER DEFAULT 0,

    -- Overall scores (0-100)
    opportunity_score INTEGER,
    performance_score INTEGER,
    accessibility_score INTEGER,
    seo_score INTEGER,
    security_score INTEGER,

    -- CMS/Tech Detection
    cms_detected TEXT,  -- wordpress, drupal, aem, webflow, sitecore, etc.
    cms_version TEXT,
    framework_detected TEXT,  -- react, vue, angular, etc.
    framework_version TEXT,
    server_detected TEXT,  -- nginx, apache, etc.
    hosting_detected TEXT,  -- aws, pantheon, wpengine, acquia, vercel, etc.

    -- Tech stack (JSON array)
    tech_stack TEXT,  -- ["jQuery 3.6", "Bootstrap 5", "Google Analytics 4"]
    outdated_libraries TEXT,  -- ["jQuery 1.x", "Bootstrap 3"]

    -- Performance metrics
    lighthouse_performance INTEGER,
    lighthouse_accessibility INTEGER,
    lighthouse_best_practices INTEGER,
    lighthouse_seo INTEGER,
    first_contentful_paint REAL,  -- seconds
    largest_contentful_paint REAL,
    cumulative_layout_shift REAL,
    total_blocking_time INTEGER,  -- ms
    page_size_kb INTEGER,
    request_count INTEGER,

    -- Accessibility issues
    accessibility_errors INTEGER DEFAULT 0,
    accessibility_warnings INTEGER DEFAULT 0,
    accessibility_issues TEXT,  -- JSON array of issues
    wcag_level TEXT,  -- estimated: none, A, AA, AAA

    -- SEO analysis
    has_meta_description BOOLEAN,
    has_og_tags BOOLEAN,
    has_structured_data BOOLEAN,
    has_sitemap BOOLEAN,
    has_robots_txt BOOLEAN,
    mobile_friendly BOOLEAN,
    https_enabled BOOLEAN,
    seo_issues TEXT,  -- JSON array

    -- Content analysis
    copyright_year INTEGER,
    content_freshness TEXT,  -- stale, moderate, fresh
    last_blog_post_date TEXT,
    broken_links_count INTEGER DEFAULT 0,
    broken_links TEXT,  -- JSON array

    -- Analytics/Privacy
    analytics_detected TEXT,  -- ga4, gtm, adobe, etc.
    has_cookie_banner BOOLEAN,
    has_privacy_policy BOOLEAN,
    gdpr_compliant BOOLEAN,

    -- Signals
    hiring_web_roles BOOLEAN,
    recent_rebrand BOOLEAN,
    redesign_signals TEXT,  -- JSON array of signals

    -- AI Analysis
    ai_summary TEXT,
    ai_opportunity_reasons TEXT,  -- JSON array
    ai_suggested_pitch TEXT,
    ai_confidence INTEGER,  -- 0-100

    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Page-level scan data
CREATE TABLE IF NOT EXISTS scan_pages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,

    url TEXT NOT NULL,
    page_type TEXT,  -- homepage, about, services, blog, contact, careers
    title TEXT,
    meta_description TEXT,

    -- Page metrics
    status_code INTEGER,
    load_time_ms INTEGER,
    page_size_kb INTEGER,

    -- Content
    h1_text TEXT,
    word_count INTEGER,
    image_count INTEGER,
    images_without_alt INTEGER,

    -- Issues found
    issues TEXT,  -- JSON array

    crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (scan_id) REFERENCES scans(id)
);

-- Tech detections (many-to-one with scans)
CREATE TABLE IF NOT EXISTS scan_technologies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,

    category TEXT NOT NULL,  -- cms, framework, analytics, cdn, hosting, library, etc.
    name TEXT NOT NULL,
    version TEXT,
    is_outdated BOOLEAN DEFAULT 0,
    latest_version TEXT,
    confidence INTEGER DEFAULT 100,  -- 0-100

    FOREIGN KEY (scan_id) REFERENCES scans(id)
);

-- Opportunity signals
CREATE TABLE IF NOT EXISTS scan_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id INTEGER NOT NULL,

    signal_type TEXT NOT NULL,  -- performance, accessibility, outdated_tech, hiring, rebrand, etc.
    signal_title TEXT NOT NULL,
    signal_detail TEXT,
    severity TEXT DEFAULT 'medium',  -- low, medium, high, critical
    opportunity_weight INTEGER DEFAULT 5,  -- 1-10 contribution to opportunity score

    FOREIGN KEY (scan_id) REFERENCES scans(id)
);

-- Views

-- View: Latest scan per company
CREATE VIEW IF NOT EXISTS v_latest_scans AS
SELECT
    c.id as company_id,
    c.name as company_name,
    c.segment,
    s.*
FROM companies c
LEFT JOIN scans s ON c.id = s.company_id
WHERE s.id = (
    SELECT MAX(s2.id) FROM scans s2 WHERE s2.company_id = c.id
) OR s.id IS NULL;

-- View: High opportunity prospects
CREATE VIEW IF NOT EXISTS v_opportunities AS
SELECT
    c.name,
    c.segment,
    c.fit_score,
    s.opportunity_score,
    s.cms_detected,
    s.lighthouse_performance,
    s.lighthouse_accessibility,
    s.ai_summary,
    s.ai_suggested_pitch,
    s.scan_date
FROM companies c
JOIN scans s ON c.id = s.company_id
WHERE s.opportunity_score >= 70
  AND s.id = (SELECT MAX(s2.id) FROM scans s2 WHERE s2.company_id = c.id)
ORDER BY s.opportunity_score DESC;

-- View: Scan signals summary
CREATE VIEW IF NOT EXISTS v_scan_signals_summary AS
SELECT
    c.name,
    s.opportunity_score,
    GROUP_CONCAT(ss.signal_title, ' | ') as signals
FROM companies c
JOIN scans s ON c.id = s.company_id
JOIN scan_signals ss ON s.id = ss.scan_id
WHERE s.id = (SELECT MAX(s2.id) FROM scans s2 WHERE s2.company_id = c.id)
GROUP BY c.id
ORDER BY s.opportunity_score DESC;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_scans_company ON scans(company_id);
CREATE INDEX IF NOT EXISTS idx_scans_opportunity ON scans(opportunity_score);
CREATE INDEX IF NOT EXISTS idx_scans_date ON scans(scan_date);
CREATE INDEX IF NOT EXISTS idx_scan_pages_scan ON scan_pages(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_tech_scan ON scan_technologies(scan_id);
CREATE INDEX IF NOT EXISTS idx_scan_signals_scan ON scan_signals(scan_id);
