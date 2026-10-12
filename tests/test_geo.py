"""Tests for the FIPS parsing behind the project map (notebook 02 (part B))."""

import pandas as pd

from src import geo


def test_first_fips_restores_leading_zero_and_splits_concatenated_codes():
    codes = pd.Series([4005.0, 48001.0, 4800148003.0, 4017480014800348005.0, None, -9223372036854775808.0])
    out = geo.first_fips(codes)
    assert out.tolist()[:4] == ["04005", "48001", "48001", "04017"]
    assert out.isna().tolist()[4:] == [True, True]  # missing and the negative sentinel stay missing


def test_first_fips_applies_the_county_rename_alias():
    assert geo.first_fips(pd.Series([46113.0])).iloc[0] == "46102"
