from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel

from core.serializable import Serializable


class Generation(BaseModel):
    """A single text generation output."""

    text: str
    """Generated text output."""

    generation_info: Optional[Dict[str, Any]] = None
    """Raw response from the provider. May include things like the 
        reason for finishing or token log probabilities.
    """
    type: Literal["Generation"] = "Generation"
    """Type is used exclusively for serialization purposes."""
    # TODO: add log probs as separate attribute