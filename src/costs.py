"""Token counting and rough cost estimates (gpt-4o-mini)."""
import tiktoken

ENCODING = "o200k_base"

INPUT_PER_1M = 0.15
OUTPUT_PER_1M = 0.60


def count_tokens(text: str) -> int:
    enc = tiktoken.get_encoding(ENCODING)
    return len(enc.encode(text))


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (input_tokens / 1e6) * INPUT_PER_1M + (output_tokens / 1e6) * OUTPUT_PER_1M
