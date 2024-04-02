"""
 BaseLanguageModel
    --> BaseLLM [ invoke() -> generate_prompt() -> generate() -> _generate_helper() -> _generate():abstract]
        --> LLM(_call:abstract) [_generate() -> _call()]
            --> <name>(_call:override)
"""
from abc import ABC

from pydantic.v1 import Field, BaseModel
from typing import Any, Optional, List, Dict, Mapping

from pydantic import SecretStr
from pydantic.v1 import root_validator

from core.env import get_from_dict_or_env
from core.language_models.ModelClient import SideKickClient
from core.language_models.base import BaseLanguageModel
from core.language_models.llms import LLM
from core.utils import convert_to_secret_str, get_pydantic_field_names, build_extra_kwargs


class SideKickCommon(BaseLanguageModel):

    client: Any = None  #: :meta private:
    async_client: Any = None  #: :meta private:

    model: str = Field(default="sidekick", alias="model_name")
    """Model name to use."""

    max_tokens_to_sample: int = Field(default=256, alias="max_tokens")
    """Denotes the number of tokens to predict per generation."""

    temperature: Optional[float] = None
    """A non-negative float that tunes the degree of randomness in generation."""

    top_k: Optional[int] = None
    """Number of most likely tokens to consider at each step."""

    top_p: Optional[float] = None
    """Total probability mass of tokens to consider at each step."""

    streaming: bool = False
    """Whether to stream the results."""

    default_request_timeout: Optional[float] = None
    """Timeout for requests to Anthropic Completion API. Default is 600 seconds."""

    max_retries: int = 2
    """Number of retries allowed for requests sent to the Anthropic Completion API."""

    anthropic_api_url: Optional[str] = None

    # anthropic_api_key: Optional[SecretStr] = None

    anthropic_api_key: str = "sk_apikey"

    HUMAN_PROMPT: Optional[str] = None

    AI_PROMPT: Optional[str] = None

    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    @root_validator(pre=True)
    def build_extra(cls, values: Dict) -> Dict:
        extra = values.get("model_kwargs", {})
        all_required_field_names = get_pydantic_field_names(cls)
        values["model_kwargs"] = build_extra_kwargs(
            extra, values, all_required_field_names
        )
        return values

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""

        print("Running root validator")
        print(values)

        values["anthropic_api_key"] = convert_to_secret_str(
            get_from_dict_or_env(values, "anthropic_api_key", "ANTHROPIC_API_KEY")
        )

        # Get custom api url from environment.
        # values["anthropic_api_url"] = get_from_dict_or_env(
        #     values,
        #     "anthropic_api_url",
        #     "ANTHROPIC_API_URL",
        #     default="https://api.anthropic.com",
        # )

        try:
            # import anthropic

            # check_package_version("anthropic", gte_version="0.3")

            # values["client"] = anthropic.Anthropic(
            #     base_url=values["anthropic_api_url"],
            #     api_key=values["anthropic_api_key"].get_secret_value(),
            #     timeout=values["default_request_timeout"],
            #     max_retries=values["max_retries"],
            # )

            values["client"] = SideKickClient(
                base_url='localhost',
                api_key='sk_123',
                timeout=10,
                max_retries=3
            )

            values['HUMAN_PROMPT'] = 'THIS IS HUMAN PROMPT'

            # values["async_client"] = anthropic.AsyncAnthropic(
            #     base_url=values["anthropic_api_url"],
            #     api_key=values["anthropic_api_key"].get_secret_value(),
            #     timeout=values["default_request_timeout"],
            #     max_retries=values["max_retries"],
            # )
            # values["HUMAN_PROMPT"] = anthropic.HUMAN_PROMPT
            # values["AI_PROMPT"] = anthropic.AI_PROMPT
            # values["count_tokens"] = values["client"].count_tokens

        except ImportError:
            raise ImportError(
                "Could not import anthropic python package. "
                "Please it install it with `pip install anthropic`."
            )

        return values

    def _get_anthropic_stop(self, stop: Optional[List[str]] = None) -> List[str]:

        if not self.HUMAN_PROMPT or not self.AI_PROMPT:
            raise NameError("Please ensure the anthropic package is loaded")

        if stop is None:
            stop = []

        # Never want model to invent new turns of Human / Assistant dialog.
        stop.extend([self.HUMAN_PROMPT])

        return stop

    @property
    def _default_params(self) -> Mapping[str, Any]:
        """Get the default parameters for calling Anthropic API."""
        d = {
            "max_tokens_to_sample": self.max_tokens_to_sample,
            "model": self.model,
        }
        if self.temperature is not None:
            d["temperature"] = self.temperature
        if self.top_k is not None:
            d["top_k"] = self.top_k
        if self.top_p is not None:
            d["top_p"] = self.top_p

        print(d)
        print(self.model_kwargs)

        return {**d}


class CallbackManagerForLLMRun:
    pass


class SideKickModel(SideKickCommon, LLM):
    """Sidekick large language models.

       To you should have the ``anthropic`` python package installed, and the
       environment variable ``ANTHROPIC_API_KEY`` set with your API key, or pass
       it as a named parameter to the constructor.

       Example:
           .. code-block:: python

               import anthropic
               from langchain_community.llms import Anthropic

               model = Anthropic(model="<model_name>", anthropic_api_key="my-api-key")

               # Simplest invocation, automatically wrapped with HUMAN_PROMPT
               # and AI_PROMPT.
               response = model("What are the biggest risks facing humanity?")

               # Or if you want to use the chat mode, build a few-shot-prompt, or
               # put words in the Assistant's mouth, use HUMAN_PROMPT and AI_PROMPT:
               raw_prompt = "What are the biggest risks facing humanity?"
               prompt = f"{anthropic.HUMAN_PROMPT} {prompt}{anthropic.AI_PROMPT}"
               response = model(prompt)
       """

    class Config:
        """Configuration for this pydantic object."""

        allow_population_by_field_name = True
        arbitrary_types_allowed = True

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "sideKick-llm"

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Any = None,  # Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        r"""Call out to Anthropic's completion endpoint.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                prompt = "What are the biggest risks facing humanity?"
                prompt = f"\n\nHuman: {prompt}\n\nAssistant:"
                response = model(prompt)

        """
        stop = []  # self._get_anthropic_stop(stop)
        params = {**self._default_params, **kwargs}

        print("We are inside call function")

        print("Processing ....")

        print("client = ", self.client)

        response = self.client.completions.create(
            prompt=self._wrap_prompt(prompt),
            stop_sequences=stop,
            **params,
        )
        return response.completion


if __name__ == '__main__':
    sModel = SideKickModel(name='SideKickModel', verbose=True)
    print(sModel)

    sModel.invoke(_input='This is a prompt')
