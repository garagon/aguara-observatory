-- Performance indexes for Aguara Observatory

-- Skills lookups
CREATE INDEX IF NOT EXISTS idx_skills_registry ON skills(registry_id);
CREATE INDEX IF NOT EXISTS idx_skills_hash ON skills(content_hash);
CREATE INDEX IF NOT EXISTS idx_skills_last_seen ON skills(last_seen);
CREATE INDEX IF NOT EXISTS idx_skills_deleted ON skills(deleted);
CREATE INDEX IF NOT EXISTS idx_skills_last_scanned ON skills(last_scanned);

-- Findings queries
CREATE INDEX IF NOT EXISTS idx_findings_scan ON findings(scan_id);
CREATE INDEX IF NOT EXISTS idx_findings_skill ON findings(skill_id);
CREATE INDEX IF NOT EXISTS idx_findings_severity ON findings(severity);
CREATE INDEX IF NOT EXISTS idx_findings_category ON findings(category);
CREATE INDEX IF NOT EXISTS idx_findings_rule ON findings(rule_id);

-- Latest findings (dashboard queries)
CREATE INDEX IF NOT EXISTS idx_findings_latest_skill ON findings_latest(skill_id);
CREATE INDEX IF NOT EXISTS idx_findings_latest_severity ON findings_latest(severity);
CREATE INDEX IF NOT EXISTS idx_findings_latest_category ON findings_latest(category);

-- Scores
CREATE INDEX IF NOT EXISTS idx_skill_scores_grade ON skill_scores(grade);
CREATE INDEX IF NOT EXISTS idx_skill_scores_score ON skill_scores(score);

-- Vendor audits
CREATE INDEX IF NOT EXISTS idx_vendor_audits_skill ON vendor_audits(skill_id);
CREATE INDEX IF NOT EXISTS idx_vendor_audits_vendor ON vendor_audits(vendor);

-- Daily stats (trend charts)
CREATE INDEX IF NOT EXISTS idx_daily_stats_date ON daily_stats(date);
CREATE INDEX IF NOT EXISTS idx_daily_stats_registry ON daily_stats(registry_id);

-- Scans
CREATE INDEX IF NOT EXISTS idx_scans_registry ON scans(registry_id);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);
