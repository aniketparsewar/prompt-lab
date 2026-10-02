#!/usr/bin/env python3
"""Evaluate RAG pipelines with the prompt-lab harness.

Compares vector stores built with different chunk sizes (or any stores)
against a golden test set, reusing prompt-lab's judges and report.

Each test can be repeated N times (--repeat): pass = majority of runs.
This smooths out generation flakiness AND judge noise.

Usage (from the prompt-lab folder):
    python rag_eval.py --stores ../docchat/store-200 ../docchat/store-500 ../docchat/store-1000
    python rag_eval.py --stores ../docchat/store-500 --repeat 3
    python rag_eval.py --stores ../docchat/store-500 --repeat 3 --no-judge
"""
import argparse
import importlib
import importlib.util
import sys
from pathlib import Path


def load_package(alias: str, path: Path):
    """Load a package from `path` under a different top-level name.

    Needed because docchat's code lives in a package also called `src`,
    which would collide with prompt-lab's own `src` package on a plain
    sys.path import.
    """
    if not (path / "__init__.py").exists():
        raise RuntimeError(f"docchat src not found at {path} "
                           f"(expected a sibling 'docchat' folder)")
    spec = importlib.util.spec_from_file_location(
        alias, path / "__init__.py", submodule_search_locations=[str(path)]
    )
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[alias] = pkg
    spec.loader.exec_module(pkg)
    return pkg


PROMPT_LAB = Path(__file__).resolve().parent
DOCCHAT_SRC = PROMPT_LAB.parent / "docchat" / "src"

load_package("docchat_src", DOCCHAT_SRC)
docchat_store = importlib.import_module("docchat_src.store")
docchat_rag = importlib.import_module("docchat_src.rag")

from src import judges, report, runner  # prompt-lab's own modules (via CWD)


def run_once(t, chunks, matrix, top_k, min_score, use_judge, hybrid):
    res = docchat_rag.answer(t["question"], chunks, matrix,
                             top_k=top_k, min_score=min_score,
                             hybrid=hybrid)
    kw = judges.keyword_check(t, res["answer"])
    # Citation check against the retrieved chunks as the source context.
    retrieved_ctx = "\n\n".join(chunks[i] for i in res["chunks_used"])
    cite = judges.citation_check(t, res["answer"], retrieved_ctx)

    judge_result = None
    judge_cost = 0.0
    if use_judge and t.get("rubric"):
        judge_result = judges.llm_judge(t, res["answer"])
        judge_cost = judge_result.get("cost_usd", 0.0)

    passed = (kw["passed"] and cite["passed"]
              and (judge_result is None or judge_result["passed"]))
    return {
        "test_id": t["id"],
        "question": t["question"],
        "answer": res["answer"],
        "keyword": kw,
        "citation": cite,
        "judge": judge_result,
        "passed": passed,
        "cost_usd": res["cost_usd"] + judge_cost,
    }


def evaluate_store(store_dir, tests, top_k, min_score, use_judge, repeat, hybrid):
    chunks, matrix = docchat_store.load(store_dir)
    aggregated = []
    for t in tests:
        runs = [run_once(t, chunks, matrix, top_k, min_score, use_judge,
                         hybrid)
                for _ in range(repeat)]
        passes = sum(1 for r in runs if r["passed"])
        majority_pass = passes > repeat / 2
        # Representative run: first run matching the majority outcome,
        # so the failures display shows a real example of the verdict.
        rep = next(r for r in runs if r["passed"] == majority_pass)
        aggregated.append({
            "test_id": t["id"],
            "question": t["question"],
            "answer": rep["answer"],
            "keyword": rep["keyword"],
            "citation": rep["citation"],
            "judge": rep["judge"],
            "passed": majority_pass,
            "pass_rate": f"{passes}/{repeat}",
            "cost_usd": sum(r["cost_usd"] for r in runs),
            "repeats": runs,
        })
    return aggregated, len(chunks)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate RAG vector stores against golden tests.")
    parser.add_argument("--stores", nargs="+", required=True,
                        help="Vector store directories to compare")
    parser.add_argument("--tests", default="tests/rag_sample_tests.json",
                        help="Golden test set")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.25)
    parser.add_argument("--no-judge", action="store_true",
                        help="Skip the LLM judge (keyword checks only)")
    parser.add_argument("--repeat", type=int, default=1,
                        help="Run each test N times; pass = majority vote")
    parser.add_argument("--hybrid", action="store_true",
                    help="Use hybrid (vector + keyword RRF) retrieval")

    args = parser.parse_args()

    tests = runner.load_tests(args.tests)
    results = {}
    for store_dir in args.stores:
        name = Path(store_dir).name + ("+hybrid" if args.hybrid else "")
        print(f"Running {len(tests)} tests x{args.repeat} against '{name}'...")
        runs, n_chunks = evaluate_store(store_dir, tests, args.top_k,
                                        args.min_score,
                                        use_judge=not args.no_judge,
                                        repeat=args.repeat,
                                        hybrid=args.hybrid)
        print(f"  ({n_chunks} chunks in store)")
        results[name] = runs

    report.summarize(results)
    report.failures(results)

    if args.repeat > 1:
        print("\nSTABILITY (pass rate across repeats):")
        for name, runs in results.items():
            print(f"  {name}:")
            for r in runs:
                solid = r["pass_rate"] in (f"0/{args.repeat}",
                                          f"{args.repeat}/{args.repeat}")
                flag = "" if solid else "  <-- flaky"
                print(f"    {r['pass_rate']}  {r['test_id']}{flag}")


if __name__ == "__main__":
    main()
