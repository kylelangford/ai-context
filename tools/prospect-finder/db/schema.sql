-- Lookalike Prospect Database Schema
-- Created: 2026-09-28

-- Companies table - core prospect data
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,

    -- Classification
    industry TEXT,
    segment TEXT,  -- healthcare, higher-ed, publishing, etc.
    org_type TEXT, -- enterprise, nonprofit, startup, etc.

    -- Size & Geography
    size_range TEXT,  -- "50-100", "1000-5000", etc.
    employee_count INTEGER,
    geography TEXT,  -- regional, national, global
    headquarters TEXT,

    -- Similarity
    similar_to TEXT,  -- which existing client they match
    match_tier INTEGER DEFAULT 2,  -- 1=high, 2=strong, 3=good
    match_reason TEXT,

    -- Scoring
    fit_score INTEGER DEFAULT 50,  -- 0-100
    budget_estimate TEXT,  -- "enterprise", "mid-market", "small"
    budget_low INTEGER,
    budget_high INTEGER,
    likelihood INTEGER DEFAULT 50,  -- 0-100 close probability
    urgency INTEGER DEFAULT 50,  -- 0-100 how soon they might buy
    priority_rank INTEGER,

    -- Status
    status TEXT DEFAULT 'new',  -- new, researching, outreach, pitched, negotiating, won, lost, dormant
    stage TEXT DEFAULT 'prospect',  -- prospect, lead, opportunity, customer
    lost_reason TEXT,

    -- Research
    website TEXT,
    linkedin_url TEXT,
    cms_platform TEXT,
    tech_stack TEXT,
    recent_news TEXT,
    funding_stage TEXT,
    funding_amount TEXT,
    last_funding_date TEXT,

    -- Signals
    signal_type TEXT,  -- funding, merger, rebrand, rfi, leadership
    signal_detail TEXT,
    signal_date TEXT,

    -- Metadata
    source TEXT DEFAULT 'lookalike-finder',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Tags (comma-separated)
    tags TEXT
);

-- Contacts table - people at companies
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,

    -- Basic info
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    title TEXT,
    department TEXT,  -- marketing, IT, executive, etc.

    -- Contact info
    email TEXT,
    phone TEXT,
    linkedin_url TEXT,

    -- Role
    is_decision_maker BOOLEAN DEFAULT 0,
    is_influencer BOOLEAN DEFAULT 0,
    is_champion BOOLEAN DEFAULT 0,

    -- Status
    relationship_status TEXT DEFAULT 'unknown',  -- unknown, cold, warm, engaged, advocate

    -- Metadata
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (company_id) REFERENCES companies(id)
);

-- Outreach table - tracking touches
CREATE TABLE IF NOT EXISTS outreach (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    contact_id INTEGER,

    -- Activity
    activity_type TEXT NOT NULL,  -- email, call, meeting, linkedin, event, referral
    direction TEXT DEFAULT 'outbound',  -- outbound, inbound
    subject TEXT,
    content TEXT,

    -- Result
    outcome TEXT,  -- sent, opened, replied, meeting_booked, no_response, declined
    next_step TEXT,
    follow_up_date DATE,

    -- Metadata
    activity_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    logged_by TEXT,

    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

-- Notes table - research and general notes
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    contact_id INTEGER,

    -- Content
    note_type TEXT DEFAULT 'general',  -- general, research, meeting, call, competitive, technical
    title TEXT,
    content TEXT NOT NULL,

    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,

    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

-- Tags table - for flexible categorization
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    color TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Company-Tags junction table
CREATE TABLE IF NOT EXISTS company_tags (
    company_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (company_id, tag_id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (tag_id) REFERENCES tags(id)
);

-- Views for common queries

-- View: Hot prospects (high fit, recent signal)
CREATE VIEW IF NOT EXISTS v_hot_prospects AS
SELECT
    c.id,
    c.name,
    c.segment,
    c.fit_score,
    c.status,
    c.signal_type,
    c.signal_detail,
    c.similar_to,
    c.match_tier
FROM companies c
WHERE c.fit_score >= 70
  AND c.status NOT IN ('won', 'lost', 'dormant')
ORDER BY c.fit_score DESC, c.match_tier ASC;

-- View: Needs follow-up
CREATE VIEW IF NOT EXISTS v_needs_followup AS
SELECT
    c.name,
    c.status,
    o.activity_type,
    o.outcome,
    o.follow_up_date,
    o.next_step
FROM companies c
JOIN outreach o ON c.id = o.company_id
WHERE o.follow_up_date <= DATE('now', '+7 days')
  AND o.follow_up_date >= DATE('now', '-30 days')
  AND c.status NOT IN ('won', 'lost', 'dormant')
ORDER BY o.follow_up_date ASC;

-- View: Pipeline summary by stage
CREATE VIEW IF NOT EXISTS v_pipeline_summary AS
SELECT
    status,
    COUNT(*) as count,
    AVG(fit_score) as avg_fit_score,
    SUM(CASE WHEN match_tier = 1 THEN 1 ELSE 0 END) as tier1_count
FROM companies
GROUP BY status
ORDER BY
    CASE status
        WHEN 'negotiating' THEN 1
        WHEN 'pitched' THEN 2
        WHEN 'outreach' THEN 3
        WHEN 'researching' THEN 4
        WHEN 'new' THEN 5
        ELSE 6
    END;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_companies_segment ON companies(segment);
CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
CREATE INDEX IF NOT EXISTS idx_companies_fit_score ON companies(fit_score);
CREATE INDEX IF NOT EXISTS idx_companies_match_tier ON companies(match_tier);
CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_outreach_company ON outreach(company_id);
CREATE INDEX IF NOT EXISTS idx_outreach_date ON outreach(activity_date);
CREATE INDEX IF NOT EXISTS idx_notes_company ON notes(company_id);

-- Triggers for updated_at
CREATE TRIGGER IF NOT EXISTS update_companies_timestamp
AFTER UPDATE ON companies
BEGIN
    UPDATE companies SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_contacts_timestamp
AFTER UPDATE ON contacts
BEGIN
    UPDATE contacts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
