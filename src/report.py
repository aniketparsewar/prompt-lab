"""Side-by-side comparison report: which prompt version wins, and where each fails."""


def summarize(results: dict[str, list[dict]]) -> None:
    print("\n" + "=" * 72)
    print(f"{'Prompt':<18} {'Pass':<8} {'Keyword':<10} {'Judge':<8} {'Avg $/q':<10}")
    print("=" * 72)
    for name, runs in results.items():
        n = len(runs)
        passed = sum(1 for r in runs if r["passed"])
        kw_ok = sum(1 for r in runs if r["keyword"]["passed"])
        judge_runs = [r for r in runs if r["judge"] is not None]
        judge_ok = sum(1 for r in judge_runs if r["judge"]["passed"])
        avg_cost = sum(r["cost_usd"] for r in runs) / n if n else 0
        judge_str = f"{judge_ok}/{len(judge_runs)}" if judge_runs else "-"
        print(f"{name:<18} {passed}/{n:<7} {kw_ok}/{n:<9} {judge_str:<8} ${avg_cost:<9.4f}")
    print("=" * 72)


def failures(results: dict[str, list[dict]]) -> None:
    print("\nFAILURES (this is where you improve the prompt):")
    any_fail = False
    for name, runs in results.items():
        for r in runs:
            if not r["passed"]:
                any_fail = True
                print(f"\n[{name}] {r['test_id']}: {r['question']}")
                print(f"  answer: {r['answer'][:600]}") 
                if not r["keyword"]["passed"]:
                    print(f"  keyword: {r['keyword']['details']}")
                if r["judge"] and not r["judge"]["passed"]:
                    print(f"  judge:   {r['judge']['details']}")
                if not r["citation"]["passed"]:
                    print(f"  citation: {r['citation']['details']}")
    if not any_fail:
        print("  none — all green.")
