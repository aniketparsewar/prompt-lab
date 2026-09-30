"""Load prompt versions and test cases; run the full matrix."""
import json
from pathlib import Path

from . import judges, llm


def load_prompts(prompts_dir: str) -> dict[str, str]:
    """Each prompts/*.txt file is one version: filename (sans ext) -> prompt text."""
    versions = {}
    for path in sorted(Path(prompts_dir).glob("*.txt")):
        versions[path.stem] = path.read_text(encoding="utf-8").strip()
    if not versions:
        raise RuntimeError(f"No prompt versions found in {prompts_dir}")
    return versions


def load_tests(tests_path: str) -> list[dict]:
    with open(tests_path, encoding="utf-8") as f:
        tests = json.load(f)
    if not tests:
        raise RuntimeError(f"No tests found in {tests_path}")
    return tests


def run_one(system_prompt: str, test: dict, context: str,
            use_judge: bool = True, temperature: float = 0.2) -> dict:
    user_prompt = (
        f"CONTEXT:\n---\n{context}\n---\n\n"
        f"QUESTION: {test['question']}\n\n"
        f"Answer based only on the context above."
    )
    resp = llm.ask(system_prompt, user_prompt, temperature=temperature)

    kw = judges.keyword_check(test, resp["answer"])
    cite = judges.citation_check(test, resp["answer"], context)

    judge_result = None
    judge_cost = 0.0
    if use_judge and test.get("rubric"):
        judge_result = judges.llm_judge(test, resp["answer"])
        judge_cost = judge_result.get("cost_usd", 0.0)

    passed = (
        kw["passed"]
        and cite["passed"]
        and (judge_result is None or judge_result["passed"])
    )
    return {
        "test_id": test["id"],
        "question": test["question"],
        "answer": resp["answer"],
        "keyword": kw,
        "citation": cite,
        "judge": judge_result,
        "passed": passed,
        "cost_usd": resp["cost_usd"] + judge_cost,
        "input_tokens": resp["input_tokens"],
        "output_tokens": resp["output_tokens"],
    }


def run_all(prompts: dict[str, str], tests: list[dict], context: str,
            use_judge: bool = True) -> dict[str, list[dict]]:
    """Returns {prompt_version: [per-test results]}."""
    all_results = {}
    for name, system_prompt in prompts.items():
        print(f"Running {len(tests)} tests against '{name}'...")
        all_results[name] = [
            run_one(system_prompt, t, context, use_judge=use_judge) for t in tests
        ]
    return all_results
