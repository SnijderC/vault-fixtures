from typing import TypeAlias

NestedStrDict: TypeAlias = dict[str, "NestedStrDict | str"]
