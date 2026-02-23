-- Crawl run history: one row per crawler execution for observability

CREATE TABLE IF NOT EXISTS crawl_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    registry_id     TEXT NOT NULL REFERENCES registries(id),
    mode            TEXT NOT NULL DEFAULT 'full',   -- full | incremental
    started_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    finished_at     TEXT,
    duration_s      REAL,
    discovered      INTEGER DEFAULT 0,
    downloaded      INTEGER DEFAULT 0,
    skipped         INTEGER DEFAULT 0,
    failed          INTEGER DEFAULT 0,
    changed_files   INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'running',          -- running | completed | failed
    error           TEXT
);

CREATE INDEX IF NOT EXISTS idx_crawl_runs_registry ON crawl_runs(registry_id);
CREATE INDEX IF NOT EXISTS idx_crawl_runs_started ON crawl_runs(started_at);
