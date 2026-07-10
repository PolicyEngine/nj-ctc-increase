"""Modal-based state-level data generation pipeline for the enacted
NJ CTC increase dashboard (S-4531 / P.L.2026, c.26).

Current law in policyengine-us (post PR #8971) already contains the
enacted 25% bracket increase for 2026-2028, so the comparison runs
backwards from the usual pattern:

- baseline sim: current law + ``reform_prior_law.json`` (bracket
  amounts restored to their pre-increase values for 2026-2028), and
- reform sim: plain current law (the enacted increase).

Runs against the ECPS state file (``states/NJ.h5``) — the same dataset
family as the district pipeline. ECPS matches NJ Treasury's
administrative CTC actuals almost exactly ($220.5M vs $220.7M outlay;
242k vs 232.5k claims) and its ~110k-household sample resolves the
poverty impact of this modest credit change. Writes CSVs to
``frontend/public/data/``.

Usage:
    modal run scripts/modal_pipeline.py
"""

import json
import os
from pathlib import Path

import modal


app = modal.App("nj-ctc-enacted-pipeline")

_REPO_ROOT = Path(__file__).resolve().parent.parent

# 1.768.2 is the first policyengine-us release that contains PR #8971
# (the enacted NJ CTC increase). An older release's "current law" would
# not include the increase and every impact would be zero.
POLICYENGINE_US_PIN = "policyengine-us==1.768.2"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        POLICYENGINE_US_PIN,
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "huggingface_hub",
    )
    # Ship the counterfactual JSON into the worker image so the worker
    # can load it at runtime (Modal otherwise only sees the script dir).
    .add_local_file(
        _REPO_ROOT / "reform_prior_law.json", "/reforms/reform_prior_law.json"
    )
)

YEAR = 2026

# ECPS state file — same dataset family as the district pipeline's
# districts/NJ-XX.h5 files.
NJ_DATASET = "hf://policyengine/policyengine-us-data/states/NJ.h5"


def _load_prior_law() -> dict:
    """Load the prior-law counterfactual from the image (or repo root,
    so this also works when invoked directly outside Modal)."""
    in_image = Path("/reforms/reform_prior_law.json")
    if in_image.exists():
        path = in_image
    else:
        path = _REPO_ROOT / "reform_prior_law.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_comment", None)
    return data


def _build_reform_from_overrides(overrides: dict):
    """Build a Reform that supports ``brackets[N]`` index syntax in paths.

    PolicyEngine's stock ``Reform.from_dict`` cannot navigate parameter
    paths with array-index segments, so we walk the parameter tree
    manually for any ``name[N]`` segment.
    """
    import re
    from policyengine_core.reforms import Reform
    from policyengine_core.periods import instant

    def modify(parameters):
        for path, periods in overrides.items():
            node = parameters
            for segment in path.split("."):
                match = re.match(r"(\w+)\[(\d+)\]", segment)
                if match:
                    node = getattr(node, match.group(1))[int(match.group(2))]
                else:
                    node = getattr(node, segment)
            for period_str, value in periods.items():
                if "." in period_str and len(period_str) > 10:
                    start_str, stop_str = period_str.split(".")
                else:
                    start_str = (
                        period_str if "-" in period_str else f"{period_str}-01-01"
                    )
                    stop_str = "2100-12-31"
                node.update(
                    start=instant(start_str), stop=instant(stop_str), value=value
                )
        return parameters

    class _JsonReform(Reform):
        def apply(self):
            self.modify_parameters(modify)

    return _JsonReform


@app.function(
    image=image,
    memory=16384,
    timeout=1800,
    retries=1,
)
def calculate_impacts() -> dict:
    """Run the NJ state-level microsim (prior law vs enacted law) and
    return distributional / fiscal / poverty / bracket breakdowns."""
    import numpy as np
    from policyengine_us import Microsimulation

    print(f"Starting NJ enacted-CTC calculation for {YEAR}...")

    intra_bounds = [-np.inf, -0.05, -1e-3, 1e-3, 0.05, np.inf]
    intra_labels = [
        "Lose more than 5%",
        "Lose less than 5%",
        "No change",
        "Gain less than 5%",
        "Gain more than 5%",
    ]

    prior_law = _build_reform_from_overrides(_load_prior_law())

    print("  Loading baseline (prior law) sim on ECPS NJ dataset...")
    sim_baseline = Microsimulation(dataset=NJ_DATASET, reform=prior_law)
    print("  Loading reform (enacted current law) sim on ECPS NJ dataset...")
    sim_reform = Microsimulation(dataset=NJ_DATASET)

    # Sanity: the enacted increase must actually be present in the
    # pinned policyengine-us release, or every impact is silently zero.
    ctc_baseline = float(sim_baseline.calculate("nj_ctc", period=YEAR).sum())
    ctc_reform = float(sim_reform.calculate("nj_ctc", period=YEAR).sum())
    if ctc_reform <= ctc_baseline:
        raise RuntimeError(
            f"Enacted NJ CTC increase not present: baseline nj_ctc "
            f"${ctc_baseline:,.0f} vs current law ${ctc_reform:,.0f}. "
            "Is the pinned policyengine-us release missing PR #8971?"
        )
    print(
        f"  nj_ctc outlay: prior law ${ctc_baseline/1e6:.1f}M -> "
        f"enacted ${ctc_reform/1e6:.1f}M "
        f"(ratio {ctc_reform/ctc_baseline:.4f}, expected 1.25)"
    )

    # ===== FISCAL IMPACT =====
    nj_baseline = sim_baseline.calculate("nj_income_tax", period=YEAR, map_to="household")
    nj_reform = sim_reform.calculate("nj_income_tax", period=YEAR, map_to="household")
    state_tax_revenue_impact = float((nj_reform - nj_baseline).sum())

    fed_baseline = sim_baseline.calculate("income_tax", period=YEAR, map_to="household")
    fed_reform = sim_reform.calculate("income_tax", period=YEAR, map_to="household")
    federal_tax_revenue_impact = float((fed_reform - fed_baseline).sum())

    tax_revenue_impact = federal_tax_revenue_impact + state_tax_revenue_impact
    budgetary_impact = tax_revenue_impact

    baseline_net_income = sim_baseline.calculate(
        "household_net_income", period=YEAR, map_to="household"
    )
    reform_net_income = sim_reform.calculate(
        "household_net_income", period=YEAR, map_to="household"
    )
    income_change = reform_net_income - baseline_net_income
    change_arr = np.array(income_change)
    baseline_net_income_arr = np.array(baseline_net_income)
    household_weight = sim_reform.calculate("household_weight", period=YEAR)
    weight_arr = np.array(household_weight)

    total_households = float(weight_arr.sum())
    winners = float(weight_arr[change_arr > 1].sum())
    losers = float(weight_arr[change_arr < -1].sum())
    beneficiary_mask = change_arr > 0
    beneficiaries = float(weight_arr[beneficiary_mask].sum())
    avg_benefit = (
        float(
            (change_arr[beneficiary_mask] * weight_arr[beneficiary_mask]).sum()
            / beneficiaries
        )
        if beneficiaries > 0
        else 0.0
    )
    winners_rate = winners / total_households * 100 if total_households else 0.0
    losers_rate = losers / total_households * 100 if total_households else 0.0

    # Resident-based winners/losers: a resident counts as a winner when
    # their household's net income rises (matches the person-weighted
    # intra-decile chart).
    person_change = np.array(
        sim_reform.calculate("household_net_income", period=YEAR, map_to="person")
    ) - np.array(
        sim_baseline.calculate("household_net_income", period=YEAR, map_to="person")
    )
    person_weight = np.array(
        sim_baseline.calculate("person_weight", period=YEAR)
    )
    total_residents = float(person_weight.sum())
    winners_residents = float(person_weight[person_change > 1].sum())
    losers_residents = float(person_weight[person_change < -1].sum())
    winners_rate_residents = (
        winners_residents / total_residents * 100 if total_residents else 0.0
    )
    losers_rate_residents = (
        losers_residents / total_residents * 100 if total_residents else 0.0
    )

    # ===== INCOME DECILE =====
    decile = sim_baseline.calculate(
        "household_income_decile", period=YEAR, map_to="household"
    )
    decile_average = {}
    decile_relative = {}
    for d in range(1, 11):
        dmask = decile == d
        d_weight = weight_arr[dmask]
        d_count = float(d_weight.sum())
        if d_count > 0:
            d_baseline_sum = float(
                (baseline_net_income_arr[dmask] * d_weight).sum()
            )
            d_change_sum = float((change_arr[dmask] * d_weight).sum())
            decile_average[str(d)] = d_change_sum / d_count
            decile_relative[str(d)] = (
                d_change_sum / d_baseline_sum if d_baseline_sum != 0 else 0.0
            )
        else:
            decile_average[str(d)] = 0.0
            decile_relative[str(d)] = 0.0

    people_per_hh = sim_baseline.calculate(
        "household_count_people", period=YEAR, map_to="household"
    )
    capped_baseline = np.maximum(baseline_net_income_arr, 1)
    rel_change_arr = change_arr / capped_baseline

    decile_arr = np.array(decile)
    people_weighted = np.array(people_per_hh) * weight_arr

    intra_decile_deciles = {label: [] for label in intra_labels}
    for d in range(1, 11):
        dmask = decile_arr == d
        d_people = people_weighted[dmask]
        d_total_people = d_people.sum()
        d_rel = rel_change_arr[dmask]
        for lower, upper, label in zip(
            intra_bounds[:-1], intra_bounds[1:], intra_labels
        ):
            in_group = (d_rel > lower) & (d_rel <= upper)
            proportion = (
                float(d_people[in_group].sum() / d_total_people)
                if d_total_people > 0
                else 0.0
            )
            intra_decile_deciles[label].append(proportion)
    intra_decile_all = {
        label: sum(intra_decile_deciles[label]) / 10 for label in intra_labels
    }

    # ===== POVERTY =====
    pov_bl = sim_baseline.calculate("in_poverty", period=YEAR, map_to="person")
    pov_rf = sim_reform.calculate("in_poverty", period=YEAR, map_to="person")
    poverty_baseline_rate = float(pov_bl.mean() * 100)
    poverty_reform_rate = float(pov_rf.mean() * 100)
    poverty_rate_change = poverty_reform_rate - poverty_baseline_rate
    poverty_percent_change = (
        poverty_rate_change / poverty_baseline_rate * 100
        if poverty_baseline_rate > 0
        else 0.0
    )

    age_arr = np.array(sim_baseline.calculate("age", period=YEAR))
    is_child = age_arr < 18
    pw_arr = np.array(sim_baseline.calculate("person_weight", period=YEAR))
    child_w = pw_arr[is_child]
    total_child_w = child_w.sum()

    pov_bl_arr = np.array(pov_bl).astype(bool)
    pov_rf_arr = np.array(pov_rf).astype(bool)

    def _child_rate(arr):
        return (
            float((arr[is_child] * child_w).sum() / total_child_w * 100)
            if total_child_w > 0
            else 0.0
        )

    child_poverty_baseline_rate = _child_rate(pov_bl_arr)
    child_poverty_reform_rate = _child_rate(pov_rf_arr)
    child_poverty_rate_change = (
        child_poverty_reform_rate - child_poverty_baseline_rate
    )
    child_poverty_percent_change = (
        child_poverty_rate_change / child_poverty_baseline_rate * 100
        if child_poverty_baseline_rate > 0
        else 0.0
    )

    deep_bl = sim_baseline.calculate("in_deep_poverty", period=YEAR, map_to="person")
    deep_rf = sim_reform.calculate("in_deep_poverty", period=YEAR, map_to="person")
    deep_poverty_baseline_rate = float(deep_bl.mean() * 100)
    deep_poverty_reform_rate = float(deep_rf.mean() * 100)
    deep_poverty_rate_change = deep_poverty_reform_rate - deep_poverty_baseline_rate
    deep_poverty_percent_change = (
        deep_poverty_rate_change / deep_poverty_baseline_rate * 100
        if deep_poverty_baseline_rate > 0
        else 0.0
    )

    deep_bl_arr = np.array(deep_bl).astype(bool)
    deep_rf_arr = np.array(deep_rf).astype(bool)
    deep_child_poverty_baseline_rate = _child_rate(deep_bl_arr)
    deep_child_poverty_reform_rate = _child_rate(deep_rf_arr)
    deep_child_poverty_rate_change = (
        deep_child_poverty_reform_rate - deep_child_poverty_baseline_rate
    )
    deep_child_poverty_percent_change = (
        deep_child_poverty_rate_change / deep_child_poverty_baseline_rate * 100
        if deep_child_poverty_baseline_rate > 0
        else 0.0
    )

    # ===== INCOME BRACKETS =====
    # Tax-unit level, bucketed by NJ taxable income — the credit's own
    # eligibility measure — using the statute's tiers, so all impact
    # lands at or below the $80k ceiling by construction. (Bucketing
    # households by AGI instead smears benefits into higher brackets:
    # multi-tax-unit households, and AGI > NJ taxable income.)
    nj_taxable = np.array(
        sim_baseline.calculate("nj_taxable_income", period=YEAR)
    )
    tu_weight = np.array(sim_baseline.calculate("tax_unit_weight", period=YEAR))
    ctc_change_tu = np.array(
        sim_reform.calculate("nj_ctc", period=YEAR)
    ) - np.array(sim_baseline.calculate("nj_ctc", period=YEAR))
    gainer_mask = ctc_change_tu > 0

    # Statute tiers: "$X or under" / "over X but not over Y" (S-4531).
    income_brackets = [
        (-float("inf"), 30_000, "$30k or less"),
        (30_000, 40_000, "$30k - $40k"),
        (40_000, 50_000, "$40k - $50k"),
        (50_000, 60_000, "$50k - $60k"),
        (60_000, 80_000, "$60k - $80k"),
        (80_000, float("inf"), "Over $80k"),
    ]
    by_income_bracket = []
    for min_inc, max_inc, label in income_brackets:
        mask = (nj_taxable > min_inc) & (nj_taxable <= max_inc) & gainer_mask
        bracket_beneficiaries = float(tu_weight[mask].sum())
        if bracket_beneficiaries > 0:
            bracket_cost = float((ctc_change_tu[mask] * tu_weight[mask]).sum())
            bracket_avg = float(
                np.average(ctc_change_tu[mask], weights=tu_weight[mask])
            )
        else:
            bracket_cost = 0.0
            bracket_avg = 0.0
        by_income_bracket.append({
            "bracket": label,
            "beneficiaries": bracket_beneficiaries,
            "total_cost": bracket_cost,
            "avg_benefit": bracket_avg,
        })

    print("  Done.")
    return {
        "year": YEAR,
        "budget": {
            "budgetary_impact": budgetary_impact,
            "federal_tax_revenue_impact": federal_tax_revenue_impact,
            "state_tax_revenue_impact": state_tax_revenue_impact,
            "tax_revenue_impact": tax_revenue_impact,
            "households": total_households,
        },
        "decile": {"average": decile_average, "relative": decile_relative},
        "intra_decile": {"all": intra_decile_all, "deciles": intra_decile_deciles},
        "total_cost": -budgetary_impact,
        "beneficiaries": beneficiaries,
        "avg_benefit": avg_benefit,
        "winners": winners,
        "losers": losers,
        "winners_rate": winners_rate,
        "losers_rate": losers_rate,
        "residents": total_residents,
        "winners_residents": winners_residents,
        "losers_residents": losers_residents,
        "winners_rate_residents": winners_rate_residents,
        "losers_rate_residents": losers_rate_residents,
        "poverty_baseline_rate": poverty_baseline_rate,
        "poverty_reform_rate": poverty_reform_rate,
        "poverty_rate_change": poverty_rate_change,
        "poverty_percent_change": poverty_percent_change,
        "child_poverty_baseline_rate": child_poverty_baseline_rate,
        "child_poverty_reform_rate": child_poverty_reform_rate,
        "child_poverty_rate_change": child_poverty_rate_change,
        "child_poverty_percent_change": child_poverty_percent_change,
        "deep_poverty_baseline_rate": deep_poverty_baseline_rate,
        "deep_poverty_reform_rate": deep_poverty_reform_rate,
        "deep_poverty_rate_change": deep_poverty_rate_change,
        "deep_poverty_percent_change": deep_poverty_percent_change,
        "deep_child_poverty_baseline_rate": deep_child_poverty_baseline_rate,
        "deep_child_poverty_reform_rate": deep_child_poverty_reform_rate,
        "deep_child_poverty_rate_change": deep_child_poverty_rate_change,
        "deep_child_poverty_percent_change": deep_child_poverty_percent_change,
        "by_income_bracket": by_income_bracket,
    }


def _save_csvs(result: dict, output_dir: str) -> None:
    """Write the dashboard CSVs for the single enacted-reform result."""
    import pandas as pd

    year = result["year"]

    # Distributional impact (decile)
    distributional_rows = []
    for d, avg in result["decile"]["average"].items():
        distributional_rows.append({
            "year": year,
            "decile": d,
            "average_change": round(avg, 2),
            "relative_change": round(result["decile"]["relative"][d], 6),
        })

    # Metrics (flat)
    metrics_rows = []
    flat = [
        ("budgetary_impact", result["budget"]["budgetary_impact"]),
        ("federal_tax_revenue_impact", result["budget"]["federal_tax_revenue_impact"]),
        ("state_tax_revenue_impact", result["budget"]["state_tax_revenue_impact"]),
        ("tax_revenue_impact", result["budget"]["tax_revenue_impact"]),
        ("households", result["budget"]["households"]),
        ("total_cost", result["total_cost"]),
        ("beneficiaries", result["beneficiaries"]),
        ("avg_benefit", result["avg_benefit"]),
        ("winners", result["winners"]),
        ("losers", result["losers"]),
        ("winners_rate", result["winners_rate"]),
        ("losers_rate", result["losers_rate"]),
        ("residents", result["residents"]),
        ("winners_residents", result["winners_residents"]),
        ("losers_residents", result["losers_residents"]),
        ("winners_rate_residents", result["winners_rate_residents"]),
        ("losers_rate_residents", result["losers_rate_residents"]),
        ("poverty_baseline_rate", result["poverty_baseline_rate"]),
        ("poverty_reform_rate", result["poverty_reform_rate"]),
        ("poverty_rate_change", result["poverty_rate_change"]),
        ("poverty_percent_change", result["poverty_percent_change"]),
        ("child_poverty_baseline_rate", result["child_poverty_baseline_rate"]),
        ("child_poverty_reform_rate", result["child_poverty_reform_rate"]),
        ("child_poverty_rate_change", result["child_poverty_rate_change"]),
        ("child_poverty_percent_change", result["child_poverty_percent_change"]),
        ("deep_poverty_baseline_rate", result["deep_poverty_baseline_rate"]),
        ("deep_poverty_reform_rate", result["deep_poverty_reform_rate"]),
        ("deep_poverty_rate_change", result["deep_poverty_rate_change"]),
        ("deep_poverty_percent_change", result["deep_poverty_percent_change"]),
        ("deep_child_poverty_baseline_rate", result["deep_child_poverty_baseline_rate"]),
        ("deep_child_poverty_reform_rate", result["deep_child_poverty_reform_rate"]),
        ("deep_child_poverty_rate_change", result["deep_child_poverty_rate_change"]),
        ("deep_child_poverty_percent_change", result["deep_child_poverty_percent_change"]),
    ]
    for metric, value in flat:
        metrics_rows.append({"year": year, "metric": metric, "value": value})

    # Winners / losers
    intra = result["intra_decile"]
    winners_losers_rows = [{
        "year": year,
        "decile": "All",
        "gain_more_5pct": intra["all"]["Gain more than 5%"],
        "gain_less_5pct": intra["all"]["Gain less than 5%"],
        "no_change": intra["all"]["No change"],
        "lose_less_5pct": intra["all"]["Lose less than 5%"],
        "lose_more_5pct": intra["all"]["Lose more than 5%"],
    }]
    for i in range(10):
        winners_losers_rows.append({
            "year": year,
            "decile": str(i + 1),
            "gain_more_5pct": intra["deciles"]["Gain more than 5%"][i],
            "gain_less_5pct": intra["deciles"]["Gain less than 5%"][i],
            "no_change": intra["deciles"]["No change"][i],
            "lose_less_5pct": intra["deciles"]["Lose less than 5%"][i],
            "lose_more_5pct": intra["deciles"]["Lose more than 5%"][i],
        })

    # Income brackets
    income_bracket_rows = []
    for b in result["by_income_bracket"]:
        income_bracket_rows.append({
            "year": year,
            "bracket": b["bracket"],
            "beneficiaries": b["beneficiaries"],
            "total_cost": b["total_cost"],
            "avg_benefit": b["avg_benefit"],
        })

    outputs = {
        "distributional_impact.csv": distributional_rows,
        "metrics.csv": metrics_rows,
        "winners_losers.csv": winners_losers_rows,
        "income_brackets.csv": income_bracket_rows,
    }
    for filename, rows in outputs.items():
        path = os.path.join(output_dir, filename)
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"Saved: {path}")


@app.local_entrypoint()
def main():
    """Run the NJ state-level microsim on Modal for the enacted reform."""
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "frontend",
        "public",
        "data",
    )
    os.makedirs(output_dir, exist_ok=True)

    print(f"Running NJ enacted-CTC pipeline on Modal (year {YEAR})...")
    print(f"Dataset: {NJ_DATASET}")
    print(f"Output: {output_dir}")

    result = calculate_impacts.remote()
    _save_csvs(result, output_dir)

    print("\nDone.")
