# NJ Child Tax Credit increase dashboard

Models New Jersey's enacted 25% Child Tax Credit increase for tax
years 2026-2028 (S-4531 / P.L.2026, c.26, part of the FY2027 budget)
on households, statewide revenue, and the state's twelve congressional
districts. Formerly the `nj-ctc-eitc-expansion` dashboard, which
modeled the pre-enactment NJ Cash Alliance proposal.

Because policyengine-us current law (post
[PR #8971](https://github.com/PolicyEngine/policyengine-us/pull/8971))
already includes the enacted increase, all comparisons run against the
`reform_prior_law.json` counterfactual: **baseline = current law with
pre-increase amounts restored for 2026-2028; reform = plain current
law**. Impact = reform − baseline.

- **Frontend**: `frontend/` (Next.js / Tailwind)
- **Modal pipelines**:
  - `scripts/build_populace_nj_slice.py` — one-time NJ slice of the
    pinned Populace dataset (run per revision bump)
  - `scripts/modal_pipeline.py` — statewide impacts on the Populace NJ
    slice
  - `scripts/modal_district_pipeline.py` — per-district impacts on the
    legacy district-calibrated files
    (`policyengine-us-data/districts/NJ-XX.h5`)
- **Pre-computed CSVs**: `frontend/public/data/*.csv`

## Dataset note

Statewide figures use the Populace NJ slice (~1,650 households);
district figures use the legacy per-district calibrated files (~9,000
households each), because Populace carries only ~130 raw households
per NJ district. District figures therefore do not exactly aggregate
to statewide figures.

## Refreshing data

1. Wait for a policyengine-us release containing PR #8971, then pin it
   in `pyproject.toml` and the two Modal pipeline images
   (`POLICYENGINE_US_PIN`).
2. `modal run scripts/build_populace_nj_slice.py`
3. `modal run scripts/modal_pipeline.py`
4. `modal run scripts/modal_district_pipeline.py`
5. Once api.policyengine.org deploys that release:
   `uv run --with requests scripts/compute_example_households.py`

Both pipelines fail loudly if the pinned release does not contain the
enacted increase (baseline CTC totals would equal current-law totals).

Live: <https://nj-ctc-increase.vercel.app/us/nj-ctc-increase>
