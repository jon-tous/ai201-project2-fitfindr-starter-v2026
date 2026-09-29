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
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



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
