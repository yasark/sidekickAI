from __future__ import annotations

from typing import Any, List, Literal
from pydantic.v1 import Field, BaseModel


class Document(BaseModel):
    """Class for storing a piece of text and associated metadata."""

    page_content: str
    """String text."""
    metadata: dict = Field(default_factory=dict)
    """Arbitrary metadata about the page content (e.g., source, relationships to other
        documents, etc.).
    """
    type: Literal["Document"] = "Document"

    def __init__(self, page_content: str, **kwargs: Any) -> None:
        """Pass page_content in as positional or named arg."""
        super().__init__(page_content=page_content, **kwargs)


if __name__ == '__main__':
    d = Document(page_content="This is a page", size=10)
    print(d)

