"""Tests for the nj_credit_calc.reforms module.

These tests verify that the prior-law counterfactual JSON (the
comparison baseline for the enacted 25% NJ CTC increase) loads
correctly and resolves to a PolicyEngine reform class.
"""

import json
from pathlib import Path

import pytest
from nj_credit_calc.reforms import (
    DEFAULT_VARIANT,
    REFORM_PATH,
    REFORM_PATHS,
    load_reform,
)


PRIOR_LAW_AMOUNTS = [1000, 800, 600, 400, 200]
PRIOR_LAW_PERIOD = "2026-01-01.2028-12-31"


class TestReformPaths:
    """Tests for the reform JSON path constants."""

    def test_default_variant(self):
        assert DEFAULT_VARIANT == "prior_law"

    def test_reform_paths_cover_prior_law(self):
        assert set(REFORM_PATHS) == {"prior_law"}

    def test_reform_path_default_alias(self):
        assert REFORM_PATH == REFORM_PATHS[DEFAULT_VARIANT]

    def test_reform_json_exists_and_parses(self):
        path = REFORM_PATHS["prior_law"]
        assert isinstance(path, Path)
        assert path.name == "reform_prior_law.json"
        assert path.exists(), f"Expected {path} to exist"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)


class TestLoadReform:
    """Tests for load_reform()."""

    def test_load_returns_dict(self):
        reform = load_reform("prior_law")
        assert isinstance(reform, dict)
        assert "_comment" not in reform

    def test_unknown_variant_raises(self):
        with pytest.raises(ValueError):
            load_reform("unknown")

    def test_paths_target_new_jersey_ctc(self):
        reform = load_reform("prior_law")
        for path in reform:
            assert path.startswith("gov.states.nj.tax.income.credits.ctc"), (
                f"Non-NJ-CTC parameter {path!r} in prior_law reform"
            )

    def test_restores_prior_amounts_for_2026_2028_only(self):
        """The counterfactual must restore the five pre-increase bracket
        amounts over exactly the enacted window (2029+ reverts on its
        own under current law)."""
        reform = load_reform("prior_law")
        assert len(reform) == len(PRIOR_LAW_AMOUNTS)
        for i, amount in enumerate(PRIOR_LAW_AMOUNTS):
            path = (
                "gov.states.nj.tax.income.credits.ctc.amount"
                f".brackets[{i}].amount"
            )
            assert reform[path] == {PRIOR_LAW_PERIOD: amount}
