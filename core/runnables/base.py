import inspect
from abc import ABC, abstractmethod
from typing import Generic, Optional, Type, Any

from pydantic.v1 import BaseModel
from typing_extensions import Literal, get_args

from core.runnables.config import RunnableConfig, run_in_executor
from core.runnables.utils import create_model, Input, Output
from core.serializable import Serializable

"""
Pydantic supports the creation of generic models to make it easier to reuse a common model structure.

In order to declare a generic model, you perform the following steps:

Declare one or more typing.TypeVar instances to use to parameterize your model.
Declare a pydantic model that inherits from pydantic.generics.GenericModel and typing.Generic, where you pass the TypeVar instances as parameters to typing.Generic.
Use the TypeVar instances as annotations where you will want to replace them with other types or pydantic models.
Here is an example using GenericModel to create an easily-reused HTTP response payload wrapper:
AT = TypeVar('AT')
BT = TypeVar('BT')

class Model(GenericModel, Generic[AT, BT]):
    a: AT
    b: BT
"""


class Runnable(Generic[Input, Output], ABC):
    """A unit of work that can be invoked, batched, streamed, transformed and composed.

     Key Methods
     ===========

    - **invoke/ainvoke**: Transforms a single input into an output.
    - **batch/abatch**: Efficiently transforms multiple inputs into outputs.
    - **stream/astream**: Streams output from a single input as it's produced.
    - **astream_log**: Streams output and selected intermediate results from an input.

    Built-in optimizations:

    - **Batch**: By default, batch runs invoke() in parallel using a thread pool executor.
             Override to optimize batching.

    - **Async**: Methods with "a" suffix are asynchronous. By default, they execute
             the sync counterpart using asyncio's thread pool.
             Override for native async.

    All methods accept an optional config argument, which can be used to configure
    execution, add tags and metadata for tracing and debugging etc.

    Runnables expose schematic information about their input, output and config via
    the input_schema property, the output_schema property and config_schema method.
    """

    name: Optional[str] = None
    """The name of the runnable. Used for debugging and tracing."""

    def get_name(
            self, suffix: Optional[str] = None, *, name: Optional[str] = None
    ) -> str:
        """Get the name of the runnable."""
        name = name or self.name or self.__class__.__name__
        if suffix:
            if name[0].isupper():
                return name + suffix.title()
            else:
                return name + "_" + suffix.lower()
        else:
            return name

    @property
    def InputType(self) -> Type[Input]:
        """The type of input this runnable accepts specified as a type annotation."""
        for cls in self.__class__.__orig_bases__:  # type: ignore[attr-defined]
            type_args = get_args(cls)
            print("type args")
            print(type_args)
            if type_args and len(type_args) == 2:
                return type_args[0]

        raise TypeError(
            f"Runnable {self.get_name()} doesn't have an inferable InputType. "
            "Override the InputType property to specify the input type."
        )

    @property
    def OutputType(self) -> Type[Output]:
        """The type of output this runnable produces specified as a type annotation."""
        for cls in self.__class__.__orig_bases__:  # type: ignore[attr-defined]
            type_args = get_args(cls)
            if type_args and len(type_args) == 2:
                return type_args[1]

        raise TypeError(
            f"Runnable {self.get_name()} doesn't have an inferable OutputType. "
            "Override the OutputType property to specify the output type."
        )

    @property
    def input_schema(self) -> Type[BaseModel]:
        """The type of input this runnable accepts specified as a pydantic model."""
        return self.get_input_schema()

    def get_input_schema(
            self, config: Optional[RunnableConfig] = None
    ) -> Type[BaseModel]:
        """Get a pydantic model that can be used to validate input to the runnable.

        Runnables that leverage the configurable_fields and configurable_alternatives
        methods will have a dynamic input schema that depends on which
        configuration the runnable is invoked with.

        This method allows to get an input schema for a specific configuration.

        Args:
            config: A config to use when generating the schema.

        Returns:
            A pydantic model that can be used to validate input.
        """
        root_type = self.InputType

        if inspect.isclass(root_type) and issubclass(root_type, BaseModel):
            return root_type

        print('get input schema')
        print("\t config name = " + config.get('run_name') or None)
        print("\t root_type= ", root_type)

        return create_model(
            self.get_name("Input"),
            __root__=(root_type, None),
        )

    #@abstractmethod
    def invoke(self, _input: Input, config: Optional[RunnableConfig] = None) -> Output:
        """Transform a single input into an output. Override to implement.

        Args:
            _input: The input to the runnable.
            config: A config to use when invoking the runnable.
               The config supports standard keys like 'tags', 'metadata' for tracing
               purposes, 'max_concurrency' for controlling how much work to do
               in parallel, and other keys. Please refer to the RunnableConfig
               for more details.

        Returns:
            The output of the runnable.
        """

    async def ainvoke(
            self, _input: Input, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> Output:
        """Default implementation of ainvoke, calls invoke from a thread.

        The default implementation allows usage of async code even if
        the runnable did not implement a native async version of invoke.

        Subclasses should override this method if they can run asynchronously.
        """
        return await run_in_executor(config, self.invoke, _input, config, **kwargs)


class RunnableSerializable(BaseModel, Runnable[Input, Output]):
    """Runnable that can be serialized to JSON."""

    name: Optional[str] = None
    """The name of the runnable. Used for debugging and tracing."""


if __name__ == '__main__':
    # Need to comment @abstractmethod annotation to run
    obj = Runnable()
    obj.name = "xyz"
    print(obj.name)
    print(obj.InputType)
    print(obj.OutputType)
    input_schema_model = obj.get_input_schema(RunnableConfig(run_name='config', tags=['A', 'B']))
