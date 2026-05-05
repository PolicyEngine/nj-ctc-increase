# NJ CTC + EITC Expansion dashboard

Models the NJ Cash Alliance coalition's proposed CTC and EITC
expansions on households, statewide revenue, and the state's twelve
congressional districts.

- **Frontend**: `frontend/` (Next.js / Tailwind)
- **Modal pipelines**: `scripts/modal_pipeline.py` (statewide, 3 variants),
  `scripts/modal_district_pipeline.py` (per-district, 3 variants)
- **Pre-computed CSVs**: `frontend/public/data/*.csv`

Live: <https://nj-ctc-eitc-expansion.vercel.app/us/nj-ctc-eitc-expansion>
