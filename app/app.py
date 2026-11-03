"""The dashboard (``make app``): the decision page first, the report's decision beside it.

What: a Streamlit app of three pages. *Decide* (``app/decide.py``) — the
options, your book and your reasons, the advisor's challenge, your result
against the advisor's. *A worked example* (``app/example.py``) — one
executive's recorded round through those steps. *The report's decision*
(``app/executive.py``) — the recommendation of the report on one screen,
for presenting it.
Why: one command opens one dashboard (decision #118); the decision page
comes first because deciding, not reading, is what the dashboard is for
(decision #119).
Reads: nothing itself; each page reads ``results/`` only.
Writes: nothing itself.
Used by: ``streamlit run app/app.py``; ``tests/test_app.py``.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src import advisor as adv  # noqa: E402

st.set_page_config(page_title="Beyond Prediction — the dashboard", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 3.4rem; padding-bottom: 2rem; max-width: 1400px;}
h1 {font-size: 2.0rem !important; margin-bottom: 0.2rem;}
h2 {font-size: 1.4rem !important; margin-top: 0.6rem;}
h3 {font-size: 1.15rem !important;}
[data-testid="stMetricValue"] {font-size: 1.8rem;}
[data-testid="stMetricLabel"] {font-size: 0.95rem; color: #5F6368;}
.reading {color: #5F6368; font-size: 0.95rem; margin-top: -0.4rem; margin-bottom: 0.8rem;}
.howto {background: #F4F5F7; border-left: 4px solid #13294B; padding: 0.8rem 1.1rem; border-radius: 6px; font-size: 0.98rem; line-height: 1.5; margin: 0.4rem 0 1rem 0;}
.rec {background: #13294B; color: white; padding: 1.1rem 1.4rem; border-radius: 10px; font-size: 1.02rem; line-height: 1.5;}
.rec b {color: #FFFFFF;}
.quote {background: #F4F5F7; border-left: 4px solid #0072B2; padding: 0.8rem 1rem; border-radius: 6px; font-size: 0.98rem;}
.masthead {background: #13294B; color: white; padding: 1.0rem 1.4rem 0.9rem 1.4rem; border-radius: 10px; margin: 0 0 0.9rem 0;}
.masthead .title {font-size: 1.75rem; font-weight: 700; line-height: 1.2; margin: 0;}
.masthead .subtitle {font-size: 1.0rem; color: #DDE3EC; margin: 0.3rem 0 0 0;}
.masthead .byline {font-size: 0.9rem; color: #B8C2D3; margin: 0.45rem 0 0 0;}
</style>
""", unsafe_allow_html=True)
st.markdown("""<div class="masthead"><p class="title">Beyond Prediction: Prescriptive AI for Strategic Energy Capital Allocation</p>
<p class="subtitle">A Governed Decision Intelligence System for Risk, Returns, and Investment Committee Choices Across Oil, Gas, Power, Renewables, and Storage</p>
<p class="byline">Alan Mössinger · SIADS 699 Capstone, University of Michigan · the dashboard: decide, a worked example, the report's decision</p></div>""",
            unsafe_allow_html=True)
backend = adv.backend_name()
st.markdown(f"""<div class="howto"><b>Before you start.</b> Every number on these pages is read from the report's result tables, and the
recorded rounds replay with no key. To have the advisor challenge <i>your own</i> book you need a key for a language model — any
provider's: put <code>ANTHROPIC_API_KEY</code> in <code>.env</code>, or <code>LLM_API_KEY</code> with <code>LLM_BASE_URL</code> and
<code>LLM_MODEL</code> for any OpenAI-compatible service (OpenAI, Gemini, Mistral, a local server), or sign in to the <code>claude</code>
command. {"A live call would use " + backend + "." if backend else "No key is set on this machine, so the pages replay the recorded rounds only."}</div>""",
            unsafe_allow_html=True)
st.navigation([st.Page("decide.py", title="Decide", default=True), st.Page("example.py", title="A worked example"), st.Page("executive.py", title="The report's decision")]).run()
