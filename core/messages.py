from typing import List, Union, Dict, Optional, Any

from pydantic import Field, Extra

from core.serializable import Serializable

from typing import List, Literal


class BaseMessage(Serializable):
    """Base abstract Message class.

    Messages are the inputs and outputs of ChatModels.
    """

    content: Union[str, List[Union[str, Dict]]]
    """The string contents of the message."""

    additional_kwargs: dict = Field(default_factory=dict)
    """Reserved for additional payload data associated with the message.

    For example, for a message from an AI, this could include tool calls."""

    response_metadata: dict = Field(default_factory=dict)
    """Response metadata. For example: response headers, logprobs, token counts."""

    type: str

    name: Optional[str] = None

    id: Optional[str] = None

    class Config:
        extra = Extra.allow

    def __init__(
            self, content: Union[str, List[Union[str, Dict]]], **kwargs: Any
    ) -> None:
        """Pass in content as positional arg."""
        return super().__init__(content=content, **kwargs)

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "messages"]


class HumanMessage(BaseMessage):
    """Message from a human."""

    example: bool = False
    """Whether this Message is being passed in to the model as part of an example 
        conversation.
    """

    type: Literal["human"] = "human"

    @classmethod
    def get_lc_namespace(cls) -> List[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "messages"]
