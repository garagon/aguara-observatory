-- Aguara Observatory Schema v1
-- Turso/SQLite

-- Known registries
CREATE TABLE IF NOT EXISTS registries (
    id          TEXT PRIMARY KEY,   -- skills-sh, clawhub, mcp-registry, mcp-so, lobehub
    name        TEXT NOT NULL,
    url         TEXT NOT NULL,
    description TEXT,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

INSERT OR IGNORE INTO registries (id, name, url, description) VALUES
    ('skills-sh',    'Skills.sh',    'https://skills.sh',       'Community AI agent skills marketplace'),
    ('clawhub',      'ClawHub',      'https://clawhub.ai',      'ClawHub AI agent skills registry'),
    ('mcp-registry', 'PulseMCP',     'https://www.pulsemcp.com','PulseMCP MCP server directory'),
    ('mcp-so',       'mcp.so',       'https://mcp.so',          'MCP server discovery platform'),
    ('lobehub',      'LobeHub',      'https://lobehub.com',     'LobeHub plugin marketplace');

-- Discovered skills/servers
CREATE TABLE IF NOT EXISTS skills (
    id            TEXT PRIMARY KEY,  -- {registry}:{slug}
    registry_id   TEXT NOT NULL REFERENCES registries(id),
    slug          TEXT NOT NULL,     -- unique within registry
    name          TEXT,
    url           TEXT,
    content_hash  TEXT,              -- SHA-256 of content, NULL if never downloaded
    content_size  INTEGER DEFAULT 0,
    first_seen    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_seen     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    last_scanned  TEXT,
    deleted       INTEGER DEFAULT 0,
    metadata      TEXT,              -- JSON blob for registry-specific fields
    UNIQUE(registry_id, slug)
);

-- Scan runs
CREATE TABLE IF NOT EXISTS scans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    finished_at     TEXT,
    registry_id     TEXT REFERENCES registries(id),
    skills_scanned  INTEGER DEFAULT 0,
    findings_count  INTEGER DEFAULT 0,
    aguara_version  TEXT,
    status          TEXT DEFAULT 'running',  -- running, completed, failed
    error           TEXT
);

-- Individual findings from scans
CREATE TABLE IF NOT EXISTS findings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_id       INTEGER NOT NULL REFERENCES scans(id),
    skill_id      TEXT NOT NULL REFERENCES skills(id),
    rule_id       TEXT NOT NULL,
    severity      TEXT NOT NULL,       -- CRITICAL, HIGH, MEDIUM, LOW, INFO
    category      TEXT NOT NULL,
    subcategory   TEXT,
    line          INTEGER,
    matched_text  TEXT,
    message       TEXT,
    score_impact  INTEGER DEFAULT 0,   -- points deducted from score
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Latest findings per skill (materialized by aggregator)
CREATE TABLE IF NOT EXISTS findings_latest (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id      TEXT NOT NULL REFERENCES skills(id),
    scan_id       INTEGER NOT NULL REFERENCES scans(id),
    rule_id       TEXT NOT NULL,
    severity      TEXT NOT NULL,
    category      TEXT NOT NULL,
    subcategory   TEXT,
    line          INTEGER,
    matched_text  TEXT,
    message       TEXT,
    score_impact  INTEGER DEFAULT 0,
    updated_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Computed skill scores (A-F grades)
CREATE TABLE IF NOT EXISTS skill_scores (
    skill_id      TEXT PRIMARY KEY REFERENCES skills(id),
    score         INTEGER NOT NULL DEFAULT 100,  -- 0-100
    grade         TEXT NOT NULL DEFAULT 'A',      -- A, B, C, D, F
    finding_count INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    high_count    INTEGER DEFAULT 0,
    medium_count  INTEGER DEFAULT 0,
    low_count     INTEGER DEFAULT 0,
    categories    TEXT,                -- JSON array of categories found
    last_scan_id  INTEGER REFERENCES scans(id),
    updated_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Vendor audit results (ATH, Socket, Snyk)
CREATE TABLE IF NOT EXISTS vendor_audits (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id      TEXT NOT NULL REFERENCES skills(id),
    vendor        TEXT NOT NULL,        -- agent-trust-hub, socket, snyk
    verdict       TEXT,                 -- Pass/Fail (ATH)
    risk_level    TEXT,                 -- Safe/Low/Med/High/Critical
    risk_score    REAL,                 -- 0.0-1.0 (Snyk)
    alert_count   INTEGER DEFAULT 0,
    findings      TEXT,                 -- JSON array of vendor findings
    raw_data      TEXT,                 -- JSON blob of full parsed result
    scraped_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE(skill_id, vendor)
);

-- Daily aggregated stats per registry
CREATE TABLE IF NOT EXISTS daily_stats (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    date              TEXT NOT NULL,       -- YYYY-MM-DD
    registry_id       TEXT NOT NULL REFERENCES registries(id),
    total_skills      INTEGER DEFAULT 0,
    skills_scanned    INTEGER DEFAULT 0,
    total_findings    INTEGER DEFAULT 0,
    critical_count    INTEGER DEFAULT 0,
    high_count        INTEGER DEFAULT 0,
    medium_count      INTEGER DEFAULT 0,
    low_count         INTEGER DEFAULT 0,
    avg_score         REAL DEFAULT 100.0,
    grade_a_count     INTEGER DEFAULT 0,
    grade_b_count     INTEGER DEFAULT 0,
    grade_c_count     INTEGER DEFAULT 0,
    grade_d_count     INTEGER DEFAULT 0,
    grade_f_count     INTEGER DEFAULT 0,
    new_skills        INTEGER DEFAULT 0,
    deleted_skills    INTEGER DEFAULT 0,
    UNIQUE(date, registry_id)
);
