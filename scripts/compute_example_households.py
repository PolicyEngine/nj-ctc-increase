"""Pre-compute a handful of representative New Jersey households so the
household tab can show example impacts without hitting the PE API on
page load.

Hits https://api.policyengine.org/us/calculate twice per profile —
once with no policy override (current NJ law), once with the NJ Cash
Alliance combined CTC + EITC expansion applied (reform) — and writes
the diff into ``frontend/public/data/example_households.json``.

Sign convention:

    impact = reform (NJ Cash Alliance package) - baseline (current NJ law)

so positive numbers mean the household gains under the proposal.

The example profiles all have qualifying children, since the NJ CTC
and EITC expansions only matter for families with kids:

  - Single parent, $30k, 1 child age 4: in the EITC peak and the
    top NJ CTC bracket ($1,000 → $1,500). Big proportional gain.
  - Married couple, $50k, 2 kids ages 7 and 10: kids currently age out
    of the NJ CTC (under 6 only); the reform expands eligibility to
    under 12 so both kids become eligible at $750 each in this bracket.
  - Married couple, $80k, 2 kids ages 4 and 8: the older kid is newly
    eligible under the age expansion, and the household sits at the top
    of the NJ CTC income range ($60-80k bracket).

Usage:
    uv run --with requests scripts/compute_example_households.py
"""

import json
from pathlib import Path

import requests

PE_API = "https://api.policyengine.org/us/calculate"
YEAR = 2026
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "frontend" / "public" / "data" / "example_households.json"

PROFILES = [
    {
        "label": "Single parent, $30k, 1 young child",
        "income": 30_000,
        "age_head": 30,
        "married": False,
        "dependents": [4],
    },
    {
        "label": "Married couple, $50k, 2 school-age kids",
        "income": 50_000,
        "age_head": 36,
        "married": True,
        "dependents": [7, 10],
    },
    {
        "label": "Married couple, $80k, 2 kids",
        "income": 80_000,
        "age_head": 42,
        "married": True,
        "dependents": [4, 8],
    },
]


def reform_policy() -> dict:
    """NJ Cash Alliance combined CTC + EITC expansion. Mirrors the
    REFORM_POLICY in frontend/lib/household.ts."""
    period = "2026-01-01.2100-12-31"
    return {
        "gov.states.nj.tax.income.credits.ctc.amount[0].amount": {period: 1500},
        "gov.states.nj.tax.income.credits.ctc.amount[1].amount": {period: 1000},
        "gov.states.nj.tax.income.credits.ctc.amount[2].amount": {period: 750},
        "gov.states.nj.tax.income.credits.ctc.amount[3].amount": {period: 500},
        "gov.states.nj.tax.income.credits.ctc.amount[4].amount": {period: 250},
        "gov.states.nj.tax.income.credits.ctc.age_limit": {period: 12},
        "gov.states.nj.tax.income.credits.eitc.match": {period: 0.5},
    }


def build_household(profile: dict, with_axes: bool = False) -> dict:
    """Build a PolicyEngine household situation for the given profile.

    If ``with_axes`` is True, sweeps employment_income from $0 to a
    profile-derived max so we can pre-compute the full net-income chart.
    """
    year = str(YEAR)
    income_for_baseline = None if with_axes else profile["income"]
    people: dict = {
        "you": {
            "age": {year: profile["age_head"]},
            "employment_income": {year: income_for_baseline},
        }
    }
    members = ["you"]
    marital_units: dict = {"your marital unit": {"members": ["you"]}}

    if profile["married"]:
        people["your partner"] = {"age": {year: 35}}
        members.append("your partner")
        marital_units["your marital unit"]["members"].append("your partner")

    for i, age in enumerate(profile["dependents"]):
        cid = (
            "your first dependent"
            if i == 0
            else "your second dependent"
            if i == 1
            else f"dependent_{i + 1}"
        )
        people[cid] = {"age": {year: age}}
        members.append(cid)
        marital_units[f"{cid}'s marital unit"] = {"members": [cid]}

    situation: dict = {
        "people": people,
        "families": {"your family": {"members": members}},
        "marital_units": marital_units,
        "spm_units": {"your household": {"members": members}},
        "tax_units": {
            "your tax unit": {
                "members": members,
                "adjusted_gross_income": {year: None},
                "income_tax": {year: None},
                "nj_income_tax": {year: None},
            }
        },
        "households": {
            "your household": {
                "members": members,
                "state_code": {year: "NJ"},
                "household_net_income": {year: None},
            }
        },
    }

    if with_axes:
        axis_max = max(profile["income"] * 2, 100_000)
        situation["axes"] = [
            [
                {
                    "name": "employment_income",
                    "min": 0,
                    "max": axis_max,
                    "count": 201,
                    "period": year,
                    "target": "person",
                }
            ]
        ]
    return situation


def calc(situation: dict, policy: dict | None) -> dict:
    body: dict = {"household": situation}
    if policy:
        body["policy"] = policy
    response = requests.post(
        PE_API, json=body, headers={"Content-Type": "application/json"}, timeout=180
    )
    if not response.ok:
        raise RuntimeError(f"{response.status_code}: {response.text[:500]}")
    return response.json()["result"]


def extract(result: dict) -> dict:
    yr = str(YEAR)
    hh = result["households"]["your household"]
    tu = result["tax_units"]["your tax unit"]
    return {
        "household_net_income": hh["household_net_income"][yr],
        "nj_income_tax": tu["nj_income_tax"][yr],
        "income_tax": tu["income_tax"][yr],
    }


def compute_profile(profile: dict) -> dict:
    """Run baseline (current NJ law) + reform (NJ Cash Alliance) at the
    user's income point and as an income sweep, so the page can render
    the full net-income chart instantly."""
    yr = str(YEAR)

    # Point estimate.
    point_situation = build_household(profile, with_axes=False)
    baseline_pt = extract(calc(point_situation, None))
    reform_pt = extract(calc(point_situation, reform_policy()))

    # Income sweep for the chart.
    sweep_situation = build_household(profile, with_axes=True)
    base_sweep = calc(sweep_situation, None)
    ref_sweep = calc(sweep_situation, reform_policy())

    income_range = base_sweep["people"]["you"]["employment_income"][yr]
    base_net = base_sweep["households"]["your household"]["household_net_income"][yr]
    ref_net = ref_sweep["households"]["your household"]["household_net_income"][yr]
    base_state = base_sweep["tax_units"]["your tax unit"]["nj_income_tax"][yr]
    ref_state = ref_sweep["tax_units"]["your tax unit"]["nj_income_tax"][yr]
    base_fed = base_sweep["tax_units"]["your tax unit"]["income_tax"][yr]
    ref_fed = ref_sweep["tax_units"]["your tax unit"]["income_tax"][yr]

    net_income_change = [r - b for r, b in zip(ref_net, base_net)]
    state_tax_change = [r - b for r, b in zip(ref_state, base_state)]
    federal_tax_change = [r - b for r, b in zip(ref_fed, base_fed)]

    return {
        **profile,
        "baseline": baseline_pt,
        "reform": reform_pt,
        "net_income_change": reform_pt["household_net_income"]
        - baseline_pt["household_net_income"],
        "nj_tax_change": reform_pt["nj_income_tax"]
        - baseline_pt["nj_income_tax"],
        "chart": {
            "income_range": income_range,
            "net_income_change": net_income_change,
            "state_tax_change": state_tax_change,
            "federal_tax_change": federal_tax_change,
        },
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for profile in PROFILES:
        print(f"  Computing: {profile['label']}...")
        rows.append(compute_profile(profile))

    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump({"year": YEAR, "households": rows}, fh, indent=2)
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
