"""Two judges: cheap keyword checks, and an LLM judge for what keywords can't see.

A test passes only if BOTH pass. Keywords are deterministic and free;
the LLM judge catches semantic failures (like invented math that happens
to contain the right numbers).
"""
from . import llm


import re

def _norm(s: str) -> str:
    """Lowercase and strip currency formatting so '$18.07', '18.07' and '$ 18.07' all match."""
    return re.sub(r"[$,\s]", "", s).lower()


def keyword_check(test: dict, answer: str) -> dict:
    """Check must_contain / must_not_contain (case-insensitive, format-insensitive)."""
    lowered = _norm(answer)
    missing = [p for p in test.get("must_contain", []) if _norm(p) not in lowered]
    forbidden = [p for p in test.get("must_not_contain", []) if _norm(p) in lowered]
    passed = not missing and not forbidden
    details = []
    if missing:
        details.append(f"missing: {missing}")
    if forbidden:
        details.append(f"forbidden present: {forbidden}")
    return {"passed": passed, "details": "; ".join(details) or "all keyword checks ok"}


def llm_judge(test: dict, answer: str) -> dict:
    """Ask the judge model to verdict the answer against the rubric."""
    result = llm.judge(test["question"], answer, test.get("rubric", ""))
    return {
        "passed": result["verdict"] == "PASS",
        "details": result["reason"],
        "cost_usd": result["cost_usd"],
    }


# ---- EXERCISES ----
# 1. Add a "regex_check" judge: test cases get "must_match" regex patterns.
#    When is regex better than plain keywords? (Hint: dates, amounts.)
# 2. The judge can be gamed by verbose answers. Tighten JUDGE_SYSTEM in llm.py
#    to penalize answers that are correct but rambling.
# 3. Add a "consistency" judge: ask the same question twice at temperature 0.7
#    and FAIL if the two answers contradict each other.
