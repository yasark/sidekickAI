from abc import ABC, abstractmethod
from typing import List, Literal

from core.messages import BaseMessage, HumanMessage
from core.serializable import Serializable


class PromptValue(Serializable, ABC):
    """Base abstract class for inputs to any language model.

    PromptValues can be converted to both LLM (pure text-generation) inputs and
        ChatModel inputs.
    """

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "prompt"]

    @abstractmethod
    def to_string(self) -> str:
        """Return prompt value as string."""

    @abstractmethod
    def to_messages(self) -> List[BaseMessage]:
        """Return prompt as a list of Messages."""


class StringPromptValue(PromptValue):
    """String prompt value."""

    text: str
    """Prompt text."""
    type: Literal["StringPromptValue"] = "StringPromptValue"

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "prompts", "base"]

    def to_string(self) -> str:
        """Return prompt as string."""
        return self.text

    def to_messages(self) -> List[BaseMessage]:
        """Return prompt as messages."""
        return [HumanMessage(content=self.text)]