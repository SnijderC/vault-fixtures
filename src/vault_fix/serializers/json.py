import json
from typing import Any, TextIO


def json_serializer(data: dict[str, Any], **kwargs) -> str:
    return json.dumps(data, indent=4 if kwargs.get("pretty", False) else None)


def json_deserializer(fh: TextIO, **kwargs) -> dict[str, Any]:
    return json.load(fh, **kwargs)
