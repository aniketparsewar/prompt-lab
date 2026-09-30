# Project 2 Brief — Prompt Lab (eval harness)

## Goal
Build a harness that runs versioned prompts against a golden test set and
scores them — so every prompt change is backed by data. Point it at your
project 1 prompts and prove v2 beats v1.

## Why this matters
In project 1 you caught a hallucinated interest calculation by hand. That
doesn't scale. This harness catches it automatically, every time you touch
a prompt. This is the single most hireable skill in the 3-month track:
every serious AI team runs evals; almost no junior portfolio shows one.

## Scope (keep it small)
- Local CLI. Prompts as `.txt` files, tests as JSON. No web UI, no DB.
- Two judges: keyword checks + LLM-as-judge. No embedding-similarity scoring yet.

## Weekend task list

### Day 1 — Make it run
- [x] Setup: venv, requirements, `.env` (same key as project 1)
- [x] Create `statement.txt`: from project 1's folder run
      `python -c "from src.pdf_reader import extract_text; t,_ = extract_text('statement.pdf'); open('/path/to/prompt-lab/statement.txt','w').write(t)"`
      (adapt the numbers in `tests/statement_tests.json` to YOUR statement if they differ)
- [x] `python eval.py --context statement.txt --no-judge` — keyword checks only
- [x] Read `src/judges.py` until you can explain why two judges exist
- [x] `python eval.py --context statement.txt` — full run with the LLM judge
- [x] Study the failures table: which tests does v1 fail that v2 passes?

### Day 2 — Make it yours
- [x] Write prompt `v3`: try to beat v2. Ideas: few-shot example in the system
      prompt, or an explicit "first quote the relevant lines, then answer" step.
- [x] Re-run the harness. Did v3 win? If not, read the failures and iterate —
      this loop IS the job.
- [x] Exercises in `src/judges.py`: regex judge, anti-rambling judge, consistency judge
- [x] Add 2 new test cases of your own (think: what else could go wrong?)
- [x] `git init`, commit, push to GitHub. Fill in README's "What I learned."

## Done means
- [x] `eval.py` runs clean on your statement; v2 (or v3) measurably beats v1
- [x] You can explain: why LLM-as-judge, why strict rubrics, what keywords miss
- [x] Repo public on GitHub with the comparison table in the README
- [x] The interest-hallucination test fails on v1 and passes on v2 (regression proof)

## Stretch
- Track results over time: append each run to a `runs.jsonl` and plot scores
- `--compare v1 v3`: head-to-head on one test with both answers printed
- Point the harness at a friend's prompt and evaluate theirs

## Concepts this teaches (for interviews later)
"How do you know a prompt change helped?" → golden test set + automated scoring.
"What are the limits of LLM-as-judge?" → judges have biases too; keep keyword
checks as the deterministic backstop, and spot-check verdicts by hand.
"How do you prevent regressions?" → the test set runs on every prompt edit,
like unit tests for prompts.
