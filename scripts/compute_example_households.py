"""Pre-compute a handful of representative New Jersey households so the
household tab can show example impacts without hitting any API on page
load.

Computes locally with the pinned policyengine-us (which contains the
enacted 25% NJ CTC increase from S-4531 / P.L.2026, c.26) via
``nj_credit_calc.calculate_household_impact``: baseline applies the
prior-law counterfactual, reform is plain current law, and the diff is
written to ``frontend/public/data/example_households.json``.

Sign convention:

    impact = current law (enacted increase) - prior law (counterfactual)

so positive numbers mean the household gains from the enacted increase.

The example profiles all have children age 5 or younger, since only
under-6 children qualify for the NJ CTC (eligibility is unchanged):

  - Single parent, $25k, 1 child age 4: top NJ CTC bracket
    ($1,000 → $1,250 per child).
  - Married couple, $48k, 2 kids ages 2 and 5: middle bracket
    ($600 → $750 per child, +$300 total).
  - Married couple, $75k, 1 child age 3: top of the NJ CTC income
    range ($200 → $250).

Usage:
    uv run scripts/compute_example_households.py
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from nj_credit_calc.household import calculate_household_impact  # noqa: E402

YEAR = 2026
OUTPUT_PATH = REPO_ROOT / "frontend" / "public" / "data" / "example_households.json"

PROFILES = [
    {
        "label": "Single parent, $25k, 1 young child",
        "income": 25_000,
        "age_head": 30,
        "married": False,
        "dependents": [4],
    },
    {
        "label": "Married couple, $48k, 2 young kids",
        "income": 48_000,
        "age_head": 36,
        "married": True,
        "dependents": [2, 5],
    },
    {
        "label": "Married couple, $75k, 1 young child",
        "income": 75_000,
        "age_head": 42,
        "married": True,
        "dependents": [3],
    },
]


def compute_profile(profile: dict) -> dict:
    """Run the prior-law vs enacted-law sweep for one profile and shape
    the result the way frontend/components/ExampleHouseholds.tsx expects."""
    result = calculate_household_impact(
        age_head=profile["age_head"],
        age_spouse=35 if profile["married"] else None,
        dependent_ages=profile["dependents"],
        income=profile["income"],
        year=YEAR,
        max_earnings=max(profile["income"] * 2, 100_000),
    )
    baseline = result["point"]["baseline"]
    reform = result["point"]["reform"]
    return {
        **profile,
        "baseline": baseline,
        "reform": reform,
        "net_income_change": reform["household_net_income"]
        - baseline["household_net_income"],
        "nj_tax_change": reform["nj_income_tax"] - baseline["nj_income_tax"],
        "chart": {
            "income_range": result["income_range"],
            "net_income_change": result["net_income_change"],
            "state_tax_change": result["nj_income_tax_change"],
            "federal_tax_change": result["income_tax_change"],
        },
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for profile in PROFILES:
        print(f"  Computing: {profile['label']}...", flush=True)
        row = compute_profile(profile)
        print(
            f"    net income change at ${profile['income']:,}: "
            f"${row['net_income_change']:+,.0f}",
            flush=True,
        )
        rows.append(row)

    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump({"year": YEAR, "households": rows}, fh, indent=2)
    print(f"Saved: {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
