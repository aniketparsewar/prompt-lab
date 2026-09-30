#!/usr/bin/env python3
"""Prompt Lab — run versioned prompts against a golden test set and compare.

Usage:
    # First, save your statement text to a file (one time):
    python -c "from src.pdf_reader import extract_text; ..."  # see PROJECT_BRIEF.md

    python eval.py --context statement.txt
    python eval.py --context statement.txt --no-judge      # keyword checks only (fast/cheap)
    python eval.py --context statement.txt --prompt v2_guardrailed
"""
import argparse

from src import report, runner


def main():
    parser = argparse.ArgumentParser(description="Evaluate prompt versions against tests.")
    parser.add_argument("--context", required=True,
                        help="Text file with the context (e.g. extracted statement)")
    parser.add_argument("--prompts", default="prompts",
                        help="Directory of prompt versions (*.txt)")
    parser.add_argument("--tests", default="tests/statement_tests.json",
                        help="JSON test set")
    parser.add_argument("--prompt", default=None,
                        help="Run only this prompt version")
    parser.add_argument("--no-judge", action="store_true",
                        help="Skip the LLM judge (keyword checks only)")
    args = parser.parse_args()

    with open(args.context, encoding="utf-8") as f:
        context = f.read()

    prompts = runner.load_prompts(args.prompts)
    if args.prompt:
        if args.prompt not in prompts:
            parser.error(f"Unknown prompt version '{args.prompt}'. "
                         f"Available: {list(prompts)}")
        prompts = {args.prompt: prompts[args.prompt]}

    tests = runner.load_tests(args.tests)
    results = runner.run_all(prompts, tests, context, use_judge=not args.no_judge)
    report.summarize(results)
    report.failures(results)


if __name__ == "__main__":
    main()
