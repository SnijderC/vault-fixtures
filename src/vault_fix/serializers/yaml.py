from typing import TextIO

import yaml

from vault_fix._type import NestedStrDict


def yaml_serializer(data: NestedStrDict, **kwargs) -> str:
    return f"---\n{yaml.safe_dump(data)}"


def yaml_deserializer(fh: TextIO, **kwargs) -> NestedStrDict:
    return yaml.safe_load(fh.read(), **kwargs)
