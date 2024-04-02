from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class Response:
    """Response object.

    Attributes:
        response: The response text.

    """

    response: Optional[str]
    metadata: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        """Convert to string representation."""
        return self.response or "None"

    def get_formatted_sources(self, length: int = 100) -> str:
        """Get formatted sources text."""
        texts = []
        return "\n\n".join(texts)
