-- Audit overrides: mark findings as FP/TP to adjust score computation
-- Populated by heuristic agents and human reviewers

CREATE TABLE IF NOT EXISTS audit_overrides (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id    TEXT NOT NULL REFERENCES skills(id),
    rule_id     TEXT NOT NULL,
    verdict     TEXT NOT NULL,           -- 'fp', 'tp', 'downgrade'
    reason      TEXT,                    -- human-readable explanation
    auditor     TEXT NOT NULL DEFAULT 'heuristic',  -- 'heuristic', 'human', 'agent'
    confidence  REAL NOT NULL DEFAULT 0.5,          -- 0.0 to 1.0
    matched_text_hash TEXT,             -- SHA-256 of matched_text for dedup
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE(skill_id, rule_id, matched_text_hash)
);

-- Rule-level overrides: blanket FP/TP for a rule across all skills
CREATE TABLE IF NOT EXISTS audit_rule_overrides (
    rule_id     TEXT PRIMARY KEY,
    verdict     TEXT NOT NULL,           -- 'fp', 'tp', 'downgrade'
    reason      TEXT,
    auditor     TEXT NOT NULL DEFAULT 'heuristic',
    confidence  REAL NOT NULL DEFAULT 0.5,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_audit_overrides_skill ON audit_overrides(skill_id);
CREATE INDEX IF NOT EXISTS idx_audit_overrides_rule ON audit_overrides(rule_id);
CREATE INDEX IF NOT EXISTS idx_audit_overrides_verdict ON audit_overrides(verdict);
