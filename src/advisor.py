"""The LLM advisor: grounded in result tables, recorded on every call, replayable offline, number-checked.

What: a thin client of the Anthropic Messages API with three disciplines
(PLAN.md §14.10). *Grounding* — the model sees only the result tables of
``results/`` pasted into the user message, and ``verify_numbers`` checks
that every number in an answer appears in that context. *Recording* —
every call is appended to ``results/advisor_runs.jsonl`` (prompts, model,
parameters, response, usage, verification). *Replay* — a call whose
prompts match a recorded one is served from the record, so ``make all``
runs offline without a key; a call with no record and no key returns
``None`` and the notebook writes a "not recorded" row instead of failing.
Also the prompt templates of ``prompts/``, the challenge round (the
motivated-reasoning check and the ideological Turing test), the override
gate and the decision-ledger append.
Why: the course asks for an AI component whose outputs are evaluated, and
the report must reproduce without a key; a recommendation that cites a
number the tables do not hold is worthless, so the check is mechanical.
Reads: ``.env`` (``ANTHROPIC_API_KEY``, never printed), ``prompts/*.md``,
``results/advisor_runs.jsonl``.
Writes: ``results/advisor_runs.jsonl``, ``results/decision_ledger.csv`` (append).
Used by: notebook 10, the dashboard (``app/app.py``); ``tests/test_advisor.py``.
"""

import hashlib
import json
import os
import re
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from src import paths

MODEL = "claude-sonnet-5-5"  # the model id recorded with every call; the dashboard shows it
MAX_TOKENS = 1800
TEMPERATURE = 0.0  # a recommendation is a deterministic function of the tables, as far as the API allows
PROMPTS = paths.REPO / "prompts"
RUNS = paths.RESULTS / "advisor_runs.jsonl"
LEDGER = paths.RESULTS / "decision_ledger.csv"
LEDGER_COLUMNS = ["entry_id", "date", "actor", "mode", "horizon", "revenue_case", "budget", "lam", "technology_cap", "members", "n_members", "capex",
                  "expected_npv_oos", "cvar_loss_oos", "override", "reasoning_answered", "realized_npv", "scored_on", "note"]
REASONING_QUESTIONS = {  # the five questions of the motivated-reasoning check; the override gate needs an answer to each
    "context_and_stakes": "What happens if this decision is wrong?",
    "parties": "What does each party to the decision want?",
    "emotional_investment": "Where is my emotional investment (a sunk cost, a past position, a sector I like)?",
    "evidence": "Which evidence did I emphasise and which did I dismiss?",
    "framing": "What alternative did I leave off the table?",
}
NUMBER = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?!\w|\.\d)")
YEAR_RANGE = (1980, 2060)


# --- key, prompts, context ---------------------------------------------------------------------

def api_key():
    """The Anthropic key from ``.env`` or the environment, or None; the value is never logged."""
    load_dotenv(paths.ENV_FILE)
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    return key or None


def load_prompt(name):
    """A template of ``prompts/`` without its status note (the note is for the repository, not the model)."""
    text = (PROMPTS / f"{name}.md").read_text(encoding="utf-8")
    return "\n".join(line for line in text.splitlines() if not line.startswith("> Status:")).strip() + "\n"


def render(name, **fields):
    """A template with its ``{placeholders}`` filled."""
    return load_prompt(name).format(**fields)


def fmt(x):
    """One number formatter for every table pasted to the model, so the grounding check compares like with like."""
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, (int, np.integer)):
        return f"{int(x):,}"
    if isinstance(x, (float, np.floating)):
        if pd.isna(x):
            return ""
        if abs(x) >= 1000:
            return f"{x:,.0f}"
        if abs(x) >= 10:
            return f"{x:.1f}"
        return f"{x:.2f}"
    return str(x)


def format_table(df, title, provenance, note=None, max_rows=80):
    """A result table as a pipe table with a title line and its provenance label."""
    part = df.head(max_rows)
    head = "| " + " | ".join(str(c) for c in part.columns) + " |"
    sep = "|" + "---|" * len(part.columns)
    rows = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in part.itertuples(index=False)]
    lines = [f"### {title} ({provenance})"] + ([note] if note else []) + [head, sep] + rows
    if len(df) > max_rows:
        lines.append(f"({len(df) - max_rows} more rows not shown)")
    return "\n".join(lines) + "\n"


def numbers_in(text):
    """The numeric tokens of a text, normalised (no thousands separators, no trailing zeros)."""
    out = set()
    for m in NUMBER.finditer(text):
        token = m.group(0).replace(",", "")
        try:
            value = float(token)
        except ValueError:
            continue
        out.add(_norm(value))
    return out


def _norm(value):
    return f"{value:.6g}"


def verify_numbers(answer, context, allow_small_integers=50):
    """Check that every number in ``answer`` appears in ``context`` (the tables the model was shown).

    Returns
    -------
    dict
        ``n_numbers``, ``n_grounded``, ``rate``, ``ungrounded`` (the tokens not found).

    Notes
    -----
    Years (1980–2060) and small integers up to ``allow_small_integers`` are
    not checked: "24 candidates" or "five years" is a count, not a figure
    the tables must hold. A number written with a different rounding than
    the table's ("$20.7B" for 20,654) counts as ungrounded, on purpose: the
    rule the prompt states is "exactly as shown", and a looser check would
    let a plausible invention through.
    """
    allowed = numbers_in(context)
    checked, ungrounded = 0, []
    for m in NUMBER.finditer(answer):
        token = m.group(0).replace(",", "")
        try:
            value = float(token)
        except ValueError:
            continue
        if value.is_integer() and (YEAR_RANGE[0] <= value <= YEAR_RANGE[1] or abs(value) <= allow_small_integers):
            continue
        checked += 1
        if _norm(value) not in allowed:
            ungrounded.append(m.group(0))
    grounded = checked - len(ungrounded)
    return {"n_numbers": checked, "n_grounded": grounded, "rate": (grounded / checked) if checked else 1.0, "ungrounded": ungrounded}


def parse_json(text):
    """The first JSON object in a response (fenced or bare), or None."""
    if text is None:
        return None
    body = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.M)
    start, end = body.find("{"), body.rfind("}")
    if start < 0 or end < 0:
        return None
    try:
        return json.loads(body[start:end + 1])
    except json.JSONDecodeError:
        return None


# --- the client ---------------------------------------------------------------------------------

class Advisor:
    """Calls the API or replays the record; every call is written down.

    Parameters
    ----------
    mode : {"auto", "live", "replay"}
        ``auto`` calls the API when a key is present and replays otherwise;
        ``replay`` never calls (``make all`` offline); ``live`` requires the key.
    model : str
        Model id recorded with the call.
    runs_path : pathlib.Path
        The JSONL record.
    """

    def __init__(self, mode="auto", model=MODEL, runs_path=RUNS, max_tokens=MAX_TOKENS, temperature=TEMPERATURE):
        key = api_key()
        if mode == "live" and key is None:
            raise RuntimeError("ANTHROPIC_API_KEY is missing from .env (live mode); use mode='replay' to run offline")
        self.live = mode == "live" or (mode == "auto" and key is not None)
        self.model, self.max_tokens, self.temperature, self.runs_path = model, max_tokens, temperature, runs_path
        self._client = None
        self.records = self._load()
        self.calls = {"replayed": 0, "live": 0, "missing": 0}

    def _load(self):
        records = {}
        if self.runs_path.exists():
            for line in self.runs_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    records[rec["key"]] = rec
        return records

    def _key(self, system, user):
        return hashlib.sha256(json.dumps({"model": self.model, "system": system, "user": user}, ensure_ascii=False).encode("utf-8")).hexdigest()

    def ask(self, system, user, mode_name="", tag=""):
        """The recorded or fresh response to (system, user), with its verification; None when offline with no record."""
        key = self._key(system, user)
        if key in self.records:
            self.calls["replayed"] += 1
            return {**self.records[key], "replayed": True}
        if not self.live:
            self.calls["missing"] += 1
            return None
        if self._client is None:
            import anthropic  # imported here so the module loads without the package in replay-only environments
            self._client = anthropic.Anthropic(api_key=api_key())
        response = self._client.messages.create(model=self.model, max_tokens=self.max_tokens, temperature=self.temperature, system=system,
                                                messages=[{"role": "user", "content": user}])
        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        record = {"key": key, "time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "mode": mode_name, "tag": tag, "model": response.model,
                  "temperature": self.temperature, "max_tokens": self.max_tokens, "system": system, "user": user, "response": text,
                  "usage": {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens},
                  "verification": verify_numbers(text, system + "\n" + user)}
        with open(self.runs_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.records[key] = record
        self.calls["live"] += 1
        return {**record, "replayed": False}


# --- the challenge round and the override gate ------------------------------------------------

def challenge(advisor, human_statement, opposing_book, context, tag=""):
    """One round of "reason my thinking": the motivated-reasoning check, then the opposing case.

    Returns
    -------
    dict
        ``check`` and ``opposing`` (the two responses or None), ``converge``
        and ``disagree`` parsed from the opposing case's last line, and a
        markdown ``transcript``.
    """
    system = load_prompt("advisor_system") + "\nDATA\n\n" + context
    check = advisor.ask(system, render("motivated_reasoning_check", human_statement=human_statement), "challenge/check", tag)
    opposing = advisor.ask(system, render("ideological_turing_test", human_statement=human_statement, opposing_book=opposing_book), "challenge/opposing", tag)
    converge, disagree = None, None
    if opposing is not None:
        m = re.search(r"CONVERGE:\s*(.*?)\s*\|\s*DISAGREE:\s*(.*)", opposing["response"], flags=re.S)
        if m:
            converge, disagree = m.group(1).strip(), m.group(2).strip()
    lines = ["## The human's statement", "", human_statement, "", "## The motivated-reasoning check", "",
             check["response"] if check else "_not recorded (no key, no record)_", "", "## The opposing case", "",
             opposing["response"] if opposing else "_not recorded (no key, no record)_", ""]
    return {"check": check, "opposing": opposing, "converge": converge, "disagree": disagree, "transcript": "\n".join(lines)}


def override_allowed(answers, opposing_case_read=False, min_chars=20):
    """The override gate: the human may override the advisor only after answering the five questions and reading the opposing case.

    Returns
    -------
    tuple of (bool, list)
        Allowed, and the keys still missing.
    """
    missing = [k for k in REASONING_QUESTIONS if len(str(answers.get(k, "")).strip()) < min_chars]
    if not opposing_case_read:
        missing.append("opposing_case_read")
    return len(missing) == 0, missing


def ledger_append(row, path=LEDGER):
    """Append one decision to the ledger with the fixed columns; returns the ledger."""
    ledger = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=LEDGER_COLUMNS)
    full = {c: row.get(c, "") for c in LEDGER_COLUMNS}
    full["date"] = full["date"] or date.today().isoformat()
    ledger = pd.concat([ledger, pd.DataFrame([full])], ignore_index=True)
    ledger.to_csv(path, index=False)
    return ledger
