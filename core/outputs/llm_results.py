from copy import deepcopy
from typing import List, Optional

from pydantic import BaseModel

from core.outputs.generation import Generation


class LLMResult(BaseModel):
    """Class that contains all results for a batched LLM call."""

    generations: List[List[Generation]]
    """List of generated outputs. This is a List[List[]] because
    each input could have multiple candidate generations."""
    llm_output: Optional[dict] = None
    """Arbitrary LLM provider-specific output."""


if __name__ == "__main__":
    g = Generation(
        text="test",
        generation_info={"token": "test"})
    print(g)
    d = [[g]]
    print(d[0][0])
    x = LLMResult(generations=d)

    print(x)
