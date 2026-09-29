# Lookalike Client Finder

## Command
Say: `find prospects` or `run prospect finder`

## What It Does
Analyzes your client roster and finds similar organizations that would be good prospects.

## Output Log
**IMPORTANT:** Every time this tool runs, create a timestamped log file:

```
~/ai-context/tools/prospect-finder/logs/YYYY-MM-DD_prospect-run.md
```

The log should contain:
1. Run timestamp
2. Segments searched
3. Number of prospects found per segment
4. Top 10 immediate targets (table format)
5. Full prospect list with similarity explanations
6. Search queries used
7. Any errors or limitations encountered

Example filename: `2026-09-28_prospect-run.md`

## How to Use

### Full Analysis
```
find prospects
```
This will:
1. Read the client roster from `~/ai-context/tools/prospect-finder/client-roster.json`
2. Identify patterns across your strongest clients
3. Search for 100 similar organizations
4. Return matches with similarity explanations

### Segment-Specific Search
```
find prospects in [SEGMENT]
```
Example segments:
- `healthcare` - Health insurers, digital health, providers
- `higher-ed` - Universities, colleges, alumni magazines
- `publishing` - Enthusiast media, magazines, digital publishers
- `nonprofit` - Cause organizations, foundations, associations
- `edtech` - K-12 and higher ed technology companies
- `energy` - Utilities, clean energy, infrastructure
- `saas` - B2B software, martech, enterprise tools

### Update Client Roster
```
add client [NAME] to roster
```
This will add a new client to the JSON and re-analyze patterns.

## Output Files

| File | Description |
|------|-------------|
| `client-roster.json` | All clients with attributes |
| `client-analysis.md` | Pattern analysis and sweet spots |
| `search-profiles.json` | Search criteria by segment |
| `prospect-recommendations.md` | Full prospect list with explanations |
| `logs/YYYY-MM-DD_prospect-run.md` | Timestamped run log with results |

## Attributes Tracked

For each client:
- **Industry** - Primary sector
- **Org Type** - Enterprise, nonprofit, startup, etc.
- **Size** - Employee count range
- **Geography** - Regional, national, global
- **Characteristics** - Key traits (B2B, content-heavy, regulated, etc.)
- **Digital Complexity** - Low, medium, high
- **Budget Tier** - Enterprise, mid-market, small, nonprofit

## Database Commands

The prospect database is at `~/ai-context/tools/prospect-finder/db/prospects.db`

### Quick Queries (via Claude)
Say any of these:
- `show hot prospects` - Top 20 high-fit prospects
- `show prospects in [segment]` - Filter by healthcare, higher-ed, publishing, etc.
- `search prospects for [query]` - Search by name or tags
- `show [company name]` - Full details for a company
- `show pipeline` - Status summary
- `show segments` - Counts by segment

### Update Prospects
- `update [company] status to [status]` - Change status (new/researching/outreach/pitched/won/lost)
- `add note to [company]: [text]` - Add a research note
- `log [type] for [company]` - Log outreach (email/call/meeting/linkedin)
- `add prospect [name]` - Add a new company to the database

### Export
- `export prospects` - Export to CSV

### CLI Usage
```bash
cd ~/ai-context/tools/prospect-finder/db
python3 query.py hot
python3 query.py segment healthcare
python3 query.py search bcbs
python3 query.py show "Point32Health"
python3 query.py status "Point32Health" outreach
python3 query.py export
```

## Website Opportunity Scanner

Scan prospect websites to detect opportunities:

### Scan Commands (via Claude)
- `scan [url]` - Scan a single URL
- `scan company [name]` - Scan a company in the database
- `scan top 10` - Scan top 10 prospects by fit score
- `scan segment healthcare` - Scan all in a segment
- `show scan results` - Show recent scans
- `show opportunities` - Show high-opportunity prospects

### What It Detects
- **CMS**: WordPress, Drupal, AEM, Sitecore, Webflow, etc.
- **Tech Stack**: React, Vue, Angular, jQuery, Bootstrap, etc.
- **Hosting**: AWS, Pantheon, Acquia, WPEngine, Vercel, etc.
- **Performance**: Lighthouse scores, Core Web Vitals
- **Accessibility**: WCAG compliance issues
- **SEO**: Meta tags, structured data, sitemap, etc.
- **Privacy**: Cookie consent, privacy policy
- **Signals**: Hiring web roles, outdated libraries, rebrand signs

### Output
```
Acme Corp — 87/100 opportunity
CMS: Drupal 9
Hosting: Pantheon

Signals:
  🟠 Poor Performance (score: 45)
  🟠 Accessibility Issues (score: 62)
  🟡 Outdated jQuery 1.x

Summary: Drupal site with poor mobile performance
Suggested pitch: Drupal modernization + accessibility remediation
```

### CLI Usage
```bash
cd ~/ai-context/tools/prospect-finder/scanner
python3 scan_cli.py https://example.com
python3 scan_cli.py company "Brown University"
python3 scan_cli.py top 10
python3 scan_cli.py results
python3 scan_cli.py opportunities
```

## Web Dashboard

View prospects and scan results in your browser:

```bash
cd ~/ai-context/tools/prospect-finder/web
python3 server.py
```

Then open: **http://localhost:5555**

Features:
- Filter by segment, status, or search
- Sort by fit score, opportunity, or name
- Click any company for full details
- View scan signals and suggested pitches

## Refreshing Results

Results are point-in-time. To refresh:
```
refresh prospects
```
This will re-run web searches for recent funding, RFPs, leadership changes, and rebrands.
