from abc import abstractmethod, ABC
from typing import Union, Optional, List, Dict, Any, TypeVar

from pydantic import Field
from pydantic.v1 import validator

# from core.caches import BaseCache
# from core.callbacks.base import Callbacks
from core.messages import BaseMessage
from core.prompt_values import PromptValue
from core.runnables.base import Runnable, RunnableSerializable

LanguageModelInput = Union[PromptValue, str]
LanguageModelOutput = Union[BaseMessage, str]
LanguageModelOutputVar = TypeVar("LanguageModelOutputVar", BaseMessage, str)


class BaseLanguageModel(
    RunnableSerializable[LanguageModelInput, LanguageModelOutputVar],
    ABC
):
    """Abstract base class for interfacing with language models.

    All language model wrappers inherit from BaseLanguageModel.
    """

    # cache: Union[BaseCache, bool, None] = None
    # cache: Union[bool, None] = None

    """Whether to cache the response.

    * If true, will use the global cache.
    * If false, will not use a cache
    * If None, will use the global cache if it's set, otherwise no cache.
    * If instance of BaseCache, will use the provided cache.

    Caching is not currently supported for streaming methods of models.
    """
    verbose: bool = Field(default=False)
    """Whether to print out response text."""
    #callbacks: Callbacks = Field(default=None, exclude=True)
    """Callbacks to add to the run trace."""
    tags: Optional[List[str]] = Field(default=['llm'], exclude=True)
    """Tags to add to the run trace."""
    metadata: Optional[Dict[str, Any]] = Field(default=None, exclude=True)
    """Metadata to add to the run trace."""

    @validator("verbose", pre=True, always=True)
    def set_verbose(cls, verbose: Optional[bool]) -> bool:
        """If verbose is None, set it.

        This allows users to pass in None as verbose to access the global setting.
        """
        if verbose is None:
            return True
        else:
            return verbose

    # @abstractmethod
    def generate_prompt(
            self,
            prompts: str,  # List[PromptValue],
            stop: Optional[List[str]] = None,
            #callbacks: Callbacks = None,
            **kwargs: Any,
    ) -> str:  # LLMResult:
        """Pass a sequence of prompts to the model and return model generations.

        This method should make use of batched calls for models that expose a batched
        API.

        Use this method when you want to:
            1. take advantage of batched calls,
            2. need more output from the model than just the top generated value,
            3. are building chains that are agnostic to the underlying language model
                type (e.g., pure text completion models vs chat models).

        Args:
            prompts: List of PromptValues. A PromptValue is an object that can be
                converted to match the format of any language model (string for pure
                text generation models and BaseMessages for chat models).
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of these substrings.
            callbacks: Callbacks to pass through. Used for executing additional
                functionality, such as logging or streaming, throughout generation.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            An LLMResult, which contains a list of candidate Generations for each input
                prompt and additional model provider-specific output.
        """

        return "This is a prompt"


if __name__ == '__main__':

    model = BaseLanguageModel(name="SidekickBase", verbose=True)
    print(model)
