"""Tests for the precomputed CSV data files.

These tests verify that the pipeline CSVs have the correct structure
and can be parsed by the frontend. Only tax year 2026 is meaningful
for the enacted NJ CTC increase dashboard.
"""

import csv
from pathlib import Path

import pytest


DATA_DIR = Path(__file__).parent.parent / "frontend" / "public" / "data"
EXPECTED_YEARS = [2026]
EXPECTED_BRACKETS = {
    "$0 - $25k",
    "$25k - $50k",
    "$50k - $75k",
    "$75k - $100k",
    "$100k - $150k",
    "$150k - $200k",
    "$200k+",
}


def _load_csv(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        pytest.skip(f"{filename} not generated yet")
    with open(path, "r") as f:
        return list(csv.DictReader(f))


class TestDistributionalImpactCSV:
    """Tests for distributional_impact.csv."""

    def test_has_required_columns(self):
        data = _load_csv("distributional_impact.csv")
        required = ["year", "decile", "average_change", "relative_change"]
        for row in data:
            for col in required:
                assert col in row, f"Missing column: {col}"

    def test_has_all_deciles(self):
        data = _load_csv("distributional_impact.csv")
        for year in EXPECTED_YEARS:
            year_data = [r for r in data if int(r["year"]) == year]
            deciles = {r["decile"] for r in year_data}
            expected = {str(d) for d in range(1, 11)}
            assert deciles == expected, f"Missing deciles for year {year}"

    def test_values_are_numeric(self):
        data = _load_csv("distributional_impact.csv")
        for row in data:
            float(row["year"])
            float(row["average_change"])
            float(row["relative_change"])


class TestMetricsCSV:
    """Tests for metrics.csv."""

    def test_has_required_columns(self):
        data = _load_csv("metrics.csv")
        required = ["year", "metric", "value"]
        for row in data:
            for col in required:
                assert col in row, f"Missing column: {col}"

    def test_has_required_metrics(self):
        data = _load_csv("metrics.csv")
        required_metrics = [
            "budgetary_impact",
            "state_tax_revenue_impact",
            "federal_tax_revenue_impact",
            "winners",
            "losers",
            "poverty_baseline_rate",
            "poverty_reform_rate",
        ]
        for year in EXPECTED_YEARS:
            year_data = [r for r in data if int(r["year"]) == year]
            metrics = {r["metric"] for r in year_data}
            for metric in required_metrics:
                assert metric in metrics, (
                    f"Missing metric '{metric}' for year {year}"
                )


class TestWinnersLosersCSV:
    """Tests for winners_losers.csv."""

    def test_has_required_columns(self):
        data = _load_csv("winners_losers.csv")
        required = [
            "year", "decile",
            "gain_more_5pct", "gain_less_5pct", "no_change",
            "lose_less_5pct", "lose_more_5pct",
        ]
        for row in data:
            for col in required:
                assert col in row, f"Missing column: {col}"

    def test_has_all_deciles_and_all(self):
        data = _load_csv("winners_losers.csv")
        for year in EXPECTED_YEARS:
            year_data = [r for r in data if int(r["year"]) == year]
            deciles = {r["decile"] for r in year_data}
            expected = {"All"} | {str(d) for d in range(1, 11)}
            assert deciles == expected, f"Missing deciles for year {year}"

    def test_values_sum_to_one(self):
        data = _load_csv("winners_losers.csv")
        for row in data:
            total = (
                float(row["gain_more_5pct"])
                + float(row["gain_less_5pct"])
                + float(row["no_change"])
                + float(row["lose_less_5pct"])
                + float(row["lose_more_5pct"])
            )
            assert abs(total - 1.0) < 0.01, f"Row does not sum to 1: {row}"


class TestIncomeBracketsCSV:
    """Tests for income_brackets.csv."""

    def test_has_required_columns(self):
        data = _load_csv("income_brackets.csv")
        required = ["year", "bracket", "beneficiaries", "total_cost", "avg_benefit"]
        for row in data:
            for col in required:
                assert col in row, f"Missing column: {col}"

    def test_has_all_brackets(self):
        data = _load_csv("income_brackets.csv")
        for year in EXPECTED_YEARS:
            year_data = [r for r in data if int(r["year"]) == year]
            brackets = {r["bracket"] for r in year_data}
            assert brackets == EXPECTED_BRACKETS, (
                f"Missing brackets for year {year}"
            )


class TestCongressionalDistrictsCSV:
    """Tests for congressional_districts.csv (NJ only)."""

    def test_has_required_columns(self):
        data = _load_csv("congressional_districts.csv")
        required = [
            "district",
            "average_household_income_change",
            "relative_household_income_change",
            "state",
            "year",
        ]
        for row in data:
            for col in required:
                assert col in row, f"Missing column: {col}"

    def test_new_jersey_only(self):
        """All rows must be NJ districts."""
        data = _load_csv("congressional_districts.csv")
        states = {r["state"] for r in data}
        assert states == {"NJ"}, f"Expected only NJ rows, got {states}"

    def test_twelve_districts(self):
        """New Jersey has 12 congressional districts."""
        data = _load_csv("congressional_districts.csv")
        districts = {r["district"] for r in data}
        expected = {f"NJ-{d:02d}" for d in range(1, 13)}
        assert districts == expected, (
            f"Expected NJ-01..NJ-12, got {districts}"
        )
