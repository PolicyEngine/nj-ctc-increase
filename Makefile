.PHONY: install dev build test test-python test-frontend lint clean
.PHONY: pipeline pipeline-districts households deploy-household-endpoint

# Install dependencies (frontend is npm-canonical: package-lock.json)
install:
	cd frontend && npm ci
	uv sync --extra dev

# Start the frontend dev server (hybrid-precomputed pattern: no local backend)
dev:
	cd frontend && npm run dev

build:
	cd frontend && npm run build

test: test-python test-frontend

test-python:
	uv run pytest

test-frontend:
	cd frontend && npm run test

lint:
	cd frontend && npm run lint

clean:
	rm -rf frontend/.next frontend/node_modules

# Regenerate statewide CSVs (frontend/public/data/) on Modal
pipeline:
	uv run modal run scripts/modal_pipeline.py

# Regenerate congressional_districts.csv on Modal
pipeline-districts:
	uv run modal run scripts/modal_district_pipeline.py

# Recompute frontend/public/data/example_households.json locally with the
# pinned policyengine-us
households:
	uv run python scripts/compute_example_households.py

# Redeploy the household calculator backend (bump BUILD_REV in the script
# whenever the pin or nj_credit_calc changes)
deploy-household-endpoint:
	uv run modal deploy scripts/modal_household_endpoint.py
