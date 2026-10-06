"""The fair baseline: Aalen–Johansen incidence per region × technology × size band.

What: the "industry average" of notebook 05 (region × technology) with one
more cut, the FERC size band, and shrinkage to the parent cell when a cell
is thin.
Why: size is the second-strongest driver in notebook 09's explanation and
the v1 baseline ignores it, so part of the measured gain over the baseline
could be a size lookup rather than machine learning. Scoring every v2
criterion against this baseline as well shows what survives a lookup table
that any analyst could build (PLAN.md §8, decision #42).
Reads / writes: nothing.
Used by: notebook 11 (and every later notebook that compares with a
baseline); ``tests/test_baselines.py``.
"""

import pandas as pd

from src import survival_tools

MIN_CELL = 50  # a cell with fewer training requests falls back to its parent, as in notebook 05's baseline


def fair_baseline_cif(train, target, horizons, min_n=MIN_CELL):
    """P(operation by t) from the request's region × technology × size-band cell.

    Parameters
    ----------
    train : pandas.DataFrame
        Training requests with ``region``, ``tech``, ``size_regime``,
        ``duration_years`` and ``event``.
    target : pandas.DataFrame
        Requests to predict for (``region``, ``tech``, ``size_regime``).
    horizons : list of int
        Years at which P(operation by t) is reported.
    min_n : int
        Cells with fewer training requests fall back to region × technology,
        then to region.

    Returns
    -------
    pandas.DataFrame
        Index of ``target``, one column per horizon, plus ``cell`` saying
        which level was used.

    Notes
    -----
    The three levels are nested, so the estimate for a request is the
    finest cell with at least ``min_n`` training requests. With a single
    size band the function reduces to ``survival_tools.baseline_cif``, which
    ``tests/test_baselines.py`` checks. Withdrawal dates enter the operation
    curve's risk sets as recorded, as in notebook 05.
    """
    def curves(groupby, at_least):
        return {key: survival_tools.aalen_johansen(part["duration_years"], part["event"], horizons)["cif_operation"].to_numpy()
                for key, part in train.groupby(groupby) if len(part) >= at_least}

    fine = curves(["region", "tech", "size_regime"], min_n)
    mid = curves(["region", "tech"], min_n)
    coarse = curves("region", 1)  # the region curve always exists, as in notebook 05
    rows, used = [], []
    for region, tech, size in zip(target["region"], target["tech"], target["size_regime"]):
        if (region, tech, size) in fine:
            rows.append(fine[(region, tech, size)])
            used.append("region × technology × size")
        elif (region, tech) in mid:
            rows.append(mid[(region, tech)])
            used.append("region × technology")
        else:
            rows.append(coarse[region])
            used.append("region")
    out = pd.DataFrame(rows, index=target.index, columns=horizons)
    out["cell"] = used
    return out


def cell_table(train, horizons, min_n=MIN_CELL):
    """Every region × technology × size-band cell of the training data with its size and incidence.

    Returns
    -------
    pandas.DataFrame
        One row per cell: ``region``, ``tech``, ``size_regime``, ``n``,
        ``used`` (whether the cell has at least ``min_n`` requests) and
        P(operation by t) per horizon.

    Notes
    -----
    Written to ``results/fair_baseline_cells.csv`` so the report can say
    how many cells carry their own estimate and how many fall back.
    """
    records = []
    for (region, tech, size), part in train.groupby(["region", "tech", "size_regime"], observed=True):
        cif = survival_tools.aalen_johansen(part["duration_years"], part["event"], horizons)["cif_operation"].to_numpy()
        records.append({"region": region, "tech": tech, "size_regime": size, "n": len(part), "used": len(part) >= min_n,
                        **{f"p_operation_{h}": cif[i] for i, h in enumerate(horizons)}})
    return pd.DataFrame(records)
