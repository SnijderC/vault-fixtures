import json
from typing import TextIO

from vault_fix._type import NestedStrDict


def json_serializer(data: NestedStrDict, **kwargs) -> str:
    return json.dumps(data, indent=4 if kwargs.get("pretty", False) else None)


def json_deserializer(fh: TextIO, **kwargs) -> NestedStrDict:
    return json.load(fh, **kwargs)
