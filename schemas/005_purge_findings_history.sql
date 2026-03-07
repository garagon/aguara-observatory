-- Purge historical findings table to reclaim storage
-- All active data lives in findings_latest
-- The findings table was accumulating millions of rows per day with no consumer

DROP INDEX IF EXISTS idx_findings_scan;
DROP INDEX IF EXISTS idx_findings_skill;
DROP INDEX IF EXISTS idx_findings_severity;
DROP INDEX IF EXISTS idx_findings_category;
DROP INDEX IF EXISTS idx_findings_rule;
