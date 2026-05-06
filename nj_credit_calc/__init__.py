"""New Jersey CTC + EITC expansion calculation module.

Provides utilities for calculating household and aggregate impacts of
the NJ Cash Alliance proposal — a CTC bracket expansion combined with
raising the state EITC match to 50% of the federal credit. Three
forward-reform variants are supported: ``ctc`` (CTC only), ``eitc``
(EITC only), and ``combined`` (both).
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
