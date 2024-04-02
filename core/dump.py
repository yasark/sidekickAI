import json
from typing import Any, Dict


def dumpd(obj: Any) -> Dict[str, Any]:
    """Return a json dict representation of an object."""
    # TODO: dumps is different function
    return json.loads(json.dumps(obj))