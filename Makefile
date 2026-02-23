.PHONY: install test lint crawl scan aggregate export clean init-db crawl-incr-all crawl-full-all

# --- Setup ---

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -e ".[dev]"

init-db:
	python -c "from crawlers.db import connect, init_schema; conn = connect(); init_schema(conn); print('DB initialized')"

# --- Testing ---

test:
	pytest tests/ -v

lint:
	ruff check .

# --- Crawling ---

crawl-skills-sh:
	python -m crawlers.skills_sh $(ARGS)

crawl-clawhub:
	python -m crawlers.clawhub $(ARGS)

crawl-mcp-registry:
	python -m crawlers.mcp_registry $(ARGS)

crawl-mcp-so:
	python -m crawlers.mcp_so $(ARGS)

crawl-lobehub:
	python -m crawlers.lobehub $(ARGS)

crawl-vendor-audits:
	python -m crawlers.vendor_audits $(ARGS)

crawl-all: crawl-skills-sh crawl-clawhub crawl-mcp-registry crawl-mcp-so crawl-lobehub

# --- Incremental crawling ---

crawl-incr-skills-sh:
	python -m crawlers.skills_sh --mode incremental $(ARGS)

crawl-incr-clawhub:
	python -m crawlers.clawhub --mode incremental $(ARGS)

crawl-incr-mcp-registry:
	python -m crawlers.mcp_registry --mode incremental $(ARGS)

crawl-incr-mcp-so:
	python -m crawlers.mcp_so --mode incremental $(ARGS)

crawl-incr-lobehub:
	python -m crawlers.lobehub --mode incremental $(ARGS)

crawl-incr-all: crawl-incr-skills-sh crawl-incr-clawhub crawl-incr-mcp-registry crawl-incr-mcp-so crawl-incr-lobehub

# --- Full crawling (explicit) ---

crawl-full-skills-sh:
	python -m crawlers.skills_sh --mode full $(ARGS)

crawl-full-clawhub:
	python -m crawlers.clawhub --mode full $(ARGS)

crawl-full-mcp-registry:
	python -m crawlers.mcp_registry --mode full $(ARGS)

crawl-full-mcp-so:
	python -m crawlers.mcp_so --mode full $(ARGS)

crawl-full-lobehub:
	python -m crawlers.lobehub --mode full $(ARGS)

crawl-full-all: crawl-full-skills-sh crawl-full-clawhub crawl-full-mcp-registry crawl-full-mcp-so crawl-full-lobehub

# --- Scanning ---

scan:
	python -m scanner.run $(SKILLS_DIR) $(ARGS)

ingest:
	python -m scanner.ingest $(RESULTS_FILE) --registry $(REGISTRY) $(ARGS)

# --- Aggregation ---

stats:
	python -m aggregator.stats $(ARGS)

scores:
	python -m aggregator.scores

benchmarks:
	python -m aggregator.benchmarks

export:
	python -m aggregator.export $(ARGS)

aggregate: stats scores export

# --- Web ---

web-install:
	cd web && npm install

web-dev:
	cd web && npm run dev

web-build:
	python scripts/fix_sitemap.py --pre
	cd web && npm run build
	python scripts/fix_sitemap.py

# --- Cleanup ---

clean:
	rm -rf data/ bin/ web/dist/ web/public/api/ web/public/datasets/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
