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
- **Household calculator backend**: `scripts/modal_household_endpoint.py`
  — spawn-and-poll Modal app (CPID pattern) pinned to the same
  policyengine-us as the pipelines, so the calculator never depends on
  what api.policyengine.org has deployed. Deploy with
  `modal deploy scripts/modal_household_endpoint.py`; the printed URL
  goes in `NEXT_PUBLIC_MODAL_NJ_URL` (frontend `.env.local` and the
  Vercel project env).
- **Modal pipelines**:
  - `scripts/modal_pipeline.py` — statewide impacts on the ECPS state
    file (`policyengine-us-data/states/NJ.h5`, ~110k households)
  - `scripts/modal_district_pipeline.py` — per-district impacts on the
    district-calibrated files
    (`policyengine-us-data/districts/NJ-XX.h5`, ~9k households each)
- **Pre-computed CSVs**: `frontend/public/data/*.csv`

## Dataset note

Both levels run on the enhanced-CPS dataset family. The statewide
file matches NJ Treasury's administrative CTC actuals almost exactly
($220.5M vs $220.7M outlay; 242k vs 232.5k claims) and its
~110k-household sample resolves the poverty impact of this modest
credit change. Note that ECPS overstates baseline poverty *levels*
for NJ, so the dashboard emphasizes poverty *changes*. District files
are calibrated independently, so district figures may not exactly
aggregate to statewide figures.

## Refreshing data

policyengine-us is pinned to 1.768.2 (the first release containing
PR #8971) in `pyproject.toml` and the Modal images
(`POLICYENGINE_US_PIN`). To refresh after a pin bump:

1. `modal run scripts/modal_pipeline.py`
2. `modal run scripts/modal_district_pipeline.py`
3. `uv run scripts/compute_example_households.py` — computes locally
   with the pinned policyengine-us (no API dependency) and writes
   `frontend/public/data/example_households.json`.
4. `modal deploy scripts/modal_household_endpoint.py` — redeploy the
   household backend whenever the pin or `nj_credit_calc` changes
   (bump `BUILD_REV` so cached results don't leak across builds).

Both pipelines fail loudly if the pinned release does not contain the
enacted increase (baseline CTC totals would equal current-law totals).

Live: <https://nj-ctc-increase.vercel.app/us/nj-ctc-increase>
