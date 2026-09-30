"""Raw OpenAI SDK wrappers: ask() for the candidate answers, judge() for verdicts."""
import json

from . import config
from . import costs

JUDGE_SYSTEM = """You are an impartial evaluator of AI assistant answers.
Given a QUESTION, the assistant's ANSWER, and a RUBRIC, decide PASS or FAIL.
Return JSON: {"verdict": "PASS" or "FAIL", "reason": "one sentence"}.
Be strict: partial compliance is FAIL. Do not be generous."""


def ask(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> dict:
    resp = config.get_client().chat.completions.create(
        model=config.MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
    )
    usage = resp.usage
    return {
        "answer": resp.choices[0].message.content,
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "cost_usd": costs.estimate_cost(usage.prompt_tokens, usage.completion_tokens),
    }


JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["PASS", "FAIL"]},
        "reason": {"type": "string"},
    },
    "required": ["verdict", "reason"],
    "additionalProperties": False,
}


def judge(question: str, answer: str, rubric: str) -> dict:
    """LLM-as-judge: returns {"verdict", "reason", "cost_usd"}."""
    user_prompt = (
        f"QUESTION: {question}\n\nANSWER:\n{answer}\n\nRUBRIC:\n{rubric}"
    )
    resp = config.get_client().chat.completions.create(
        model=config.JUDGE_MODEL,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "judgment", "schema": JUDGE_SCHEMA, "strict": True},
        },
    )
    usage = resp.usage
    data = json.loads(resp.choices[0].message.content)
    data["cost_usd"] = costs.estimate_cost(usage.prompt_tokens, usage.completion_tokens)
    return data
