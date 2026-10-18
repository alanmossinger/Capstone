"""The decision ledger of v8: append-only, every row authorized by a named person, overrides gated where they are written.

What: ``Decision`` is one committee decision — the verb (invest now, invest
in stages, defer pending information, monitor, reject, reconsider), the
members, who authorized it and when, the what-if it was made under, the
scenario set's fingerprint, the advisor records it relied on and, when it
departs from the model's book, the answers to the five questions of the
override gate. ``record`` checks all of that and appends one line.
Why: in v6 the gate lived in the interface and ``ledger_append`` rewrote
the whole file without checking anything (audit S3). A decision the
ledger accepts is now one a person authorized, with the reasons the gate
asks for when the person overrides the model.
Reads / writes: `results/decision_ledger_v8.jsonl` (append only).
Used by: notebook 11, the decision page; `tests/test_ledger.py`.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

import numpy as np

from src import advisor as adv, paths

LEDGER_V8 = paths.RESULTS / "decision_ledger_v8.jsonl"
VERBS = ("invest now", "invest in stages", "defer pending information", "monitor", "reject", "reconsider")


class NotAuthorized(PermissionError):
    """A decision without a named authorizer, or an override without the gate's answers."""


def fingerprint(array):
    """Short SHA-256 of a scenario matrix (or any array): the ledger row says which numbers the decision saw."""
    return hashlib.sha256(np.ascontiguousarray(np.asarray(array, float)).tobytes()).hexdigest()[:16]


@dataclass
class Decision:
    """One committee decision as the ledger stores it."""

    verb: str
    members: list
    authorized_by: str
    model_members: list
    whatif: dict = field(default_factory=dict)
    scenario_fingerprint: str = ""
    advisor_records: list = field(default_factory=list)
    gate_answers: dict = field(default_factory=dict)
    opposing_case_read: bool = False
    note: str = ""

    @property
    def is_override(self):
        """True when the decided members differ from the model's book."""
        return set(self.members) != set(self.model_members)


def record(decision, path=LEDGER_V8, now=None):
    """Append one authorized decision; raise ``NotAuthorized`` or ``ValueError`` otherwise.

    Notes
    -----
    Checks, in order: the verb is one of ``VERBS``; a person is named; an
    override (members different from the model's book) carries an answer to
    every question of ``advisor.REASONING_QUESTIONS`` and a read opposing
    case (``advisor.override_allowed``). The line is appended, never
    rewritten, with its own hash and the previous line's, so an edit to an
    earlier row breaks the chain (``verify_chain``).
    """
    if decision.verb not in VERBS:
        raise ValueError(f"unknown decision {decision.verb!r}; one of {VERBS}")
    if not decision.authorized_by or not decision.authorized_by.strip():
        raise NotAuthorized("a decision needs the name of the person who authorized it")
    if decision.is_override:
        allowed, missing = adv.override_allowed(decision.gate_answers, decision.opposing_case_read)
        if not allowed:
            raise NotAuthorized(f"an override needs an answer to each of the five questions and the opposing case read; missing: {missing}")
    previous = ""
    if path.exists():
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        previous = json.loads(lines[-1])["hash"] if lines else ""
    row = {**asdict(decision), "override": decision.is_override, "time": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"), "previous": previous}
    row["hash"] = hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def verify_chain(path=LEDGER_V8):
    """True when every line's hash matches its content and the line before it."""
    if not path.exists():
        return True
    previous = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        stated = row.pop("hash")
        if row["previous"] != previous or hashlib.sha256(json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest() != stated:
            return False
        previous = stated
    return True
