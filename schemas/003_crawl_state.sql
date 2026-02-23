-- Crawl state: watermarks, ETags, timestamps for incremental crawling
-- Primary key: (registry_id, key) — each crawler stores multiple state entries

CREATE TABLE IF NOT EXISTS crawl_state (
    registry_id   TEXT NOT NULL REFERENCES registries(id),
    key           TEXT NOT NULL,          -- e.g. 'last_crawl_at', 'etag:index', 'index_hash'
    value         TEXT NOT NULL,          -- stored as text, caller interprets
    updated_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    PRIMARY KEY (registry_id, key)
);
