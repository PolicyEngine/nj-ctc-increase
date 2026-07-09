"""Build the NJ slice of the Populace national file on a Modal Volume.

The statewide pipeline only needs New Jersey's households, but the
national Populace file makes every request simulate all ~57k households.
Slicing once per dataset revision into a small NJ file collapses the
runtime while keeping exactly Populace's numbers — verified by asserting
the slice's weighted household count and baseline NJ CTC total equal the
national NJ-masked values, and that no tax/spm/family/marital unit
straddles the state boundary.

Adapted from child-poverty-impact-dashboard's
``scripts/build_populace_state_slices.py`` (NJ-only).

Run once per POPULACE_REVISION bump:
    modal run scripts/build_populace_nj_slice.py

Writes to the ``nj-ctc-populace-slices`` Volume under
/{REVISION[:8]}/NJ.h5, which scripts/modal_pipeline.py mounts read-only.
"""

import modal

app = modal.App("nj-ctc-populace-slice-builder")

# Matches scripts/modal_pipeline.py (first release containing PR #8971).
POLICYENGINE_US_PIN = "policyengine-us==1.768.2"

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    POLICYENGINE_US_PIN,
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "huggingface_hub",
)

# Same pins as scripts/modal_pipeline.py.
POPULACE_REPO = "policyengine/populace-us"
POPULACE_FILE = "populace_us_2024.h5"
POPULACE_REVISION = "053baf6cf56aaf1160e2f1bfe7631c6924d46b2e"  # 2026-07-01

NJ_FIPS = 34
YEAR = 2026

volume = modal.Volume.from_name("nj-ctc-populace-slices", create_if_missing=True)

GROUP_ENTITIES = ("tax_unit", "spm_unit", "family", "marital_unit")


@app.function(image=image, timeout=3600, memory=16384, volumes={"/slices": volume})
def build_nj_slice() -> dict:
    import os

    from huggingface_hub import hf_hub_download
    from policyengine_us.data import USSingleYearDataset

    path = hf_hub_download(
        POPULACE_REPO, POPULACE_FILE, repo_type="dataset", revision=POPULACE_REVISION
    )
    ds = USSingleYearDataset(file_path=path)
    if hasattr(ds, "load"):
        ds.load()
    hh_all = ds.household
    person_all = ds.person

    keep_hh = hh_all[hh_all["state_fips"] == NJ_FIPS]
    hh_ids = set(keep_hh["household_id"])
    person = person_all[person_all["person_household_id"].isin(hh_ids)]
    frames = {"household": keep_hh, "person": person}
    for g in GROUP_ENTITIES:
        ids = set(person[f"person_{g}_id"].unique())
        gdf = getattr(ds, g)
        frames[g] = gdf[gdf[f"{g}_id"].isin(ids)]
        # No group may straddle the state boundary: every member of every
        # kept group must be a kept person, or group sums silently shrink.
        members = person_all[person_all[f"person_{g}_id"].isin(ids)]
        if len(members) != len(person):
            raise ValueError(
                f"NJ: {g} straddles the state boundary "
                f"({len(members)} members vs {len(person)} persons)"
            )

    out_dir = f"/slices/{POPULACE_REVISION[:8]}"
    os.makedirs(out_dir, exist_ok=True)
    sliced = USSingleYearDataset(
        time_period=2024,
        **{k: v.reset_index(drop=True) for k, v in frames.items()},
    )
    out = f"{out_dir}/NJ.h5"
    sliced.save(out)
    volume.commit()
    report = {
        "households": len(keep_hh),
        "persons": len(person),
        "weighted_households": float(keep_hh["household_weight"].sum()),
        "mb": round(os.path.getsize(out) / 1e6, 1),
    }
    print(f"NJ: {report['households']} hh / {report['persons']} persons "
          f"({report['weighted_households']:,.0f} weighted) -> {report['mb']}MB",
          flush=True)
    return report


@app.function(image=image, timeout=3600, memory=32768, cpu=4.0)
def national_nj_metrics() -> dict:
    """Baseline metrics on the FULL national file, masked to NJ."""
    import numpy as np
    from huggingface_hub import hf_hub_download
    from policyengine_us import Microsimulation

    path = hf_hub_download(
        POPULACE_REPO, POPULACE_FILE, repo_type="dataset", revision=POPULACE_REVISION
    )
    sim = Microsimulation(dataset=path)
    hh_states = np.array(sim.calculate("state_code", period=YEAR)).astype(str)
    hw = np.array(sim.calculate("household_weight", period=YEAR))
    ctc = np.array(sim.calculate("nj_ctc", period=YEAR, map_to="household"))
    mask = hh_states == "NJ"
    return {
        "weighted_households": float(hw[mask].sum()),
        "nj_ctc_total": float((ctc[mask] * hw[mask]).sum()),
    }


@app.function(image=image, timeout=1800, memory=8192, volumes={"/slices": volume})
def slice_nj_metrics() -> dict:
    """The same baseline metrics on the NJ slice."""
    import numpy as np
    from policyengine_us import Microsimulation
    from policyengine_us.data import USSingleYearDataset

    sim = Microsimulation(
        dataset=USSingleYearDataset(
            file_path=f"/slices/{POPULACE_REVISION[:8]}/NJ.h5"
        )
    )
    hw = np.array(sim.calculate("household_weight", period=YEAR))
    ctc = np.array(sim.calculate("nj_ctc", period=YEAR, map_to="household"))
    return {
        "weighted_households": float(hw.sum()),
        "nj_ctc_total": float((ctc * hw).sum()),
    }


@app.local_entrypoint()
def main():
    report = build_nj_slice.remote()
    print(f"built NJ slice: {report}")
    national = national_nj_metrics.remote()
    sliced = slice_nj_metrics.remote()
    print(f"national NJ-masked: {national}")
    print(f"slice:              {sliced}")
    for key in national:
        a, b = national[key], sliced[key]
        rel = abs(a - b) / max(abs(a), abs(b), 1e-9)
        if rel > 1e-6:
            raise SystemExit(
                f"MISMATCH {key}: national={a} slice={b} rel={rel:.2e}"
            )
    print("NJ SLICE MATCHES NATIONAL")
