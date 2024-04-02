from functools import lru_cache
from typing import Any, Type, TypeVar

from pydantic.v1 import create_model as _create_model_base, BaseModel, BaseConfig, ConfigDict


class _SchemaConfig(BaseConfig):
    arbitrary_types_allowed = True
    frozen = True


def create_model(
        __model_name: str,
        **field_definitions: Any,
) -> Type[BaseModel]:

    print("create model")
    print("\t", __model_name)
    try:
        return _create_model_cached(__model_name, **field_definitions)
    except TypeError:
        # something in field definitions is not hashable
        return _create_model_base(
            __model_name, __config__=_SchemaConfig, **field_definitions
        )


@lru_cache(maxsize=256)
def _create_model_cached(
        __model_name: str,
        **field_definitions: Any,
) -> Type[BaseModel]:
    print(_SchemaConfig)
    print(field_definitions)
    return _create_model_base(
        __model_name, __config__=_SchemaConfig, **field_definitions
    )


Input = TypeVar("Input", contravariant=True)
# Output type should implement __concat__, as eg str, list, dict do
Output = TypeVar("Output", covariant=True)


class Age(BaseModel):
    __root__: int


if __name__ == '__main__':

    TestModel = _create_model_base('base_model', __config__=_SchemaConfig, name=(str, ...))
    print(TestModel(name='Test'))
    # name='Test'

    # Defining generic
    TestModel = _create_model_base('base_model', __config__=_SchemaConfig, name=(Input, ...))

    print(TestModel.schema())
    print(TestModel(name='Test-2'))
    # name = 'Test-2'

    print(TestModel(name=33))
    # name = 33

    age_model = Age(__root__=42)
    print(age_model.schema())
    print(age_model == Age(__root__=42))

