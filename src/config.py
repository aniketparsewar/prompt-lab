"""Central configuration: API keys, model choice, client setup."""
import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# A stronger model for the judge gives more reliable verdicts.
# gpt-4o-mini is fine to start; upgrade if verdicts look sloppy.
JUDGE_MODEL = os.getenv("OPENAI_JUDGE_MODEL", "gpt-4o-mini")


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env "
            "and add your key from https://platform.openai.com/api-keys"
        )
    return OpenAI(api_key=key)
