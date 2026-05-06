"""Reform definitions for the NJ CTC + EITC expansion dashboard.

Three forward-reform variants live as JSON at the repository root:

- ``reform_ctc.json`` — NJ Cash Alliance CTC expansion only.
- ``reform_eitc.json`` — NJ EITC match raised to 50% of federal.
- ``reform_combined.json`` — both expansions applied together.

Each JSON uses bracket-index segments (``credits.ctc.amount[N].amount``)
in its parameter paths, so ``Reform.from_dict`` cannot consume them
directly. Use :func:`create_nj_reform` to build a PolicyEngine reform
class via a manual ``modify_parameters`` walker.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


REPO_ROOT = Path(__file__).resolve().parent.parent

REFORM_PATHS: Dict[str, Path] = {
    "ctc": REPO_ROOT / "reform_ctc.json",
    "eitc": REPO_ROOT / "reform_eitc.json",
    "combined": REPO_ROOT / "reform_combined.json",
}

# Default variant used by helpers that do not take an explicit argument.
DEFAULT_VARIANT = "combined"

# Public alias for backward compatibility with code that imports
# ``REFORM_PATH``.
REFORM_PATH = REFORM_PATHS[DEFAULT_VARIANT]


def load_reform(variant: str = DEFAULT_VARIANT) -> Dict[str, Any]:
    """Load the NJ reform dictionary for the given variant.

    Args:
        variant: One of ``"ctc"``, ``"eitc"``, ``"combined"``.

    Returns:
        A dictionary of parameter overrides.
    """
    if variant not in REFORM_PATHS:
        raise ValueError(
            f"Unknown reform variant {variant!r}; "
            f"expected one of {sorted(REFORM_PATHS)}"
        )
    with open(REFORM_PATHS[variant], "r", encoding="utf-8") as f:
        data = json.load(f)
    data.pop("_comment", None)
    return data


def create_nj_reform(variant: str = DEFAULT_VARIANT):
    """Build a PolicyEngine Reform for the requested NJ variant."""
    import re

    from policyengine_core.periods import instant
    from policyengine_core.reforms import Reform

    overrides = load_reform(variant)

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
                    start=instant(start_str),
                    stop=instant(stop_str),
                    value=value,
                )
        return parameters

    class NJReform(Reform):
        def apply(self):
            self.modify_parameters(modify)

    return NJReform
