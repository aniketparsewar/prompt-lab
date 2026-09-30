# Prompt Lab

Versioned prompts, a golden test set, and two judges — so prompt changes are
proven with data instead of vibes.

```bash
python eval.py --context statement.txt
```

It evaluates the prompts from
(statement-explainer): `v1_baseline` is the naive prompt,
`v2_guardrailed` is the improved one. The harness shows, measurably, that the
improvement worked — including catching the hallucinated interest math.

## Setup

1. Python 3.11+, `pip install -r requirements.txt`
2. Copy `.env.example` to `.env`, add your OpenAI API key
3. Save your statement text once: from project 1's folder,
   `python -c "from src.pdf_reader import extract_text; t,_ = extract_text('statement.pdf'); open('statement.txt','w').write(t)"`
   then copy `statement.txt` here (it's gitignored)
4. `python eval.py --context statement.txt`

## How it works

```
prompts/*.txt          → one file per prompt version (v1, v2, ...)
tests/*.json          → golden test set: question + keyword checks + judge rubric
eval.py               → runs every prompt × every test, prints comparison
src/judges.py         → keyword checks (free, deterministic) + LLM-as-judge (semantic)
src/report.py         → side-by-side table + failure details
```

A test passes only if **both** judges pass. Keywords catch obvious failures;
the LLM judge catches semantic ones (e.g. invented math that contains the
right numbers).

## What I learned

- Eval-driven prompt iteration: change the prompt, re-run, keep what scores higher
- LLM-as-judge: a second model call verdicting the first, with a strict rubric
- Why keyword checks alone are insufficient (the hallucinated math passed keywords)
- Cost/quality tradeoffs per prompt version

## Exercises completed

- [x] Added a v3 prompt version and beat v2's score
- [ ] Added a regex judge for dates/amounts
- [x] Tightened the judge against rambling-but-correct answers
- [x] Added a consistency judge (same question twice at temp 0.7)
