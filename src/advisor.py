"""The LLM advisor: grounded in result tables, recorded on every call, replayable offline, number-checked.

What: a thin client of Claude with three disciplines (PLAN.md §14.10). It
reaches the model through one of two backends: the Anthropic Messages API
when ``ANTHROPIC_API_KEY`` is in ``.env``, or otherwise the Claude Code
command line (``claude -p``) signed in to the author's Claude subscription,
run with no tools, no project files and no memory, so it sees exactly the
same system prompt and user message as the API would (decision #76). *Grounding* — the model sees only the result tables of
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
Reads: ``.env`` (``ANTHROPIC_API_KEY`` if present, never printed), the
``claude`` command's own sign-in, ``prompts/*.md``, ``results/advisor_runs.jsonl``.
Writes: ``results/advisor_runs.jsonl``, ``results/decision_ledger.csv`` (append).
Used by: notebook 10, the dashboard (``app/app.py``); ``tests/test_advisor.py``.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from src import paths

MODEL = "claude-sonnet-5-5"  # the model id recorded with every call; the dashboard shows it
MAX_TOKENS = 1800
TEMPERATURE = None  # the model's default: claude-sonnet-5-5 rejects any other sampling setting, and the command line has none
CLI_TIMEOUT_S = 600  # one answer; the tables run to about 60 KB of input
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
NUMBER = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?=[BMk%]?(?!\w)|\s|$)(?!\.\d)")  # "6.15B", "40%" and "150k" are numbers too
YEAR_RANGE = (1980, 2060)


# --- key, prompts, context ---------------------------------------------------------------------

def api_key():
    """The Anthropic key from ``.env`` or the environment, or None; the value is never logged."""
    load_dotenv(paths.ENV_FILE)
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    return key or None


def cli_path():
    """The ``claude`` command on PATH, or None."""
    return shutil.which("claude")


def cli_environment():
    """The environment for a ``claude -p`` child: this process's, without any Claude or Anthropic session variables.

    Notes
    -----
    A notebook run from inside a Claude Code session inherits that session's
    variables (``CLAUDECODE``, ``ANTHROPIC_BASE_URL`` and the like), which
    would make the child refuse to start or route it through the parent
    session. An ``ANTHROPIC_API_KEY`` would also take precedence over the
    subscription sign-in. Removing every ``CLAUDE*``, ``ANTHROPIC_*`` and
    ``MCP_*`` variable leaves the child as if started from a fresh terminal;
    the two variables added back keep every CLAUDE.md and memory file out of
    its context.
    """
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith(("CLAUDE", "ANTHROPIC_", "MCP_"))}
    env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] = "1"
    env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] = "1"
    return env


def ask_cli(system, user, model=MODEL, timeout=CLI_TIMEOUT_S):
    """One answer from ``claude -p`` on the Claude subscription: the system prompt replaced, no tools, nothing loaded from disk.

    Returns
    -------
    dict
        ``text``, ``model`` (the id the command reports having used),
        ``input_tokens`` and ``output_tokens``.

    Raises
    ------
    RuntimeError
        If the command is missing, fails, or reports an error (for example a
        sign-in that has expired); the message carries the command's own
        error text, which holds no secret.

    Notes
    -----
    The system prompt goes in a file and the user message on standard input,
    because the Windows command line stops at about 32 KB and the tables are
    longer. The child runs in an empty temporary folder with ``--tools ""``
    and ``--strict-mcp-config``, so the only text it reads is the prompt it
    is given, which keeps the grounding check meaningful. Sampling cannot be
    set from the command line; the record says so.
    """
    exe = cli_path()
    if exe is None:
        raise RuntimeError("the claude command is not on PATH")
    with tempfile.TemporaryDirectory() as folder:
        system_file = os.path.join(folder, "system.md")
        with open(system_file, "w", encoding="utf-8") as f:
            f.write(system)
        args = [exe, "-p", "Answer the task in the input.", "--system-prompt-file", system_file, "--tools", "", "--strict-mcp-config",
                "--no-session-persistence", "--output-format", "json", "--model", model]
        done = subprocess.run(args, input=user.encode("utf-8"), capture_output=True, cwd=folder, env=cli_environment(), timeout=timeout)
    out = done.stdout.decode("utf-8", errors="replace")
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude -p exited {done.returncode}: {(out or done.stderr.decode('utf-8', errors='replace'))[:300]}") from None
    if body.get("is_error") or body.get("subtype") != "success":
        raise RuntimeError(f"claude -p reported an error: {str(body.get('result'))[:300]}")
    used = list(body.get("modelUsage", {}))
    usage = body.get("usage", {})
    return {"text": body.get("result", ""), "model": used[0] if used else model,
            "input_tokens": usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0) + usage.get("cache_creation_input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0)}


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
    """Calls Claude or replays the record; every call is written down.

    Parameters
    ----------
    mode : {"auto", "live", "replay"}
        ``auto`` calls Claude when a backend is available and replays
        otherwise; ``replay`` never calls (``make all`` offline); ``live``
        requires a backend.
    model : str
        Model id recorded with the call.
    runs_path : pathlib.Path
        The JSONL record.
    backend : {"auto", "api", "cli"}
        ``api`` is the Messages API with ``ANTHROPIC_API_KEY``; ``cli`` is
        ``claude -p`` on the Claude subscription; ``auto`` takes the API when
        the key is present and the command line otherwise.

    Notes
    -----
    A record is keyed by (model, system, user) only, so a call recorded
    through either backend replays identically; the backend is stored with
    the record for the reader.
    """

    def __init__(self, mode="auto", model=MODEL, runs_path=RUNS, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, backend="auto"):
        key = api_key()
        if backend == "auto":
            backend = "api" if key is not None else ("cli" if cli_path() else None)
        available = backend == "cli" and cli_path() is not None or backend == "api" and key is not None
        if mode == "live" and not available:
            raise RuntimeError("no backend for live mode: put ANTHROPIC_API_KEY in .env or sign in to the claude command; use mode='replay' to run offline")
        self.backend = backend if available else None
        self.live = mode == "live" or (mode == "auto" and available)
        self.strict = mode == "live"  # in auto mode a failed call falls back to "not recorded" so the pipeline still runs offline
        self.last_error = None
        self.model, self.max_tokens, self.temperature, self.runs_path = model, max_tokens, temperature, runs_path
        self._client = None
        self.records = self._load()
        self.calls = {"replayed": 0, "live": 0, "missing": 0}

    def _load(self):
        """The record, keyed; each record's verification is recomputed with the current checker, so a checker fix rescores the record without a call."""
        records = {}
        if self.runs_path.exists():
            for line in self.runs_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rec = json.loads(line)
                    if "system" in rec and "user" in rec:
                        rec["verification"] = verify_numbers(rec["response"], rec["system"] + "\n" + rec["user"])
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
        if self.backend == "cli":
            try:
                answer = ask_cli(system, user, self.model)
            except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
                if self.strict:
                    raise
                self.live, self.last_error = False, str(error)  # stop trying for the rest of the run; the notebook reports the reason
                self.calls["missing"] += 1
                return None
            text, used, usage = answer["text"], answer["model"], {"input_tokens": answer["input_tokens"], "output_tokens": answer["output_tokens"]}
        else:
            if self._client is None:
                import anthropic  # imported here so the module loads without the package in replay-only environments
                self._client = anthropic.Anthropic(api_key=api_key())
            sampling = {} if self.temperature is None else {"temperature": self.temperature}
            response = self._client.messages.create(model=self.model, max_tokens=self.max_tokens, system=system,
                                                    messages=[{"role": "user", "content": user}], **sampling)
            text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
            used, usage = response.model, {"input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens}
        record = {"key": key, "time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "mode": mode_name, "tag": tag, "model": used,
                  "backend": "claude -p (Claude subscription)" if self.backend == "cli" else "Messages API",
                  "temperature": "model default" if self.temperature is None else self.temperature,
                  "max_tokens": self.max_tokens if self.backend == "api" else "not set (command line)",
                  "system": system, "user": user, "response": text, "usage": usage,
                  "verification": verify_numbers(text, system + "\n" + user)}
        with open(self.runs_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.records[key] = record
        self.calls["live"] += 1
        return {**record, "replayed": False}


# --- the portfolio context (the only facts the advisor sees) ------------------------------------

def portfolio_context(stress="base", case="contracted"):
    """The DATA block of the recommend and challenge modes: the forty candidates under one stress, the six books, capital by technology, the stresses.

    Parameters
    ----------
    stress : str
        A stress name of ``results/stress_tests.csv`` (``"base"`` is the flat path).
    case : str
        The revenue case the books were scored in.

    Returns
    -------
    str
        Pipe tables rendered by ``format_table``, each with its provenance label.

    Notes
    -----
    Read from ``results/`` only, so notebook 10, the dashboard and the
    terminal session (``python -m src.advisor``) show the model the same
    tables, and the grounding check compares against the same text.
    """
    R = paths.RESULTS
    cand = pd.read_csv(R / "candidate_npv.csv")
    ids = list(cand["project_id"])
    books = pd.read_csv(R / "portfolio_books.csv", index_col=0)
    book_names = [c for c in books.columns if c not in ("technology", "capex")]
    scores = pd.read_csv(R / "portfolio_scores.csv")
    oos = scores[scores["scenarios"].str.startswith("held-out") & (scores["revenue_case"] == case)].set_index("book")
    stresses = pd.read_csv(R / "stress_tests.csv")
    stress_c = pd.read_csv(R / "stress_candidates.csv")
    alloc = pd.read_csv(R / "portfolio_allocation.csv")
    registered = json.loads((R / "success_criteria_v7_registered.json").read_text(encoding="utf-8"))
    cap = registered.get("technology_cap", 0.4)
    budget = float(pd.read_csv(R / "decision_ledger.csv").loc[0, "budget"])  # the registered budget of notebook 09
    capex = cand.set_index("project_id")["capex"].reindex(ids).to_numpy()
    x_d = books["D risk-aware MILP"].reindex(ids).to_numpy(int)
    npv_stress = stress_c[stress_c["stress"] == stress].set_index("project_id")["npv"]
    candidates = pd.DataFrame({"project_id": cand["project_id"], "technology": cand["technology"], "capex_$M": cand["capex"] / 1e6,
                               "expected_npv_merchant_$M": cand["expected_npv_base"] / 1e6, "expected_npv_contracted_$M": cand["expected_npv_contracted"] / 1e6,
                               f"npv_under_{stress.replace(' ', '_')}_$M": cand["project_id"].map(npv_stress) / 1e6,
                               "p_operation_7y": cand["p_operation_7y"].fillna(1.0), "breakeven": cand["breakeven"], "breakeven_unit": cand["breakeven_unit"],
                               "data_completeness": cand["data_completeness"], "in_book_D": x_d.astype(bool), "provenance": cand["provenance"]})
    rows = []
    for b in book_names:
        x = books[b].reindex(ids).to_numpy(int)
        rows.append({"book": b, "n_members": int(x.sum()), "capex_$B": float(capex @ x) / 1e9, "expected_npv_oos_$B": oos.loc[b, "expected_npv"] / 1e9,
                     "cvar95_loss_oos_$B": oos.loc[b, "cvar_loss"] / 1e9, "p_negative_oos": oos.loc[b, "p_negative"], "members": ";".join(np.array(ids)[x == 1])})
    s = stresses.copy()
    for c in ("book_npv_leases", "book_npv_power", "book_npv", "change_vs_base"):
        s[c + "_$B"] = s[c] / 1e9
    s = s[["stress", "book_npv_leases_$B", "book_npv_power_$B", "book_npv_$B", "change_vs_base_$B", "wti_path", "hh", "wind_cf", "solar_revenue", "delay_years", "cost"]]
    parts = [format_table(candidates, f"The forty candidates and their NPV under the stress '{stress}'", "FORECAST; lease costs ASSUMED (the upstream grid)",
                          note="Expected NPVs are timing-weighted (P(operation) from the queue models) at the flat 2024 real prices; $ million, 2024 dollars."),
             format_table(pd.DataFrame(rows), "The six books scored out of sample on the held-out scenarios", "FORECAST",
                          note=f"Budget ${budget / 1e9:.2f}B, no technology above {cap:.0%} of it; {case} revenue case; CVaR95 loss negative = the worst 5% is still a profit."),
             format_table(alloc.assign(**{c: alloc[c] / 1e9 for c in alloc.columns if c != "book"}).rename(columns=lambda c: c if c == "book" else c + "_$B"),
                          "Capital by technology in each book ($ billion)", "DERIVED"),
             format_table(s, "The default book of forty under the named stresses (flat base path)", "FORECAST; multipliers ASSUMED")]
    return "\n".join(parts)


OPPOSING_BOOK_D = ("Book D (risk-aware MILP): the leases plus the contracted wind requests and some gas combined cycle, chosen to maximise expected NPV minus "
                   "the worst-5% loss within the same budget and the 40% technology cap.")


# --- the challenge round (human in the loop) and the override gate ------------------------------

def format_answers(questions, answers):
    """The advisor's five questions paired with the human's answers, as the text the verdict and the opposing case receive.

    Parameters
    ----------
    questions : str or None
        The advisor's numbered questions (step 1), or None when the human
        answered the standing questions of ``REASONING_QUESTIONS`` instead.
    answers : dict
        Keyed as ``REASONING_QUESTIONS``; missing keys read "(no answer)".
    """
    asked = [q.strip() for q in re.split(r"\n\s*(?=\d+[.)]\s)", "\n" + (questions or "")) if q.strip()]
    lines = []
    for n, (key, standing) in enumerate(REASONING_QUESTIONS.items(), start=1):
        question = re.sub(r"^\d+[.)]\s*", "", asked[n - 1] if n - 1 < len(asked) else standing)
        answer = str(answers.get(key, "")).strip() or "(no answer)"
        lines.append(f"Q{n}. {question}\nA{n}. {answer}")
    return "\n\n".join(lines)


def challenge(advisor, human_statement, opposing_book, context, answers=None, tag=""):
    """The "reason my thinking" round with the human in the loop: the advisor asks, the human answers, then it judges and argues the other book.

    Parameters
    ----------
    advisor : Advisor
    human_statement : str
        The book the human prefers and the reasons, in the human's words.
    opposing_book : str
        The alternative the advisor must argue for (``OPPOSING_BOOK_D`` in the terminal session).
    context : str
        The DATA block (``portfolio_context``).
    answers : dict or None
        The human's answers to the five questions, keyed as ``REASONING_QUESTIONS``.
        With None the questions are still asked and recorded, and the verdict
        judges the statement alone, so a one-shot caller still gets an answer.
    tag : str
        Recorded with the calls.

    Returns
    -------
    dict
        ``questions`` (the step-1 response), ``check`` and ``opposing`` (the
        two responses or None), ``converge`` and ``disagree`` parsed from the
        opposing case's last line, and a markdown ``transcript``.

    Notes
    -----
    Step 1 asks exactly five questions tied to the statement, one per item
    of the override gate, and nothing else; the human's answers to them are
    the answers the gate needs (``override_allowed``), so the challenge and
    the override are one exchange, not two forms. Steps 2 and 3 receive the
    statement and the answers, so the verdict and the opposing case argue
    against what the human actually said (decision #79).
    """
    system = load_prompt("advisor_system") + "\nDATA\n\n" + context
    questions = advisor.ask(system, render("motivated_reasoning_questions", human_statement=human_statement), "challenge/questions", tag)
    question_text = questions["response"] if questions else None
    answer_text = format_answers(question_text, answers) if answers else "(no answers were given; judge the statement alone)"
    check = advisor.ask(system, render("motivated_reasoning_check", human_statement=human_statement, answers=answer_text), "challenge/check", tag)
    opposing = advisor.ask(system, render("ideological_turing_test", human_statement=human_statement, answers=answer_text, opposing_book=opposing_book),
                           "challenge/opposing", tag)
    converge, disagree = None, None
    if opposing is not None:
        m = re.search(r"CONVERGE:\s*(.*?)\s*\|\s*DISAGREE:\s*(.*)", opposing["response"], flags=re.S)
        if m:
            converge, disagree = m.group(1).strip(), m.group(2).strip()
    missing = "_not recorded (no backend, no record)_"
    lines = ["## The human's statement", "", human_statement, "", "## The advisor's questions", "", question_text or missing, "",
             "## The human's answers", "", answer_text, "", "## The motivated-reasoning check", "", check["response"] if check else missing, "",
             "## The opposing case", "", opposing["response"] if opposing else missing, ""]
    return {"questions": questions, "check": check, "opposing": opposing, "converge": converge, "disagree": disagree, "transcript": "\n".join(lines)}


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


def read_block(prompt):
    """Lines typed at the terminal until an empty line; returns them joined."""
    print(prompt, flush=True)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line)
    return "\n".join(lines).strip()


def terminal_session(tag=None, opposing_book=OPPOSING_BOOK_D, stress="base"):
    """Reason my thinking at the keyboard: state the book, answer the advisor's five questions, read its verdict and the opposing case.

    Notes
    -----
    Writes ``results/advisor_transcripts/challenge_<tag>.md`` and appends a
    ledger row (actor "human", mode "challenge/hitl") with the five answers,
    which are also what the override gate needs. Every model call is recorded
    like any other, so the transcript replays offline.
    """
    tag = tag or datetime.now().strftime("hitl_%Y%m%d_%H%M")
    advisor = Advisor(mode="auto")
    if not advisor.live:
        print("no backend: put ANTHROPIC_API_KEY in .env or sign in to the claude command (claude auth login); recorded exchanges still replay")
    context = portfolio_context(stress)
    statement = read_block("Your preferred book and your reasons (end with an empty line):")
    if not statement:
        print("nothing stated; nothing asked")
        return None
    system = load_prompt("advisor_system") + "\nDATA\n\n" + context
    questions = advisor.ask(system, render("motivated_reasoning_questions", human_statement=statement), "challenge/questions", tag)
    if questions is None:
        print("the advisor could not answer (no backend and no record)")
        return None
    print("\nThe advisor asks:\n")
    print(questions["response"])
    answers = {}
    for n, key in enumerate(REASONING_QUESTIONS, start=1):
        answers[key] = read_block(f"\nYour answer to question {n} (end with an empty line):")
    result = challenge(advisor, statement, opposing_book, context, answers=answers, tag=tag)
    print("\n## The motivated-reasoning check\n")
    print(result["check"]["response"] if result["check"] else "(not recorded)")
    print("\n## The opposing case\n")
    print(result["opposing"]["response"] if result["opposing"] else "(not recorded)")
    allowed, missing = override_allowed(answers, opposing_case_read=result["opposing"] is not None)
    print(f"\nOverride gate: {'open' if allowed else 'closed'}" + ("" if allowed else f" (missing: {', '.join(missing)})"))
    folder = paths.RESULTS / "advisor_transcripts"
    folder.mkdir(exist_ok=True)
    path = folder / f"challenge_{tag}.md"
    path.write_text(f"# Challenge round — {tag} (human in the loop)\n\n" + result["transcript"], encoding="utf-8")
    ledger_append({"entry_id": f"HITL-{tag}", "actor": "human", "mode": "challenge/hitl", "override": allowed,
                   "reasoning_answered": " | ".join(f"{k}: {v}" for k, v in answers.items() if v),
                   "note": f"converge: {result['converge']}; disagree: {result['disagree']}"})
    print(f"\ntranscript: {path.relative_to(paths.REPO)}; ledger entry HITL-{tag}")
    return result


if __name__ == "__main__":  # python -m src.advisor [tag]
    terminal_session(sys.argv[1] if len(sys.argv) > 1 else None)
