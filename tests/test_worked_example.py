"""The worked example's pick is leases only, the highest expected value first, within the budget, in the setting's order."""

import numpy as np

from src import worked_example as we


class FakeSetting:
    """Six candidates: four leases and two requests; the budget holds the two best leases and the fourth, not the third."""

    ids = ["LEASE|a", "REQ|x", "LEASE|b", "LEASE|c", "REQ|y", "LEASE|d"]
    tech = np.array(["Lease redevelopment", "Gas CC", "Lease redevelopment", "Lease redevelopment", "Wind", "Lease redevelopment"])
    A = np.array([[300.0, 900.0, 200.0, 100.0, 900.0, 50.0]] * 3)  # expected value per candidate (requests highest: they must still be left out)
    charge = np.array([40.0, 10.0, 40.0, 30.0, 10.0, 10.0])
    budget = 90.0


def test_pick_takes_the_best_leases_that_fit_and_keeps_the_settings_order():
    assert we.pick(FakeSetting()) == ["LEASE|a", "LEASE|b", "LEASE|d"]  # a and b fill 80; c (30) does not fit; d (10) does


def test_the_answers_pass_the_override_gate():
    from src import advisor as adv
    allowed, missing = adv.override_allowed(we.ANSWERS, opposing_case_read=True)
    assert allowed and not missing
