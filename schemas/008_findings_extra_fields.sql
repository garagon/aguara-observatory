-- Add extra fields from Aguara scan output to findings_latest
-- These were previously discarded during ingestion

ALTER TABLE findings_latest ADD COLUMN rule_name TEXT;
ALTER TABLE findings_latest ADD COLUMN description TEXT;
ALTER TABLE findings_latest ADD COLUMN analyzer TEXT;
ALTER TABLE findings_latest ADD COLUMN confidence INTEGER;
ALTER TABLE findings_latest ADD COLUMN context TEXT;
