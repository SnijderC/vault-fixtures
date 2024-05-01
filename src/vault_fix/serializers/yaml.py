from typing import Any, TextIO

import yaml


def yaml_serializer(data: dict, **kwargs) -> str:
    return f"---\n{yaml.safe_dump(data)}"


def yaml_deserializer(fh: TextIO, **kwargs) -> dict[str, Any]:
    return yaml.safe_load(fh.read(), **kwargs)
