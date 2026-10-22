"""Every story notebook declares the project kernel, so a hand run in Jupyter or VS Code uses the pinned .venv."""

import json

from run_pipeline import KERNEL, NOTEBOOKS, PIPELINE


def test_every_notebook_declares_the_project_kernel():
    notebooks = sorted(NOTEBOOKS.glob("[0-9][0-9]_*.ipynb"))
    assert {n.name[:2] for n in notebooks} == set(PIPELINE)
    wrong = {n.name: json.loads(n.read_text(encoding="utf-8"))["metadata"].get("kernelspec", {}).get("name") for n in notebooks}
    assert {name: k for name, k in wrong.items() if k != KERNEL} == {}
