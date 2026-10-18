"""A what-if reaches the numbers only through validated parameters; prices move the way the parameters say; statuses follow the stated rule."""

import numpy as np
import pandas as pd
import pytest

from src import whatif as wi


def test_unknown_parameters_and_out_of_range_values_are_refused():
    with pytest.raises(wi.WhatIfError, match="no parameter"):
        wi.WhatIf.from_dict({"interest_rate": 0.05})
    with pytest.raises(wi.WhatIfError, match="outside the range"):
        wi.WhatIf.from_dict({"wti_level": 500.0})
    with pytest.raises(wi.WhatIfError, match="no candidate"):
        wi.WhatIf.from_dict({"forced_in": ["LEASE|NOPE"]}, ids=["LEASE|G1"])
    w = wi.WhatIf.from_dict({"wti_level": 45.0, "wti_years": 5, "budget_multiplier": 0.8})
    assert w.changes() == {"wti_level": 45.0, "budget_multiplier": 0.8}


def test_prices_move_as_the_parameters_say():
    rng = np.random.default_rng(0)
    prices = np.exp(rng.normal(0, 0.3, size=(200, 240, 3))) * np.array([70.0, 2.5, 30.0])
    out = wi.apply_prices(prices, wi.WhatIf(wti_level=45.0, wti_years=5, hh_multiplier=1.5, ercot_volatility=0.5))
    assert np.all(out[:, :60, 0] == 45.0) and np.allclose(out[:, 60:, 0], prices[:, 60:, 0])
    assert np.allclose(out[:, :, 1], prices[:, :, 1] * 1.5)
    spread_before = np.log(prices[:, :, 2]).std(axis=0).mean()
    spread_after = np.log(out[:, :, 2]).std(axis=0).mean()
    assert abs(spread_after / spread_before - 0.5) < 1e-9  # half the spread around the same median
    assert np.allclose(np.median(np.log(out[:, :, 2]), axis=0), np.median(np.log(prices[:, :, 2]), axis=0))
    assert np.array_equal(wi.apply_prices(prices, wi.WhatIf()), prices)  # the base case changes nothing


def test_status_rule():
    row = {"in_book": True, "sector": "ERCOT power", "agreement_known": False, "expected_npv_$M": 5.0}
    assert wi.status_of(row) == "invest in stages"
    assert wi.status_of({**row, "agreement_known": True}) == "invest now"
    assert wi.status_of({**row, "in_book": False}) == "monitor"
    assert wi.status_of({**row, "in_book": False, "expected_npv_$M": -1.0}) == "reject"
