"""Enacted New Jersey CTC increase calculation module.

Provides utilities for calculating household and aggregate impacts of
the enacted 25% NJ Child Tax Credit increase for tax years 2026-2028
(S-4531 / P.L.2026, c.26). Because current law in policyengine-us
already includes the increase, impacts are computed against the
``prior_law`` counterfactual (pre-increase bracket amounts restored
for 2026-2028).
"""

from .household import build_household_situation, calculate_household_impact
from .reforms import (
    DEFAULT_VARIANT,
    REFORM_PATH,
    REFORM_PATHS,
    create_nj_reform,
    load_reform,
)
from .microsimulation import calculate_aggregate_impact

__all__ = [
    "build_household_situation",
    "calculate_household_impact",
    "create_nj_reform",
    "load_reform",
    "REFORM_PATH",
    "REFORM_PATHS",
    "DEFAULT_VARIANT",
    "calculate_aggregate_impact",
]

__version__ = "1.0.0"
