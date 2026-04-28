"""Modal-based congressional-district pipeline for the NJ Cash Alliance
CTC + EITC expansion dashboard.

Calculates per-district impacts for New Jersey's 12 congressional
districts (NJ-01..NJ-12; state FIPS 34) for one or more reform variants
and writes one CSV per variant to ``frontend/public/data/``.

Usage:
    modal run scripts/modal_district_pipeline.py                        # all 3 variants
    modal run scripts/modal_district_pipeline.py --variant ctc          # one
    modal run scripts/modal_district_pipeline.py --variants eitc,combined
"""

import json
import os
from pathlib import Path

import modal


app = modal.App("nj-ctc-eitc-expansion-district-pipeline")

_REPO_ROOT = Path(__file__).resolve().parent.parent

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install(
        "policyengine-us>=1.665.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "huggingface_hub",
    )
    .add_local_file(_REPO_ROOT / "reform_ctc.json", "/reforms/reform_ctc.json")
    .add_local_file(_REPO_ROOT / "reform_eitc.json", "/reforms/reform_eitc.json")
    .add_local_file(_REPO_ROOT / "reform_combined.json", "/reforms/reform_combined.json")
)

YEAR = 2026
NJ_STATE = "NJ"
NJ_STATE_FIPS = 34
NJ_DISTRICTS = list(range(1, 13))  # NJ has 12 congressional districts.

VARIANTS = ("ctc", "eitc", "combined")


def _load_reform(variant: str) -> dict:
    """Load a reform JSON; tries the in-image /reforms/ path first."""
    in_image = Path(f"/reforms/reform_{variant}.json")
    if in_image.exists():
        path = in_image
    else:
        path = Path(__file__).resolve().parent.parent / f"reform_{variant}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_comment", None)
    return data


def _build_reform_from_overrides(overrides: dict):
    """Build a Reform that supports ``brackets[N]`` index syntax in paths."""
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


def get_nj_districts() -> list[str]:
    return [f"{NJ_STATE}-{d:02d}" for d in NJ_DISTRICTS]


@app.function(
    image=image,
    memory=16384,
    timeout=1800,
    retries=2,
)
def calculate_district(district_id: str, variant: str) -> dict:
    """Run a single (district, variant) sim and return its impact row."""
    import numpy as np
    from policyengine_us import Microsimulation
    from policyengine_core.reforms import Reform

    print(f"Calculating {district_id} variant={variant}...")
    dataset_url = f"hf://policyengine/policyengine-us-data/districts/{district_id}.h5"
    reform = _build_reform_from_overrides(_load_reform(variant))

    try:
        sim_baseline = Microsimulation(dataset=dataset_url)
        sim_reform = Microsimulation(dataset=dataset_url, reform=reform)

        household_weight = np.array(
            sim_baseline.calculate("household_weight", period=YEAR)
        )
        baseline_net = np.array(
            sim_baseline.calculate("household_net_income", period=YEAR)
        )
        reform_net = np.array(
            sim_reform.calculate("household_net_income", period=YEAR)
        )
        income_change = reform_net - baseline_net  # positive => household gain

        total_weight = household_weight.sum()
        if total_weight > 0:
            avg_change = (income_change * household_weight).sum() / total_weight
            avg_baseline = (baseline_net * household_weight).sum() / total_weight
            rel_change = avg_change / avg_baseline if avg_baseline > 0 else 0.0
            winners_share = (
                (household_weight * (income_change > 1)).sum() / total_weight
            )
            losers_share = (
                (household_weight * (income_change < -1)).sum() / total_weight
            )
        else:
            avg_change = rel_change = winners_share = losers_share = 0.0

        try:
            spm_unit_weight = np.array(
                sim_baseline.calculate("spm_unit_weight", period=YEAR)
            )
            total_spm_weight = spm_unit_weight.sum()
            if total_spm_weight > 0:
                pov_bl = np.array(
                    sim_baseline.calculate(
                        "spm_unit_is_in_spm_poverty", period=YEAR
                    )
                )
                pov_rf = np.array(
                    sim_reform.calculate(
                        "spm_unit_is_in_spm_poverty", period=YEAR
                    )
                )
                bl_rate = (pov_bl * spm_unit_weight).sum() / total_spm_weight
                rf_rate = (pov_rf * spm_unit_weight).sum() / total_spm_weight
                poverty_pct_change = (
                    (rf_rate - bl_rate) / bl_rate * 100 if bl_rate > 0 else 0.0
                )
                children = np.array(
                    sim_baseline.calculate(
                        "spm_unit_count_children", period=YEAR
                    )
                )
                child_w = spm_unit_weight * children
                total_child_w = child_w.sum()
                if total_child_w > 0:
                    bl_child = (pov_bl * child_w).sum() / total_child_w
                    rf_child = (pov_rf * child_w).sum() / total_child_w
                    child_poverty_pct_change = (
                        (rf_child - bl_child) / bl_child * 100
                        if bl_child > 0
                        else 0.0
                    )
                else:
                    child_poverty_pct_change = 0.0
            else:
                poverty_pct_change = child_poverty_pct_change = 0.0
        except Exception as poverty_err:
            print(f"  Poverty calc failed for {district_id}: {poverty_err}")
            poverty_pct_change = child_poverty_pct_change = 0.0

        result = {
            "district": district_id,
            "average_household_income_change": round(float(avg_change), 2),
            "relative_household_income_change": round(float(rel_change), 6),
            "winners_share": round(float(winners_share), 4),
            "losers_share": round(float(losers_share), 4),
            "poverty_pct_change": round(float(poverty_pct_change), 2),
            "child_poverty_pct_change": round(float(child_poverty_pct_change), 2),
            "state": NJ_STATE,
            "year": YEAR,
            "variant": variant,
        }
        print(
            f"  {district_id} {variant}: avg=${avg_change:.2f}  "
            f"winners={winners_share:.1%}  poverty={poverty_pct_change:+.1f}%"
        )
        return result
    except Exception as e:
        print(f"  ERROR {district_id} {variant}: {e}")
        return None


@app.local_entrypoint()
def main(variant: str = "", variants: str = ""):
    import pandas as pd

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "frontend",
        "public",
        "data",
    )
    os.makedirs(output_dir, exist_ok=True)

    if variants:
        target = [v.strip() for v in variants.split(",") if v.strip()]
    elif variant:
        target = [variant]
    else:
        target = list(VARIANTS)

    bad = [v for v in target if v not in VARIANTS]
    if bad:
        raise ValueError(f"Unknown variant(s): {bad}. Choose from {VARIANTS}.")

    districts = get_nj_districts()
    print(f"Running NJ districts {districts} variants={target} on Modal (year {YEAR})...")

    pairs = [(d, v) for v in target for d in districts]
    results = list(calculate_district.starmap(pairs))
    rows = [r for r in results if r is not None]
    failed = len(results) - len(rows)
    if failed:
        print(f"WARNING: {failed} (district, variant) combinations failed")

    if not rows:
        print("ERROR: no rows produced")
        return

    df = pd.DataFrame(rows)
    for v in target:
        sub = df[df["variant"] == v].drop(columns=["variant"])
        sub = sub.sort_values(["state", "district"]).reset_index(drop=True)
        path = os.path.join(output_dir, f"congressional_districts_{v}.csv")
        sub.to_csv(path, index=False)
        print(f"Saved: {path}")
