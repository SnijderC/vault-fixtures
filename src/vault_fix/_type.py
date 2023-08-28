from typing_extensions import TypeAlias

NestedStrDict: TypeAlias = dict[str, "NestedStrDict | str"]
