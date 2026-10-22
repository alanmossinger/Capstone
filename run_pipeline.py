"""Execute the project notebooks in order, top to bottom, in place.

What: runs the story notebooks ``notebooks/01_*.ipynb`` … ``12_*.ipynb`` in
dependency order (PLAN.md §14) with ``jupyter nbconvert --execute --inplace``
on the ``queue-survival`` kernel and stops at the first notebook that fails.
Why: one command rebuilds every interim table, result and figure from the
raw files (PLAN.md §4), and each notebook's saved outputs always match the
code that produced them.
Reads / writes: whatever the notebooks read and write.
Used by: ``make all`` and the per-step ``make`` targets.

Usage::

    python run_pipeline.py              # every notebook of the pipeline that exists
    python run_pipeline.py --only 01    # just notebook 01
    python run_pipeline.py --only 04 07 # several
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

NOTEBOOKS = Path(__file__).resolve().parent / "notebooks"
# The notebooks are numbered by the story (PLAN.md §14) and run in dependency order: 06, the evaluation
# record, runs last because it reads every scored table (decision #63); 05, 08 and 10 join as they are built.
PIPELINE = ["01", "02", "03", "04", "05", "07", "08", "09", "06", "10", "11", "12"]  # 11, the decision system of v8, reads 07–09 (decision #91); 12, the three questions of v10, reads 11
KERNEL = "queue-survival"  # registered from .venv by `make setup`


def run(prefixes):
    """Execute the notebooks whose names start with the given prefixes, in order."""
    for prefix in prefixes:
        found = sorted(NOTEBOOKS.glob(f"{prefix}_*.ipynb"))
        if not found:
            print(f"[skip] no notebook {prefix}_*.ipynb yet")
            continue
        for notebook in found:
            start = time.time()
            print(f"[run ] {notebook.name}", flush=True)
            result = subprocess.run(
                [sys.executable, "-m", "nbconvert", "--to", "notebook",
                 "--execute", "--inplace", f"--ExecutePreprocessor.kernel_name={KERNEL}",
                 "--ExecutePreprocessor.timeout=3600",
                 "--ExecutePreprocessor.record_timing=False",  # no timestamps, so reruns diff cleanly
                 str(notebook)])
            if result.returncode != 0:
                sys.exit(f"[fail] {notebook.name} — stopping the pipeline")
            print(f"[done] {notebook.name} in {time.time() - start:.0f} s", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the project notebooks in order.")
    parser.add_argument("--only", nargs="+", metavar="NN",
                        help="notebook number prefixes to run, e.g. 01 or 05 06")
    run(parser.parse_args().only or PIPELINE)
