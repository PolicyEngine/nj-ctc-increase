"""Tests for the nj_credit_calc.reforms module.

These tests verify that the three forward-reform JSONs (CTC only, EITC
only, combined) load correctly and resolve to PolicyEngine reform
classes.
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


class TestReformPaths:
    """Tests for the reform JSON path constants."""

    def test_default_variant(self):
        assert DEFAULT_VARIANT == "combined"

    def test_reform_paths_cover_three_variants(self):
        assert set(REFORM_PATHS) == {"ctc", "eitc", "combined"}

    def test_reform_path_default_alias(self):
        assert REFORM_PATH == REFORM_PATHS[DEFAULT_VARIANT]

    @pytest.mark.parametrize("variant", ["ctc", "eitc", "combined"])
    def test_reform_json_exists_and_parses(self, variant):
        path = REFORM_PATHS[variant]
        assert isinstance(path, Path)
        assert path.name == f"reform_{variant}.json"
        assert path.exists(), f"Expected {path} to exist"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)


class TestLoadReform:
    """Tests for load_reform()."""

    @pytest.mark.parametrize("variant", ["ctc", "eitc", "combined"])
    def test_load_returns_dict(self, variant):
        reform = load_reform(variant)
        assert isinstance(reform, dict)
        assert "_comment" not in reform

    def test_unknown_variant_raises(self):
        with pytest.raises(ValueError):
            load_reform("unknown")

    def test_combined_includes_ctc_and_eitc_paths(self):
        reform = load_reform("combined")
        keys = set(reform)
        assert any("credits.ctc" in k for k in keys), (
            "combined reform should touch ctc parameters"
        )
        assert any("credits.eitc" in k for k in keys), (
            "combined reform should touch eitc parameters"
        )

    def test_paths_target_new_jersey(self):
        for variant in ("ctc", "eitc", "combined"):
            reform = load_reform(variant)
            for path in reform:
                assert path.startswith("gov.states.nj."), (
                    f"Non-NJ parameter {path!r} in {variant} reform"
                )
