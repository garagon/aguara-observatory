-- Prevent duplicate findings in findings_latest
-- Same skill + rule + matched_text should only appear once

CREATE UNIQUE INDEX IF NOT EXISTS idx_findings_latest_dedup
    ON findings_latest(skill_id, rule_id, severity, COALESCE(matched_text, ''));
