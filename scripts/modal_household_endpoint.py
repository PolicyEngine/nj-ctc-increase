"""Modal-hosted household calculator backend for the enacted NJ CTC
increase dashboard.

Mirrors the CPID spawn-and-poll pattern: the browser POSTs a job to
``/household/start``, gets back a ``job_id``, then GETs
``/household/status/{job_id}`` until ``status`` flips from
``computing`` to ``ok`` / ``error``. The two-simulation income sweep
(prior-law counterfactual vs current law) runs as a spawned Modal
function so each HTTP request stays under the per-request wall-clock
limit.

Pinned to the same policyengine-us as the data pipelines, so the
household calculator never depends on what api.policyengine.org has
deployed.

Deploy with::

    modal deploy scripts/modal_household_endpoint.py

The persistent URL Modal prints is what to put in
``NEXT_PUBLIC_MODAL_NJ_URL`` (frontend ``.env.local`` and the Vercel
project's environment variables).

Test locally with::

    modal serve scripts/modal_household_endpoint.py
"""

from __future__ import annotations

from pathlib import Path

import modal

app = modal.App("nj-ctc-household")

_REPO_ROOT = Path(__file__).resolve().parent.parent

# Matches scripts/modal_pipeline.py (first release containing PR #8971).
POLICYENGINE_US_PIN = "policyengine-us==1.768.2"

# Cache-bust marker — bump when the compute code or pins change, so old
# cached results never leak across builds.
BUILD_REV = "2026-07-09-pe-us-1.768.2"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        POLICYENGINE_US_PIN,
        "numpy>=1.24.0",
        "fastapi",
    )
    # NJ_CTC_REPO_ROOT points nj_credit_calc.reforms at the mounted
    # counterfactual JSON (the package itself mounts under /root, away
    # from the repository root).
    .env({"NJ_CTC_BUILD_REV": BUILD_REV, "NJ_CTC_REPO_ROOT": "/reforms"})
    .add_local_file(
        _REPO_ROOT / "reform_prior_law.json", "/reforms/reform_prior_law.json"
    )
    .add_local_python_source("nj_credit_calc")
)

# Results cache: identical (payload, build) pairs return the stored
# result instead of re-simulating, so common profiles are instant.
results_cache = modal.Dict.from_name(
    "nj-ctc-household-cache", create_if_missing=True
)


def _cache_key(payload: dict) -> str:
    import hashlib
    import json

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(f"{BUILD_REV}|{canonical}".encode()).hexdigest()
    return f"household:{BUILD_REV}:{digest[:32]}"


def _cache_get(key: str):
    try:
        return results_cache[key]
    except KeyError:
        return None
    except Exception:  # cache is best-effort, never a failure source
        return None


def _cache_put(key: str, value: dict) -> None:
    try:
        results_cache[key] = value
    except Exception:
        pass


@app.function(image=image, timeout=600, memory=4096)
def compute_household_sweep(payload: dict) -> dict:
    """Run the prior-law vs enacted-law household sweep on Modal."""
    from nj_credit_calc.household import calculate_household_impact

    result = calculate_household_impact(
        age_head=int(payload["age_head"]),
        age_spouse=(
            int(payload["age_spouse"])
            if payload.get("age_spouse") is not None
            else None
        ),
        dependent_ages=[int(a) for a in payload.get("dependent_ages", [])],
        income=float(payload["income"]),
        year=int(payload.get("year", 2026)),
        max_earnings=float(payload.get("max_earnings", 100_000)),
        state_code=payload.get("state_code", "NJ"),
    )
    _cache_put(_cache_key(payload), result)
    return result


_ALLOW_ORIGINS = [
    "http://localhost:3008",
    "https://policyengine.org",
    "https://www.policyengine.org",
]
_ALLOW_ORIGIN_REGEX = r"https://.*\.vercel\.app"


@app.function(image=image, timeout=300, memory=512)
@modal.asgi_app()
def web():
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware

    api = FastAPI()
    api.add_middleware(
        CORSMiddleware,
        allow_origins=_ALLOW_ORIGINS,
        allow_origin_regex=_ALLOW_ORIGIN_REGEX,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @api.post("/household/start")
    def household_start(payload: dict) -> dict:
        key = _cache_key(payload)
        if _cache_get(key) is not None:
            return {"job_id": f"cache:{key}"}
        call = compute_household_sweep.spawn(payload)
        return {"job_id": call.object_id}

    @api.get("/household/status/{job_id}")
    def household_status(job_id: str) -> dict:
        # Cache-backed pseudo-jobs: the start endpoint found a stored
        # result for this exact (payload, build) pair.
        if job_id.startswith("cache:"):
            cached = _cache_get(job_id[len("cache:"):])
            if cached is not None:
                return {"status": "ok", "result": cached, "cached": True}
            return {
                "status": "error",
                "message": "Cached result expired; retry.",
            }
        try:
            call = modal.FunctionCall.from_id(job_id)
            result = call.get(timeout=0)
            return {"status": "ok", "result": result}
        except modal.exception.OutputExpiredError:
            raise HTTPException(status_code=410, detail="Result expired.")
        except TimeoutError:
            return {"status": "computing"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

    @api.get("/healthz")
    def healthz() -> dict:
        from importlib.metadata import version

        return {
            "status": "ok",
            "build_rev": BUILD_REV,
            "policyengine_us": version("policyengine-us"),
        }

    return api
