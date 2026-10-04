"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    # Criterion 1 — Milestone 5 change. Originally this was one scenario
    # ("vintage graphic tee under $30") retried 5 times. The Milestone 4
    # diagnosis found that didn't test what the criterion's own "why" claims:
    # "some phrasings will miss" is about phrasing variety, but retrying one
    # query 5 times only measures parse-step consistency at temperature=0.0,
    # which is already near-deterministic. These 5 are different, more
    # colloquially-phrased queries instead — each run once, the same way
    # criterion 4's item scenarios are below — so a MET verdict here actually
    # says something about search robustness across phrasing.
    {
        "name": "matching query 1 — cozy oversized knitwear",
        "query": "something cozy and oversized for fall",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "matching query 2 — grunge band shirt",
        "query": "edgy grunge band shirt",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "matching query 3 — neutral basics",
        "query": "comfy basics in neutral earth tones",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "matching query 4 — boho summer top",
        "query": "cute boho top for summer",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        "name": "matching query 5 — nice leather jacket",
        "query": "a leather jacket that feels expensive",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    # Criterion 3 (state): id(session["selected_item"]) must equal the id of
    # the `new_item` actually received by suggest_outfit. That requires
    # instrumenting the call itself — run_eval.py's generic run_once only
    # records the session, not what a tool was literally called with — so
    # this one is checked by a separate script, check_state.py, which
    # monkeypatches suggest_outfit to capture its real argument. It reuses the
    # 5 queries below rather than adding its own scenario entries here.
    #
    # Criterion 4 (fit card mentions price) and criterion 5 (fit cards don't
    # repeat sentences) both need several DIFFERENT items, not the same query
    # retried — so each of these 5 is a different item, run once each rather
    # than five times. Criterion 5 is scored by comparing the 5 resulting fit
    # cards against each other after the run, so it shares this same data
    # instead of needing its own scenarios.
    {
        "name": "fit card item 1 — graphic tee",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card item 2 — track jacket",
        "query": "90s track jacket in size M",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card item 3 — slip dress",
        "query": "silk slip dress in midi length under $40",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card item 4 — platform sneakers",
        "query": "platform sneakers size 8",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        "name": "fit card item 5 — denim jacket",
        "query": "denim jacket under $50",
        "wardrobe": "example",
        "criterion": 4,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("query", "").strip():
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
