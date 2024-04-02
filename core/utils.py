import warnings
from typing import Union, Dict, Any, Set

from pydantic.v1 import SecretStr


def get_pydantic_field_names(pydantic_cls: Any) -> Set[str]:
    """Get field names, including aliases, for a pydantic class.

    Args:
        pydantic_cls: Pydantic class."""
    all_required_field_names = set()
    for field in pydantic_cls.__fields__.values():
        all_required_field_names.add(field.name)
        if field.has_alias:
            all_required_field_names.add(field.alias)
    return all_required_field_names


def build_extra_kwargs(
        extra_kwargs: Dict[str, Any],
        values: Dict[str, Any],
        all_required_field_names: Set[str],
) -> Dict[str, Any]:
    """Build extra kwargs from values and extra_kwargs.

    Args:
        extra_kwargs: Extra kwargs passed in by user.
        values: Values passed in by user.
        all_required_field_names: All required field names for the pydantic class.
    """
    for field_name in list(values):
        if field_name in extra_kwargs:
            raise ValueError(f"Found {field_name} supplied twice.")
        if field_name not in all_required_field_names:
            warnings.warn(
                f"""WARNING! {field_name} is not default parameter.
                {field_name} was transferred to model_kwargs.
                Please confirm that {field_name} is what you intended."""
            )
            extra_kwargs[field_name] = values.pop(field_name)

    invalid_model_kwargs = all_required_field_names.intersection(extra_kwargs.keys())
    if invalid_model_kwargs:
        raise ValueError(
            f"Parameters {invalid_model_kwargs} should be specified explicitly. "
            f"Instead they were passed in as part of `model_kwargs` parameter."
        )

    return extra_kwargs


def convert_to_secret_str(value: Union[SecretStr, str]) -> SecretStr:
    """Convert a string to a SecretStr if needed."""
    if isinstance(value, SecretStr):
        return value
    return SecretStr(value)
