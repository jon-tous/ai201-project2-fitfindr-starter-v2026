# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

A user describes what they're thrifting for in plain language (e.g. "vintage
graphic tee under $30, size M"). FitFindr searches a fixed catalog of
secondhand listings for the best match, asks a model to suggest an outfit
pairing it with the user's existing wardrobe (or general styling advice if the
wardrobe is empty), and turns that into a short caption someone could actually
post. If nothing matches or the query can't be parsed, it stops and says what
to change instead of guessing.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the fixed listings dataset for items whose keywords overlap a text query, optionally filtered to an exact size-token match and a max price, ranked by overlap score.
- **Inputs:** `description` (str) — free-text keywords describing the item. `size` (str | None) — matched by exact token, case-insensitive, against the tokens in the listing's size string (e.g. "M" matches "S/M", but not "US 9"); skipped entirely if None. `max_price` (float | None) — inclusive price ceiling; skipped if None.
- **Returns:** A list of listing dicts, best match first, capped at `config.SEARCH_RESULT_LIMIT`. Each dict has: `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None), `platform`.
- **When it has nothing:** An empty list — never `None`, never an exception — when nothing scores above zero after price/size filtering.

### `suggest_outfit`

- **What it does:** Calls the model to suggest one or two outfits pairing a candidate thrifted item with pieces from the user's wardrobe, or general styling advice if the wardrobe is empty.
- **Inputs:** `new_item` (dict) — a listing dict as returned by `search_listings`. `wardrobe` (dict) — a wardrobe dict with an `items` key holding a list of item dicts (`id`, `name`, `category`, `colors`, `style_tags`, `notes`); the list may be empty.
- **Returns:** A non-empty string with outfit suggestion(s), naming specific wardrobe pieces when the wardrobe is non-empty.
- **When it has nothing:** With an empty wardrobe, returns general styling advice for the new item (still a non-empty string) rather than raising or returning `""`.

### `create_fit_card`

- **What it does:** Calls the model to write a two-to-four sentence, social-caption-style write-up naming the item, its price, its platform, and the outfit's vibe.
- **Inputs:** `outfit` (str) — the outfit suggestion string from `suggest_outfit`. `new_item` (dict) — the listing dict for the item.
- **Returns:** A two-to-four sentence caption string.
- **When it has nothing:** If `outfit` is empty or whitespace-only, returns a descriptive message string rather than raising or calling the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what to change (keywords/size/price) and stop — do not call `suggest_outfit`. Otherwise, take the first result as `session["selected_item"]` and continue to `suggest_outfit`, then `create_fit_card`. A second branch covers parsing: if the model-based parser doesn't return a usable `description`/`size`/`max_price`, put a message in `session["error"]` and stop before calling `search_listings`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Asking the model, via `generate()` — the raw query is sent to the model with a request to return structured `description`/`size`/`max_price`.

**What moves through the session:** `query` → `parsed` (`description`, `size`, `max_price`) → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`, with `error` set (and every later field left `None`) if the run stops early.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'
  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Pair that adorable butterfly baby tee with your baggy dark-wash straight-leg jeans for the ultimate 2000s contrast between fitted and loose! Throw on your chunky white sneakers to keep it comfy, and layer the vintage black denim jacket on top when you need an extra layer.

  Fit card: Channel your inner 2000s pop princess with this dreamy butterfly baby tee! Score this ultimate throwback energy for just $18.00 right now on Depop. Grab it before it's gone and go live your best nostalgic life!
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'price': 18.0, 'size': 'S/M', ...}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'price': 24.0, 'size': 'L', ...}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'price': 15.0, 'size': 'S/M', ...}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'price': 19.0, 'size': 'L', ...}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'price': 27.0, 'size': 'W29', ...}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'price': 26.0, 'size': 'L', ...}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Grab those vintage Levi's and pair them with your white ribbed tank top and a brown leather belt for an effortless, classic base. Throw on your black cropped zip hoodie for a cool, slightly edgy layer, and finish the whole look with your chunky white sneakers. It's the ultimate casual street-style vibe!
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Channeling total off-duty model energy with these vintage Levi's 501s! Pair them with your freshest white sneakers for that effortlessly cool weekend stroll. Snag this medium wash dream on depop right now for just $38.00 before someone else beats you to it!
```

*(`suggest_outfit` and `create_fit_card` call the model through `generate()`, which caches identical prompts by default — see config.py's `CACHE_ENABLED`. Re-running these exact commands will replay the same cached text; running with the cache off, or on different items, produces different wording each time, which is what the fit-card criteria in criteria.md actually test.)*

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Help deciding what "matching size" should mean in `search_listings`, since the docstring warned a plain substring match breaks (`"s" in "us 9"` is `True`, `"l" in "xl"` is `True`).
- *What came back:* Three options — exact token match, normalize-then-match, or skip size filtering for now — with the tradeoffs of each.
- *What I changed:* Picked exact token match, case-insensitive, and wrote that rule into the Tool Inventory before any filtering code existed. `_tokenize()`/`_size_matches()` in `tools.py` implement exactly that rule.

**Moment 2**

- *What I asked for:* I ran `create_fit_card` three times on the same item, per the milestone's instructions, and got word-for-word identical captions back. I asked why.
- *What came back:* Claude pointed to `config.CACHE_ENABLED` rather than assuming the tool was broken — `generate()` replays a cached answer for an identical prompt by default — then reran the same test with caching bypassed to confirm the model's actual output does vary (three different captions at `TEMPERATURE = 0.9`).
- *What I changed:* Nothing in the code — I'd assumed a repeat prompt implied a broken tool, so this changed my read of the output rather than the tool itself.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. Matching query completes all three tools, returns a fit card | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. Impossible query stops before `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. `id` in `session["selected_item"]` matches `id` received by `suggest_outfit` | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Fit card mentions the item's price, across 5 different items | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. No exact sentence repeats across 5 different items' fit cards | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

For criteria 1, 2 and 4, each "Try" is one of the 5 repeated runs from
`python run_eval.py --label before` (scenarios in `scenarios.py`, full output
in `results/run_2026-10-03_2328_before.md`). Criterion 4's 5 tries are 5
*different items* (not the same item retried), since the criterion is about
item diversity, not retry reliability — see the note under the table in
`scenarios.py`. Criterion 3 doesn't fit `run_eval.py`'s model (it needs to
inspect what a tool was actually called with, not just the final session), so
it's checked by a separate script, `check_state.py`, which monkeypatches
`suggest_outfit` to capture its real argument; its 5 tries are the same 5
items used for criterion 4. Criterion 5 is scored by comparing all 5 of those
items' fit cards against each other after the fact (10 pairs, 0 shared
sentences allowed) — each "Try" is PASS if that item's sentences don't
collide with any other item's.

**Real output from one try**, pasted as text, naming the file and function
that produced it:

**Criterion 1 — `run_eval.py::run_once` → `agent.py::run_agent`, try 1 of "matching query completes":**

```
- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Fit card:

Channel your inner 2000s pop princess with this adorable butterfly baby tee! Score this ultimate off-duty model look for just $18.00 over on depop before it flies away. Get ready to live your best nostalgic life!
```

**Criterion 2 — `run_eval.py::run_once` → `agent.py::run_agent`, try 1 of "impossible query stops early":**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping

- stopped early: yes — No listings matched that search. Try a broader description, a higher max price, or a different size.
- selected_item: (none)
- search_results: 0
```

**Criterion 3 — `check_state.py::main`, try 1 of 5 ("vintage graphic tee under $30"):**

```
try 1: query='vintage graphic tee under $30'
  session['selected_item']['id']        = 'lst_002'
  id actually received by suggest_outfit = 'lst_002'
  PASS
...
5 of 5 passed
```

**Criterion 4 — `run_eval.py::run_once` → `tools.py::create_fit_card`, item 1 of 5 ("fit card item 1 — graphic tee", $18.0):**

```
Channel your inner 2000s pop star with this dreamy butterfly baby tee! Score this ultimate throwback for just $18.00 over on depop before someone else snags it. Grab your favorite baggy jeans and chunky sneakers, and you're ready to serve major nostalgic looks all weekend long!
```
`$18.00` matches the target item's price (18.0).

**Criterion 5 — the same 5 "fit card item N" runs, compared against each other:**

Checked all 5 captions (item 1 above, plus track jacket/$45, slip dress/$30,
platform sneakers/$48, denim jacket/$42) sentence-by-sentence. All 5 open with
a near-identical template ("Channel your inner ... with this ...") but no two
cards share one *exact* sentence — 0 overlaps across all 10 pairs.

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools, returns a fit card | 4 of 5 | MET (5/5) | All 5 tries of `vintage graphic tee under $30` completed parse → search → `suggest_outfit` → `create_fit_card` with a non-empty fit card and `stopped early: no` — read straight off `results/run_2026-10-03_2328_before.md`. |
| 2 | Impossible query stops before `suggest_outfit` | 5 of 5 | MET (5/5) | All 5 tries of `designer ballgown size XXS under $5` show `search_results: 0`, `session["error"]` set, and the trace ending at step 2 (`search_listings`) — `suggest_outfit` never appears. |
| 3 | `id` of `selected_item` equals `id` received by `suggest_outfit` | 5 of 5 | MET (5/5) | `check_state.py` monkeypatched `suggest_outfit` to record the real `id` it was called with, across 5 different queries; all 5 matched `session["selected_item"]["id"]` exactly. |
| 4 | Fit card mentions the item's price | 4 of 5 | MET (5/5) | Checked the price regex against all 25 captures in the run (5 items × 5 tries each), not just one try per item — 25 of 25 passed. |
| 5 | No shared sentence across items' fit cards | 5 of 5 | MET (5/5) | Compared every sentence of every fit card against every *other* item's fit cards — 250 cross-item pairs (5 items × 5 tries each), 0 shared sentences. |

**Diagnoses**

No misses this round — every criterion held, and criteria 4 and 5 held even
under more data than the target required (25 fit cards checked instead of 5,
250 cross-item pairs instead of 10). That's a good sign for
`create_fit_card`'s prompt, but it also means I didn't get to practice
diagnosing a real miss. So rather than stop at "all green," I did the
milestone's suggested exercise anyway — arguing the opposite verdict as hard
as I could against my own results:

1. **Criterion 2 is close to untestable as written.** `search_listings` has
   no randomness — same query, same fixed dataset, same answer every time —
   and `_parse_query` runs at `temperature=0.0`, which is close to
   deterministic too. Running the *same* impossible query 5 times mostly
   re-confirms one deterministic computation rather than sampling 5
   independent chances to fail. The target (5 of 5) isn't wrong, but the test
   I built under-exercises it. **What I'd tighten:** use 5 *different*
   impossible queries (different missing keywords, sizes, price ceilings)
   instead of one query 5 times, so a 5/5 verdict means something about
   reliability across inputs, not just repeatability of one input.

2. **Criterion 1's test didn't match its own stated reasoning.** The "why" I
   wrote in `criteria.md` says 4 of 5 because "my search is a plain keyword
   match and some phrasings will miss" — but the scenario I actually ran is
   one query, run 5 times, which tests parse-step consistency (also near
   deterministic at `temperature=0.0`), not search robustness across
   different real phrasings, which is the failure mode the target was
   written for. **What I'd tighten:** swap in 5 different matching queries,
   phrased the way a real user would rather than keyword-for-keyword matches
   to the data, so the test actually probes what the target accounts for.

Neither of these is "the criterion couldn't be measured" — both were
measured, and both passed — so this isn't the kind of revision `criteria.md`
gives credit for; it's a weaker finding about my *test*, not the criterion.
I'm leaving criteria 1 and 2's numbers as written rather than quietly
tightening them after the fact. If I rerun Milestone 3 with varied queries,
this is exactly what changes first in `scenarios.py`.



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 1 items: Platform Sneakers — White Chunky Sole
[3] suggest_outfit
      in:  dict with keys: new_item
      out: Oh, those platform sneakers are going to be your new absolute faves! Pair them with your baggy dark wash jeans…
[4] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Channel your inner 90s supermodel with these chunky white platform sneakers, just scored on Poshmark for $48.0…
```

**Empty search**

```
[1] parse_query
      in:  dict with keys: query
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping
```

**On the MCP move:** `run_agent()` now calls `call_tool("search_listings", {...})`
from `mcp_client.py` instead of calling `search_listings()` directly. Nothing
else in the loop changed. The return value was identical before and after the
move — same list of dicts, `price` still a plain float — so the rewire didn't
surface anything that had been hiding in the direct call.


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
