-- Prevent duplicate findings in findings_latest
-- First remove existing duplicates, keeping the one with the highest id

DELETE FROM findings_latest
WHERE id NOT IN (
    SELECT MAX(id) FROM findings_latest
    GROUP BY skill_id, rule_id, severity, COALESCE(matched_text, '')
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_findings_latest_dedup
    ON findings_latest(skill_id, rule_id, severity, COALESCE(matched_text, ''));
