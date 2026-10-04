#!/usr/bin/env python3
"""
Criterion 3 check — state identity, not model output. ← Milestone 3

criteria.md #3: the `id` of `session["selected_item"]` (captured right after
`search_listings` returns) must equal the `id` of the `new_item` argument
*actually received* by `suggest_outfit`.

`run_eval.py`'s run_once() only records the final session — it never looks at
what a tool was literally called with, so it can't catch a bug where
run_agent() quietly rebuilt a dict instead of passing the same one through.
This script instruments the call directly: it wraps `suggest_outfit` to
record the id of its real argument, then compares that against the session.

generate() is stubbed out here (no real API calls) — this criterion is about
wiring inside our own code, not about what the model says, so there's nothing
to gain from paying for five real model calls to check it.

    python check_state.py
"""

import json

import agent
import tools
from utils.data_loader import get_example_wardrobe

QUERIES = [
    "vintage graphic tee under $30",
    "90s track jacket in size M",
    "silk slip dress in midi length under $40",
    "platform sneakers size 8",
    "denim jacket under $50",
]


def _stub_parse(prompt, system=None, cache=True, temperature=None):
    # Stands in for _parse_query's model call: a naive "pass the whole query
    # through as the description" parse. Good enough here — this criterion
    # checks wiring, not parse quality.
    return json.dumps({"description": prompt, "size": None, "max_price": None})


def _stub_outfit(prompt, system=None, cache=True, temperature=None):
    return "stubbed response — check_state.py doesn't call the real model"


def main():
    agent.generate = _stub_parse
    tools.generate = _stub_outfit

    real_suggest_outfit = tools.suggest_outfit
    received_ids = []

    def capturing_suggest_outfit(new_item, wardrobe):
        received_ids.append(new_item.get("id"))
        return real_suggest_outfit(new_item, wardrobe)

    agent.suggest_outfit = capturing_suggest_outfit

    wardrobe = get_example_wardrobe()
    passes = 0

    for i, query in enumerate(QUERIES, 1):
        received_ids.clear()
        session = agent.run_agent(query, wardrobe)

        selected_id = (session.get("selected_item") or {}).get("id")
        received_id = received_ids[0] if received_ids else None
        ok = selected_id is not None and selected_id == received_id
        passes += ok

        print(f"try {i}: query={query!r}")
        print(f"  session['selected_item']['id']        = {selected_id!r}")
        print(f"  id actually received by suggest_outfit = {received_id!r}")
        print(f"  {'PASS' if ok else 'FAIL'}")
        print()

    print(f"{passes} of {len(QUERIES)} passed")


if __name__ == "__main__":
    main()
