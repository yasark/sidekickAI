import os
import platform
from functools import lru_cache
from typing import Dict, Any, Optional


@lru_cache(maxsize=1)
def get_runtime_environment() -> dict:
    """Get information about the LangChain runtime environment."""
    # Lazy import to avoid circular imports

    return {
        "library_version": "1.0.0",
        "library": "langchain-core",
        "platform": platform.platform(),
        "runtime": "python",
        "runtime_version": platform.python_version(),
    }


def get_from_dict_or_env(
        data: Dict[str, Any], key: str, env_key: str, default: Optional[str] = None
) -> str:
    """Get a value from a dictionary or an environment variable."""
    if key in data and data[key]:
        return data[key]
    else:
        return get_from_env(key, env_key, default=default)


def get_from_env(key: str, env_key: str, default: Optional[str] = None) -> str:
    """Get a value from a dictionary or an environment variable."""

    if env_key in os.environ and os.environ[env_key]:
        return os.environ[env_key]
    elif default is not None:
        return default
    else:
        raise ValueError(
            f"Did not find {key}, please add an environment variable"
            f" `{env_key}` which contains it, or pass"
            f" `{key}` as a named parameter."
        )


if __name__=='__main__':
    print("Starting")
    print(os.environ)
    print(os.getenv("SIDEKICK_API_KEY"))
    print(os.getenv("ANTHROPIC_API_KEY"))
    print(get_from_dict_or_env({}, "anthropic_api_key", "SIDEKICK_API_KEY"))
