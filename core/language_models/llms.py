import inspect
import uuid
import warnings
from abc import ABC, abstractmethod
from typing import Optional, Dict, Type, List, Any, Union, cast

from pydantic import Field
from pydantic.v1 import root_validator

from core.caches import BaseCache
from core.callbacks.base import BaseCallbackManager, Callbacks
from core.dump import dumpd
from core.language_models.base import BaseLanguageModel, LanguageModelInput
from core.outputs.generation import Generation
from core.outputs.llm_results import LLMResult
from core.prompt_values import PromptValue, StringPromptValue
from core.runnables.config import RunnableConfig


def get_prompts(params, prompts):
    pass


def get_llm_cache():
    pass


class BaseLLM(BaseLanguageModel[str], ABC):
    """Base LLM abstract interface.

    It should take in a prompt and return a string."""

    # callback_manager: Optional[BaseCallbackManager] = Field(default=None, exclude=True)
    """[DEPRECATED]"""

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def invoke(
            self,
            _input: LanguageModelInput,
            config: Optional[RunnableConfig] = None,
            *,
            stop: Optional[List[str]] = None,
            **kwargs: Any,
    ) -> str:
        config = RunnableConfig()

        op = self.generate_prompt(
            [self._convert_input(_input)],
            stop=stop,
            # callbacks=config.get("callbacks"),
            tags=config.get("tags"),
            metadata=config.get("metadata"),
            run_name=config.get("run_name"),
            run_id=config.pop("run_id", None),
            **kwargs,
        )
        print("Generated prompt ", op)

        return (
            op.generations[0][0].text
        )

    def generate_prompt(
            self,
            prompts: List[PromptValue],
            stop: Optional[List[str]] = None,
            # callbacks: Optional[Union[Callbacks, List[Callbacks]]] = None,
            **kwargs: Any,
    ) -> LLMResult:
        print(prompts)
        prompt_strings = [p for p in prompts]
        return self.generate(prompt_strings, stop=stop,
                             # callbacks=callbacks,
                             **kwargs)

    def generate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            # callbacks: Optional[Union[Callbacks, List[Callbacks]]] = None,
            *,
            tags: Optional[Union[List[str], List[List[str]]]] = None,
            metadata: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
            run_name: Optional[Union[str, List[str]]] = None,
            run_id: Optional[Union[uuid.UUID, List[Optional[uuid.UUID]]]] = None,
            **kwargs: Any,
    ) -> LLMResult:
        """Pass a sequence of prompts to a model and return generations.

        This method should make use of batched calls for models that expose a batched
        API.

        Use this method when you want to:
            1. take advantage of batched calls,
            2. need more output from the model than just the top generated value,
            3. are building chains that are agnostic to the underlying language model
                type (e.g., pure text completion models vs chat models).

        Args:
            prompts: List of string prompts.
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

        output = self._generate_helper(
            prompts, stop, [], True, **kwargs)

        return output

    def _generate_helper(
            self,
            prompts: List[str],
            stop: Optional[List[str]],
            run_managers: List[Any],  # List[CallbackManagerForLLMRun],
            new_arg_supported: bool,
            **kwargs: Any,
    ) -> LLMResult:
        try:
            output = (
                self._generate(
                    prompts,
                    stop=stop,
                    # TODO: support multiple run managers
                    run_manager=run_managers[0] if run_managers else None,
                    **kwargs,
                )
                if new_arg_supported
                else self._generate(prompts, stop=stop)
            )
        except BaseException as e:
            for run_manager in run_managers:
                run_manager.on_llm_error(e, response=LLMResult(generations=[]))
            raise e

        return output

    @abstractmethod
    def _generate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            run_manager: Any = None,  # Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> LLMResult:
        """Run the LLM on the given prompts."""

        text = "This is output"
        g = Generation(
            text=text,
            generation_info={"token": str("test")}, )

        res = LLMResult(generations=[[g]], llm_output={})

        # res.generations = [[g]]

        return res

    def _convert_input(self, input):
        return input


class LLM(BaseLLM):
    """Base LLM abstract class.

    The purpose of this class is to expose a simpler interface for working
    with LLMs, rather than expect the user to implement the full _generate method.
    """

    @abstractmethod
    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Any = None,  # Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        """Run the LLM on the given prompt and input."""

    def _generate(
            self,
            prompts: List[str],
            stop: Optional[List[str]] = None,
            run_manager: Any = None,  # Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> LLMResult:
        """Run the LLM on the given prompt and input."""
        # TODO: add caching here.
        generations = []

        text = "This is output"
        g = Generation(
            text=text,
            generation_info={"token": str("test")}, )

        res = LLMResult(generations=[[g]], llm_output={})

        print("Prompt ", prompts[0])

        self._call(prompt=prompts[0], stop=stop, run_manager=run_manager, **kwargs)
        # new_arg_supported = inspect.signature(self._call).parameters.get("run_manager")
        # for prompt in prompts:
        #     text = (
        #         self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
        #         if new_arg_supported
        #         else self._call(prompt, stop=stop, **kwargs)
        #     )
        #     generations.append([Generation(text=text)])
        # return LLMResult(generations=generations)

        return res


if __name__ == '__main__':
    # Need to comment abstractmethod annotation to tun indepnt.
    bllm = BaseLLM()
    bllm.invoke("Hala!")
