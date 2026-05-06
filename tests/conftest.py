"""
Pytest configuration and shared fixtures for the New Jersey 2026 tax changes.
"""

import pytest


@pytest.fixture
def sample_household_params():
    """Sample New Jersey single-parent household for testing."""
    return {
        "age_head": 30,
        "age_spouse": None,
        "dependent_ages": [2],
        "income": 35000,
        "year": 2026,
        "max_earnings": 500000,
        "state_code": "NJ",
    }


@pytest.fixture
def married_household_params():
    """Sample New Jersey married-with-children household for testing."""
    return {
        "age_head": 32,
        "age_spouse": 30,
        "dependent_ages": [1, 3],
        "income": 60000,
        "year": 2026,
        "max_earnings": 500000,
        "state_code": "NJ",
    }
